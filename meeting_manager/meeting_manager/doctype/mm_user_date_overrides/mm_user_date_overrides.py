# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate
from datetime import time


class MMUserDateOverrides(Document):
	def validate(self):
		"""Validate date override before saving"""
		self.validate_date_required()
		self.validate_duplicate_date()
		self.validate_custom_hours()
		self.validate_date_not_in_past()
		self.validate_custom_hours_format()

	def validate_date_required(self):
		"""Ensure date is provided"""
		if not self.date:
			frappe.throw("Date is required for date override.")

	def validate_duplicate_date(self):
		"""Ensure no duplicate dates for the same user availability rule"""
		if not self.date:
			return

		parent_doc = self.get("parent")
		if not parent_doc:
			return

		# Get parent document to access all date overrides
		parent = frappe.get_doc("MM User Availability Rule", parent_doc)

		# Check for duplicate dates (excluding current row if updating)
		for override in parent.date_overrides:
			if override.date and getdate(override.date) == getdate(self.date):
				# Skip current row (same idx means same row)
				if hasattr(self, 'idx') and hasattr(override, 'idx') and override.idx == self.idx:
					continue

				frappe.throw(
					f"A date override for {self.date} already exists. "
					f"Each date can only have one override entry. "
					f"Please update the existing override instead of creating a new one."
				)

	def validate_custom_hours(self):
		"""Validate custom hours if user is available"""
		if self.available:
			# If available, custom hours should be provided
			if not self.custom_hours_start or not self.custom_hours_end:
				frappe.throw(
					"Custom Start Hours and Custom End Hours are required when Available is checked."
				)

			# Validate end time is after start time
			if self.custom_hours_end <= self.custom_hours_start:
				frappe.throw(
					"Custom End Hours must be after Custom Start Hours."
				)

			# Validate reasonable hours (not exceeding 24 hours)
			start_time = self.custom_hours_start
			end_time = self.custom_hours_end

			# Convert to time objects for comparison
			if isinstance(start_time, str):
				start_parts = start_time.split(':')
				start_time = time(int(start_parts[0]), int(start_parts[1]))
			if isinstance(end_time, str):
				end_parts = end_time.split(':')
				end_time = time(int(end_parts[0]), int(end_parts[1]))

			# Check if duration exceeds 24 hours (shouldn't be possible for same-day override)
			start_minutes = start_time.hour * 60 + start_time.minute
			end_minutes = end_time.hour * 60 + end_time.minute

			duration_minutes = end_minutes - start_minutes
			if duration_minutes > 1440:  # 24 hours
				frappe.throw("Custom hours duration cannot exceed 24 hours.")

			# Warn about very long hours (> 12 hours)
			if duration_minutes > 720:  # 12 hours
				frappe.msgprint(
					f"Warning: Custom hours span {duration_minutes / 60:.1f} hours (more than 12 hours). "
					f"Please verify this is correct.",
					alert=True,
					indicator="orange"
				)
		else:
			# If not available, custom hours should be cleared
			self.custom_hours_start = None
			self.custom_hours_end = None

	def validate_date_not_in_past(self):
		"""Prevent creating overrides for past dates"""
		if not self.date:
			return

		if getdate(self.date) < getdate(today()):
			frappe.msgprint(
				f"Warning: You are creating an override for a past date ({self.date}). "
				"This will not affect past bookings.",
				alert=True,
				indicator="orange"
			)

	def validate_custom_hours_format(self):
		"""Validate custom hours are in correct time format"""
		if not self.available:
			return

		# Validate start time format
		if self.custom_hours_start:
			try:
				if isinstance(self.custom_hours_start, str):
					parts = self.custom_hours_start.split(':')
					hour = int(parts[0])
					minute = int(parts[1])

					if hour < 0 or hour > 23:
						frappe.throw("Custom Start Hours: Hour must be between 0 and 23.")
					if minute < 0 or minute > 59:
						frappe.throw("Custom Start Hours: Minute must be between 0 and 59.")
			except (ValueError, IndexError):
				frappe.throw("Custom Start Hours must be in HH:MM format (e.g., 09:00).")

		# Validate end time format
		if self.custom_hours_end:
			try:
				if isinstance(self.custom_hours_end, str):
					parts = self.custom_hours_end.split(':')
					hour = int(parts[0])
					minute = int(parts[1])

					if hour < 0 or hour > 23:
						frappe.throw("Custom End Hours: Hour must be between 0 and 23.")
					if minute < 0 or minute > 59:
						frappe.throw("Custom End Hours: Minute must be between 0 and 59.")
			except (ValueError, IndexError):
				frappe.throw("Custom End Hours must be in HH:MM format (e.g., 17:00).")
