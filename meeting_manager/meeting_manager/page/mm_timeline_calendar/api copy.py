"""
API endpoints for Timeline Calendar page
Provides resources (team members) and events (meetings) for FullCalendar
"""

import frappe
from frappe import _
from datetime import datetime


@frappe.whitelist()
def get_resources(department=None):
	"""
	Get team members to display as calendar resources

	Args:
		department (str, optional): Filter by department

	Returns:
		list: Resources in FullCalendar format
		[
			{"id": "user@example.com", "title": "John Doe"},
			...
		]
	"""
	try:
		user_roles = frappe.get_roles()
		resources = []

		if department:
			# Get members from specific department
			members = frappe.get_all(
				"MM Department Member",
				filters={"parent": department, "is_active": 1},
				fields=["user"],
				order_by="user asc"
			)

			for member in members:
				user_name = frappe.get_value("User", member.user, "full_name")
				resources.append({
					"id": member.user,
					"title": user_name or member.user
				})

		elif "System Manager" in user_roles:
			# System managers see all users with meeting access
			# Get all unique users who are assigned to meetings or are department members
			users = frappe.db.sql("""
				SELECT DISTINCT user.name, user.full_name
				FROM `tabUser` user
				WHERE user.enabled = 1
					AND user.name NOT IN ('Guest', 'Administrator')
				ORDER BY user.full_name ASC
			""", as_dict=True)

			for user in users:
				resources.append({
					"id": user.name,
					"title": user.full_name or user.name
				})

		else:
			# For department leaders and team members, get their accessible users
			if "Department Leader" in user_roles:
				# Get departments led by current user
				led_departments = frappe.get_all(
					"MM Department",
					filters={"department_leader": frappe.session.user, "is_active": 1},
					pluck="name"
				)

				# Get members from these departments
				if led_departments:
					members = frappe.get_all(
						"MM Department Member",
						filters={"parent": ["in", led_departments], "is_active": 1},
						fields=["user"],
						order_by="user asc"
					)

					for member in members:
						user_name = frappe.get_value("User", member.user, "full_name")
						resources.append({
							"id": member.user,
							"title": user_name or member.user
						})
			else:
				# Regular team members see only themselves
				user_name = frappe.get_value("User", frappe.session.user, "full_name")
				resources.append({
					"id": frappe.session.user,
					"title": user_name or frappe.session.user
				})

		# Remove duplicates
		seen = set()
		unique_resources = []
		for resource in resources:
			if resource["id"] not in seen:
				seen.add(resource["id"])
				unique_resources.append(resource)

		return unique_resources

	except Exception as e:
		frappe.log_error(f"Error fetching resources: {str(e)}", "Timeline Calendar API")
		frappe.throw(_("Failed to load resources. Please try again."))


@frappe.whitelist()
def get_events(start, end, department=None, status=None, assigned_to=None):
	"""
	Get meetings for calendar display

	Args:
		start (str): Start datetime (ISO format)
		end (str): End datetime (ISO format)
		department (str, optional): Filter by department
		status (str, optional): Filter by booking status
		assigned_to (str, optional): Filter by assigned user

	Returns:
		list: Events in FullCalendar format
		[
			{
				"id": "MM-MB-0001",
				"resourceId": "user@example.com",
				"title": "John Doe - 30-min Call",
				"start": "2025-12-17T14:00:00",
				"end": "2025-12-17T14:30:00",
				"backgroundColor": "#10b981",
				"borderColor": "#10b981",
				"textColor": "#ffffff",
				"extendedProps": {...}
			},
			...
		]
	"""
	try:
		user_roles = frappe.get_roles()

		# Build base filters
		filters = {
			"start_datetime": [">=", start],
			"end_datetime": ["<=", end]
		}

		if status:
			filters["booking_status"] = status

		# Permission-based filtering
		accessible_users = None

		if "System Manager" not in user_roles:
			if "Department Leader" in user_roles:
				# Get departments led by current user
				led_departments = frappe.get_all(
					"MM Department",
					filters={"department_leader": frappe.session.user, "is_active": 1},
					pluck="name"
				)

				# Get members from these departments
				if led_departments:
					accessible_users = frappe.get_all(
						"MM Department Member",
						filters={"parent": ["in", led_departments], "is_active": 1},
						pluck="user"
					)
			else:
				# Regular team members see only their bookings
				accessible_users = [frappe.session.user]

		# Fetch meetings
		meetings = frappe.get_all(
			"MM Meeting Booking",
			filters=filters,
			fields=[
				"name",
				"booking_reference",
				"is_internal",
				"meeting_type",
				"customer_name",
				"customer_email",
				"customer_phone",
				"start_datetime",
				"end_datetime",
				"duration",
				"booking_status",
				"location_type",
				"video_meeting_url",
				"meeting_title"
			],
			order_by="start_datetime asc",
			limit=500  # Limit for performance
		)

		# Color mapping based on status
		color_map = {
			"Confirmed": "#10b981",   # Green
			"Pending": "#f59e0b",     # Yellow/Orange
			"Cancelled": "#ef4444",   # Red
			"Completed": "#3b82f6",   # Blue
			"No-Show": "#6b7280",     # Gray
			"Rescheduled": "#8b5cf6"  # Purple
		}

		# Build events list
		events = []
		for meeting in meetings:
			# Get assigned users from child table
			assigned_users = frappe.get_all(
				"MM Meeting Booking Assigned User",
				filters={"parent": meeting.name},
				fields=["user", "is_primary_host"],
				order_by="is_primary_host desc"
			)

			# Filter by permission if needed
			if accessible_users:
				# Check if any assigned user is in accessible_users
				meeting_users = [au.user for au in assigned_users]
				if not any(user in accessible_users for user in meeting_users):
					continue  # Skip this meeting

			# Get meeting type name
			meeting_type_name = frappe.get_value(
				"MM Meeting Type",
				meeting.meeting_type,
				"meeting_name"
			) if meeting.meeting_type else "Meeting"

			# Determine event title
			customer_name = meeting.customer_name or meeting.customer_email or "Guest"
			event_title = f"{customer_name} - {meeting_type_name}"

			# Get status color
			event_color = color_map.get(meeting.booking_status, "#6b7280")

			# Create event for each assigned user (resource)
			for assigned_user in assigned_users:
				# Format datetime for FullCalendar
				start_dt = meeting.start_datetime
				end_dt = meeting.end_datetime

				if isinstance(start_dt, str):
					start_dt = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
				if isinstance(end_dt, str):
					end_dt = datetime.fromisoformat(end_dt.replace('Z', '+00:00'))

				event = {
					"id": meeting.name,
					"resourceId": assigned_user.user,
					"title": event_title,
					"start": start_dt.isoformat(),
					"end": end_dt.isoformat(),
					"backgroundColor": event_color,
					"borderColor": event_color,
					"textColor": "#ffffff",
					"extendedProps": {
						"booking_reference": meeting.booking_reference,
						"customer_name": meeting.customer_name or "N/A",
						"customer_email": meeting.customer_email or "N/A",
						"customer_phone": meeting.customer_phone or "N/A",
						"status": meeting.booking_status,
						"meeting_type": meeting_type_name,
						"location_type": meeting.location_type or "N/A",
						"video_meeting_url": meeting.video_meeting_url or "",
						"is_primary_host": assigned_user.is_primary_host,
						"duration": meeting.duration or 0
					}
				}

				events.append(event)

		return events

	except Exception as e:
		frappe.log_error(f"Error fetching events: {str(e)}", "Timeline Calendar API")
		frappe.throw(_("Failed to load events. Please try again."))
