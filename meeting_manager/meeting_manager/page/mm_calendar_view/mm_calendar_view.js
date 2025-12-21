/**
 * Meeting Manager Calendar View Page
 * Redirects to the mm-calendar-view www page
 */

frappe.pages['mm-calendar-view'].on_page_load = function(wrapper) {
	// Redirect to the actual calendar view
	window.location.href = '/mm-calendar-view';
}
