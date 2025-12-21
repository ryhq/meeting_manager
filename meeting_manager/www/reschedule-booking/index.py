import frappe
from frappe import _
from frappe.utils import getdate, get_time
from datetime import datetime
from meeting_manager.meeting_manager.api.public import get_booking_details, reschedule_booking

def get_context(context):
	"""
	Reschedule booking route handler
	Handles all reschedule pages based on URL parameters

	Routes:
	/reschedule-booking?token={token} -> Step 1: Current booking details
	/reschedule-booking?token={token}&step=date -> Step 2: Date picker
	/reschedule-booking?token={token}&step=time&date=2024-12-15 -> Step 3: Time slots
	/reschedule-booking?token={token}&step=confirm&date=2024-12-15&time=10:00 -> Step 4: Confirmation
	"""
	context.no_cache = 1
	context.show_sidebar = False

	# Get token from URL
	reschedule_token = frappe.form_dict.get('token')

	if not reschedule_token:
		context.error = _("No reschedule token provided. Please use the link from your confirmation email.")
		context.title = "Invalid Link"
		return context

	# Get booking details using token
	try:
		booking_details = get_booking_details(reschedule_token)
		context.booking = frappe._dict(booking_details)
		context.reschedule_token = reschedule_token
	except Exception as e:
		frappe.log_error(f"Error loading reschedule page: {str(e)}", "Reschedule Booking Page Error")
		context.error = str(e)
		context.title = "Error"
		return context

	# Get step and other parameters
	step = frappe.form_dict.get('step')
	date = frappe.form_dict.get('date')
	time = frappe.form_dict.get('time')
	confirmed = frappe.form_dict.get('confirmed')

	# Extract department and meeting type info
	department_info = booking_details.get("department", {})
	meeting_type_info = booking_details.get("meeting_type", {})

	context.department = frappe._dict(department_info)
	context.meeting_type = frappe._dict(meeting_type_info)

	# Route based on step
	if step == 'date' or (not step and not date and not time):
		# Step 2: Date picker
		return render_date_picker(context)
	elif step == 'time' or (date and not time):
		# Step 3: Time slot selection
		return render_time_slots(context, date)
	elif step == 'confirm' or (date and time and not confirmed):
		# Step 4: Confirmation
		return render_confirmation(context, date, time)
	elif confirmed == '1':
		# Process reschedule
		return process_reschedule(context, date, time)
	else:
		# Step 1: Current booking details (default)
		return render_booking_details(context)


def render_booking_details(context):
	"""Step 1: Show current booking details"""
	context.title = "Reschedule Your Booking"
	context.meta_description = "View your booking details and select a new date and time"
	context.current_step = 1
	context.total_steps = 4
	return context


def render_date_picker(context):
	"""Step 2: Date picker calendar"""
	# Get current month/year
	now = datetime.now()

	meeting_type = context.meeting_type
	department = context.department

	context.title = f"Select New Date - {meeting_type.meeting_name}"
	context.meta_description = f"Choose a new date for your {meeting_type.meeting_name}"
	context.current_month = now.month
	context.current_year = now.year
	context.current_step = 2
	context.total_steps = 4

	return context


def render_time_slots(context, date_str):
	"""Step 3: Time slot selection"""
	meeting_type = context.meeting_type

	# Validate date
	try:
		selected_date = getdate(date_str)
	except:
		frappe.throw(_("Invalid date format"), frappe.ValidationError)

	context.title = f"Select New Time - {meeting_type.meeting_name}"
	context.meta_description = f"Choose a new time for your {meeting_type.meeting_name} on {selected_date.strftime('%B %d, %Y')}"
	context.selected_date = date_str
	context.selected_date_display = selected_date.strftime("%B %d, %Y")
	context.current_step = 3
	context.total_steps = 4

	return context


def render_confirmation(context, date_str, time_str):
	"""Step 4: Confirmation page"""
	meeting_type = context.meeting_type
	booking = context.booking

	# Validate date and time
	try:
		selected_date = getdate(date_str)
		selected_time = get_time(time_str)
	except:
		frappe.throw(_("Invalid date or time format"), frappe.ValidationError)

	context.title = f"Confirm Reschedule - {meeting_type.meeting_name}"
	context.meta_description = "Confirm your booking reschedule"
	context.selected_date = date_str
	context.selected_date_display = selected_date.strftime("%B %d, %Y")
	context.selected_time = time_str
	context.selected_time_display = selected_time.strftime("%I:%M %p")
	context.current_step = 4
	context.total_steps = 4

	return context


def process_reschedule(context, date_str, time_str):
	"""Process the reschedule request"""
	try:
		result = reschedule_booking(context.reschedule_token, date_str, time_str)
		context.rescheduled = True
		context.title = "Booking Rescheduled Successfully"
		context.result = frappe._dict(result)
		return context
	except Exception as e:
		frappe.log_error(f"Error processing reschedule: {str(e)}", "Reschedule Processing Error")
		context.error = str(e)
		context.title = "Reschedule Failed"
		return context
