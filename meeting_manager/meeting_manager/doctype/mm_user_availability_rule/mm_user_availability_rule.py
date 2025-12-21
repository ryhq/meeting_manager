# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MMUserAvailabilityRule(Document):
	def validate(self):
		"""Validate availability rule before saving"""
		self.validate_user_exists()
		self.validate_buffer_times()
		self.validate_booking_limits()
		self.validate_scheduling_constraints()
		self.validate_default_rule()
		self.validate_date_overrides()

	def validate_user_exists(self):
		"""Ensure the selected user exists"""
		if not self.user:
			frappe.throw("User is required.")

		if not frappe.db.exists("User", self.user):
			frappe.throw(f"User '{self.user}' does not exist.")

	def validate_buffer_times(self):
		"""Validate buffer times are non-negative"""
		if self.buffer_time_before is not None and self.buffer_time_before < 0:
			frappe.throw("Buffer Time Before cannot be negative.")

		if self.buffer_time_after is not None and self.buffer_time_after < 0:
			frappe.throw("Buffer Time After cannot be negative.")

		# Check for reasonable buffer times (max 4 hours = 240 minutes)
		if self.buffer_time_before and self.buffer_time_before > 240:
			frappe.throw("Buffer Time Before cannot exceed 240 minutes (4 hours).")

		if self.buffer_time_after and self.buffer_time_after > 240:
			frappe.throw("Buffer Time After cannot exceed 240 minutes (4 hours).")

	def validate_booking_limits(self):
		"""Validate booking limits are non-negative"""
		if self.max_bookings_per_day is not None and self.max_bookings_per_day < 0:
			frappe.throw("Max Bookings Per Day cannot be negative. Use 0 for unlimited.")

		if self.max_bookings_per_week is not None and self.max_bookings_per_week < 0:
			frappe.throw("Max Bookings Per Week cannot be negative. Use 0 for unlimited.")

		# Check for reasonable limits (max 50 per day, 200 per week)
		if self.max_bookings_per_day and self.max_bookings_per_day > 50:
			frappe.throw("Max Bookings Per Day cannot exceed 50. Use 0 for unlimited.")

		if self.max_bookings_per_week and self.max_bookings_per_week > 200:
			frappe.throw("Max Bookings Per Week cannot exceed 200. Use 0 for unlimited.")

		# Logical check: daily limit cannot exceed weekly limit (if both are set)
		if (self.max_bookings_per_day and self.max_bookings_per_day > 0 and
			self.max_bookings_per_week and self.max_bookings_per_week > 0):
			if self.max_bookings_per_day > self.max_bookings_per_week:
				frappe.throw(
					f"Max Bookings Per Day ({self.max_bookings_per_day}) cannot exceed "
					f"Max Bookings Per Week ({self.max_bookings_per_week}). "
					f"Daily limit must be less than or equal to weekly limit."
				)

	def validate_scheduling_constraints(self):
		"""Validate scheduling constraints are positive and reasonable"""
		if not self.min_notice_hours:
			frappe.throw("Minimum Notice Hours is required.")

		if self.min_notice_hours < 0:
			frappe.throw("Minimum Notice Hours must be at least 0.")

		if self.min_notice_hours > 720:  # 30 days
			frappe.throw("Minimum Notice Hours cannot exceed 720 hours (30 days).")

		if not self.max_days_advance:
			frappe.throw("Maximum Days in Advance is required.")

		if self.max_days_advance <= 0:
			frappe.throw("Maximum Days in Advance must be greater than 0.")

		if self.max_days_advance > 365:
			frappe.throw("Maximum Days in Advance cannot exceed 365 days (1 year).")

		# Logical check: min_notice_hours should be less than max_days_advance
		min_notice_days = self.min_notice_hours / 24
		if min_notice_days >= self.max_days_advance:
			frappe.throw(
				f"Minimum Notice Hours ({self.min_notice_hours} hours = {min_notice_days:.1f} days) "
				f"must be less than Maximum Days in Advance ({self.max_days_advance} days)."
			)

	def validate_default_rule(self):
		"""Ensure only one default rule per user"""
		if not self.is_default:
			return

		# Check if another default rule exists for this user
		filters = {
			"user": self.user,
			"is_default": 1
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]

		existing_default = frappe.db.exists("MM User Availability Rule", filters)
		if existing_default:
			frappe.throw(
				f"A default availability rule already exists for user '{self.user}'. "
				f"Please uncheck 'Is Default' on the existing rule first, or uncheck it on this rule."
			)

	def validate_date_overrides(self):
		"""Validate date override entries

		Note: Most validation is handled by the child table (MM User Date Overrides) validate() method.
		This method only performs minimal checks that can't be done at the child table level.
		"""
		# Child table validation will handle:
		# - Required date field
		# - Duplicate date checking
		# - Custom hours format (HH:MM)
		# - Custom hours time range validation
		# - Past date warnings
		# - Long hours warnings

		# No additional validation needed here - child table handles everything
		pass
