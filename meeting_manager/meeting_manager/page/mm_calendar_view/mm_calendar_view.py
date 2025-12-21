"""
Meeting Manager Calendar View Page
Redirects to the mm-calendar-view www page
"""

import frappe

def get_context(context):
	"""
	Redirect to the mm-calendar-view www page
	"""
	context.no_cache = 1
	frappe.redirect_to_message(
		_("Redirecting to Meeting Manager Calendar"),
		_("You will be redirected to the calendar view page"),
		http_status_code=301,
		indicator_color="blue"
	)
	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = "/mm-calendar-view"
