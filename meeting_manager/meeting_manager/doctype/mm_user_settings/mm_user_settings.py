# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class MMUserSettings(Document):
	def validate(self):
		"""Validate user settings before saving"""
		self.validate_working_hours_json()
		self.validate_user_exists()

	def validate_user_exists(self):
		"""Ensure the selected user exists in the User doctype"""
		if not self.user:
			frappe.throw("User is required.")

		if not frappe.db.exists("User", self.user):
			frappe.throw(f"User '{self.user}' does not exist.")

	def validate_working_hours_json(self):
		"""Validate working_hours_json structure and data"""
		if not self.working_hours_json:
			# Set default working hours if empty
			self.working_hours_json = json.dumps({
				"monday": {"enabled": True, "start": "09:00", "end": "17:00"},
				"tuesday": {"enabled": True, "start": "09:00", "end": "17:00"},
				"wednesday": {"enabled": True, "start": "09:00", "end": "17:00"},
				"thursday": {"enabled": True, "start": "09:00", "end": "17:00"},
				"friday": {"enabled": True, "start": "09:00", "end": "17:00"},
				"saturday": {"enabled": False},
				"sunday": {"enabled": False}
			})
			return

		# Parse JSON to validate structure
		try:
			if isinstance(self.working_hours_json, str):
				working_hours = json.loads(self.working_hours_json)
			else:
				working_hours = self.working_hours_json
		except json.JSONDecodeError:
			frappe.throw("Invalid JSON format for Working Hours.")

		# Validate structure
		valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

		if not isinstance(working_hours, dict):
			frappe.throw("Working Hours must be a JSON object.")

		for day in valid_days:
			if day not in working_hours:
				frappe.throw(f"Missing configuration for '{day}' in Working Hours.")

			day_config = working_hours[day]

			if not isinstance(day_config, dict):
				frappe.throw(f"Configuration for '{day}' must be an object.")

			if "enabled" not in day_config:
				frappe.throw(f"Missing 'enabled' field for '{day}'.")

			if not isinstance(day_config["enabled"], bool):
				frappe.throw(f"'enabled' field for '{day}' must be true or false.")

			# If enabled, validate start and end times
			if day_config["enabled"]:
				if "start" not in day_config or "end" not in day_config:
					frappe.throw(f"'{day}' is enabled but missing 'start' or 'end' time.")

				# Validate time format (HH:MM)
				import re
				time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')

				if not time_pattern.match(day_config["start"]):
					frappe.throw(f"Invalid start time format for '{day}'. Use HH:MM format (e.g., 09:00).")

				if not time_pattern.match(day_config["end"]):
					frappe.throw(f"Invalid end time format for '{day}'. Use HH:MM format (e.g., 17:00).")

				# Validate that end time is after start time
				start_minutes = int(day_config["start"].split(":")[0]) * 60 + int(day_config["start"].split(":")[1])
				end_minutes = int(day_config["end"].split(":")[0]) * 60 + int(day_config["end"].split(":")[1])

				if end_minutes <= start_minutes:
					frappe.throw(f"End time must be after start time for '{day}'.")

		# Ensure at least one day is enabled
		enabled_days = [day for day in valid_days if working_hours[day].get("enabled")]
		if not enabled_days:
			frappe.throw("At least one day must be enabled in Working Hours.")
