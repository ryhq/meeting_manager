# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Time Zone Handling Utilities

This module provides functions for timezone conversion, validation,
and display formatting for the Meeting Manager system.
"""

import frappe
from frappe.utils import get_datetime, now_datetime
from datetime import datetime
import pytz


def get_department_timezone(department):
	"""
	Get the timezone for a department

	Args:
		department (str): Department ID or name

	Returns:
		str: Timezone string (e.g., "Europe/Copenhagen")
	"""
	timezone = frappe.get_value("MM Department", department, "timezone")
	return timezone or "UTC"


def get_user_timezone(user):
	"""
	Get the timezone for a user

	Args:
		user (str): User ID

	Returns:
		str: Timezone string (e.g., "Europe/Copenhagen")
	"""
	# Try to get from MM User Settings first
	timezone = frappe.get_value("MM User Settings", {"user": user}, "timezone")

	if not timezone:
		# Fall back to Frappe user timezone
		timezone = frappe.get_value("User", user, "time_zone")

	return timezone or "UTC"


def convert_to_timezone(dt, from_tz, to_tz):
	"""
	Convert datetime from one timezone to another

	Args:
		dt (datetime or str): Datetime to convert
		from_tz (str): Source timezone (e.g., "UTC")
		to_tz (str): Target timezone (e.g., "Europe/Copenhagen")

	Returns:
		datetime: Converted datetime
	"""
	if isinstance(dt, str):
		dt = get_datetime(dt)

	# Get timezone objects
	from_timezone = pytz.timezone(from_tz)
	to_timezone = pytz.timezone(to_tz)

	# Localize to source timezone if naive
	if dt.tzinfo is None:
		dt = from_timezone.localize(dt)
	else:
		dt = dt.astimezone(from_timezone)

	# Convert to target timezone
	return dt.astimezone(to_timezone)


def convert_to_utc(dt, source_tz):
	"""
	Convert datetime from any timezone to UTC

	Args:
		dt (datetime or str): Datetime to convert
		source_tz (str): Source timezone

	Returns:
		datetime: UTC datetime
	"""
	return convert_to_timezone(dt, source_tz, "UTC")


def convert_from_utc(dt, target_tz):
	"""
	Convert datetime from UTC to any timezone

	Args:
		dt (datetime or str): UTC datetime to convert
		target_tz (str): Target timezone

	Returns:
		datetime: Converted datetime
	"""
	return convert_to_timezone(dt, "UTC", target_tz)


def format_datetime_with_timezone(dt, tz, format_string="%Y-%m-%d %H:%M %Z"):
	"""
	Format datetime with timezone information

	Args:
		dt (datetime or str): Datetime to format
		tz (str): Timezone
		format_string (str): Format string

	Returns:
		str: Formatted datetime string
	"""
	if isinstance(dt, str):
		dt = get_datetime(dt)

	timezone = pytz.timezone(tz)

	if dt.tzinfo is None:
		dt = timezone.localize(dt)
	else:
		dt = dt.astimezone(timezone)

	return dt.strftime(format_string)


def get_timezone_offset(tz, dt=None):
	"""
	Get the UTC offset for a timezone at a specific datetime

	Args:
		tz (str): Timezone
		dt (datetime, optional): Datetime to check (defaults to now)

	Returns:
		str: Offset string (e.g., "+01:00", "-05:00")
	"""
	if dt is None:
		dt = now_datetime()

	timezone = pytz.timezone(tz)
	localized_dt = timezone.localize(dt) if dt.tzinfo is None else dt.astimezone(timezone)

	offset = localized_dt.strftime("%z")
	# Format as +HH:MM
	return f"{offset[:3]}:{offset[3:]}"


def validate_timezone(tz):
	"""
	Validate if a timezone string is valid

	Args:
		tz (str): Timezone string

	Returns:
		bool: True if valid, False otherwise
	"""
	try:
		pytz.timezone(tz)
		return True
	except pytz.UnknownTimeZoneError:
		return False


def get_common_timezones():
	"""
	Get list of common timezones for selection

	Returns:
		list: List of timezone strings
	"""
	return pytz.common_timezones


def detect_visitor_timezone(request=None):
	"""
	Attempt to detect visitor's timezone from browser/request

	This is a placeholder - actual implementation would use JavaScript
	in the frontend to detect timezone and pass it to backend

	Args:
		request (optional): HTTP request object

	Returns:
		str: Detected timezone or "UTC" as fallback
	"""
	# In real implementation, this would come from:
	# 1. JavaScript: Intl.DateTimeFormat().resolvedOptions().timeZone
	# 2. IP geolocation
	# 3. Browser headers

	# For now, return UTC as safe default
	return "UTC"


def format_time_slot_display(start_time, end_time, timezone, visitor_timezone=None):
	"""
	Format a time slot for display, showing both timezones if different

	Args:
		start_time (datetime or str): Start datetime
		end_time (datetime or str): End datetime
		timezone (str): Meeting timezone (department/user timezone)
		visitor_timezone (str, optional): Visitor's timezone

	Returns:
		str: Formatted time slot string
	"""
	from datetime import datetime as dt, time

	# Handle string inputs
	if isinstance(start_time, str):
		start_time = get_datetime(start_time)
	if isinstance(end_time, str):
		end_time = get_datetime(end_time)

	# Handle time objects - convert to datetime (should not happen but handle gracefully)
	if isinstance(start_time, time):
		start_time = dt.combine(dt.today(), start_time)
	if isinstance(end_time, time):
		end_time = dt.combine(dt.today(), end_time)

	# Format in meeting timezone
	meeting_tz = pytz.timezone(timezone)
	start_local = start_time.astimezone(meeting_tz) if start_time.tzinfo else meeting_tz.localize(start_time)
	end_local = end_time.astimezone(meeting_tz) if end_time.tzinfo else meeting_tz.localize(end_time)

	meeting_time_str = f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')} {timezone}"

	# If visitor timezone is different, show both
	if visitor_timezone and visitor_timezone != timezone:
		visitor_tz = pytz.timezone(visitor_timezone)
		start_visitor = start_time.astimezone(visitor_tz) if start_time.tzinfo else convert_to_timezone(start_time, timezone, visitor_timezone)
		end_visitor = end_time.astimezone(visitor_tz) if end_time.tzinfo else convert_to_timezone(end_time, timezone, visitor_timezone)

		visitor_time_str = f"{start_visitor.strftime('%H:%M')} - {end_visitor.strftime('%H:%M')} {visitor_timezone}"
		return f"{meeting_time_str} ({visitor_time_str} your time)"

	return meeting_time_str


def is_dst_transition(dt, tz):
	"""
	Check if a datetime falls during a DST transition

	Args:
		dt (datetime): Datetime to check
		tz (str): Timezone

	Returns:
		bool: True if during DST transition
	"""
	timezone = pytz.timezone(tz)

	try:
		timezone.localize(dt)
		return False
	except pytz.AmbiguousTimeError:
		# Time occurs twice (fall back)
		return True
	except pytz.NonExistentTimeError:
		# Time doesn't exist (spring forward)
		return True


def get_next_occurrence_in_timezone(time_str, tz, from_datetime=None):
	"""
	Get the next occurrence of a time (HH:MM) in a specific timezone

	Args:
		time_str (str): Time string (e.g., "14:30")
		tz (str): Timezone
		from_datetime (datetime, optional): Start searching from this datetime

	Returns:
		datetime: Next occurrence of the time in the specified timezone
	"""
	if from_datetime is None:
		from_datetime = now_datetime()

	timezone = pytz.timezone(tz)
	local_dt = from_datetime.astimezone(timezone) if from_datetime.tzinfo else timezone.localize(from_datetime)

	# Parse time
	hour, minute = map(int, time_str.split(":"))

	# Create datetime with the target time
	target_dt = local_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

	# If target time has passed today, move to tomorrow
	if target_dt <= local_dt:
		target_dt = target_dt.replace(day=target_dt.day + 1)

	return target_dt
