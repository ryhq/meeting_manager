# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url
import re


class MMMeetingType(Document):
	def validate(self):
		"""Validate meeting type before saving"""
		self.set_created_by()
		self.validate_department_exists()
		self.validate_meeting_slug()
		self.validate_availability_flags()
		self.validate_duration()
		self.validate_reminder_schedule()
		self.validate_location_settings()
		self.set_public_booking_url()

	def set_created_by(self):
		"""Auto-set created_by to current user if not already set"""
		if not self.created_by and self.is_new():
			self.created_by = frappe.session.user

	def validate_department_exists(self):
		"""Ensure the selected department exists and is active"""
		if not self.department:
			frappe.throw("Department is required.")

		department = frappe.get_doc("MM Department", self.department)
		if not department.is_active:
			frappe.throw(f"Department '{self.department}' is not active. Please select an active department.")

	def validate_meeting_slug(self):
		"""Ensure meeting_slug is URL-safe and unique within the department"""
		if not self.meeting_slug:
			frappe.throw("Meeting Slug is required.")

		# Convert to lowercase and strip leading/trailing whitespace
		self.meeting_slug = self.meeting_slug.lower().strip()

		# Replace spaces with hyphens
		self.meeting_slug = self.meeting_slug.replace(" ", "-")

		# Remove any characters that aren't lowercase letters, numbers, or hyphens
		self.meeting_slug = re.sub(r'[^a-z0-9\-]', '', self.meeting_slug)

		# Replace consecutive hyphens with a single hyphen
		self.meeting_slug = re.sub(r'-+', '-', self.meeting_slug)

		# Remove leading and trailing hyphens
		self.meeting_slug = self.meeting_slug.strip('-')

		# Ensure slug is not empty after cleaning
		if not self.meeting_slug:
			frappe.throw("Meeting Slug must contain at least one letter or number.")

		# Check uniqueness within the department (excluding current document if updating)
		filters = {
			"department": self.department,
			"meeting_slug": self.meeting_slug
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]

		existing = frappe.db.exists("MM Meeting Type", filters)
		if existing:
			frappe.throw(
				f"Meeting Slug '{self.meeting_slug}' already exists in department '{self.department}'. "
				f"Please use a unique slug within this department."
			)

	def validate_availability_flags(self):
		"""Ensure at least one of is_public or is_internal is checked"""
		if not self.is_public and not self.is_internal:
			frappe.throw(
				"At least one availability flag must be checked: "
				"'Available for Public/Customer Booking' or 'Available for Internal Meetings'."
			)

	def validate_duration(self):
		"""Validate duration is positive and reasonable"""
		if not self.duration:
			frappe.throw("Duration is required.")

		if self.duration <= 0:
			frappe.throw("Duration must be greater than 0 minutes.")

		if self.duration > 480:  # 8 hours
			frappe.throw("Duration cannot exceed 480 minutes (8 hours).")

	def validate_reminder_schedule(self):
		"""Validate reminder schedule entries"""
		if not self.reminder_schedule:
			return

		seen_hours = set()

		for reminder in self.reminder_schedule:
			# Validate hours_before_meeting
			if reminder.hours_before_meeting is None:
				frappe.throw("Hours Before Meeting is required for all reminder schedule entries.")

			if reminder.hours_before_meeting < 0:
				frappe.throw("Hours Before Meeting cannot be negative.")

			# Check for reasonable reminder times (max 720 hours = 30 days)
			if reminder.hours_before_meeting > 720:
				frappe.throw("Hours Before Meeting cannot exceed 720 hours (30 days).")

			# Check for duplicate reminder times
			if reminder.hours_before_meeting in seen_hours:
				frappe.throw(f"Duplicate reminder found for {reminder.hours_before_meeting} hours before meeting. Each reminder time must be unique.")
			seen_hours.add(reminder.hours_before_meeting)

	def validate_location_settings(self):
		"""Validate location type and related fields"""
		if not self.location_type:
			return

		# Validate video platform is set if location_type is Video Call
		if self.location_type == "Video Call" and not self.video_platform:
			frappe.throw("Video Platform is required when Location Type is 'Video Call'.")

		# Validate custom_location is set for Physical Location or Custom
		if self.location_type in ["Physical Location", "Custom"] and not self.custom_location:
			frappe.msgprint(
				f"Custom Location is recommended when Location Type is '{self.location_type}'.",
				alert=True,
				indicator="orange"
			)

	def set_public_booking_url(self):
		"""Auto-generate public booking URL based on department and meeting slugs"""
		if not self.department or not self.meeting_slug:
			return

		# Get department slug
		department_slug = frappe.db.get_value("MM Department", self.department, "department_slug")
		if not department_slug:
			return

		site_url = get_url()
		self.public_booking_url = f"{site_url}/book/{department_slug}/{self.meeting_slug}"
