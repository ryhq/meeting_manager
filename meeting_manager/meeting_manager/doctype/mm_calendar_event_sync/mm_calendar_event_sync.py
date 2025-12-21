# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime
import json
import re


class MMCalendarEventSync(Document):
	def validate(self):
		"""Validate calendar event sync before saving"""
		self.validate_calendar_integration_exists()
		self.validate_external_event_id_unique()
		self.validate_event_timing()
		self.validate_attendees_json()
		self.validate_organizer_email()
		self.validate_meeting_booking_link()

	def validate_calendar_integration_exists(self):
		"""Ensure the selected calendar integration exists and is active"""
		if not self.calendar_integration:
			frappe.throw("Calendar Integration is required.")

		if not frappe.db.exists("MM Calendar Integration", self.calendar_integration):
			frappe.throw(f"Calendar Integration '{self.calendar_integration}' does not exist.")

		# Check if calendar integration is active
		is_active = frappe.db.get_value(
			"MM Calendar Integration",
			self.calendar_integration,
			"is_active"
		)
		if not is_active:
			frappe.msgprint(
				f"Warning: Calendar Integration '{self.calendar_integration}' is not active. "
				f"This event may not sync properly.",
				alert=True,
				indicator="orange"
			)

	def validate_external_event_id_unique(self):
		"""Ensure external_event_id is unique within the calendar integration"""
		if not self.external_event_id:
			frappe.throw("External Event ID is required.")

		# Check uniqueness within the calendar integration (excluding current document if updating)
		filters = {
			"calendar_integration": self.calendar_integration,
			"external_event_id": self.external_event_id
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]

		existing = frappe.db.exists("MM Calendar Event Sync", filters)
		if existing:
			frappe.throw(
				f"External Event ID '{self.external_event_id}' already exists in calendar integration "
				f"'{self.calendar_integration}'. Each event must have a unique external ID."
			)

	def validate_event_timing(self):
		"""Validate event start and end times are logical"""
		if not self.start_datetime:
			frappe.throw("Start DateTime is required.")

		if not self.end_datetime:
			frappe.throw("End DateTime is required.")

		# Convert to datetime objects for comparison
		try:
			start_dt = get_datetime(self.start_datetime)
			end_dt = get_datetime(self.end_datetime)
		except:
			frappe.throw("Invalid datetime format for Start or End DateTime.")

		# Validate end is after start
		if end_dt <= start_dt:
			frappe.throw("End DateTime must be after Start DateTime.")

		# Calculate duration
		duration_seconds = (end_dt - start_dt).total_seconds()
		duration_hours = duration_seconds / 3600

		# Warn about very long events (> 24 hours)
		if duration_hours > 24:
			frappe.msgprint(
				f"Warning: This event has a duration of {duration_hours:.1f} hours (> 24 hours). "
				f"Please verify the event timing is correct.",
				alert=True,
				indicator="orange"
			)

		# Validate events are not in the distant past (> 2 years ago)
		current_dt = now_datetime()
		days_in_past = (current_dt - start_dt).days

		if days_in_past > 730:  # 2 years
			frappe.msgprint(
				f"Warning: This event started {days_in_past} days ago. "
				f"Very old events may not need to be synced.",
				alert=True,
				indicator="orange"
			)

	def validate_attendees_json(self):
		"""Validate attendees_json structure if provided"""
		if not self.attendees_json:
			return

		# Parse JSON to validate structure
		try:
			if isinstance(self.attendees_json, str):
				attendees = json.loads(self.attendees_json)
			else:
				attendees = self.attendees_json
		except json.JSONDecodeError:
			frappe.throw("Invalid JSON format for Attendees.")

		# Validate structure - should be a list
		if not isinstance(attendees, list):
			frappe.throw("Attendees must be a JSON array of email addresses or objects.")

		# Validate each attendee entry
		email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

		for idx, attendee in enumerate(attendees):
			# Attendee can be either a string (email) or an object with email field
			if isinstance(attendee, str):
				email = attendee
			elif isinstance(attendee, dict):
				if "email" not in attendee:
					frappe.throw(f"Attendee at index {idx} is missing 'email' field.")
				email = attendee.get("email")
			else:
				frappe.throw(f"Attendee at index {idx} must be a string or object.")

			# Validate email format
			if email and not email_pattern.match(email):
				frappe.throw(f"Invalid email format for attendee: '{email}'")

	def validate_organizer_email(self):
		"""Validate organizer email format if provided"""
		if not self.organizer_email:
			return

		# Validate email format
		email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

		if not email_pattern.match(self.organizer_email):
			frappe.throw(f"Invalid email format for Organizer Email: '{self.organizer_email}'")

	def validate_meeting_booking_link(self):
		"""Validate meeting booking link if provided"""
		if not self.meeting_booking:
			return

		# Check if meeting booking exists
		if not frappe.db.exists("MM Meeting Booking", self.meeting_booking):
			frappe.throw(f"Meeting Booking '{self.meeting_booking}' does not exist.")

		# Check if meeting booking is already linked to another calendar event
		filters = {
			"meeting_booking": self.meeting_booking
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]

		existing_link = frappe.db.exists("MM Calendar Event Sync", filters)
		if existing_link:
			frappe.msgprint(
				f"Warning: Meeting Booking '{self.meeting_booking}' is already linked to another calendar event. "
				f"Multiple calendar events for the same booking may cause sync conflicts.",
				alert=True,
				indicator="orange"
			)

		# Verify timing consistency between event and booking
		booking_start = frappe.db.get_value("MM Meeting Booking", self.meeting_booking, "start_datetime")
		booking_end = frappe.db.get_value("MM Meeting Booking", self.meeting_booking, "end_datetime")

		if booking_start and booking_end:
			event_start = get_datetime(self.start_datetime)
			event_end = get_datetime(self.end_datetime)
			booking_start_dt = get_datetime(booking_start)
			booking_end_dt = get_datetime(booking_end)

			# Allow small time differences (up to 5 minutes) for timezone/rounding differences
			time_tolerance_seconds = 300  # 5 minutes

			start_diff = abs((event_start - booking_start_dt).total_seconds())
			end_diff = abs((event_end - booking_end_dt).total_seconds())

			if start_diff > time_tolerance_seconds or end_diff > time_tolerance_seconds:
				frappe.msgprint(
					f"Warning: Event timing does not match linked Meeting Booking timing. "
					f"This may indicate a sync issue.",
					alert=True,
					indicator="orange"
				)

	def on_update(self):
		"""Hook called after document is saved"""
		# Update last_synced timestamp
		if self.sync_status == "Synced":
			self.db_set("last_synced", now_datetime(), update_modified=False)

	def on_trash(self):
		"""Hook called before document is deleted"""
		# Log deletion if linked to a meeting booking
		if self.meeting_booking:
			frappe.log_error(
				message=f"Calendar Event Sync '{self.name}' linked to Meeting Booking '{self.meeting_booking}' was deleted.",
				title="Calendar Event Sync Deletion"
			)
