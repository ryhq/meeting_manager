# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Internal Calendar View for System Managers and Department Leaders

This page provides a drag-and-drop calendar interface for managing bookings:
- Month/Week/Day views
- Department and member filtering
- Drag-to-reschedule bookings
- Drag-to-reassign bookings between members
- Quick actions (cancel, mark complete, etc.)
"""

import frappe
from frappe import _
from frappe.utils import getdate, get_datetime, add_days, now_datetime
from datetime import datetime, timedelta


def get_context(context):
	"""
	Calendar view for authenticated users only

	Permissions:
	- System Manager: Can view all bookings across all departments
	- Department Leader: Can view bookings for their departments
	- Department Member: Can view their own bookings only
	"""
	context.no_cache = 1
	context.show_sidebar = True

	# Check authentication
	if frappe.session.user == "Guest":
		frappe.throw(_("You must be logged in to access the calendar view"), frappe.PermissionError)

	# Get user roles
	user_roles = frappe.get_roles()
	context.user_roles = user_roles
	context.is_system_manager = "System Manager" in user_roles
	context.is_department_leader = "Department Leader" in user_roles

	# Get departments accessible to user
	if context.is_system_manager:
		# System managers see all departments
		departments = frappe.get_all(
			"MM Department",
			filters={"is_active": 1},
			fields=["name", "department_name", "department_slug"]
		)
	elif context.is_department_leader:
		# Department leaders see their departments
		departments = frappe.get_all(
			"MM Department",
			filters={
				"department_leader": frappe.session.user,
				"is_active": 1
			},
			fields=["name", "department_name", "department_slug"]
		)
	else:
		# Regular members see departments they belong to
		department_members = frappe.get_all(
			"MM Department Member",
			filters={
				"member": frappe.session.user,
				"is_active": 1
			},
			fields=["parent"],
			pluck="parent"
		)
		departments = frappe.get_all(
			"MM Department",
			filters={
				"name": ["in", department_members],
				"is_active": 1
			},
			fields=["name", "department_name", "department_slug"]
		) if department_members else []

	context.departments = departments

	# Get initial filters from query params
	context.selected_department = frappe.form_dict.get("department")
	context.selected_member = frappe.form_dict.get("member")
	context.view_type = frappe.form_dict.get("view", "month")  # month, week, day

	# Get members for selected department (for filtering)
	context.members = []
	if context.selected_department:
		members = frappe.get_all(
			"MM Department Member",
			filters={
				"parent": context.selected_department,
				"is_active": 1
			},
			fields=["member"]
		)

		context.members = []
		for m in members:
			user = frappe.get_doc("User", m.member)
			context.members.append({
				"user_id": user.name,
				"full_name": user.full_name,
				"email": user.email
			})

	# Page title
	context.title = _("Calendar View - Meeting Manager")

	return context


@frappe.whitelist()
def get_calendar_events(department=None, member=None, start=None, end=None):
	"""
	Get calendar events for FullCalendar

	Args:
		department (str, optional): Filter by department
		member (str, optional): Filter by member
		start (str): Start date (ISO format)
		end (str): End date (ISO format)

	Returns:
		list: Array of event objects for FullCalendar
	"""
	# Build filters
	filters = {}

	# Date range filter
	if start:
		filters["scheduled_date"] = [">=", getdate(start)]
	if end:
		filters["scheduled_date"] = ["<=", getdate(end)]

	# Permission-based filtering
	user_roles = frappe.get_roles()

	if "System Manager" in user_roles:
		# System managers see all bookings
		if department:
			filters["department"] = department
		if member:
			filters["assigned_to"] = member

	elif "Department Leader" in user_roles:
		# Department leaders see bookings for their departments
		led_departments = frappe.get_all(
			"MM Department",
			filters={"department_leader": frappe.session.user},
			pluck="name"
		)

		if led_departments:
			if department and department in led_departments:
				filters["department"] = department
			else:
				filters["department"] = ["in", led_departments]

			if member:
				filters["assigned_to"] = member
		else:
			return []  # Leader has no departments

	else:
		# Regular members see only their own bookings
		filters["assigned_to"] = frappe.session.user

	# Get bookings
	bookings = frappe.get_all(
		"MM Meeting Booking",
		filters=filters,
		fields=[
			"name", "booking_reference", "booking_type", "department",
			"meeting_type", "assigned_to", "customer_name",
			"scheduled_date", "scheduled_start_time", "scheduled_end_time",
			"duration", "status", "location_type", "video_platform",
			"meeting_link", "customer_email", "customer_phone"
		],
		order_by="scheduled_date asc, scheduled_start_time asc"
	)

	# Convert to FullCalendar event format
	events = []
	for booking in bookings:
		# Combine date and time
		start_datetime = datetime.combine(booking.scheduled_date, booking.scheduled_start_time)
		end_datetime = datetime.combine(booking.scheduled_date, booking.scheduled_end_time)

		# Get meeting type name
		meeting_type_name = frappe.get_value("MM Meeting Type", booking.meeting_type, "meeting_name")

		# Get assigned user name
		assigned_user_name = frappe.get_value("User", booking.assigned_to, "full_name")

		# Determine color based on status
		color_map = {
			"Confirmed": "#10b981",  # Green
			"Pending": "#f59e0b",    # Yellow
			"Cancelled": "#ef4444",  # Red
			"Completed": "#3b82f6",  # Blue
			"No-show": "#6b7280"     # Gray
		}

		# Event title
		if booking.booking_type == "Customer Booking":
			title = f"{booking.customer_name} - {meeting_type_name}"
		else:
			title = f"{meeting_type_name} (Internal)"

		events.append({
			"id": booking.name,
			"resourceId": booking.assigned_to,  # For resource timeline view
			"title": title,
			"start": start_datetime.isoformat(),
			"end": end_datetime.isoformat(),
			"backgroundColor": color_map.get(booking.status, "#6b7280"),
			"borderColor": color_map.get(booking.status, "#6b7280"),
			"textColor": "#ffffff",
			"extendedProps": {
				"booking_id": booking.name,
				"booking_reference": booking.booking_reference,
				"booking_type": booking.booking_type,
				"department": booking.department,
				"meeting_type": booking.meeting_type,
				"meeting_type_name": meeting_type_name,
				"assigned_to": booking.assigned_to,
				"assigned_to_name": assigned_user_name,
				"customer_name": booking.customer_name,
				"customer_email": booking.customer_email,
				"customer_phone": booking.customer_phone,
				"status": booking.status,
				"duration": booking.duration,
				"location_type": booking.location_type,
				"video_platform": booking.video_platform,
				"meeting_link": booking.meeting_link
			}
		})

	return events


@frappe.whitelist()
def get_department_members(department=None):
	"""
	Get active members of a department (for resource view)

	Args:
		department (str, optional): Department name. If None, returns all accessible members.

	Returns:
		list: Array of member objects
	"""
	# Check permissions
	user_roles = frappe.get_roles()

	# Get members based on department and permissions
	if department:
		# Check permissions for specific department
		if "System Manager" not in user_roles and "Department Leader" not in user_roles:
			is_member = frappe.db.exists(
				"MM Department Member",
				{"parent": department, "member": frappe.session.user, "is_active": 1}
			)
			if not is_member:
				frappe.throw(_("You don't have permission to view this department's members"))

		# Get members for specific department
		members = frappe.get_all(
			"MM Department Member",
			filters={"parent": department, "is_active": 1},
			fields=["member"],
			distinct=True
		)
	else:
		# Get all accessible members
		if "System Manager" in user_roles:
			# System managers see all members
			members = frappe.get_all(
				"MM Department Member",
				filters={"is_active": 1},
				fields=["member"],
				distinct=True
			)
		elif "Department Leader" in user_roles:
			# Department leaders see members from their departments
			led_departments = frappe.get_all(
				"MM Department",
				filters={"department_leader": frappe.session.user},
				pluck="name"
			)
			members = frappe.get_all(
				"MM Department Member",
				filters={"parent": ["in", led_departments], "is_active": 1},
				fields=["member"],
				distinct=True
			) if led_departments else []
		else:
			# Regular members see only themselves
			members = [{"member": frappe.session.user}]

	# Build result with unique members
	result = []
	seen_members = set()
	for m in members:
		if m.member not in seen_members:
			seen_members.add(m.member)
			user = frappe.get_doc("User", m.member)
			result.append({
				"id": user.name,
				"title": user.full_name,
				"email": user.email
			})

	return result
