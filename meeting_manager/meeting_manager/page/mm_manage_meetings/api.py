"""
API endpoints for Manage Meetings page
Provides data to the React frontend
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_meetings(status=None):
	"""
	Get meetings for the current user based on their role

	Args:
		status (str, optional): Filter by status (Confirmed, Pending, etc.)

	Returns:
		dict: Contains meetings list and statistics
	"""
	try:
		# Get user roles
		user_roles = frappe.get_roles()

		# Build filters
		filters = {}
		if status:
			filters["booking_status"] = status

		# Permission-based filtering
		# For now, system managers see all meetings
		# TODO: Implement proper role-based filtering when schema supports it
		if "System Manager" not in user_roles:
			# Non-system managers see all meetings for now
			# Future: filter by assigned users
			pass

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
				"booking_date",
				"start_datetime",
				"end_datetime",
				"duration",
				"booking_status",
				"location_type",
				"video_meeting_url",
				"meeting_title",
			],
			order_by="booking_date desc, start_datetime desc",
			limit=100  # Limit to prevent performance issues
		)

		# Enrich meeting data with related info
		enriched_meetings = []
		for meeting in meetings:
			# Get meeting type name
			meeting_type_name = frappe.get_value(
				"MM Meeting Type",
				meeting.meeting_type,
				"meeting_name"
			) if meeting.meeting_type else "N/A"

			# Get assigned users from child table
			assigned_users = frappe.get_all(
				"MM Meeting Booking Assigned User",
				filters={"parent": meeting.name},
				fields=["user"],
				limit=1
			)
			assigned_to = assigned_users[0].user if assigned_users else None
			assigned_to_name = frappe.get_value("User", assigned_to, "full_name") if assigned_to else "Not Assigned"

			# Format datetime strings
			from datetime import datetime
			if meeting.start_datetime:
				start_dt = meeting.start_datetime
				scheduled_date = start_dt.strftime("%Y-%m-%d") if isinstance(start_dt, datetime) else str(start_dt).split()[0]
				start_time = start_dt.strftime("%H:%M") if isinstance(start_dt, datetime) else str(start_dt).split()[1][:5]
			else:
				scheduled_date = str(meeting.booking_date) if meeting.booking_date else "N/A"
				start_time = "N/A"

			if meeting.end_datetime:
				end_dt = meeting.end_datetime
				end_time = end_dt.strftime("%H:%M") if isinstance(end_dt, datetime) else str(end_dt).split()[1][:5]
			else:
				end_time = "N/A"

			enriched_meetings.append({
				"name": meeting.name,
				"booking_reference": meeting.booking_reference,
				"booking_type": "Internal Booking" if meeting.is_internal else "Customer Booking",
				"meeting_type": meeting.meeting_type,
				"meeting_type_name": meeting_type_name,
				"assigned_to": assigned_to,
				"assigned_to_name": assigned_to_name,
				"customer_name": meeting.customer_name or "N/A",
				"customer_email": meeting.customer_email or "N/A",
				"customer_phone": meeting.customer_phone or "N/A",
				"scheduled_date": scheduled_date,
				"scheduled_start_time": start_time,
				"scheduled_end_time": end_time,
				"duration": meeting.duration or 0,
				"status": meeting.booking_status,
				"location_type": meeting.location_type or "N/A",
				"video_platform": "Video Call" if meeting.video_meeting_url else "N/A",
				"meeting_link": meeting.video_meeting_url or "",
				"department_name": "N/A",  # Not in current schema
			})

		# Calculate statistics (without status filter for overall stats)
		stats_filters = {}
		# Note: We don't filter by department or assigned user for now since schema doesn't support it directly

		stats = {
			"total": frappe.db.count("MM Meeting Booking", filters=stats_filters),
			"confirmed": frappe.db.count(
				"MM Meeting Booking",
				filters={**stats_filters, "booking_status": "Confirmed"}
			),
			"pending": frappe.db.count(
				"MM Meeting Booking",
				filters={**stats_filters, "booking_status": "Pending"}
			),
			"completed": frappe.db.count(
				"MM Meeting Booking",
				filters={**stats_filters, "booking_status": "Completed"}
			),
			"cancelled": frappe.db.count(
				"MM Meeting Booking",
				filters={**stats_filters, "booking_status": "Cancelled"}
			),
		}

		return {
			"meetings": enriched_meetings,
			"stats": stats
		}

	except Exception as e:
		frappe.log_error(f"Error fetching meetings: {str(e)}", "Manage Meetings API")
		frappe.throw(
			_("Failed to fetch meetings. Please try again."),
			title=_("Error")
		)
