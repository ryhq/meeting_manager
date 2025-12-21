import frappe
from frappe import _
from meeting_manager.meeting_manager.api.public import get_booking_confirmation

def get_context(context):
	"""
	Confirmation page after successful booking
	Route: /booking-confirmation?booking_id={booking_id}
	"""
	context.no_cache = 1
	context.show_sidebar = False

	# Get booking ID from URL
	booking_id = frappe.form_dict.get('booking_id')

	if not booking_id:
		frappe.throw(_("Booking ID is required"), frappe.ValidationError)

	# Use the public API to get booking confirmation details
	try:
		confirmation_data = get_booking_confirmation(booking_id)
	except Exception as e:
		frappe.log_error(f"Error fetching booking confirmation: {str(e)}", "Booking Confirmation Error")
		frappe.throw(_("Unable to load booking confirmation. Please try again."))

	# Extract data from API response
	booking_data = confirmation_data.get("booking", {})
	meeting_type_data = confirmation_data.get("meeting_type", {})
	department_data = confirmation_data.get("department", {})
	assigned_users_data = confirmation_data.get("assigned_users", [])

	# Set context for template
	context.title = "Booking Confirmed!"
	context.booking = frappe._dict(booking_data)
	context.meeting_type = frappe._dict(meeting_type_data)
	context.department = frappe._dict(department_data)
	context.assigned_users = assigned_users_data
	context.assigned_users_names = [user.get("name") for user in assigned_users_data]

	return context
