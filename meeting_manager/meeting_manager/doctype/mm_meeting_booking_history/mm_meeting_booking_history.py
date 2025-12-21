# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MMMeetingBookingHistory(Document):
	def validate(self):
		"""Validate booking history before saving"""
		self.validate_event_type()
		self.set_event_by()

	def validate_event_type(self):
		"""Validate event type is set"""
		if not self.event_type:
			frappe.throw("Event Type is required.")

	def set_event_by(self):
		"""Auto-set event_by to current user if not already set"""
		if not self.event_by:
			self.event_by = frappe.session.user
