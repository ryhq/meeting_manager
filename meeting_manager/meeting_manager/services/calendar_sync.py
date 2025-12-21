# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Calendar Sync Service

This module handles synchronization with external calendars:
- Google Calendar (OAuth 2.0)
- Microsoft Outlook (OAuth 2.0)
- iCal (URL-based subscription)

Scheduled to run every 5-10 minutes to keep local calendar data fresh.
"""

import frappe
from frappe.utils import now_datetime, add_to_date
from datetime import timedelta
import hashlib

def sync_all_users_calendars():
	"""
	Scheduled job to sync all users' external calendars

	This function is called by the scheduler every 10 minutes.
	It iterates through all active calendar integrations and syncs them.
	"""
	frappe.logger().info("Starting calendar sync for all users")

	# Get all active calendar integrations
	integrations = frappe.get_all(
		"MM Calendar Integration",
		filters={"is_active": 1},
		fields=["name", "user", "integration_type"]
	)

	success_count = 0
	error_count = 0

	for integration in integrations:
		try:
			sync_user_calendar_integration(integration.name)
			success_count += 1
		except Exception as e:
			error_count += 1
			frappe.log_error(
				title=f"Calendar Sync Error - {integration.user}",
				message=f"Failed to sync calendar integration {integration.name}: {str(e)}"
			)

			# Update integration with error status
			frappe.db.set_value(
				"MM Calendar Integration",
				integration.name,
				{
					"sync_status": "Failed",
					"sync_error_log": str(e)[:1000]  # Limit error message length
				},
				update_modified=False
			)

	frappe.logger().info(
		f"Calendar sync completed. Success: {success_count}, Errors: {error_count}"
	)


def sync_user_calendar_integration(integration_id):
	"""
	Sync a single calendar integration

	Args:
		integration_id (str): MM Calendar Integration ID
	"""
	integration = frappe.get_doc("MM Calendar Integration", integration_id)

	# Skip if not active
	if not integration.is_active:
		return

	# Call appropriate sync function based on integration type
	if integration.integration_type == "Google Calendar":
		sync_google_calendar(integration)
	elif integration.integration_type == "Outlook Calendar":
		sync_outlook_calendar(integration)
	elif integration.integration_type == "iCal":
		sync_ical_calendar(integration)
	else:
		frappe.throw(f"Unknown integration type: {integration.integration_type}")

	# Update last sync time
	integration.last_sync = now_datetime()
	integration.sync_status = "Success"
	integration.sync_error_log = None
	integration.save(ignore_permissions=True)


def sync_google_calendar(integration):
	"""
	Sync events from Google Calendar

	This is a placeholder implementation. Full implementation requires:
	1. Google OAuth 2.0 setup in Google Cloud Console
	2. Google Calendar API client library
	3. Token refresh mechanism

	Args:
		integration: MM Calendar Integration document
	"""
	# Check if we have valid credentials
	if not integration.access_token:
		frappe.throw("No access token available. Please reconnect your Google Calendar.")

	# TODO: Implement Google Calendar API integration
	# For now, this is a placeholder

	frappe.logger().info(f"Syncing Google Calendar for user {integration.user}")

	# Pseudo-code for actual implementation:
	#
	# 1. Check if access token is expired, refresh if needed
	# 2. Call Google Calendar API to fetch events (next 60 days)
	# 3. For each event:
	#    - Calculate sync_hash (MD5 of event data)
	#    - Check if event exists in MM Calendar Event Sync
	#    - If new or changed: Create/Update MM Calendar Event Sync record
	# 4. Delete MM Calendar Event Sync records for events no longer in Google Calendar

	# Placeholder: Log that sync would happen here
	frappe.logger().debug(
		f"Google Calendar sync for {integration.user} - "
		f"Would sync events from {integration.calendar_id or 'primary'}"
	)

	# Example of what actual sync would look like:
	# events = fetch_google_calendar_events(integration)
	# process_calendar_events(integration, events)


def sync_outlook_calendar(integration):
	"""
	Sync events from Microsoft Outlook Calendar

	This is a placeholder implementation. Full implementation requires:
	1. Azure AD app registration
	2. Microsoft Graph API client library
	3. Token refresh mechanism

	Args:
		integration: MM Calendar Integration document
	"""
	if not integration.access_token:
		frappe.throw("No access token available. Please reconnect your Outlook Calendar.")

	frappe.logger().info(f"Syncing Outlook Calendar for user {integration.user}")

	# Placeholder: Log that sync would happen here
	frappe.logger().debug(
		f"Outlook Calendar sync for {integration.user} - "
		f"Would sync events from calendar {integration.calendar_id or 'default'}"
	)

	# Example of what actual sync would look like:
	# events = fetch_outlook_calendar_events(integration)
	# process_calendar_events(integration, events)


def sync_ical_calendar(integration):
	"""
	Sync events from iCal URL

	Args:
		integration: MM Calendar Integration document
	"""
	if not integration.ical_url:
		frappe.throw("No iCal URL configured")

	frappe.logger().info(f"Syncing iCal for user {integration.user}")

	try:
		# Fetch and parse iCal feed
		import requests
		from icalendar import Calendar
		from datetime import datetime

		response = requests.get(integration.ical_url, timeout=30)
		response.raise_for_status()

		# Parse iCal data
		cal = Calendar.from_ical(response.content)

		# Get events for next 60 days
		start_date = now_datetime()
		end_date = add_to_date(start_date, days=60)

		events_to_sync = []

		for component in cal.walk():
			if component.name == "VEVENT":
				event_start = component.get('dtstart').dt
				event_end = component.get('dtend').dt

				# Convert to datetime if date
				if not isinstance(event_start, datetime):
					event_start = datetime.combine(event_start, datetime.min.time())
				if not isinstance(event_end, datetime):
					event_end = datetime.combine(event_end, datetime.min.time())

				# Only sync events within our window
				if start_date <= event_start <= end_date:
					events_to_sync.append({
						"external_event_id": str(component.get('uid')),
						"event_summary": str(component.get('summary', 'Busy')),
						"event_start": event_start,
						"event_end": event_end,
						"event_status": "Busy",  # iCal doesn't provide status
						"is_all_day": component.get('dtstart').dt.__class__.__name__ == 'date'
					})

		# Process events
		process_calendar_events(integration, events_to_sync)

	except ImportError:
		frappe.throw(
			"iCal support requires 'icalendar' and 'requests' Python packages. "
			"Install with: pip install icalendar requests"
		)
	except Exception as e:
		frappe.throw(f"Failed to sync iCal calendar: {str(e)}")


def process_calendar_events(integration, events):
	"""
	Process fetched calendar events and update MM Calendar Event Sync

	Args:
		integration: MM Calendar Integration document
		events (list): List of event dictionaries with keys:
			- external_event_id
			- event_summary
			- event_start
			- event_end
			- event_status
			- is_all_day
	"""
	synced_event_ids = []

	for event in events:
		# Calculate sync hash
		sync_hash = calculate_event_hash(event)

		# Check if event already exists
		existing_sync = frappe.db.exists(
			"MM Calendar Event Sync",
			{
				"integration": integration.name,
				"external_event_id": event["external_event_id"]
			}
		)

		if existing_sync:
			# Check if event has changed
			current_hash = frappe.db.get_value(
				"MM Calendar Event Sync",
				existing_sync,
				"sync_hash"
			)

			if current_hash != sync_hash:
				# Event has changed, update it
				sync_doc = frappe.get_doc("MM Calendar Event Sync", existing_sync)
				update_calendar_event_sync(sync_doc, integration, event, sync_hash)
				sync_doc.save(ignore_permissions=True)

			synced_event_ids.append(existing_sync)
		else:
			# New event, create it
			sync_doc = frappe.get_doc({
				"doctype": "MM Calendar Event Sync",
				"user": integration.user,
				"integration": integration.name
			})

			update_calendar_event_sync(sync_doc, integration, event, sync_hash)
			sync_doc.insert(ignore_permissions=True)
			synced_event_ids.append(sync_doc.name)

	# Delete events that no longer exist in external calendar
	delete_orphaned_calendar_events(integration, synced_event_ids)


def update_calendar_event_sync(sync_doc, integration, event, sync_hash):
	"""Update a calendar event sync document with event data"""
	sync_doc.external_event_id = event["external_event_id"]
	sync_doc.event_summary = event["event_summary"]
	sync_doc.event_start = event["event_start"]
	sync_doc.event_end = event["event_end"]
	sync_doc.event_status = event.get("event_status", "Busy")
	sync_doc.is_all_day = event.get("is_all_day", 0)
	sync_doc.last_synced = now_datetime()
	sync_doc.sync_hash = sync_hash


def delete_orphaned_calendar_events(integration, synced_event_ids):
	"""
	Delete calendar event syncs that no longer exist in external calendar

	Args:
		integration: MM Calendar Integration document
		synced_event_ids (list): List of event sync IDs that were just synced
	"""
	# Find all events for this integration that weren't in the sync
	orphaned_events = frappe.get_all(
		"MM Calendar Event Sync",
		filters={
			"integration": integration.name,
			"name": ["not in", synced_event_ids] if synced_event_ids else ["!=", ""]
		},
		pluck="name"
	)

	for event_id in orphaned_events:
		frappe.delete_doc("MM Calendar Event Sync", event_id, ignore_permissions=True)

	if orphaned_events:
		frappe.logger().info(
			f"Deleted {len(orphaned_events)} orphaned calendar events for {integration.user}"
		)


def calculate_event_hash(event):
	"""
	Calculate MD5 hash of event data for change detection

	Args:
		event (dict): Event data

	Returns:
		str: MD5 hash
	"""
	event_string = (
		f"{event['external_event_id']}"
		f"{event['event_summary']}"
		f"{event['event_start'].isoformat()}"
		f"{event['event_end'].isoformat()}"
		f"{event.get('event_status', 'Busy')}"
	)

	return hashlib.md5(event_string.encode()).hexdigest()


# Placeholder functions for Google/Outlook API calls
# These would be implemented with actual API libraries

def fetch_google_calendar_events(integration):
	"""
	Fetch events from Google Calendar API

	This would use the Google Calendar API client library:
	- google-auth
	- google-auth-oauthlib
	- google-api-python-client

	Returns:
		list: List of event dictionaries
	"""
	# TODO: Implement with Google Calendar API
	# from googleapiclient.discovery import build
	# service = build('calendar', 'v3', credentials=credentials)
	# events = service.events().list(...).execute()
	return []


def fetch_outlook_calendar_events(integration):
	"""
	Fetch events from Microsoft Outlook Calendar API

	This would use the Microsoft Graph API:
	- requests or msal library for OAuth
	- Microsoft Graph API endpoints

	Returns:
		list: List of event dictionaries
	"""
	# TODO: Implement with Microsoft Graph API
	# headers = {'Authorization': f'Bearer {integration.access_token}'}
	# response = requests.get('https://graph.microsoft.com/v1.0/me/events', headers=headers)
	# events = response.json()['value']
	return []


def refresh_google_token(integration):
	"""
	Refresh expired Google OAuth token

	Args:
		integration: MM Calendar Integration document
	"""
	# TODO: Implement OAuth token refresh
	# This would use the refresh_token to get a new access_token
	pass


def refresh_outlook_token(integration):
	"""
	Refresh expired Outlook OAuth token

	Args:
		integration: MM Calendar Integration document
	"""
	# TODO: Implement OAuth token refresh
	pass


def create_calendar_event_in_external(booking):
	"""
	Create/update a booking in the assigned member's external calendar

	This is called when a booking is created or updated in Meeting Manager
	to push the event to the member's Google Calendar/Outlook

	Args:
		booking: MM Meeting Booking document
	"""
	# Get member's active calendar integrations with two-way sync
	integrations = frappe.get_all(
		"MM Calendar Integration",
		filters={
			"user": booking.assigned_to,
			"is_active": 1,
			"sync_direction": "Two-way"
		},
		fields=["name", "integration_type"]
	)

	for integration in integrations:
		try:
			if integration.integration_type == "Google Calendar":
				# TODO: Create event in Google Calendar
				pass
			elif integration.integration_type == "Outlook Calendar":
				# TODO: Create event in Outlook
				pass
			# iCal is read-only, skip
		except Exception as e:
			frappe.log_error(
				title=f"Failed to create event in {integration.integration_type}",
				message=f"Booking: {booking.name}, Error: {str(e)}"
			)


def delete_calendar_event_from_external(booking):
	"""
	Delete a booking from external calendar when cancelled

	Args:
		booking: MM Meeting Booking document
	"""
	# Similar to create_calendar_event_in_external but for deletion
	# TODO: Implement deletion in external calendars
	pass
