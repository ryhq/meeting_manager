# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Conflict Detection and Availability Validation Utilities

This module provides core validation functions for checking member availability,
detecting scheduling conflicts, and validating booking requests.
"""

import frappe
from frappe.utils import getdate, get_time, get_datetime, add_to_date, now_datetime
from datetime import datetime, timedelta, time
import json


def check_member_availability(member, scheduled_date, scheduled_start_time, duration_minutes, exclude_booking=None):
	"""
	Check if a member is available at the specified date/time

	Args:
		member (str): User ID of the member
		scheduled_date (date or str): Date of the booking
		scheduled_start_time (time or str): Start time of the booking
		duration_minutes (int): Duration of the meeting in minutes
		exclude_booking (str, optional): Booking ID to exclude from conflict check (for updates)

	Returns:
		dict: {
			"available": bool,
			"conflicts": list of conflict details,
			"reason": str (if not available)
		}
	"""
	# Convert inputs to proper types
	scheduled_date = getdate(scheduled_date)
	scheduled_start_time = get_time(scheduled_start_time)

	# Calculate end time
	start_datetime = datetime.combine(scheduled_date, scheduled_start_time)
	end_datetime = start_datetime + timedelta(minutes=duration_minutes)
	scheduled_end_time = end_datetime.time()

	conflicts = []

	# 1. Check working hours
	working_hours_check = check_working_hours(member, scheduled_date, scheduled_start_time, scheduled_end_time)
	if not working_hours_check["available"]:
		conflicts.append({
			"type": "working_hours",
			"message": working_hours_check["reason"]
		})

	# 2. Check date overrides (vacations, special availability)
	date_override_check = check_date_overrides(member, scheduled_date, scheduled_start_time, scheduled_end_time)
	if not date_override_check["available"]:
		conflicts.append({
			"type": "date_override",
			"message": date_override_check["reason"]
		})

	# 3. Check existing bookings
	booking_conflicts = check_booking_conflicts(member, scheduled_date, scheduled_start_time, scheduled_end_time, exclude_booking)
	if booking_conflicts:
		conflicts.extend([{
			"type": "booking_conflict",
			"booking_id": conflict["booking_id"],
			"message": conflict["message"]
		} for conflict in booking_conflicts])

	# 4. Check synced calendar events
	calendar_conflicts = check_calendar_event_conflicts(member, start_datetime, end_datetime)
	if calendar_conflicts:
		conflicts.extend([{
			"type": "calendar_event",
			"event_title": conflict["event_title"],
			"message": conflict["message"]
		} for conflict in calendar_conflicts])

	# 5. Check buffer times
	buffer_conflicts = check_buffer_time_conflicts(member, start_datetime, end_datetime, exclude_booking)
	if buffer_conflicts:
		conflicts.extend([{
			"type": "buffer_time",
			"message": conflict["message"]
		} for conflict in buffer_conflicts])

	# 6. Check availability rules (max bookings per day/week)
	availability_rule_check = check_availability_rules(member, scheduled_date)
	if not availability_rule_check["available"]:
		conflicts.append({
			"type": "availability_rule",
			"message": availability_rule_check["reason"]
		})

	return {
		"available": len(conflicts) == 0,
		"conflicts": conflicts,
		"reason": conflicts[0]["message"] if conflicts else None
	}


def check_working_hours(member, scheduled_date, start_time, end_time):
	"""
	Check if the time falls within member's working hours

	Returns:
		dict: {"available": bool, "reason": str}
	"""
	# Get user settings
	user_settings = frappe.get_value(
		"MM User Settings",
		{"user": member},
		["working_hours_json"],
		as_dict=True
	)

	if not user_settings or not user_settings.working_hours_json:
		# No working hours defined - assume 24/7 availability
		return {"available": True, "reason": None}

	try:
		working_hours = json.loads(user_settings.working_hours_json)
	except (json.JSONDecodeError, TypeError):
		# Invalid JSON - assume 24/7 availability
		return {"available": True, "reason": None}

	# Get day of week (0 = Monday, 6 = Sunday)
	day_of_week = scheduled_date.weekday()
	day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
	day_name = day_names[day_of_week]

	day_config = working_hours.get(day_name, {})

	# Check if day is enabled
	if not day_config.get("enabled", False):
		return {
			"available": False,
			"reason": f"Member is not available on {day_name.capitalize()}s"
		}

	# Check if time is within working hours
	work_start = get_time(day_config.get("start", "00:00"))
	work_end = get_time(day_config.get("end", "23:59"))

	if start_time < work_start or end_time > work_end:
		return {
			"available": False,
			"reason": f"Time is outside working hours ({work_start.strftime('%H:%M')} - {work_end.strftime('%H:%M')})"
		}

	return {"available": True, "reason": None}


def check_date_overrides(member, scheduled_date, start_time, end_time):
	"""
	Check date-specific overrides (vacations, special availability)

	Returns:
		dict: {"available": bool, "reason": str}
	"""
	# Get user's availability rules with date overrides
	availability_rules = frappe.get_all(
		"MM User Availability Rule",
		filters={"user": member},
		fields=["name", "is_default"]
	)

	if not availability_rules:
		return {"available": True, "reason": None}

	# Check all rules for date overrides
	for rule in availability_rules:
		# Get date overrides for this rule
		overrides = frappe.get_all(
			"MM User Date Overrides",
			filters={
				"parent": rule.name,
				"parenttype": "MM User Availability Rule",
				"date": scheduled_date
			},
			fields=["available", "custom_hours_start", "custom_hours_end", "reason"]
		)

		for override in overrides:
			if not override.available:
				reason = override.reason or "Member is not available on this date"
				return {
					"available": False,
					"reason": reason
				}

			# If available with custom hours, check if time falls within custom hours
			if override.custom_hours_start and override.custom_hours_end:
				custom_start = get_time(override.custom_hours_start)
				custom_end = get_time(override.custom_hours_end)

				if start_time < custom_start or end_time > custom_end:
					return {
						"available": False,
						"reason": f"Time is outside custom hours for this date ({custom_start.strftime('%H:%M')} - {custom_end.strftime('%H:%M')})"
					}

	return {"available": True, "reason": None}


def check_booking_conflicts(member, scheduled_date, start_time, end_time, exclude_booking=None):
	"""
	Check for overlapping bookings

	Returns:
		list: List of conflicting bookings
	"""
	# Convert date + time to datetime for comparison
	scheduled_start_datetime = datetime.combine(scheduled_date, start_time)
	scheduled_end_datetime = datetime.combine(scheduled_date, end_time)

	# Query bookings where member is assigned (via child table)
	# Use SQL query to join with child table
	query = """
		SELECT DISTINCT
			mb.name,
			mb.start_datetime,
			mb.end_datetime,
			mb.meeting_type
		FROM `tabMM Meeting Booking` mb
		INNER JOIN `tabMM Meeting Booking Assigned User` au
			ON au.parent = mb.name AND au.parenttype = 'MM Meeting Booking'
		WHERE au.user = %(member)s
			AND mb.booking_status IN ('Confirmed', 'Pending')
			AND mb.start_datetime < %(end_datetime)s
			AND mb.end_datetime > %(start_datetime)s
			{exclude_condition}
	""".format(
		exclude_condition=f"AND mb.name != %(exclude_booking)s" if exclude_booking else ""
	)

	params = {
		"member": member,
		"start_datetime": scheduled_start_datetime,
		"end_datetime": scheduled_end_datetime
	}

	if exclude_booking:
		params["exclude_booking"] = exclude_booking

	existing_bookings = frappe.db.sql(query, params, as_dict=True)

	conflicts = []
	for booking in existing_bookings:
		# Convert to time for display
		booking_start = get_datetime(booking.start_datetime).time()
		booking_end = get_datetime(booking.end_datetime).time()

		conflicts.append({
			"booking_id": booking.name,
			"message": f"Conflicts with existing booking {booking.name} ({booking_start.strftime('%H:%M')} - {booking_end.strftime('%H:%M')})"
		})

	return conflicts


def check_calendar_event_conflicts(member, start_datetime, end_datetime):
	"""
	Check for conflicts with synced external calendar events

	Returns:
		list: List of conflicting calendar events
	"""
	# Get calendar event syncs for this member (join with calendar_integration to get user)
	query = """
		SELECT
			ces.name,
			ces.event_title,
			ces.start_datetime,
			ces.end_datetime
		FROM `tabMM Calendar Event Sync` ces
		INNER JOIN `tabMM Calendar Integration` ci
			ON ces.calendar_integration = ci.name
		WHERE ci.user = %(member)s
			AND ces.is_blocking_availability = 1
			AND ces.event_type != 'All-Day Event'
			AND ces.sync_status = 'Synced'
			AND ces.start_datetime < %(end_datetime)s
			AND ces.end_datetime > %(start_datetime)s
	"""

	params = {
		"member": member,
		"start_datetime": start_datetime,
		"end_datetime": end_datetime
	}

	calendar_events = frappe.db.sql(query, params, as_dict=True)

	conflicts = []
	for event in calendar_events:
		event_start = get_datetime(event.start_datetime)
		event_end = get_datetime(event.end_datetime)

		conflicts.append({
			"event_title": event.event_title or "Busy",
			"message": f"Conflicts with calendar event: {event.event_title or 'Busy'} ({event_start.strftime('%H:%M')} - {event_end.strftime('%H:%M')})"
		})

	return conflicts


def check_buffer_time_conflicts(member, start_datetime, end_datetime, exclude_booking=None):
	"""
	Check if buffer times are respected between meetings

	Returns:
		list: List of buffer time violations
	"""
	# Get user's availability rules for buffer times
	availability_rules = frappe.get_all(
		"MM User Availability Rule",
		filters={"user": member},
		fields=["buffer_time_before", "buffer_time_after", "is_default"],
		order_by="is_default desc",
		limit=1
	)

	if not availability_rules:
		return []

	rule = availability_rules[0]
	buffer_before = rule.buffer_time_before or 0
	buffer_after = rule.buffer_time_after or 0

	if buffer_before == 0 and buffer_after == 0:
		return []

	# Calculate buffer windows
	buffer_start = start_datetime - timedelta(minutes=buffer_before)
	buffer_end = end_datetime + timedelta(minutes=buffer_after)

	# Check for bookings within buffer windows using child table join
	# Note: assigned_to field doesn't exist on MM Meeting Booking, need to query through child table
	query = """
		SELECT DISTINCT
			mb.name,
			mb.start_datetime,
			mb.end_datetime
		FROM `tabMM Meeting Booking` mb
		INNER JOIN `tabMM Meeting Booking Assigned User` au
			ON au.parent = mb.name AND au.parenttype = 'MM Meeting Booking'
		WHERE au.user = %(member)s
			AND DATE(mb.start_datetime) = %(scheduled_date)s
			AND mb.booking_status IN ('Confirmed', 'Pending')
			AND (
				(mb.start_datetime >= %(buffer_start)s AND mb.start_datetime < %(buffer_end)s)
				OR (mb.end_datetime > %(buffer_start)s AND mb.end_datetime <= %(buffer_end)s)
			)
			{exclude_condition}
	""".format(
		exclude_condition="AND mb.name != %(exclude_booking)s" if exclude_booking else ""
	)

	params = {
		"member": member,
		"scheduled_date": start_datetime.date(),
		"buffer_start": buffer_start,
		"buffer_end": buffer_end
	}

	if exclude_booking:
		params["exclude_booking"] = exclude_booking

	nearby_bookings = frappe.db.sql(query, params, as_dict=True)

	conflicts = []
	for booking in nearby_bookings:
		booking_start = get_datetime(booking.start_datetime)
		booking_end = get_datetime(booking.end_datetime)

		# Check if booking violates buffer zones
		if not (booking_end <= buffer_start or booking_start >= buffer_end):
			if booking_end > buffer_start and booking_end <= start_datetime:
				conflicts.append({
					"message": f"Violates {buffer_before}-minute buffer before meeting (conflicts with {booking.name})"
				})
			elif booking_start < buffer_end and booking_start >= end_datetime:
				conflicts.append({
					"message": f"Violates {buffer_after}-minute buffer after meeting (conflicts with {booking.name})"
				})

	return conflicts


def check_availability_rules(member, scheduled_date):
	"""
	Check if member has reached max bookings per day/week limits

	Returns:
		dict: {"available": bool, "reason": str}
	"""
	# Get user's availability rules
	availability_rules = frappe.get_all(
		"MM User Availability Rule",
		filters={"user": member},
		fields=["max_bookings_per_day", "max_bookings_per_week", "is_default"],
		order_by="is_default desc",
		limit=1
	)

	if not availability_rules:
		return {"available": True, "reason": None}

	rule = availability_rules[0]

	# Check max bookings per day
	if rule.max_bookings_per_day:
		# Count bookings through child table
		query = """
			SELECT COUNT(DISTINCT mb.name) as count
			FROM `tabMM Meeting Booking` mb
			INNER JOIN `tabMM Meeting Booking Assigned User` au
				ON au.parent = mb.name AND au.parenttype = 'MM Meeting Booking'
			WHERE au.user = %(member)s
				AND DATE(mb.start_datetime) = %(scheduled_date)s
				AND mb.booking_status IN ('Confirmed', 'Pending')
		"""
		result = frappe.db.sql(query, {"member": member, "scheduled_date": scheduled_date}, as_dict=True)
		day_bookings = result[0].count if result else 0

		if day_bookings >= rule.max_bookings_per_day:
			return {
				"available": False,
				"reason": f"Member has reached maximum bookings per day ({rule.max_bookings_per_day})"
			}

	# Check max bookings per week
	if rule.max_bookings_per_week:
		# Calculate week start (Monday) and end (Sunday)
		week_start = scheduled_date - timedelta(days=scheduled_date.weekday())
		week_end = week_start + timedelta(days=6)

		# Count bookings through child table
		query = """
			SELECT COUNT(DISTINCT mb.name) as count
			FROM `tabMM Meeting Booking` mb
			INNER JOIN `tabMM Meeting Booking Assigned User` au
				ON au.parent = mb.name AND au.parenttype = 'MM Meeting Booking'
			WHERE au.user = %(member)s
				AND DATE(mb.start_datetime) BETWEEN %(week_start)s AND %(week_end)s
				AND mb.booking_status IN ('Confirmed', 'Pending')
		"""
		result = frappe.db.sql(query, {"member": member, "week_start": week_start, "week_end": week_end}, as_dict=True)
		week_bookings = result[0].count if result else 0

		if week_bookings >= rule.max_bookings_per_week:
			return {
				"available": False,
				"reason": f"Member has reached maximum bookings per week ({rule.max_bookings_per_week})"
			}

	return {"available": True, "reason": None}


def validate_minimum_notice(member, scheduled_datetime):
	"""
	Check if booking respects minimum notice period

	Args:
		member (str): User ID
		scheduled_datetime (datetime): Scheduled start datetime

	Returns:
		dict: {"valid": bool, "reason": str}
	"""
	# Get user's availability rules
	availability_rules = frappe.get_all(
		"MM User Availability Rule",
		filters={"user": member},
		fields=["min_notice_hours", "is_default"],
		order_by="is_default desc",
		limit=1
	)

	if not availability_rules or not availability_rules[0].min_notice_hours:
		return {"valid": True, "reason": None}

	min_notice_hours = availability_rules[0].min_notice_hours
	min_allowed_datetime = now_datetime() + timedelta(hours=min_notice_hours)

	if scheduled_datetime < min_allowed_datetime:
		return {
			"valid": False,
			"reason": f"Booking requires at least {min_notice_hours} hours notice"
		}

	return {"valid": True, "reason": None}


def validate_advance_booking_window(member, scheduled_date):
	"""
	Check if booking is within the allowed advance booking window

	Args:
		member (str): User ID
		scheduled_date (date): Scheduled date

	Returns:
		dict: {"valid": bool, "reason": str}
	"""
	# Get user's availability rules
	availability_rules = frappe.get_all(
		"MM User Availability Rule",
		filters={"user": member},
		fields=["max_days_advance", "is_default"],
		order_by="is_default desc",
		limit=1
	)

	if not availability_rules or not availability_rules[0].max_days_advance:
		return {"valid": True, "reason": None}

	max_days_advance = availability_rules[0].max_days_advance
	max_allowed_date = getdate() + timedelta(days=max_days_advance)

	if scheduled_date > max_allowed_date:
		return {
			"valid": False,
			"reason": f"Booking is too far in advance (maximum {max_days_advance} days)"
		}

	return {"valid": True, "reason": None}
