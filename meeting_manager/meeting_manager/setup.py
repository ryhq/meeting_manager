"""
Setup functions for Meeting Manager app
"""
import frappe
import json


def create_calendar_page():
	"""
	Create the mm-calendar-view Page DocType if it doesn't exist
	This is required for the workspace link to work
	"""
	if not frappe.db.exists("Page", "mm-calendar-view"):
		print("Creating mm-calendar-view Page...")
		page = frappe.new_doc("Page")
		page.name = "mm-calendar-view"
		page.title = "Meeting Manager Calendar"
		page.module = "Meeting Manager"
		page.standard = "Yes"
		page.page_name = "mm-calendar-view"
		page.insert(ignore_permissions=True)
		frappe.db.commit()
		print("✅ Meeting Manager Calendar Page created")
	else:
		print("ℹ️  Meeting Manager Calendar Page already exists")


def after_install():
	"""
	Called automatically after app installation
	Creates the Meeting Manager workspace and calendar-view Page
	"""
	try:
		# Create calendar-view Page if it doesn't exist
		create_calendar_page()

		# Create workspace
		setup_workspace()

		print("\n" + "="*60)
		print("✅ Meeting Manager workspace created automatically!")
		print("="*60)
		print("\n📌 Next Steps:")
		print("1. Refresh your browser (Ctrl+R or Cmd+R)")
		print("2. Click on 'Apps' in the top menu")
		print("3. You should see 'Meeting Manager' app")
		print("4. Click it to access the workspace")
		print("\n")
	except Exception as e:
		frappe.log_error(f"Workspace creation failed during installation: {str(e)}", "Meeting Manager Installation")
		print(f"\n⚠️  Warning: Workspace creation failed: {str(e)}")
		print("You can create it manually later by running:")
		print("bench --site [site-name] execute meeting_manager.meeting_manager.setup.setup_workspace")
		print()


def setup_workspace():
	"""
	Create or update Meeting Manager workspace with proper Frappe v15 structure

	Usage:
		bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.setup_workspace
	"""

	print("\n" + "="*60)
	print("🚀 SETTING UP MEETING MANAGER WORKSPACE (Frappe v15)")
	print("="*60 + "\n")

	# Check if workspace exists
	workspace_name = "Meeting Manager"

	if frappe.db.exists("Workspace", workspace_name):
		print(f"Updating existing workspace: {workspace_name}")
		workspace = frappe.get_doc("Workspace", workspace_name)
		# Clear existing links and shortcuts
		workspace.links = []
		workspace.shortcuts = []
	else:
		print(f"Creating new workspace: {workspace_name}")
		workspace = frappe.new_doc("Workspace")
		workspace.name = workspace_name
		workspace.title = workspace_name

	# Set basic properties
	workspace.module = "Meeting Manager"
	workspace.app = "meeting_manager"
	workspace.icon = "calendar"
	workspace.indicator_color = "green"
	workspace.is_hidden = 0
	workspace.public = 1

	# Create proper Frappe v15 workspace content structure
	# Key insight: shortcut blocks reference shortcuts by label (shortcut_name)
	# and card blocks organize links into sections (card_name matches "Card Break" label)
	content = [
		{
			"id": "shortcuts_header",
			"type": "header",
			"data": {
				"text": "<span class='h4'><b>Quick Access</b></span>",
				"col": 12
			}
		},
		{
			"id": "shortcut_meeting_bookings",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Meeting Bookings",
				"col": 4
			}
		},
		{
			"id": "shortcut_new_department",
			"type": "shortcut",
			"data": {
				"shortcut_name": "New Department",
				"col": 4
			}
		},
		{
			"id": "shortcut_meeting_types",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Meeting Types",
				"col": 4
			}
		},
		{
			"id": "shortcut_my_settings",
			"type": "shortcut",
			"data": {
				"shortcut_name": "User Settings",
				"col": 4
			}
		},
		{
			"id": "shortcut_availability",
			"type": "shortcut",
			"data": {
				"shortcut_name": "User Availability Rule",
				"col": 4
			}
		},
		{
			"id": "spacer_1",
			"type": "spacer",
			"data": {
				"col": 12
			}
		},
		{
			"id": "bookings_by_status_header",
			"type": "header",
			"data": {
				"text": "<span class='h4'><b>Bookings by Status</b></span>",
				"col": 12
			}
		},
		{
			"id": "shortcut_pending",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Pending",
				"col": 4
			}
		},
		{
			"id": "shortcut_confirmed",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Confirmed",
				"col": 4
			}
		},
		{
			"id": "shortcut_cancelled",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Cancelled",
				"col": 4
			}
		},
		{
			"id": "shortcut_completed",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Completed",
				"col": 4
			}
		},
		{
			"id": "shortcut_no_show",
			"type": "shortcut",
			"data": {
				"shortcut_name": "No-Show",
				"col": 4
			}
		},
		{
			"id": "shortcut_rescheduled",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Rescheduled",
				"col": 4
			}
		},
		{
			"id": "spacer_2",
			"type": "spacer",
			"data": {
				"col": 12
			}
		},
		{
			"id": "links_header",
			"type": "header",
			"data": {
				"text": "<span class='h4'><b>Meeting Manager</b></span>",
				"col": 12
			}
		},
		{
			"id": "card_bookings",
			"type": "card",
			"data": {
				"card_name": "Bookings",
				"col": 4
			}
		},
		{
			"id": "card_setup",
			"type": "card",
			"data": {
				"card_name": "Setup",
				"col": 4
			}
		},
		{
			"id": "card_configuration",
			"type": "card",
			"data": {
				"card_name": "Configuration",
				"col": 4
			}
		}
	]

	workspace.content = json.dumps(content)

	# Add shortcuts with proper Frappe v15 structure
	# Note: label must match shortcut_name in content blocks
	shortcuts = [
		{
			"label": "Meeting Bookings",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Grey",
			"format": "{} Total"
		},
		{
			"label": "New Department",
			"link_to": "MM Department",
			"type": "DocType",
			"doc_view": "New",
			"color": "Blue",
			"format": "{} Create"
		},
		{
			"label": "Meeting Types",
			"link_to": "MM Meeting Type",
			"type": "DocType",
			"doc_view": "List",
			"color": "Green",
			"format": "{} Available"
		},
		{
			"label": "User Settings",
			"link_to": "MM User Settings",
			"type": "DocType",
			"doc_view": "List",
			"color": "Orange",
			"format": "{} Settings"
		},
		{
			"label": "User Availability Rule",
			"link_to": "MM User Availability Rule",
			"type": "DocType",
			"doc_view": "List",
			"color": "Purple",
			"format": "{} Rules"
		},
		# Booking Status Shortcuts
		{
			"label": "Pending",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Yellow",
			"format": "{} Pending",
			"stats_filter": "{\"booking_status\":\"Pending\"}"
		},
		{
			"label": "Confirmed",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Green",
			"format": "{} Confirmed",
			"stats_filter": "{\"booking_status\":\"Confirmed\"}"
		},
		{
			"label": "Cancelled",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Red",
			"format": "{} Cancelled",
			"stats_filter": "{\"booking_status\":\"Cancelled\"}"
		},
		{
			"label": "Completed",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Blue",
			"format": "{} Completed",
			"stats_filter": "{\"booking_status\":\"Completed\"}"
		},
		{
			"label": "No-Show",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Grey",
			"format": "{} No-Show",
			"stats_filter": "{\"booking_status\":\"No-Show\"}"
		},
		{
			"label": "Rescheduled",
			"link_to": "MM Meeting Booking",
			"type": "DocType",
			"doc_view": "List",
			"color": "Orange",
			"format": "{} Rescheduled",
			"stats_filter": "{\"booking_status\":\"Rescheduled\"}"
		}
	]

	for shortcut in shortcuts:
		workspace.append("shortcuts", shortcut)

	# Add links with proper Card Break structure (Frappe v15 style)
	# Card Break creates sections, Link adds actual links within sections
	# The "Card Break" label must match the card_name in content blocks
	links_data = [
		# Top-level Calendar link (appears directly under Meeting Manager)
		{
			"label": "Calendar",
			"type": "Link",
			"link_type": "Page",
			"link_to": "mm-calendar-view",
			"onboard": 0,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		# Bookings Section
		{
			"label": "Bookings",
			"type": "Card Break",
			"hidden": 0,
			"onboard": 0,
			"link_count": 0
		},
		{
			"label": "Meeting Bookings",
			"type": "Link",
			"link_type": "DocType",
			"link_to": "MM Meeting Booking",
			"onboard": 1,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		{
			"label": "Calendar",
			"type": "Link",
			"link_type": "Page",
			"link_to": "mm-calendar-view",
			"onboard": 0,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		{
			"label": "Timeline Calendar",
			"type": "Link",
			"link_type": "Page",
			"link_to": "mm-timeline-calendar",
			"onboard": 0,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		# Setup Section
		{
			"label": "Setup",
			"type": "Card Break",
			"hidden": 0,
			"onboard": 0,
			"link_count": 0
		},
		{
			"label": "Departments",
			"type": "Link",
			"link_type": "DocType",
			"link_to": "MM Department",
			"onboard": 1,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		{
			"label": "Meeting Types",
			"type": "Link",
			"link_type": "DocType",
			"link_to": "MM Meeting Type",
			"onboard": 0,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		# Configuration Section
		{
			"label": "Configuration",
			"type": "Card Break",
			"hidden": 0,
			"onboard": 0,
			"link_count": 0
		},
		{
			"label": "User Settings",
			"type": "Link",
			"link_type": "DocType",
			"link_to": "MM User Settings",
			"onboard": 0,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		},
		{
			"label": "Availability Rules",
			"type": "Link",
			"link_type": "DocType",
			"link_to": "MM User Availability Rule",
			"onboard": 0,
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0
		}
	]

	for link in links_data:
		workspace.append("links", link)

	# Save the workspace
	workspace.save(ignore_permissions=True)
	frappe.db.commit()

	print(f"✅ Workspace '{workspace_name}' created/updated successfully")
	print(f"\n📄 Workspace saved to: meeting_manager/workspace/meeting_manager/meeting_manager.json")
	print(f"\n📊 Workspace contains:")
	print(f"   - {len(shortcuts)} shortcuts (Quick Access buttons)")
	print(f"   - {len([l for l in links_data if l['type'] == 'Link'])} links in {len([l for l in links_data if l['type'] == 'Card Break'])} sections")
	print(f"   - {len(content)} content blocks (layout structure)")
	print(f"\n💡 You can now customize the workspace layout via the UI:")
	print(f"   - http://bestsecurity.local:8001/app/workspace/Meeting Manager")
	print(f"\n🔄 To export your UI customizations back to code, run:")
	print(f"   bench --site bestsecurity.local export-fixtures")

	# Export workspace to JSON file
	export_workspace_to_file(workspace)

	print("\n" + "="*60)
	print("✅ SETUP COMPLETE! Refresh your browser to see changes.")
	print("="*60)

	return workspace


def export_workspace_to_file(workspace):
	"""
	Export workspace to JSON file for fixtures
	"""
	import os

	# Get the workspace directory path
	workspace_dir = frappe.get_app_path("meeting_manager", "meeting_manager", "workspace", "meeting_manager")

	# Create directory if it doesn't exist
	if not os.path.exists(workspace_dir):
		os.makedirs(workspace_dir)

	# Export to JSON file
	workspace_file = os.path.join(workspace_dir, "meeting_manager.json")

	with open(workspace_file, 'w') as f:
		json.dump(workspace.as_dict(), f, indent=1, default=str)

	print(f"📁 Workspace exported to: {workspace_file}")
