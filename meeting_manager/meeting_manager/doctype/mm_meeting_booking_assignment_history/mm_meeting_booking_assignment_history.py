# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MMMeetingBookingAssignmentHistory(Document):
	def validate(self):
		"""Validate assignment history before saving"""
		self.validate_user_exists()
		self.set_action_by()

	def validate_user_exists(self):
		"""Ensure the selected user exists"""
		if not self.user:
			frappe.throw("User is required.")

		if not frappe.db.exists("User", self.user):
			frappe.throw(f"User '{self.user}' does not exist.")

	def set_action_by(self):
		"""Auto-set action_by to current user if not already set"""
		if not self.action_by:
			self.action_by = frappe.session.user
