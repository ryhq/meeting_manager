# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Department Availability Calculator Service

This module calculates availability for departments by aggregating
individual member availability. Used for public booking interface.
"""

import frappe
from frappe.utils import getdate, get_time, get_datetime, add_to_date
from datetime import datetime, timedelta, time
from meeting_manager.meeting_manager.utils.validation import check_member_availability, validate_minimum_notice, validate_advance_booking_window
from meeting_manager.meeting_manager.utils.timezone import get_department_timezone, convert_from_utc, convert_to_utc
import json


def get_department_available_dates(department_slug, meeting_type_slug, month, year):
	"""
	Get available dates for a department/meeting type combination

	A date is available if AT LEAST ONE active member is available for the entire meeting duration

	Args:
		department_slug (str): Department slug
		meeting_type_slug (str): Meeting type slug
		month (int): Month (1-12)
		year (int): Year

	Returns:
		dict: {
			"available_dates": list of date strings,
			"timezone": department timezone,
			"department": department name,
			"meeting_type": meeting type name
		}
	"""
	# Get department
	department = frappe.get_value(
		"MM Department",
		{"department_slug": department_slug, "is_active": 1},
		["name", "department_name", "timezone"],
		as_dict=True
	)

	if not department:
		frappe.throw(f"Department '{department_slug}' not found or inactive")

	# Get meeting type
	meeting_type = frappe.get_value(
		"MM Meeting Type",
		{
			"meeting_slug": meeting_type_slug,
			"department": department.name,
			"is_active": 1,
			"is_public": 1
		},
		["name", "meeting_name", "duration"],
		as_dict=True
	)

	if not meeting_type:
		frappe.throw(f"Meeting type '{meeting_type_slug}' not found or inactive")

	# Get active department members
	members = frappe.get_all(
		"MM Department Member",
		filters={
			"parent": department.name,
			"parenttype": "MM Department",
			"is_active": 1
		},
		fields=["member"]
	)

	if not members:
		return {
			"available_dates": [],
			"timezone": department.timezone or "UTC",
			"department": department.department_name,
			"meeting_type": meeting_type.meeting_name
		}

	member_ids = [m.member for m in members]

	# Calculate date range for the month
	start_date = getdate(f"{year}-{month:02d}-01")
	if month == 12:
		end_date = getdate(f"{year + 1}-01-01") - timedelta(days=1)
	else:
		end_date = getdate(f"{year}-{month + 1:02d}-01") - timedelta(days=1)

	# Iterate through each date in the month
	available_dates = []
	current_date = start_date

	while current_date <= end_date:
		# Check if date is in the past
		if current_date < getdate():
			current_date += timedelta(days=1)
			continue

		# Check if any member is available on this date
		date_has_availability = False

		for member in member_ids:
			# Check advance booking window
			advance_check = validate_advance_booking_window(member, current_date)
			if not advance_check["valid"]:
				continue

			# Check if member has any availability on this date
			if has_member_availability_on_date(member, current_date, meeting_type.duration):
				date_has_availability = True
				break

		if date_has_availability:
			available_dates.append(current_date.strftime("%Y-%m-%d"))

		current_date += timedelta(days=1)

	return {
		"available_dates": available_dates,
		"timezone": department.timezone or "UTC",
		"department": department.department_name,
		"meeting_type": meeting_type.meeting_name
	}


def get_department_available_slots(department_slug, meeting_type_slug, date, visitor_timezone=None):
	"""
	Get available time slots for a specific date

	Shows slots where AT LEAST ONE member is available

	Args:
		department_slug (str): Department slug
		meeting_type_slug (str): Meeting type slug
		date (str): Date (YYYY-MM-DD)
		visitor_timezone (str, optional): Visitor's timezone for display

	Returns:
		dict: {
			"slots": list of time slot objects,
			"date": date string,
			"timezone": department timezone,
			"visitor_timezone": visitor timezone
		}
	"""
	# Get department
	department = frappe.get_value(
		"MM Department",
		{"department_slug": department_slug, "is_active": 1},
		["name", "department_name", "timezone"],
		as_dict=True
	)

	if not department:
		frappe.throw(f"Department '{department_slug}' not found or inactive")

	# Get meeting type
	meeting_type = frappe.get_value(
		"MM Meeting Type",
		{
			"meeting_slug": meeting_type_slug,
			"department": department.name,
			"is_active": 1,
			"is_public": 1
		},
		["name", "meeting_name", "duration"],
		as_dict=True
	)

	if not meeting_type:
		frappe.throw(f"Meeting type '{meeting_type_slug}' not found or inactive")

	# Get active department members
	members = frappe.get_all(
		"MM Department Member",
		filters={
			"parent": department.name,
			"parenttype": "MM Department",
			"is_active": 1
		},
		fields=["member"]
	)

	if not members:
		return {
			"slots": [],
			"date": date,
			"timezone": department.timezone or "UTC",
			"visitor_timezone": visitor_timezone or department.timezone or "UTC"
		}

	member_ids = [m.member for m in members]
	scheduled_date = getdate(date)
	duration = meeting_type.duration

	# Generate time slots based on meeting duration
	# Using typical business hours (8 AM - 6 PM) to optimize performance
	# Individual member working hours will be validated in availability check
	time_slots = []
	current_time = time(8, 0)  # Start at 8 AM
	end_time = time(18, 0)  # End at 6 PM

	# Use meeting duration as slot interval (e.g., 15 min, 30 min, 45 min)
	slot_interval = duration

	while current_time <= end_time:
		time_slots.append(current_time)
		# Increment by meeting duration
		dt = datetime.combine(scheduled_date, current_time) + timedelta(minutes=slot_interval)
		current_time = dt.time()

	# Check availability for each time slot
	available_slots = []

	for slot_time in time_slots:
		# Count how many members are available at this time
		available_members = []

		for member in member_ids:
			# Check if member is available
			availability = check_member_availability(
				member,
				scheduled_date,
				slot_time,
				duration
			)

			if availability["available"]:
				# Also check minimum notice
				slot_datetime = datetime.combine(scheduled_date, slot_time)
				notice_check = validate_minimum_notice(member, slot_datetime)

				if notice_check["valid"]:
					available_members.append(member)

		# If at least one member is available, add slot
		if available_members:
			# Calculate end time
			start_datetime = datetime.combine(scheduled_date, slot_time)
			end_datetime = start_datetime + timedelta(minutes=duration)

			slot_data = {
				"start_time": slot_time.strftime("%H:%M"),
				"end_time": end_datetime.time().strftime("%H:%M"),
				"start_datetime_utc": convert_to_utc(start_datetime, department.timezone or "UTC").isoformat(),
				"available_member_count": len(available_members),
				"available_members": available_members if frappe.session.user != "Guest" else None  # Hide member details from public
			}

			# Add visitor timezone display if different from department timezone
			if visitor_timezone and visitor_timezone != department.timezone:
				from meeting_manager.meeting_manager.utils.timezone import format_time_slot_display
				slot_data["visitor_timezone_display"] = format_time_slot_display(
					start_datetime,
					end_datetime,
					department.timezone or "UTC",
					visitor_timezone
				)

			available_slots.append(slot_data)

	return {
		"slots": available_slots,
		"date": date,
		"timezone": department.timezone or "UTC",
		"visitor_timezone": visitor_timezone or department.timezone or "UTC",
		"department": {
			"name": department.department_name
		},
		"meeting_type": {
			"name": meeting_type.meeting_name,
			"duration": duration
		}
	}


def has_member_availability_on_date(member, date, duration_minutes):
	"""
	Quick check if member has ANY availability on a given date

	Args:
		member (str): User ID
		date (date): Date to check
		duration_minutes (int): Meeting duration

	Returns:
		bool: True if member has at least one available slot
	"""
	# Get user's working hours for this day
	user_settings = frappe.get_value(
		"MM User Settings",
		{"user": member},
		["working_hours_json"],
		as_dict=True
	)

	if not user_settings or not user_settings.working_hours_json:
		# No working hours - assume available
		return True

	try:
		working_hours = json.loads(user_settings.working_hours_json)
	except (json.JSONDecodeError, TypeError):
		return True

	# Get day of week
	day_of_week = date.weekday()
	day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
	day_name = day_names[day_of_week]

	day_config = working_hours.get(day_name, {})

	# If day is not enabled, no availability
	if not day_config.get("enabled", False):
		return False

	# Check for date overrides that make member unavailable
	overrides = frappe.get_all(
		"MM User Date Overrides",
		filters={
			"parenttype": "MM User Availability Rule",
			"date": date
		},
		fields=["available", "parent"]
	)

	for override in overrides:
		# Check if this override belongs to this member
		rule_user = frappe.get_value("MM User Availability Rule", override.parent, "user")
		if rule_user == member and not override.available:
			return False

	# If we got here, member potentially has availability
	return True


def get_member_available_slots(member, date, duration_minutes, meeting_type=None):
	"""
	Get all available time slots for a specific member on a date

	Args:
		member (str): User ID
		date (date or str): Date
		duration_minutes (int): Meeting duration
		meeting_type (str, optional): Meeting type ID

	Returns:
		list: List of available time slot objects
	"""
	scheduled_date = getdate(date)

	# Generate time slots
	time_slots = []
	current_time = time(0, 0)
	end_time = time(23, 30)

	while current_time <= end_time:
		time_slots.append(current_time)
		dt = datetime.combine(scheduled_date, current_time) + timedelta(minutes=15)  # 15-minute intervals
		current_time = dt.time()

	available_slots = []

	for slot_time in time_slots:
		availability = check_member_availability(
			member,
			scheduled_date,
			slot_time,
			duration_minutes
		)

		if availability["available"]:
			# Check minimum notice
			slot_datetime = datetime.combine(scheduled_date, slot_time)
			notice_check = validate_minimum_notice(member, slot_datetime)

			if notice_check["valid"]:
				end_datetime = slot_datetime + timedelta(minutes=duration_minutes)
				available_slots.append({
					"start_time": slot_time.strftime("%H:%M"),
					"end_time": end_datetime.time().strftime("%H:%M"),
					"start_datetime": slot_datetime.isoformat()
				})

	return available_slots
