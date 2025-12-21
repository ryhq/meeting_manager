# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re


class MMMeetingBookingParticipant(Document):
	def validate(self):
		"""Validate participant before saving"""
		self.validate_participant_type()
		self.validate_email_format()
		self.auto_populate_email_for_internal()

	def validate_participant_type(self):
		"""Validate participant type specific fields"""
		if self.participant_type == "Internal":
			if not self.user:
				frappe.throw("User is required for Internal participants.")

			# Validate user exists
			if not frappe.db.exists("User", self.user):
				frappe.throw(f"User '{self.user}' does not exist.")

		elif self.participant_type == "External":
			if not self.name1:
				frappe.throw("Name is required for External participants.")

	def validate_email_format(self):
		"""Validate email format"""
		if not self.email:
			frappe.throw("Email is required.")

		# Email format validation
		email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
		if not email_pattern.match(self.email):
			frappe.throw(f"Invalid email format: '{self.email}'")

	def auto_populate_email_for_internal(self):
		"""Auto-populate email from user if internal participant"""
		if self.participant_type == "Internal" and self.user and not self.email:
			self.email = frappe.db.get_value("User", self.user, "email")
