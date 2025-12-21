# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Create Meeting Forms

Two types of meeting creation:
1. Internal Meeting - Between team members
2. Customer Meeting for Member - Admin/Leader creates customer booking for specific member
"""

import frappe
from frappe import _
from frappe.utils import getdate


def get_context(context):
	"""
	Meeting creation forms for authenticated users

	Permissions:
	- System Manager: Can create all types of meetings
	- Department Leader: Can create meetings for their departments
	- Department Member: Can create customer meetings for themselves
	"""
	context.no_cache = 1
	context.show_sidebar = True

	# Check authentication
	if frappe.session.user == "Guest":
		frappe.throw(_("You must be logged in to create meetings"), frappe.PermissionError)

	# Get user roles
	user_roles = frappe.get_roles()
	context.user_roles = user_roles
	context.is_system_manager = "System Manager" in user_roles
	context.is_department_leader = "Department Leader" in user_roles

	# Get form type from query params
	context.form_type = frappe.form_dict.get("type", "internal")  # internal or customer

	# Get accessible departments
	if context.is_system_manager:
		departments = frappe.get_all(
			"MM Department",
			filters={"is_active": 1},
			fields=["name", "department_name", "department_slug", "timezone"]
		)
	elif context.is_department_leader:
		departments = frappe.get_all(
			"MM Department",
			filters={
				"department_leader": frappe.session.user,
				"is_active": 1
			},
			fields=["name", "department_name", "department_slug", "timezone"]
		)
	else:
		# Regular members can create customer meetings for themselves
		department_members = frappe.get_all(
			"MM Department Member",
			filters={
				"member": frappe.session.user,
				"is_active": 1
			},
			pluck="parent"
		)
		departments = frappe.get_all(
			"MM Department",
			filters={
				"name": ["in", department_members],
				"is_active": 1
			},
			fields=["name", "department_name", "department_slug", "timezone"]
		) if department_members else []

	context.departments = departments

	# Page title
	if context.form_type == "internal":
		context.title = _("Create Internal Meeting")
	else:
		context.title = _("Create Customer Meeting")

	return context


@frappe.whitelist()
def get_meeting_types(department):
	"""
	Get meeting types for a department based on form type

	Args:
		department (str): Department name

	Returns:
		list: Array of meeting types
	"""
	meeting_types = frappe.get_all(
		"MM Meeting Type",
		filters={
			"department": department,
			"is_active": 1
		},
		fields=["name", "meeting_name", "duration", "description", "is_internal", "is_public", "location_type"]
	)

	return meeting_types


@frappe.whitelist()
def get_department_members_list(department):
	"""
	Get all active members of a department

	Args:
		department (str): Department name

	Returns:
		list: Array of members
	"""
	# Check permissions
	user_roles = frappe.get_roles()

	if "System Manager" not in user_roles and "Department Leader" not in user_roles:
		is_member = frappe.db.exists(
			"MM Department Member",
			{"parent": department, "member": frappe.session.user, "is_active": 1}
		)
		if not is_member:
			frappe.throw(_("You don't have permission to view this department's members"))

	members = frappe.get_all(
		"MM Department Member",
		filters={"parent": department, "is_active": 1},
		fields=["member"]
	)

	result = []
	for m in members:
		user = frappe.get_doc("User", m.member)
		result.append({
			"user_id": user.name,
			"full_name": user.full_name,
			"email": user.email
		})

	return result


@frappe.whitelist()
def check_availability(member, date, time, duration):
	"""
	Check if a member is available at a specific date/time

	Args:
		member (str): User ID
		date (str): Date (YYYY-MM-DD)
		time (str): Time (HH:MM)
		duration (int): Duration in minutes

	Returns:
		dict: {
			"available": bool,
			"reason": str (if not available)
		}
	"""
	from meeting_manager.meeting_manager.utils.validation import check_member_availability
	from frappe.utils import get_time

	scheduled_date = getdate(date)
	scheduled_time = get_time(time)

	return check_member_availability(member, scheduled_date, scheduled_time, int(duration))
