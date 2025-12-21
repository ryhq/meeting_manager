import frappe
from frappe import _
from frappe.utils import getdate, get_time
from datetime import datetime
from meeting_manager.meeting_manager.api.public import get_departments, get_department_meeting_types

def get_context(context):
	"""
	Universal booking route handler
	Handles all booking pages based on URL parameters

	Routes:
	/meeting-booking -> Step 1: Department list
	/meeting-booking/sales -> Step 2: Meeting types for sales dept
	/meeting-booking/sales/product-demo -> Step 3: Date picker
	/meeting-booking/sales/product-demo/2024-12-15 -> Step 4: Time slots
	/meeting-booking/sales/product-demo/2024-12-15/10:00 -> Step 5: Customer details form
	/meeting-booking/confirm/{booking_id} -> Step 6: Confirmation (handled separately)
	"""
	context.no_cache = 1
	context.show_sidebar = False

	# Get URL parameters
	department_slug = frappe.form_dict.get('department_slug')
	meeting_type_slug = frappe.form_dict.get('meeting_type_slug')
	date = frappe.form_dict.get('date')
	time = frappe.form_dict.get('time')

	# Route based on parameters
	if not department_slug:
		# Step 1: Department selection
		return render_department_list(context)
	elif not meeting_type_slug:
		# Step 2: Meeting type selection
		return render_meeting_types(context, department_slug)
	elif not date:
		# Step 3: Date picker
		return render_date_picker(context, department_slug, meeting_type_slug)
	elif not time:
		# Step 4: Time slot selection
		return render_time_slots(context, department_slug, meeting_type_slug, date)
	else:
		# Step 5: Customer details form
		return render_customer_form(context, department_slug, meeting_type_slug, date, time)


def render_department_list(context):
	"""Step 1: Show list of departments"""
	context.title = "Book a Meeting"
	context.meta_description = "Select a department to book a meeting"

	# Use API instead of direct database queries
	api_response = get_departments()
	context.departments = api_response.get("departments", [])

	context.current_step = 1
	context.total_steps = 6
	# No template needed - default step1_departments.html from index.html

	return context


def render_meeting_types(context, department_slug):
	"""Step 2: Show meeting types for department"""
	# Use API instead of direct database queries
	api_response = get_department_meeting_types(department_slug)

	department_data = api_response.get("department", {})
	meeting_types = api_response.get("meeting_types", [])

	# Transform API response to match template expectations
	department_info = {
		"department_name": department_data.get('name'),
		"department_slug": department_data.get('slug'),
		"description": department_data.get('description'),
		"timezone": department_data.get('timezone')
	}

	context.title = f"Select Meeting Type - {department_info['department_name']}"
	context.meta_description = f"Choose a meeting type with {department_info['department_name']}"
	context.department = department_info
	context.meeting_types = meeting_types
	context.current_step = 2
	context.total_steps = 6
	# Don't set template - let index.html handle it

	return context


def render_date_picker(context, department_slug, meeting_type_slug):
	"""Step 3: Date picker calendar"""
	# Get department and meeting type
	department, meeting_type = get_department_and_meeting_type(department_slug, meeting_type_slug)

	# Get current month/year
	now = datetime.now()

	context.title = f"Select Date - {meeting_type.meeting_name}"
	context.meta_description = f"Choose a date for your {meeting_type.meeting_name} with {department.department_name}"
	context.department = department
	context.meeting_type = meeting_type
	context.current_month = now.month
	context.current_year = now.year
	context.current_step = 3
	context.total_steps = 6
	# Don't set template - let index.html handle it

	return context


def render_time_slots(context, department_slug, meeting_type_slug, date_str):
	"""Step 4: Time slot selection"""
	# Get department and meeting type
	department, meeting_type = get_department_and_meeting_type(department_slug, meeting_type_slug)

	# Validate date
	try:
		selected_date = getdate(date_str)
	except:
		frappe.throw(_("Invalid date format"), frappe.ValidationError)

	context.title = f"Select Time - {meeting_type.meeting_name}"
	context.meta_description = f"Choose a time for your {meeting_type.meeting_name} on {selected_date.strftime('%B %d, %Y')}"
	context.department = department
	context.meeting_type = meeting_type
	context.selected_date = date_str
	context.selected_date_display = selected_date.strftime("%B %d, %Y")
	context.current_step = 4
	context.total_steps = 6
	# Don't set template - let index.html handle it

	return context


def render_customer_form(context, department_slug, meeting_type_slug, date_str, time_str):
	"""Step 5: Customer details form"""
	# Get department and meeting type
	department, meeting_type = get_department_and_meeting_type(department_slug, meeting_type_slug)

	# Validate date and time
	try:
		selected_date = getdate(date_str)
		selected_time = get_time(time_str)
	except:
		frappe.throw(_("Invalid date or time format"), frappe.ValidationError)

	context.title = f"Enter Your Details - {meeting_type.meeting_name}"
	context.meta_description = "Complete your booking by providing your contact information"
	context.department = department
	context.meeting_type = meeting_type
	context.selected_date = date_str
	context.selected_date_display = selected_date.strftime("%B %d, %Y")
	context.selected_time = time_str
	context.selected_time_display = selected_time.strftime("%I:%M %p")
	context.current_step = 5
	context.total_steps = 6
	# Don't set template - let index.html handle it

	return context


def get_department_and_meeting_type(department_slug, meeting_type_slug):
	"""Helper function to get department and meeting type"""
	# Get department
	department = frappe.get_value(
		"MM Department",
		{"department_slug": department_slug, "is_active": 1},
		["name", "department_name", "department_slug", "timezone"],
		as_dict=True
	)

	if not department:
		frappe.throw(_("Department not found or inactive"), frappe.DoesNotExistError)

	# Get meeting type
	meeting_type = frappe.get_value(
		"MM Meeting Type",
		{
			"meeting_slug": meeting_type_slug,
			"department": department.name,
			"is_active": 1,
			"is_public": 1
		},
		["name", "meeting_name", "meeting_slug", "description", "duration", "location_type"],
		as_dict=True
	)

	if not meeting_type:
		frappe.throw(_("Meeting type not found or inactive"), frappe.DoesNotExistError)

	return department, meeting_type
