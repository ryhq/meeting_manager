# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime
import re
import random
import string


class MMMeetingBooking(Document):
	def validate(self):
		"""Validate meeting booking before saving"""
		self.set_created_by()
		self.validate_meeting_type_exists()
		self.validate_timing()
		self.calculate_duration()
		self.validate_customer_details()
		self.validate_assigned_users()
		self.validate_participants()
		self.validate_approval_workflow()
		self.validate_calendar_sync()
		self.validate_location_settings()
		self.validate_booking_status()
		self.set_booking_reference()

	def before_save(self):
		"""Hook called before document is saved"""
		# Track status changes for history
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.booking_status != self.booking_status:
				self.add_history_entry(
					event_type=self.booking_status,
					description=f"Booking status changed from {old_doc.booking_status} to {self.booking_status}"
				)

	def set_created_by(self):
		"""Auto-set created_by to current user if not already set"""
		if not self.created_by and self.is_new():
			self.created_by = frappe.session.user

	def validate_meeting_type_exists(self):
		"""Ensure the selected meeting type exists and is active"""
		if not self.meeting_type:
			frappe.throw("Meeting Type is required.")

		meeting_type = frappe.get_doc("MM Meeting Type", self.meeting_type)
		if not meeting_type.is_active:
			frappe.throw(f"Meeting Type '{self.meeting_type}' is not active. Please select an active meeting type.")

		# Validate is_internal flag matches meeting type availability
		if self.is_internal and not meeting_type.is_internal:
			frappe.throw(
				f"Meeting Type '{self.meeting_type}' is not available for internal meetings. "
				f"Please select a meeting type that allows internal meetings."
			)

		if not self.is_internal and not meeting_type.is_public:
			frappe.throw(
				f"Meeting Type '{self.meeting_type}' is not available for public bookings. "
				f"Please select a meeting type that allows public bookings."
			)

		# Set requires_approval from meeting type if not already set
		if self.is_new() and meeting_type.requires_approval:
			self.requires_approval = 1
			self.approval_status = "Pending"

		# Copy location settings from meeting type if not already set
		if self.is_new():
			if not self.location_type:
				self.location_type = meeting_type.location_type
			if not self.meeting_location and meeting_type.custom_location:
				self.meeting_location = meeting_type.custom_location

	def validate_timing(self):
		"""Validate booking timing is logical and available"""
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

		# Validate booking is not in the past (for new bookings)
		if self.is_new():
			current_dt = now_datetime()
			if start_dt < current_dt:
				frappe.throw("Cannot create a booking in the past. Please select a future date and time.")

		# Validate booking doesn't exceed maximum advance booking window
		if self.is_new() and self.assigned_users:
			for assigned_user in self.assigned_users:
				user = assigned_user.user
				# Get user's availability rules
				availability_rule = frappe.get_value(
					"MM User Availability Rule",
					{"user": user, "is_active": 1, "is_default": 1},
					["max_days_advance", "min_notice_hours"],
					as_dict=True
				)

				if availability_rule:
					current_dt = now_datetime()
					days_in_advance = (start_dt - current_dt).days
					hours_in_advance = (start_dt - current_dt).total_seconds() / 3600

					if days_in_advance > availability_rule.max_days_advance:
						frappe.throw(
							f"Booking is too far in advance for user '{user}'. "
							f"Maximum advance booking is {availability_rule.max_days_advance} days."
						)

					if hours_in_advance < availability_rule.min_notice_hours:
						frappe.throw(
							f"Booking does not meet minimum notice requirement for user '{user}'. "
							f"Minimum notice is {availability_rule.min_notice_hours} hours."
						)

	def calculate_duration(self):
		"""Calculate duration in minutes from start and end times"""
		if not self.start_datetime or not self.end_datetime:
			return

		start_dt = get_datetime(self.start_datetime)
		end_dt = get_datetime(self.end_datetime)

		duration_seconds = (end_dt - start_dt).total_seconds()
		self.duration = int(duration_seconds / 60)

	def validate_customer_details(self):
		"""Validate customer details for non-internal bookings"""
		if self.is_internal:
			return

		# Validate customer_name
		if not self.customer_name:
			frappe.throw("Customer Name is required for external bookings.")

		# Validate customer_email
		if not self.customer_email:
			frappe.throw("Customer Email is required for external bookings.")

		email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
		if not email_pattern.match(self.customer_email):
			frappe.throw(f"Invalid email format for Customer Email: '{self.customer_email}'")

		# Validate customer_phone format if provided
		if self.customer_phone:
			# Remove common phone formatting characters
			phone_digits = re.sub(r'[\s\-\(\)\+]', '', self.customer_phone)
			if not phone_digits.isdigit() or len(phone_digits) < 7:
				frappe.throw("Invalid phone number format. Please provide a valid phone number.")

	def validate_assigned_users(self):
		"""Validate assigned users and ensure at least one primary host"""
		if not self.assigned_users or len(self.assigned_users) == 0:
			frappe.throw("At least one user must be assigned to this booking.")

		# Check for duplicate users
		user_list = [au.user for au in self.assigned_users]
		if len(user_list) != len(set(user_list)):
			frappe.throw("Duplicate users found in assigned users. Each user can only be assigned once.")

		# Validate each assigned user exists
		for assigned_user in self.assigned_users:
			if not frappe.db.exists("User", assigned_user.user):
				frappe.throw(f"User '{assigned_user.user}' does not exist.")

			# Set assigned_by if not set
			if not assigned_user.assigned_by:
				assigned_user.assigned_by = frappe.session.user

		# Count primary hosts
		primary_count = sum(1 for au in self.assigned_users if au.is_primary_host)

		if primary_count == 0:
			frappe.throw("At least one assigned user must be marked as Primary Host.")

		if primary_count > 1:
			frappe.msgprint(
				"Warning: Multiple users are marked as Primary Host. Consider having only one primary host.",
				alert=True,
				indicator="orange"
			)

	def validate_participants(self):
		"""Validate participant details"""
		if not self.participants:
			return

		# Check for duplicate participants
		participant_emails = [p.email for p in self.participants]
		if len(participant_emails) != len(set(participant_emails)):
			frappe.throw("Duplicate participants found. Each participant email must be unique.")

		# Validate each participant
		email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

		for participant in self.participants:
			# Validate email format
			if not email_pattern.match(participant.email):
				frappe.throw(f"Invalid email format for participant: '{participant.email}'")

			# Validate internal participant has user set
			if participant.participant_type == "Internal" and not participant.user:
				frappe.throw(f"Internal participant must have a User selected: '{participant.email}'")

			# Validate external participant has name set
			if participant.participant_type == "External" and not participant.name1:
				frappe.throw(f"External participant must have a Name: '{participant.email}'")

			# Validate user exists if internal
			if participant.participant_type == "Internal" and participant.user:
				if not frappe.db.exists("User", participant.user):
					frappe.throw(f"User '{participant.user}' does not exist.")

				# Auto-populate email from user if not set
				if not participant.email:
					participant.email = frappe.db.get_value("User", participant.user, "email")

		# Warn if no participants added for confirmed bookings
		if len(self.participants) == 0 and self.booking_status == "Confirmed":
			frappe.msgprint(
				"Warning: No participants added to this confirmed booking. Consider adding participants for better tracking.",
				alert=True,
				indicator="orange"
			)

	def validate_approval_workflow(self):
		"""Validate approval workflow logic"""
		if not self.requires_approval:
			# If approval not required, clear approval fields
			self.approval_status = "Pending"
			return

		# Validate approval_status is set
		if not self.approval_status:
			self.approval_status = "Pending"

		# Validate approved_by and approval_date are set for approved/rejected bookings
		if self.approval_status in ["Approved", "Rejected"]:
			if not self.approved_by:
				self.approved_by = frappe.session.user
			if not self.approval_date:
				self.approval_date = now_datetime()

			# Update booking_status based on approval_status
			if self.approval_status == "Approved" and self.booking_status == "Pending":
				self.booking_status = "Confirmed"

			if self.approval_status == "Rejected" and self.booking_status != "Cancelled":
				self.booking_status = "Cancelled"

		# Validate rejection_reason is provided for rejected bookings
		if self.approval_status == "Rejected" and not self.rejection_reason:
			frappe.throw("Rejection Reason is required when rejecting a booking.")

	def validate_calendar_sync(self):
		"""Validate calendar sync settings"""
		if self.calendar_event_synced and not self.calendar_event:
			frappe.msgprint(
				"Warning: Calendar Event Synced is checked but no Calendar Event is linked.",
				alert=True,
				indicator="orange"
			)

		if self.calendar_event and not self.calendar_event_synced:
			# Auto-check if calendar event is linked
			self.calendar_event_synced = 1

		# Validate calendar event exists if specified
		if self.calendar_event:
			if not frappe.db.exists("MM Calendar Event Sync", self.calendar_event):
				frappe.throw(f"Calendar Event '{self.calendar_event}' does not exist.")

	def validate_location_settings(self):
		"""Validate location settings consistency"""
		if self.location_type == "Video Call" and not self.video_meeting_url:
			frappe.msgprint(
				"Video Meeting URL is recommended when Location Type is 'Video Call'.",
				alert=True,
				indicator="orange"
			)

		if self.location_type == "Physical Location" and not self.meeting_location:
			frappe.msgprint(
				"Meeting Location is recommended when Location Type is 'Physical Location'.",
				alert=True,
				indicator="orange"
			)

		# Validate video meeting URL format if provided
		if self.video_meeting_url:
			if not self.video_meeting_url.startswith(("http://", "https://")):
				frappe.throw("Video Meeting URL must start with http:// or https://")

	def validate_booking_status(self):
		"""Validate booking status transitions and requirements"""
		# Validate cancelled_at is set for cancelled bookings
		if self.booking_status == "Cancelled":
			if not self.cancelled_at:
				self.cancelled_at = now_datetime()

			# Cancellation reason is recommended
			if not self.cancellation_reason:
				frappe.msgprint(
					"Cancellation Reason is recommended when cancelling a booking.",
					alert=True,
					indicator="orange"
				)

		# Validate no-show and completed status are only for past bookings
		if self.booking_status in ["No-Show", "Completed"]:
			if self.start_datetime:
				start_dt = get_datetime(self.start_datetime)
				current_dt = now_datetime()
				if start_dt > current_dt:
					frappe.throw(
						f"Cannot mark a future booking as '{self.booking_status}'. "
						f"This status can only be set for past bookings."
					)

	def set_booking_reference(self):
		"""Generate unique booking reference for customer communication"""
		if not self.booking_reference and self.is_new():
			# Generate a unique reference code
			ref_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
			self.booking_reference = f"BK-{ref_code}"

	def add_history_entry(self, event_type, description):
		"""Add entry to booking history"""
		if not self.booking_history:
			self.booking_history = []

		self.append("booking_history", {
			"event_type": event_type,
			"event_datetime": now_datetime(),
			"event_by": frappe.session.user,
			"event_description": description
		})

	def on_update(self):
		"""Hook called after document is saved"""
		# Add creation history entry for new bookings
		if self.is_new():
			self.add_history_entry(
				event_type="Created",
				description=f"Booking created for {self.meeting_title}"
			)

		# Track assignment changes
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc:
				self.track_assignment_changes(old_doc)

	def track_assignment_changes(self, old_doc):
		"""Track changes in assigned users and add to assignment history"""
		old_users = {au.user for au in old_doc.assigned_users} if old_doc.assigned_users else set()
		new_users = {au.user for au in self.assigned_users} if self.assigned_users else set()

		# Find added users
		added_users = new_users - old_users
		for user in added_users:
			self.append("assignment_history", {
				"action_type": "Assigned",
				"user": user,
				"action_datetime": now_datetime(),
				"action_by": frappe.session.user,
				"notes": f"User {user} was assigned to this booking"
			})

		# Find removed users
		removed_users = old_users - new_users
		for user in removed_users:
			self.append("assignment_history", {
				"action_type": "Unassigned",
				"user": user,
				"action_datetime": now_datetime(),
				"action_by": frappe.session.user,
				"notes": f"User {user} was unassigned from this booking"
			})

		# Check for primary host changes
		old_primary = next((au.user for au in old_doc.assigned_users if au.is_primary_host), None) if old_doc.assigned_users else None
		new_primary = next((au.user for au in self.assigned_users if au.is_primary_host), None) if self.assigned_users else None

		if old_primary != new_primary and new_primary:
			self.append("assignment_history", {
				"action_type": "Primary Changed",
				"user": new_primary,
				"action_datetime": now_datetime(),
				"action_by": frappe.session.user,
				"notes": f"Primary host changed from {old_primary or 'None'} to {new_primary}"
			})

	def on_cancel(self):
		"""Hook called when document is cancelled"""
		self.booking_status = "Cancelled"
		self.cancelled_at = now_datetime()
		self.add_history_entry(
			event_type="Cancelled",
			description=f"Booking cancelled. Reason: {self.cancellation_reason or 'Not provided'}"
		)
