"""
Migration script to rename calendar-view page to mm-calendar-view
Run this using:
bench --site bestsecurity.local execute meeting_manager.meeting_manager.migrate_calendar_page.migrate
"""

import frappe


def migrate():
	"""
	Rename the calendar-view Page to mm-calendar-view to avoid collision with ERPNext
	"""
	print("\n" + "="*60)
	print("🔄 MIGRATING CALENDAR PAGE NAME")
	print("="*60 + "\n")

	# Check if old page exists
	if frappe.db.exists("Page", "calendar-view"):
		print("Found old calendar-view page. Renaming to mm-calendar-view...")

		try:
			# Get the old page
			old_page = frappe.get_doc("Page", "calendar-view")

			# Check if new page already exists
			if frappe.db.exists("Page", "mm-calendar-view"):
				print("⚠️  mm-calendar-view page already exists. Deleting old calendar-view...")
				old_page.delete()
				frappe.db.commit()
				print("✅ Old calendar-view page deleted")
			else:
				# Rename the page
				old_page.name = "mm-calendar-view"
				old_page.page_name = "mm-calendar-view"
				old_page.title = "Meeting Manager Calendar"

				# Update the page using SQL to avoid validation issues
				frappe.db.sql("""
					UPDATE `tabPage`
					SET name = 'mm-calendar-view',
						page_name = 'mm-calendar-view',
						title = 'Meeting Manager Calendar'
					WHERE name = 'calendar-view'
				""")

				frappe.db.commit()
				print("✅ Page renamed from calendar-view to mm-calendar-view")

			# Update workspace links
			print("\nUpdating workspace links...")
			workspaces = frappe.get_all("Workspace", filters={"name": "Meeting Manager"})

			for ws in workspaces:
				workspace = frappe.get_doc("Workspace", ws.name)
				updated = False

				for link in workspace.links:
					if link.link_type == "Page" and link.link_to == "calendar-view":
						link.link_to = "mm-calendar-view"
						updated = True
						print(f"  - Updated link in workspace: {workspace.name}")

				if updated:
					workspace.save(ignore_permissions=True)

			frappe.db.commit()
			print("✅ Workspace links updated")

		except Exception as e:
			print(f"❌ Error during migration: {str(e)}")
			frappe.db.rollback()
			raise

	else:
		print("ℹ️  Old calendar-view page not found. Nothing to migrate.")

		# Check if new page exists
		if not frappe.db.exists("Page", "mm-calendar-view"):
			print("Creating new mm-calendar-view page...")
			from meeting_manager.meeting_manager.setup import create_calendar_page
			create_calendar_page()

	print("\n" + "="*60)
	print("✅ MIGRATION COMPLETE!")
	print("="*60)
	print("\n📌 Next Steps:")
	print("1. Run: bench --site bestsecurity.local clear-cache")
	print("2. Refresh your browser (Ctrl+R or Cmd+R)")
	print("3. Access the calendar via Meeting Manager workspace")
	print("\n")
