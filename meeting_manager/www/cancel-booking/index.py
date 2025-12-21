import frappe
from frappe import _
from meeting_manager.meeting_manager.api.public import cancel_booking

def get_context(context):
	"""
	Cancel booking page - allows customers to cancel using their cancel token
	Route: /cancel-booking?token={cancel_token}
	"""
	context.no_cache = 1
	context.show_sidebar = False

	# Get cancel token from URL
	cancel_token = frappe.form_dict.get('token')
	confirmed = frappe.form_dict.get('confirmed')  # User clicked confirm button

	if not cancel_token:
		context.error = _("No cancellation token provided. Please use the link from your confirmation email.")
		context.title = "Invalid Link"
		return context

	# If user confirmed cancellation, process it
	if confirmed == '1':
		try:
			result = cancel_booking(cancel_token)
			context.cancelled = True
			context.title = "Booking Cancelled"
			context.message = result.get("message")
			return context
		except Exception as e:
			context.error = str(e)
			context.title = "Cancellation Failed"
			return context

	# Otherwise, show confirmation form
	try:
		booking = frappe.get_value(
			"MM Meeting Booking",
			{"cancel_token": cancel_token},
			[
				"name", "booking_reference", "booking_status", "customer_name",
				"customer_email", "start_datetime", "end_datetime", "meeting_type"
			],
			as_dict=True
		)

		if not booking:
			context.error = _("Invalid or expired cancellation link.")
			context.title = "Invalid Link"
			return context

		# Check if already cancelled
		if booking.booking_status == "Cancelled":
			context.already_cancelled = True
			context.title = "Already Cancelled"
			context.booking = frappe._dict(booking)
			return context

		if booking.booking_status == "Completed":
			context.error = _("This booking has already been completed and cannot be cancelled.")
			context.title = "Cannot Cancel"
			return context

		# Get meeting type details
		meeting_type = frappe.get_doc("MM Meeting Type", booking.meeting_type)
		department = frappe.get_doc("MM Department", meeting_type.department)

		# Set context for confirmation page
		context.title = "Cancel Your Booking"
		context.booking = frappe._dict(booking)
		context.meeting_type = frappe._dict({
			"meeting_name": meeting_type.meeting_name,
			"duration": meeting_type.duration
		})
		context.department = frappe._dict({
			"department_name": department.department_name
		})
		context.cancel_token = cancel_token
		context.show_confirmation = True

	except Exception as e:
		frappe.log_error(f"Error loading cancellation page: {str(e)}", "Cancel Booking Page Error")
		context.error = _("An error occurred. Please try again or contact support.")
		context.title = "Error"

	return context
