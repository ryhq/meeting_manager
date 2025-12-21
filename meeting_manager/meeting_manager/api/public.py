# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Public Booking APIs

These APIs are exposed to the public (allow_guest=True) for the
customer-facing booking interface. They handle the 6-step booking flow:
1. Get Departments
2. Get Meeting Types for Department
3. Get Available Dates
4. Get Available Time Slots
5. Create Customer Booking
"""

import frappe
from frappe import _
from frappe.utils import getdate, get_time, get_datetime, now_datetime
from datetime import datetime, timedelta
from meeting_manager.meeting_manager.api.availability import get_department_available_dates, get_department_available_slots
from meeting_manager.meeting_manager.api.assignment import assign_to_member, update_member_assignment_tracking
from meeting_manager.meeting_manager.utils.timezone import get_department_timezone
from meeting_manager.meeting_manager.utils.email_notifications import (
	send_booking_confirmation_email,
	send_cancellation_email
)
import hashlib
import secrets


@frappe.whitelist(allow_guest=True)
def get_departments():
	"""
	Step 1: Get all active departments for public booking

	Returns:
		dict: {
			"departments": list of department objects
		}
	"""
	departments = frappe.get_all(
		"MM Department",
		filters={"is_active": 1},
		fields=[
			"name",
			"department_name",
			"department_slug",
			"description",
			"timezone"
		],
		order_by="department_name"
	)

	# Add meeting types count for each department
	for dept in departments:
		dept["meeting_types_count"] = frappe.db.count(
			"MM Meeting Type",
			filters={
				"department": dept.name,
				"is_active": 1,
				"is_public": 1
			}
		)

		dept["public_booking_url"] = f"/book/{dept.department_slug}"

	return {
		"departments": departments
	}


@frappe.whitelist(allow_guest=True)
def get_department_meeting_types(department_slug):
	"""
	Step 2: Get all active public meeting types for a department

	Args:
		department_slug (str): Department slug

	Returns:
		dict: {
			"meeting_types": list of meeting type objects,
			"department": department info
		}
	"""
	# Get department
	department = frappe.get_value(
		"MM Department",
		{"department_slug": department_slug, "is_active": 1},
		["name", "department_name", "description", "timezone"],
		as_dict=True
	)

	if not department:
		frappe.throw(_("Department not found or inactive"), frappe.DoesNotExistError)

	# Get public meeting types
	meeting_types = frappe.get_all(
		"MM Meeting Type",
		filters={
			"department": department.name,
			"is_active": 1,
			"is_public": 1
		},
		fields=[
			"name",
			"meeting_name",
			"meeting_slug",
			"description",
			"duration",
			"location_type"
		],
		order_by="meeting_name"
	)

	return {
		"meeting_types": meeting_types,
		"department": {
			"name": department.department_name,
			"slug": department_slug,
			"description": department.description,
			"timezone": department.timezone
		}
	}


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def get_available_dates(department_slug, meeting_type_slug, month, year):
	"""
	Step 3: Get available dates for a department/meeting type

	Args:
		department_slug (str): Department slug
		meeting_type_slug (str): Meeting type slug
		month (int or str): Month (1-12)
		year (int or str): Year

	Returns:
		dict: {
			"available_dates": list of date strings,
			"timezone": department timezone,
			...
		}
	"""
	try:
		month = int(month)
		year = int(year)
	except (ValueError, TypeError):
		frappe.throw(_("Invalid month or year"))

	if not (1 <= month <= 12):
		frappe.throw(_("Month must be between 1 and 12"))

	if year < datetime.now().year:
		frappe.throw(_("Cannot book dates in the past"))

	result = get_department_available_dates(department_slug, meeting_type_slug, month, year)
	# Add success flag for frontend compatibility
	result["success"] = True
	return result


@frappe.whitelist(allow_guest=True)
def get_available_slots(department_slug, meeting_type_slug, date, visitor_timezone=None):
	"""
	Step 4: Get available time slots for a specific date

	Args:
		department_slug (str): Department slug
		meeting_type_slug (str): Meeting type slug
		date (str): Date (YYYY-MM-DD)
		visitor_timezone (str, optional): Visitor's timezone

	Returns:
		dict: {
			"slots": list of time slot objects,
			...
		}
	"""
	# Validate date
	try:
		booking_date = getdate(date)
	except:
		frappe.throw(_("Invalid date format. Use YYYY-MM-DD"))

	if booking_date < getdate():
		frappe.throw(_("Cannot book dates in the past"))

	result = get_department_available_slots(department_slug, meeting_type_slug, date, visitor_timezone)
	# Add success flag for frontend compatibility
	result["success"] = True
	return result


@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_customer_booking(booking_data):
	"""
	Step 5: Create a customer booking

	This is the final step where the customer submits their booking request

	Args:
		booking_data (dict): {
			"department_slug": str,
			"meeting_type_slug": str,
			"scheduled_date": str (YYYY-MM-DD),
			"scheduled_start_time": str (HH:MM),
			"customer_name": str,
			"customer_email": str,
			"customer_phone": str,
			"customer_timezone": str,
			"customer_notes": str (optional)
		}

	Returns:
		dict: {
			"success": bool,
			"booking_id": str,
			"confirmation": dict with booking details,
			"cancel_url": str,
			"reschedule_url": str
		}
	"""
	# Rate limiting (10 requests per hour per IP)
	if not check_rate_limit():
		frappe.throw(_("Too many booking requests. Please try again later."), frappe.RateLimitExceededError)

	# Parse booking data
	if isinstance(booking_data, str):
		import json
		booking_data = json.loads(booking_data)

	# Validate required fields
	required_fields = [
		"department_slug",
		"meeting_type_slug",
		"scheduled_date",
		"scheduled_start_time",
		"customer_name",
		"customer_email",
		"customer_phone"
	]

	for field in required_fields:
		if not booking_data.get(field):
			frappe.throw(_(f"Missing required field: {field}"))

	# Get department
	department = frappe.get_value(
		"MM Department",
		{"department_slug": booking_data["department_slug"], "is_active": 1},
		["name", "department_name", "timezone"],
		as_dict=True
	)

	if not department:
		frappe.throw(_("Department not found or inactive"))

	# Get meeting type
	meeting_type = frappe.get_value(
		"MM Meeting Type",
		{
			"meeting_slug": booking_data["meeting_type_slug"],
			"department": department.name,
			"is_active": 1,
			"is_public": 1
		},
		["name", "meeting_name", "duration", "location_type", "video_platform", "requires_approval"],
		as_dict=True
	)

	if not meeting_type:
		frappe.throw(_("Meeting type not found or inactive"))

	# Validate date and time
	try:
		scheduled_date = getdate(booking_data["scheduled_date"])
		scheduled_start_time = get_time(booking_data["scheduled_start_time"])
	except:
		frappe.throw(_("Invalid date or time format"))

	if scheduled_date < getdate():
		frappe.throw(_("Cannot book dates in the past"))

	# Calculate end time
	start_datetime = datetime.combine(scheduled_date, scheduled_start_time)
	end_datetime = start_datetime + timedelta(minutes=meeting_type.duration)
	scheduled_end_time = end_datetime.time()

	# Auto-assign to available member
	assignment = assign_to_member(
		department.name,
		meeting_type.name,
		scheduled_date,
		scheduled_start_time,
		meeting_type.duration
	)

	# Generate security tokens for cancel/reschedule
	cancel_token = secrets.token_urlsafe(32)
	reschedule_token = secrets.token_urlsafe(32)

	# Build self-service URLs
	site_url = frappe.utils.get_url()
	cancel_link = f"{site_url}/book/cancel?token={cancel_token}"
	reschedule_link = f"{site_url}/book/reschedule?token={reschedule_token}"

	# Create booking document
	booking = frappe.get_doc({
		"doctype": "MM Meeting Booking",
		"booking_source": "Public Booking Page",
		"is_internal": 0,
		"meeting_type": meeting_type.name,

		# Customer information
		"customer_name": booking_data["customer_name"],
		"customer_email": booking_data["customer_email"],
		"customer_phone": booking_data["customer_phone"],
		"customer_notes": booking_data.get("customer_notes"),

		# Scheduling - using combined datetime fields
		"start_datetime": start_datetime,
		"end_datetime": end_datetime,

		# Meeting details
		"location_type": meeting_type.location_type,
		"meeting_title": meeting_type.meeting_name,
		"meeting_description": meeting_type.description,

		# Status
		"booking_status": "Pending" if meeting_type.requires_approval else "Confirmed",
		"requires_approval": meeting_type.requires_approval,

		# Customer self-service tokens and links
		"cancel_token": cancel_token,
		"reschedule_token": reschedule_token,
		"cancel_link": cancel_link,
		"reschedule_link": reschedule_link
	})

	# Add assigned user to child table
	booking.append("assigned_users", {
		"user": assignment["assigned_to"],
		"is_primary_host": 1,
		"assigned_by": frappe.session.user
	})

	# Insert booking (will trigger validation and notifications)
	booking.insert(ignore_permissions=True)

	# Send confirmation emails
	try:
		email_result = send_booking_confirmation_email(booking.name)
		if not email_result.get("success"):
			frappe.log_error(
				f"Email notification failed for booking {booking.name}: {email_result.get('error')}",
				"Booking Email Warning"
			)
	except Exception as e:
		frappe.log_error(
			f"Exception while sending confirmation email for booking {booking.name}: {str(e)}",
			"Booking Email Exception"
		)

	# Generate response
	return {
		"success": True,
		"booking_id": booking.name,
		"confirmation": {
			"booking_id": booking.name,
			"meeting_type": meeting_type.meeting_name,
			"scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
			"scheduled_time": scheduled_start_time.strftime("%H:%M"),
			"duration": meeting_type.duration,
			"status": booking.booking_status,
			"assigned_to_email": frappe.get_value("User", assignment["assigned_to"], "email"),
			"message": "Your booking has been confirmed! Check your email for details and calendar invite." if booking.booking_status == "Confirmed" else "Your booking request has been received and is pending approval."
		},
		"cancel_url": booking.cancel_link,
		"reschedule_url": booking.reschedule_link
	}


def check_rate_limit():
	"""
	Check if the current IP has exceeded rate limit for booking creation

	Rate limit: 10 requests per hour per IP

	Returns:
		bool: True if within limit, False if exceeded
	"""
	if frappe.session.user != "Guest":
		# Logged in users are not rate limited
		return True

	client_ip = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None

	if not client_ip:
		return True  # Cannot determine IP, allow

	# Count bookings from this IP in the last hour
	one_hour_ago = now_datetime() - timedelta(hours=1)

	recent_bookings = frappe.db.count(
		"MM Meeting Booking",
		filters={
			"created_from_ip": client_ip,
			"creation": [">=", one_hour_ago]
		}
	)

	return recent_bookings < 10


@frappe.whitelist(allow_guest=True)
def cancel_booking(token):
	"""
	Cancel a booking using the cancel token

	Args:
		token (str): Cancel token

	Returns:
		dict: {
			"success": bool,
			"message": str
		}
	"""
	if not token:
		frappe.throw(_("Cancel token is required"))

	# Find booking by cancel token
	booking = frappe.get_value(
		"MM Meeting Booking",
		{"cancel_token": token},
		["name", "booking_status", "customer_name", "start_datetime"],
		as_dict=True
	)

	if not booking:
		frappe.throw(_("Invalid or expired cancellation link"))

	if booking.booking_status in ["Cancelled", "Completed"]:
		frappe.throw(_("This booking has already been {0}").format(booking.booking_status.lower()))

	# Cancel the booking
	booking_doc = frappe.get_doc("MM Meeting Booking", booking.name)
	booking_doc.booking_status = "Cancelled"
	booking_doc.cancellation_reason = "Customer Cancelled"
	booking_doc.cancelled_at = now_datetime()
	booking_doc.save(ignore_permissions=True)

	# Send cancellation emails
	try:
		email_result = send_cancellation_email(booking.name)
		if not email_result.get("success"):
			frappe.log_error(
				f"Cancellation email notification failed for booking {booking.name}: {email_result.get('error')}",
				"Cancellation Email Warning"
			)
	except Exception as e:
		frappe.log_error(
			f"Exception while sending cancellation email for booking {booking.name}: {str(e)}",
			"Cancellation Email Exception"
		)

	return {
		"success": True,
		"message": _("Your booking has been cancelled successfully. A confirmation email has been sent.")
	}


@frappe.whitelist(allow_guest=True)
def get_booking_details(token):
	"""
	Get booking details using reschedule token (for reschedule flow)

	Args:
		token (str): Reschedule token

	Returns:
		dict: Booking details
	"""
	if not token:
		frappe.throw(_("Token is required"))

	booking = frappe.get_value(
		"MM Meeting Booking",
		{"reschedule_token": token},
		[
			"name", "meeting_type", "start_datetime", "end_datetime",
			"customer_name", "customer_email", "booking_status"
		],
		as_dict=True
	)

	if not booking:
		frappe.throw(_("Invalid or expired link"))

	if booking.booking_status in ["Cancelled", "Completed"]:
		frappe.throw(_("This booking has already been {0}").format(booking.booking_status.lower()))

	# Get meeting type details to extract department
	meeting_type_doc = frappe.get_doc("MM Meeting Type", booking.meeting_type)
	department = frappe.get_value("MM Department", meeting_type_doc.department, ["department_name", "department_slug", "timezone"], as_dict=True)

	# Calculate duration from datetime fields
	duration = int((booking.end_datetime - booking.start_datetime).total_seconds() / 60)

	return {
		"booking_id": booking.name,
		"department": department,
		"meeting_type": {
			"meeting_name": meeting_type_doc.meeting_name,
			"meeting_slug": meeting_type_doc.meeting_slug
		},
		"current_date": booking.start_datetime.strftime("%Y-%m-%d"),
		"current_time": booking.start_datetime.strftime("%H:%M"),
		"duration": duration,
		"customer_name": booking.customer_name,
		"customer_email": booking.customer_email,
		"status": booking.booking_status
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def reschedule_booking(token, new_date, new_time):
	"""
	Reschedule a booking using the reschedule token

	Args:
		token (str): Reschedule token
		new_date (str): New date (YYYY-MM-DD)
		new_time (str): New time (HH:MM)

	Returns:
		dict: {
			"success": bool,
			"message": str,
			"booking_id": str,
			"old_datetime": dict,
			"new_datetime": dict
		}
	"""
	if not token:
		frappe.throw(_("Reschedule token is required"))

	if not new_date or not new_time:
		frappe.throw(_("New date and time are required"))

	# Find booking by reschedule token
	booking_data = frappe.get_value(
		"MM Meeting Booking",
		{"reschedule_token": token},
		[
			"name", "booking_status", "meeting_type", "start_datetime",
			"end_datetime", "customer_name", "customer_email"
		],
		as_dict=True
	)

	if not booking_data:
		frappe.throw(_("Invalid or expired reschedule link"))

	if booking_data.booking_status in ["Cancelled", "Completed"]:
		frappe.throw(_("This booking has already been {0}").format(booking_data.booking_status.lower()))

	# Get full booking document to access assigned users
	booking = frappe.get_doc("MM Meeting Booking", booking_data.name)

	# Get department from meeting type
	meeting_type_doc = frappe.get_doc("MM Meeting Type", booking.meeting_type)
	department_name = meeting_type_doc.department

	# Calculate current duration
	current_duration = int((booking.end_datetime - booking.start_datetime).total_seconds() / 60)

	# Validate new date and time
	try:
		new_scheduled_date = getdate(new_date)
		new_scheduled_start_time = get_time(new_time)
	except:
		frappe.throw(_("Invalid date or time format"))

	if new_scheduled_date < getdate():
		frappe.throw(_("Cannot reschedule to a date in the past"))

	# Store old datetime values
	old_start_datetime = booking.start_datetime
	old_end_datetime = booking.end_datetime

	# Calculate new datetime values
	new_start_datetime = datetime.combine(new_scheduled_date, new_scheduled_start_time)
	new_end_datetime = new_start_datetime + timedelta(minutes=current_duration)

	# Get primary assigned member (if any)
	current_member = None
	if booking.assigned_users:
		for assigned_user in booking.assigned_users:
			if assigned_user.is_primary_host:
				current_member = assigned_user.user
				break
		if not current_member and booking.assigned_users:
			current_member = booking.assigned_users[0].user

	# Check if currently assigned member is available at new time
	member_changed = False
	new_assigned_to = current_member

	if current_member:
		from meeting_manager.meeting_manager.utils.validation import check_member_availability

		current_member_available = check_member_availability(
			current_member,
			new_scheduled_date,
			new_scheduled_start_time,
			current_duration,
			exclude_booking=booking.name
		)

		# If current member is not available, try to find another member
		if not current_member_available["available"]:
			try:
				from meeting_manager.meeting_manager.api.assignment import assign_to_member

				assignment = assign_to_member(
					department_name,
					booking.meeting_type,
					new_scheduled_date,
					new_scheduled_start_time,
					current_duration
				)

				new_assigned_to = assignment["assigned_to"]
				member_changed = True
			except Exception as e:
				frappe.throw(_(
					"No members are available at the requested time. "
					"Please choose a different time slot. Reason: {0}"
				).format(str(e)))

	# Update booking
	booking.start_datetime = new_start_datetime
	booking.end_datetime = new_end_datetime
	booking.booking_status = "Rescheduled"

	# Update assigned user if changed
	if member_changed and new_assigned_to:
		# Clear current assignments
		booking.assigned_users = []
		# Add new assignment
		booking.append("assigned_users", {
			"user": new_assigned_to,
			"is_primary_host": 1,
			"assigned_by": frappe.session.user
		})

	# Regenerate security tokens for new booking
	import secrets
	booking.cancel_token = secrets.token_urlsafe(32)
	booking.reschedule_token = secrets.token_urlsafe(32)

	# Add to booking history
	booking.append("booking_history", {
		"event_type": "Rescheduled",
		"event_by": frappe.session.user,
		"event_datetime": now_datetime(),
		"event_description": f"Rescheduled from {old_start_datetime.strftime('%Y-%m-%d %H:%M')} to {new_start_datetime.strftime('%Y-%m-%d %H:%M')}" + (" - Member reassigned due to availability" if member_changed else "")
	})

	booking.save(ignore_permissions=True)
	frappe.db.commit()

	# Prepare datetime dictionaries for email
	old_datetime_dict = {
		"date": old_start_datetime.strftime("%B %d, %Y"),
		"time": old_start_datetime.strftime("%I:%M %p")
	}
	new_datetime_dict = {
		"date": new_start_datetime.strftime("%B %d, %Y"),
		"time": new_start_datetime.strftime("%I:%M %p")
	}

	# Send reschedule confirmation emails with new tokens
	try:
		from meeting_manager.meeting_manager.utils.email_notifications import send_reschedule_confirmation_email

		email_result = send_reschedule_confirmation_email(
			booking.name,
			old_datetime_dict,
			new_datetime_dict,
			member_changed=member_changed,
			old_assigned_to=old_assigned_to,
			new_assigned_to=new_assigned_to
		)
		if not email_result.get("success"):
			frappe.log_error(
				f"Reschedule confirmation email failed for booking {booking.name}: {email_result.get('error')}",
				"Reschedule Email Warning"
			)
	except Exception as e:
		frappe.log_error(
			f"Exception while sending reschedule confirmation email for booking {booking.name}: {str(e)}",
			"Reschedule Email Exception"
		)

	# Prepare response
	response = {
		"success": True,
		"message": _("Your booking has been rescheduled successfully. A confirmation email has been sent."),
		"booking_id": booking.name,
		"old_datetime": {
			"date": old_start_datetime.strftime("%Y-%m-%d"),
			"time": old_start_datetime.strftime("%H:%M")
		},
		"new_datetime": {
			"date": new_start_datetime.strftime("%Y-%m-%d"),
			"time": new_start_datetime.strftime("%H:%M")
		}
	}

	if member_changed:
		old_member_name = frappe.get_value("User", current_member, "full_name") if current_member else "Previous Host"
		new_member_name = frappe.get_value("User", new_assigned_to, "full_name")
		response["member_changed"] = True
		response["message"] += _(
			" Your meeting host has been changed from {0} to {1} due to availability."
		).format(old_member_name, new_member_name)
		response["old_assigned_to"] = old_member_name
		response["new_assigned_to"] = new_member_name

	return response


@frappe.whitelist(allow_guest=True)
def get_booking_confirmation(booking_id):
	"""
	Get booking confirmation details for the confirmation page

	This is called after a successful booking to display confirmation details.
	Uses booking_id to fetch all related information.

	Args:
		booking_id (str): Booking ID

	Returns:
		dict: {
			"success": bool,
			"booking": dict with booking details,
			"department": dict with department info,
			"meeting_type": dict with meeting type info,
			"assigned_users": list of assigned user names
		}
	"""
	if not booking_id:
		frappe.throw(_("Booking ID is required"))

	# Get booking details
	try:
		booking = frappe.get_doc("MM Meeting Booking", booking_id)
	except frappe.DoesNotExistError:
		frappe.throw(_("Booking not found"), frappe.DoesNotExistError)

	# Get meeting type details
	meeting_type = frappe.get_value(
		"MM Meeting Type",
		booking.meeting_type,
		["name", "meeting_name", "description", "duration", "location_type", "video_platform"],
		as_dict=True
	)

	if not meeting_type:
		frappe.throw(_("Meeting type not found"))

	# Get department details
	meeting_type_doc = frappe.get_doc("MM Meeting Type", booking.meeting_type)
	department = frappe.get_value(
		"MM Department",
		meeting_type_doc.department,
		["name", "department_name", "department_slug", "description", "timezone"],
		as_dict=True
	)

	if not department:
		frappe.throw(_("Department not found"))

	# Get assigned users with their full names
	assigned_users = []
	if booking.assigned_users:
		for assigned_user in booking.assigned_users:
			user_data = frappe.get_value(
				"User",
				assigned_user.user,
				["full_name", "email", "user_image"],
				as_dict=True
			)
			if user_data:
				assigned_users.append({
					"name": user_data.full_name,
					"email": user_data.email,
					"image": user_data.user_image,
					"is_primary": assigned_user.is_primary_host
				})

	# Format booking data for frontend
	booking_data = {
		"booking_id": booking.name,
		"booking_reference": booking.booking_reference,
		"booking_status": booking.booking_status,
		"booking_source": booking.booking_source,
		"is_internal": booking.is_internal,

		# Meeting details
		"meeting_title": booking.meeting_title,
		"meeting_description": booking.meeting_description,
		"location_type": booking.location_type,
		"meeting_location": booking.meeting_location,
		"video_meeting_url": booking.video_meeting_url,

		# Timing - keep as datetime objects for template compatibility
		"start_datetime": booking.start_datetime,
		"end_datetime": booking.end_datetime,
		"duration": booking.duration,

		# Customer info (only if not internal)
		"customer_name": booking.customer_name if not booking.is_internal else None,
		"customer_email": booking.customer_email if not booking.is_internal else None,
		"customer_phone": booking.customer_phone if not booking.is_internal else None,
		"customer_notes": booking.customer_notes if not booking.is_internal else None,

		# Self-service links
		"cancel_link": booking.cancel_link if not booking.is_internal else None,
		"reschedule_link": booking.reschedule_link if not booking.is_internal else None,

		# Approval info
		"requires_approval": booking.requires_approval,
		"approval_status": booking.approval_status if booking.requires_approval else None
	}

	return {
		"success": True,
		"booking": booking_data,
		"meeting_type": {
			"meeting_name": meeting_type.meeting_name,
			"description": meeting_type.description,
			"duration": meeting_type.duration,
			"location_type": meeting_type.location_type,
			"video_platform": meeting_type.video_platform
		},
		"department": {
			"department_name": department.department_name,
			"slug": department.department_slug,
			"description": department.description,
			"timezone": department.timezone
		},
		"assigned_users": assigned_users
	}
