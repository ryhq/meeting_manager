# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime
import re


class MMCalendarIntegration(Document):
	def validate(self):
		"""Validate calendar integration before saving"""
		self.validate_user_exists()
		self.validate_integration_name_unique()
		self.validate_integration_type_requirements()
		self.validate_sync_settings()
		self.validate_token_expiry()
		self.validate_primary_calendar()

	def validate_user_exists(self):
		"""Ensure the selected user exists"""
		if not self.user:
			frappe.throw("User is required.")

		if not frappe.db.exists("User", self.user):
			frappe.throw(f"User '{self.user}' does not exist.")

	def validate_integration_name_unique(self):
		"""Ensure integration name is unique for this user"""
		if not self.integration_name:
			frappe.throw("Integration Name is required.")

		# Check uniqueness per user (excluding current document if updating)
		filters = {
			"user": self.user,
			"integration_name": self.integration_name
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]

		existing = frappe.db.exists("MM Calendar Integration", filters)
		if existing:
			frappe.throw(
				f"Integration Name '{self.integration_name}' already exists for user '{self.user}'. "
				f"Please use a unique name for each integration."
			)

	def validate_integration_type_requirements(self):
		"""Validate integration type specific requirements"""
		if not self.integration_type:
			frappe.throw("Integration Type is required.")

		# iCal requires ical_url
		if self.integration_type == "iCal":
			if not self.ical_url:
				frappe.throw("iCal URL is required for iCal integration type.")

			# Validate URL format
			if not self.ical_url.startswith(("http://", "https://", "webcal://")):
				frappe.throw("iCal URL must start with http://, https://, or webcal://")

			# For iCal, sync direction should be read-only
			if self.sync_direction == "Two-way (Read & Write)":
				frappe.msgprint(
					"Warning: iCal integrations typically support only one-way (read-only) sync. "
					"Two-way sync may not work as expected.",
					alert=True
				)

			# Clear OAuth fields for iCal type
			if self.is_new():
				self.access_token = None
				self.refresh_token = None
				self.token_expiry = None

		# Google Calendar and Outlook require OAuth tokens
		if self.integration_type in ["Google Calendar", "Outlook Calendar"]:
			# Clear ical_url for OAuth types
			if self.is_new():
				self.ical_url = None

			# Only validate tokens if the integration is active
			if self.is_active:
				if not self.access_token:
					frappe.throw(
						f"{self.integration_type} requires an Access Token. "
						f"Please authenticate with {self.integration_type} first."
					)

				# Calendar ID is recommended for proper sync
				if not self.calendar_id:
					frappe.msgprint(
						f"Calendar ID is recommended for {self.integration_type} integration. "
						f"Without it, the primary calendar will be used by default.",
						alert=True
					)

	def validate_sync_settings(self):
		"""Validate sync configuration settings"""
		# Validate sync_past_days
		if self.sync_past_days is not None:
			if self.sync_past_days < 0:
				frappe.throw("Sync Past Days cannot be negative. Use 0 for no past sync.")

			if self.sync_past_days > 365:
				frappe.throw("Sync Past Days cannot exceed 365 days (1 year).")

		# Validate sync_future_days
		if self.sync_future_days is not None:
			if self.sync_future_days <= 0:
				frappe.throw("Sync Future Days must be greater than 0.")

			if self.sync_future_days > 730:  # 2 years
				frappe.throw("Sync Future Days cannot exceed 730 days (2 years).")

		# Validate sync_interval_minutes
		if self.auto_sync_enabled and self.sync_interval_minutes:
			if self.sync_interval_minutes < 5:
				frappe.throw("Sync Interval cannot be less than 5 minutes to avoid excessive API calls.")

			if self.sync_interval_minutes > 1440:  # 24 hours
				frappe.throw("Sync Interval cannot exceed 1440 minutes (24 hours).")

	def validate_token_expiry(self):
		"""Validate token expiry date is in the future (if set)"""
		if not self.token_expiry:
			return

		try:
			expiry_datetime = get_datetime(self.token_expiry)
			current_datetime = now_datetime()

			# If token has expired and integration is active, warn the user
			if expiry_datetime < current_datetime and self.is_active:
				frappe.msgprint(
					f"Warning: Access Token has expired on {self.token_expiry}. "
					f"Please re-authenticate to continue syncing.",
					alert=True,
					indicator="red"
				)
		except:
			frappe.throw("Invalid Token Expiry datetime format.")

	def validate_primary_calendar(self):
		"""Ensure only one primary calendar per user"""
		if not self.is_primary:
			return

		# Check if another primary calendar exists for this user
		filters = {
			"user": self.user,
			"is_primary": 1,
			"is_active": 1  # Only consider active integrations
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]

		existing_primary = frappe.db.exists("MM Calendar Integration", filters)
		if existing_primary:
			existing_name = frappe.db.get_value(
				"MM Calendar Integration",
				existing_primary,
				"integration_name"
			)
			frappe.throw(
				f"A primary calendar integration already exists for user '{self.user}': '{existing_name}'. "
				f"Please uncheck 'Is Primary Calendar' on the existing integration first, or uncheck it on this integration."
			)

	def on_update(self):
		"""Hook called after document is saved"""
		# If this is marked as primary and active, ensure it's the only active primary
		if self.is_primary and self.is_active:
			self.unmark_other_primary_calendars()

	def unmark_other_primary_calendars(self):
		"""Unmark other calendars as primary for this user"""
		other_primaries = frappe.get_all(
			"MM Calendar Integration",
			filters={
				"user": self.user,
				"is_primary": 1,
				"name": ["!=", self.name]
			},
			pluck="name"
		)

		for calendar_name in other_primaries:
			calendar = frappe.get_doc("MM Calendar Integration", calendar_name)
			calendar.is_primary = 0
			calendar.save(ignore_permissions=True)
			frappe.msgprint(
				f"Unmarked '{calendar.integration_name}' as primary calendar.",
				alert=True
			)
