# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MMDepartmentMember(Document):
	def validate(self):
		"""Validate department member before saving"""
		self.validate_member_exists()
		self.validate_member_unique()
		self.validate_assignment_priority()

	def validate_member_exists(self):
		"""Ensure the selected member user exists"""
		if not self.member:
			frappe.throw("Member is required.")

		if not frappe.db.exists("User", self.member):
			frappe.throw(f"User '{self.member}' does not exist.")

		# Check if user is enabled
		user_enabled = frappe.db.get_value("User", self.member, "enabled")
		if not user_enabled:
			frappe.msgprint(
				f"Warning: User '{self.member}' is disabled. Consider removing them from the department or enabling their account.",
				alert=True,
				indicator="orange"
			)

	def validate_member_unique(self):
		"""Ensure member is not already in the department"""
		if not self.member:
			return

		parent_doc = self.get("parent")
		if not parent_doc:
			return

		# Get parent document to access all members
		parent = frappe.get_doc("MM Department", parent_doc)

		# Count occurrences of this member (excluding current row if updating)
		member_count = 0
		for dept_member in parent.members:
			if dept_member.member == self.member:
				# Skip current row (same idx means same row)
				if hasattr(self, 'idx') and hasattr(dept_member, 'idx') and dept_member.idx == self.idx:
					continue
				member_count += 1

		if member_count > 0:
			frappe.throw(
				f"Member '{self.member}' is already in this department. "
				f"Each user can only be added once per department."
			)

	def validate_assignment_priority(self):
		"""Validate assignment priority is within acceptable range"""
		if self.assignment_priority is None:
			self.assignment_priority = 1  # Default priority

		if self.assignment_priority < 1:
			frappe.throw("Assignment Priority must be at least 1.")

		if self.assignment_priority > 10:
			frappe.throw("Assignment Priority cannot exceed 10.")

		# Provide guidance on priority values
		if self.assignment_priority > 5:
			frappe.msgprint(
				f"High assignment priority ({self.assignment_priority}) - "
				f"This member will be favored for assignment in weighted algorithms.",
				alert=True,
				indicator="blue"
			)
