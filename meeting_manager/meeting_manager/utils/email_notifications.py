import frappe
from frappe import _
from frappe.utils import get_datetime, format_datetime


def check_email_configured():
	"""Check if outgoing email is configured in Frappe"""
	try:
		email_account = frappe.get_doc("Email Account", frappe.get_value("Email Account", {"default_outgoing": 1}))
		if email_account:
			return True, None
	except Exception as e:
		return False, str(e)

	return False, "No default outgoing email account configured"


def send_booking_confirmation_email(booking_id):
	"""
	Send booking confirmation emails to customer and assigned team members

	Args:
		booking_id: Name of the MM Meeting Booking document
	"""
	try:
		# Check if email is configured
		is_configured, error_msg = check_email_configured()
		if not is_configured:
			frappe.log_error(
				f"Email not configured: {error_msg}. Booking {booking_id} created but confirmation email not sent.",
				"Email Configuration Error"
			)
			return {
				"success": False,
				"message": "Booking created successfully, but email notifications could not be sent. Please contact support.",
				"error": error_msg
			}

		# Get booking details
		booking = frappe.get_doc("MM Meeting Booking", booking_id)
		meeting_type = frappe.get_doc("MM Meeting Type", booking.meeting_type)
		# Department is linked through meeting_type, not directly on booking
		department = frappe.get_doc("MM Department", meeting_type.department)

		# Get assigned users
		assigned_users = []
		for assignment in booking.assigned_users:
			user = frappe.get_doc("User", assignment.user)
			assigned_users.append({
				"full_name": user.full_name,
				"email": user.email
			})

		# Prepare context for templates
		context = {
			"booking": booking,
			"meeting_type": meeting_type,
			"department": department,
			"assigned_users": assigned_users,
			"formatted_start": format_datetime(booking.start_datetime, "EEE, MMM dd, yyyy 'at' hh:mm a"),
			"formatted_end": format_datetime(booking.end_datetime, "hh:mm a"),
			"site_url": frappe.utils.get_url(),
			"cancel_url": f"{frappe.utils.get_url()}/cancel-booking?token={booking.cancel_token}",
			"reschedule_url": f"{frappe.utils.get_url()}/reschedule-booking?token={booking.reschedule_token}"
		}

		# Send customer confirmation email
		customer_email_sent = False
		if booking.customer_email:
			try:
				customer_subject = f"Booking Confirmed: {meeting_type.meeting_name} - {booking.booking_reference}"
				customer_message = frappe.render_template(
					"meeting_manager/templates/emails/booking_confirmation_customer.html",
					context
				)

				frappe.sendmail(
					recipients=[booking.customer_email],
					subject=customer_subject,
					message=customer_message,
					reference_doctype="MM Meeting Booking",
					reference_name=booking.name,
					now=True  # Send immediately
				)
				customer_email_sent = True
				frappe.logger().info(f"Customer confirmation email sent to {booking.customer_email}")
			except Exception as e:
				frappe.log_error(
					f"Failed to send customer confirmation email for booking {booking_id}: {str(e)}\n{frappe.get_traceback()}",
					"Customer Email Error"
				)

		# Send team member notification emails
		team_emails_sent = 0
		for user in assigned_users:
			if user["email"]:
				try:
					team_subject = f"New Meeting Assignment: {meeting_type.meeting_name} - {booking.booking_reference}"
					team_message = frappe.render_template(
						"meeting_manager/templates/emails/booking_confirmation_team.html",
						context
					)

					frappe.sendmail(
						recipients=[user["email"]],
						subject=team_subject,
						message=team_message,
						reference_doctype="MM Meeting Booking",
						reference_name=booking.name,
						now=True  # Send immediately
					)
					team_emails_sent += 1
					frappe.logger().info(f"Team member notification email sent to {user['email']}")
				except Exception as e:
					frappe.log_error(
						f"Failed to send team notification email to {user['email']} for booking {booking_id}: {str(e)}\n{frappe.get_traceback()}",
						"Team Email Error"
					)

		# Return success status
		return {
			"success": True,
			"customer_email_sent": customer_email_sent,
			"team_emails_sent": team_emails_sent,
			"message": "Booking confirmation emails have been sent"
		}

	except Exception as e:
		frappe.log_error(
			f"Error in send_booking_confirmation_email for {booking_id}: {str(e)}\n{frappe.get_traceback()}",
			"Booking Email Error"
		)
		return {
			"success": False,
			"message": "An error occurred while sending confirmation emails",
			"error": str(e)
		}


def send_reschedule_confirmation_email(booking_id, old_datetime_dict, new_datetime_dict, member_changed=False, old_assigned_to=None, new_assigned_to=None):
	"""
	Send reschedule confirmation emails to customer and assigned team members

	Args:
		booking_id: Name of the MM Meeting Booking document
		old_datetime_dict: Dictionary with old date/time {"date": "...", "time": "..."}
		new_datetime_dict: Dictionary with new date/time {"date": "...", "time": "..."}
		member_changed: Boolean indicating if assigned member changed
		old_assigned_to: Name of old assigned member (if changed)
		new_assigned_to: Name of new assigned member (if changed)
	"""
	try:
		# Check if email is configured
		is_configured, error_msg = check_email_configured()
		if not is_configured:
			frappe.log_error(
				f"Email not configured: {error_msg}. Booking {booking_id} rescheduled but notification email not sent.",
				"Email Configuration Error"
			)
			return {
				"success": False,
				"message": "Booking rescheduled successfully, but email notifications could not be sent.",
				"error": error_msg
			}

		# Get booking details
		booking = frappe.get_doc("MM Meeting Booking", booking_id)
		meeting_type = frappe.get_doc("MM Meeting Type", booking.meeting_type)
		# Department is linked through meeting_type, not directly on booking
		department = frappe.get_doc("MM Department", meeting_type.department)

		# Get assigned users
		assigned_users = []
		for assignment in booking.assigned_users:
			user = frappe.get_doc("User", assignment.user)
			assigned_users.append({
				"full_name": user.full_name,
				"email": user.email
			})

		# Prepare context for templates
		context = {
			"booking": booking,
			"meeting_type": meeting_type,
			"department": department,
			"assigned_users": assigned_users,
			"formatted_start": format_datetime(booking.start_datetime, "EEE, MMM dd, yyyy 'at' hh:mm a"),
			"formatted_end": format_datetime(booking.end_datetime, "hh:mm a"),
			"site_url": frappe.utils.get_url(),
			"cancel_url": f"{frappe.utils.get_url()}/cancel-booking?token={booking.cancel_token}",
			"reschedule_url": f"{frappe.utils.get_url()}/reschedule-booking?token={booking.reschedule_token}",
			# Reschedule-specific data
			"old_datetime": old_datetime_dict,
			"new_datetime": new_datetime_dict,
			"member_changed": member_changed,
			"old_assigned_to": old_assigned_to,
			"new_assigned_to": new_assigned_to
		}

		# Send customer reschedule confirmation email
		customer_email_sent = False
		if booking.customer_email:
			try:
				customer_subject = f"Booking Rescheduled: {meeting_type.meeting_name} - {booking.booking_reference}"
				customer_message = frappe.render_template(
					"meeting_manager/templates/emails/booking_reschedule_confirmation.html",
					context
				)

				frappe.sendmail(
					recipients=[booking.customer_email],
					subject=customer_subject,
					message=customer_message,
					reference_doctype="MM Meeting Booking",
					reference_name=booking.name,
					now=True  # Send immediately
				)
				customer_email_sent = True
				frappe.logger().info(f"Customer reschedule confirmation email sent to {booking.customer_email}")
			except Exception as e:
				frappe.log_error(
					f"Failed to send customer reschedule confirmation email for booking {booking_id}: {str(e)}\n{frappe.get_traceback()}",
					"Customer Reschedule Email Error"
				)

		# Send team member notification emails about reschedule
		team_emails_sent = 0
		for user in assigned_users:
			if user["email"]:
				try:
					team_subject = f"Meeting Rescheduled: {meeting_type.meeting_name} - {booking.booking_reference}"
					# Use the same template for team members
					team_message = frappe.render_template(
						"meeting_manager/templates/emails/booking_reschedule_confirmation.html",
						context
					)

					frappe.sendmail(
						recipients=[user["email"]],
						subject=team_subject,
						message=team_message,
						reference_doctype="MM Meeting Booking",
						reference_name=booking.name,
						now=True  # Send immediately
					)
					team_emails_sent += 1
					frappe.logger().info(f"Team member reschedule notification email sent to {user['email']}")
				except Exception as e:
					frappe.log_error(
						f"Failed to send team reschedule notification email to {user['email']} for booking {booking_id}: {str(e)}\n{frappe.get_traceback()}",
						"Team Reschedule Email Error"
					)

		# Return success status
		return {
			"success": True,
			"customer_email_sent": customer_email_sent,
			"team_emails_sent": team_emails_sent,
			"message": "Booking reschedule confirmation emails have been sent"
		}

	except Exception as e:
		frappe.log_error(
			f"Error in send_reschedule_confirmation_email for {booking_id}: {str(e)}\n{frappe.get_traceback()}",
			"Booking Reschedule Email Error"
		)
		return {
			"success": False,
			"message": "An error occurred while sending reschedule confirmation emails",
			"error": str(e)
		}


def send_cancellation_email(booking_id):
	"""
	Send cancellation notification emails to customer and assigned team members

	Args:
		booking_id: Name of the MM Meeting Booking document
	"""
	try:
		# Check if email is configured
		is_configured, error_msg = check_email_configured()
		if not is_configured:
			frappe.log_error(
				f"Email not configured: {error_msg}. Booking {booking_id} cancelled but notification email not sent.",
				"Email Configuration Error"
			)
			return {
				"success": False,
				"message": "Booking cancelled successfully, but email notifications could not be sent.",
				"error": error_msg
			}

		# Get booking details
		booking = frappe.get_doc("MM Meeting Booking", booking_id)
		meeting_type = frappe.get_doc("MM Meeting Type", booking.meeting_type)
		# Department is linked through meeting_type, not directly on booking
		department = frappe.get_doc("MM Department", meeting_type.department)

		# Get assigned users
		assigned_users = []
		for assignment in booking.assigned_users:
			user = frappe.get_doc("User", assignment.user)
			assigned_users.append({
				"full_name": user.full_name,
				"email": user.email
			})

		# Prepare context for templates
		context = {
			"booking": booking,
			"meeting_type": meeting_type,
			"department": department,
			"assigned_users": assigned_users,
			"formatted_start": format_datetime(booking.start_datetime, "EEE, MMM dd, yyyy 'at' hh:mm a"),
			"formatted_end": format_datetime(booking.end_datetime, "hh:mm a"),
			"site_url": frappe.utils.get_url(),
			"rebook_url": f"{frappe.utils.get_url()}/meeting-booking/{department.department_slug}"
		}

		# Send cancellation email to customer
		customer_email_sent = False
		if booking.customer_email:
			try:
				customer_subject = f"Booking Cancelled: {meeting_type.meeting_name} - {booking.booking_reference}"
				customer_message = frappe.render_template(
					"meeting_manager/templates/emails/booking_cancellation.html",
					context
				)

				frappe.sendmail(
					recipients=[booking.customer_email],
					subject=customer_subject,
					message=customer_message,
					reference_doctype="MM Meeting Booking",
					reference_name=booking.name,
					now=True  # Send immediately
				)
				customer_email_sent = True
				frappe.logger().info(f"Customer cancellation email sent to {booking.customer_email}")
			except Exception as e:
				frappe.log_error(
					f"Failed to send customer cancellation email for booking {booking_id}: {str(e)}\n{frappe.get_traceback()}",
					"Customer Cancellation Email Error"
				)

		# Send cancellation notification to team members
		team_emails_sent = 0
		for user in assigned_users:
			if user["email"]:
				try:
					team_subject = f"Meeting Cancelled: {meeting_type.meeting_name} - {booking.booking_reference}"
					team_message = frappe.render_template(
						"meeting_manager/templates/emails/booking_cancellation.html",
						{**context, "is_team_member": True}
					)

					frappe.sendmail(
						recipients=[user["email"]],
						subject=team_subject,
						message=team_message,
						reference_doctype="MM Meeting Booking",
						reference_name=booking.name,
						now=True  # Send immediately
					)
					team_emails_sent += 1
					frappe.logger().info(f"Team member cancellation email sent to {user['email']}")
				except Exception as e:
					frappe.log_error(
						f"Failed to send team cancellation email to {user['email']} for booking {booking_id}: {str(e)}\n{frappe.get_traceback()}",
						"Team Cancellation Email Error"
					)

		# Return success status
		return {
			"success": True,
			"customer_email_sent": customer_email_sent,
			"team_emails_sent": team_emails_sent,
			"message": "Cancellation notification emails have been sent"
		}

	except Exception as e:
		frappe.log_error(
			f"Error in send_cancellation_email for {booking_id}: {str(e)}\n{frappe.get_traceback()}",
			"Cancellation Email Error"
		)
		return {
			"success": False,
			"message": "An error occurred while sending cancellation emails",
			"error": str(e)
		}
