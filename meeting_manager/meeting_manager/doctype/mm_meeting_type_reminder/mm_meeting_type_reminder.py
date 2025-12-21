# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MMMeetingTypeReminder(Document):
	def validate(self):
		"""Validate reminder schedule before saving"""
		self.validate_hours_before_meeting()
		self.validate_notification_type()
		self.validate_duplicate_reminder()

	def validate_hours_before_meeting(self):
		"""Validate hours_before_meeting is within reasonable range"""
		if self.hours_before_meeting is None:
			frappe.throw("Hours Before Meeting is required.")

		if self.hours_before_meeting < 0:
			frappe.throw("Hours Before Meeting cannot be negative.")

		# Warn about very early reminders (more than 30 days / 720 hours)
		if self.hours_before_meeting > 720:
			frappe.msgprint(
				f"Warning: Reminder scheduled {self.hours_before_meeting} hours ({self.hours_before_meeting / 24:.1f} days) before meeting. "
				f"Very early reminders may be forgotten by the time of the meeting.",
				alert=True,
				indicator="orange"
			)

		# Provide guidance on common reminder times
		if self.hours_before_meeting == 0:
			frappe.msgprint(
				"Note: 0-hour reminder means the reminder will be sent at the meeting start time. "
				"Consider using at least 15 minutes (0.25 hours) to give participants time to join.",
				alert=True,
				indicator="blue"
			)

	def validate_notification_type(self):
		"""Validate notification type is selected"""
		if not self.notification_type:
			frappe.throw("Notification Type is required.")

		# Warn about SMS notifications (may require additional setup)
		if self.notification_type in ["SMS", "Both"]:
			frappe.msgprint(
				"SMS notifications require SMS gateway configuration. "
				"Ensure your SMS provider is properly configured before enabling SMS reminders.",
				alert=True,
				indicator="blue"
			)

	def validate_duplicate_reminder(self):
		"""Ensure no duplicate reminder times for the same meeting type"""
		if not self.hours_before_meeting:
			return

		parent_doc = self.get("parent")
		if not parent_doc:
			return

		# Get parent document to access all reminders
		parent = frappe.get_doc("MM Meeting Type", parent_doc)

		# Check for duplicate hours_before_meeting (excluding current row if updating)
		for reminder in parent.reminder_schedule:
			if reminder.hours_before_meeting == self.hours_before_meeting:
				# Skip current row (same idx means same row)
				if hasattr(self, 'idx') and hasattr(reminder, 'idx') and reminder.idx == self.idx:
					continue

				frappe.throw(
					f"A reminder at {self.hours_before_meeting} hours before meeting already exists. "
					f"Each reminder time must be unique for this meeting type."
				)

		# Recommend common reminder patterns if this is the first reminder
		active_reminders = [r for r in parent.reminder_schedule if r.is_active]
		if len(active_reminders) == 0:
			frappe.msgprint(
				"Tip: Common reminder patterns include:\n"
				"- 24 hours + 1 hour before (for important meetings)\n"
				"- 24 hours before (standard)\n"
				"- 1 hour before (last-minute reminder)\n"
				"- 15 minutes before (quick reminder)",
				alert=True,
				indicator="blue"
			)
