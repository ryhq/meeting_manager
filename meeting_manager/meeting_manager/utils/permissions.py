# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Permission helpers for Meeting Manager app
"""

import frappe


def has_app_permission(user=None):
	"""
	Check if user has permission to access Meeting Manager app

	Anyone with the following roles can access:
	- System Manager
	- Department Leader
	- Any user who is a member of at least one department

	Args:
		user (str, optional): User ID. Defaults to current user.

	Returns:
		bool: True if user has access, False otherwise
	"""
	if not user:
		user = frappe.session.user

	# Guest users cannot access
	if user == "Guest":
		return False

	# Get user roles
	roles = frappe.get_roles(user)

	# System Managers always have access
	if "System Manager" in roles:
		return True

	# Department Leaders have access
	if "Department Leader" in roles:
		return True

	# Check if user is a member of any department
	is_member = frappe.db.exists(
		"MM Department Member",
		{
			"member": user,
			"is_active": 1
		}
	)

	if is_member:
		return True

	# No access
	return False
