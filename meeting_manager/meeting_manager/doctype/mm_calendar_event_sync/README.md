# MM Calendar Event Sync - DocType Documentation

## Overview

**MM Calendar Event Sync** is the individual event record synced from external calendar services. Each record represents a single calendar event (meeting, appointment, blocked time) from Google Calendar, Outlook, or iCal that has been imported into the Meeting Manager system. These events are used to calculate user availability and prevent double-booking.

**Auto-naming Format**: `MM-CES-{calendar_integration}-{####}`

Example: `MM-CES-MM-CI-sarah@bestsecurity.com-0001-0042`

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md), calendar event sync is essential for:

1. **Availability Calculation**: External events block availability when assigning bookings to department members
2. **Conflict Prevention**: Before creating a booking, the system checks all synced events to ensure no conflicts
3. **Bidirectional Sync**: Events created in Meeting Manager are written to external calendars (if two-way sync enabled)
4. **Real-time Updates**: Changes to external events (reschedule, cancellation) are reflected in Meeting Manager availability

**Key Product Requirements** (Phase 2):
- Sync events from all configured calendar integrations (Google, Outlook, iCal)
- Track external event IDs for update/delete operations
- Support for all-day events, recurring events, and multi-attendee meetings
- Link synced events to MM Meeting Booking records (for bidirectional tracking)
- Handle event modifications (time changes, cancellations)
- Configurable blocking behavior (some events may not block availability)

---

## Key Features

### 1. **External Event Tracking**
- Stores unique external event ID from calendar provider (Google/Outlook/iCal)
- Tracks last modified timestamp from external calendar for change detection
- Maintains event metadata (title, description, location, attendees)

### 2. **Sync Status Management**
- Real-time sync status tracking: Synced, Pending Sync, Sync Failed, Deleted Externally, Deleted Locally
- Error logging for troubleshooting sync failures
- Last synced timestamp for monitoring

### 3. **Event Type Classification**
- **External Event**: Regular events from external calendar (meetings, appointments)
- **Meeting Booking**: Events created by Meeting Manager booking system
- **Blocked Time**: Manually blocked availability (focus time, breaks)
- **All-Day Event**: All-day events (holidays, vacations)

### 4. **Availability Blocking**
- `is_blocking_availability` flag controls whether event blocks user availability
- Default: true (all events block availability)
- Can be disabled for events like "Available" or "Tentative" status

### 5. **Bidirectional Linking**
- Links to `MM Meeting Booking` for events created in Meeting Manager
- Tracks sync direction: Inbound (from external), Outbound (to external), Bidirectional

### 6. **Attendee Management**
- Stores attendees as JSON array
- Supports both simple email strings and complex attendee objects
- Tracks organizer email for conflict resolution

---

## Field Reference

### Event Information Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `calendar_integration` | Link (MM Calendar Integration) | Yes | Parent calendar integration for this event |
| `external_event_id` | Data | Yes | Unique event ID from external calendar service |
| `event_title` | Data | Yes | Event title/summary |
| `event_type` | Select | No | Type: `External Event`, `Meeting Booking`, `Blocked Time`, `All-Day Event` (default: External Event) |
| `sync_status` | Select | No | Status: `Synced`, `Pending Sync`, `Sync Failed`, `Deleted Externally`, `Deleted Locally` (default: Synced) |

### Event Timing Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_datetime` | Datetime | Yes | Event start date and time |
| `end_datetime` | Datetime | Yes | Event end date and time |

### Event Details Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | Text | No | Event description/notes |
| `location` | Data | No | Event location (physical address or video call link) |
| `attendees_json` | JSON | No | Array of attendee email addresses or objects |
| `organizer_email` | Data | No | Email of event organizer |

### Linked Records Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meeting_booking` | Link (MM Meeting Booking) | No | Linked MM Meeting Booking (if this is a booked meeting) |
| `is_blocking_availability` | Check | No | Whether event blocks user availability (default: 1) |

### Sync Metadata Section

*Read-only fields managed by the system*

| Field | Type | Description |
|-------|------|-------------|
| `last_synced` | Datetime | Last time this event was synced |
| `external_last_modified` | Datetime | Last modified timestamp from external calendar |
| `sync_direction` | Select | Direction: `Inbound`, `Outbound`, `Bidirectional` (default: Inbound) |
| `sync_error_log` | Text | Error details from sync failures |

---

## Use Cases

### Use Case 1: External Event Synced from Google Calendar

**Scenario**: Sarah has a dentist appointment in her Google Calendar. The sync service imports it into Meeting Manager.

```python
# Sync service creates event record
event = frappe.get_doc({
    "doctype": "MM Calendar Event Sync",
    "calendar_integration": "MM-CI-sarah@bestsecurity.com-0001",
    "external_event_id": "abc123xyz789_google",  # From Google Calendar API
    "event_title": "Dentist Appointment",
    "event_type": "External Event",
    "sync_status": "Synced",
    "start_datetime": "2025-12-10 14:00:00",
    "end_datetime": "2025-12-10 15:00:00",
    "description": "Annual checkup at Dr. Smith's office",
    "location": "123 Main St, Dental Clinic",
    "attendees_json": ["sarah@bestsecurity.com"],
    "organizer_email": "sarah@bestsecurity.com",
    "is_blocking_availability": 1,  # This blocks her availability
    "sync_direction": "Inbound",
    "external_last_modified": "2025-12-08 10:30:00"
})
event.insert()
```

**Result**:
- Sarah is unavailable for bookings from 2:00-3:00 PM on Dec 10
- Event appears in her Meeting Manager calendar view
- If she reschedules in Google Calendar, sync updates this record

### Use Case 2: Meeting Booking Synced to External Calendar

**Scenario**: Customer books a meeting with Sarah. System creates event in her Google Calendar and tracks it.

```python
# Step 1: Customer creates booking (creates MM Meeting Booking)
booking = frappe.get_doc({
    "doctype": "MM Meeting Booking",
    "meeting_type": "MM-MT-support-30-min-call",
    "assigned_user": "sarah@bestsecurity.com",
    "start_datetime": "2025-12-12 10:00:00",
    "end_datetime": "2025-12-12 10:30:00",
    # ... other booking fields
})
booking.insert()

# Step 2: Sync service writes to Google Calendar and creates sync record
event = frappe.get_doc({
    "doctype": "MM Calendar Event Sync",
    "calendar_integration": "MM-CI-sarah@bestsecurity.com-0001",
    "external_event_id": "xyz789abc123_google",  # Returned from Google Calendar API
    "event_title": "Customer Support Call - John Doe",
    "event_type": "Meeting Booking",
    "sync_status": "Synced",
    "start_datetime": "2025-12-12 10:00:00",
    "end_datetime": "2025-12-12 10:30:00",
    "description": "Support call regarding account setup issues",
    "location": "https://meet.google.com/abc-defg-hij",
    "attendees_json": [
        {"email": "sarah@bestsecurity.com", "response_status": "accepted"},
        {"email": "john@customer.com", "response_status": "needs_action"}
    ],
    "organizer_email": "sarah@bestsecurity.com",
    "meeting_booking": booking.name,  # Link to MM Meeting Booking
    "is_blocking_availability": 1,
    "sync_direction": "Outbound",  # Written from Meeting Manager to Google
    "external_last_modified": "2025-12-08 11:00:00"
})
event.insert()
```

**Result**:
- Event appears in Sarah's Google Calendar
- External event ID stored for future updates (if booking is rescheduled)
- Two-way link between MM Meeting Booking and external calendar event

### Use Case 3: All-Day Event (Vacation/Holiday)

**Scenario**: Sarah marks "Vacation" in her Outlook calendar as an all-day event.

```python
# Sync from Outlook
event = frappe.get_doc({
    "doctype": "MM Calendar Event Sync",
    "calendar_integration": "MM-CI-sarah@bestsecurity.com-0002",  # Outlook integration
    "external_event_id": "AAMkAGI1...outlook",
    "event_title": "Vacation - Out of Office",
    "event_type": "All-Day Event",
    "sync_status": "Synced",
    "start_datetime": "2025-12-20 00:00:00",  # All-day: start at midnight
    "end_datetime": "2025-12-27 23:59:59",    # All-day: end at 11:59 PM
    "description": "Christmas vacation - will return Dec 28",
    "location": "",
    "attendees_json": ["sarah@bestsecurity.com"],
    "organizer_email": "sarah@bestsecurity.com",
    "is_blocking_availability": 1,  # Blocks entire week
    "sync_direction": "Inbound",
    "external_last_modified": "2025-12-01 09:00:00"
})
event.insert()
```

**Result**:
- Sarah is unavailable for bookings Dec 20-27
- All-day events block the entire day (not just specific time slots)
- Customers cannot book meetings during this period

### Use Case 4: Non-Blocking Event (Focus Time)

**Scenario**: Sarah schedules "Focus Time" in her calendar but wants to remain available for bookings.

```python
# Sync from Google Calendar
event = frappe.get_doc({
    "doctype": "MM Calendar Event Sync",
    "calendar_integration": "MM-CI-sarah@bestsecurity.com-0001",
    "external_event_id": "focus123_google",
    "event_title": "Focus Time - Deep Work",
    "event_type": "Blocked Time",
    "sync_status": "Synced",
    "start_datetime": "2025-12-09 09:00:00",
    "end_datetime": "2025-12-09 11:00:00",
    "description": "Concentrated work session - can interrupt for customer calls if needed",
    "location": "",
    "attendees_json": ["sarah@bestsecurity.com"],
    "organizer_email": "sarah@bestsecurity.com",
    "is_blocking_availability": 0,  # Does NOT block availability
    "sync_direction": "Inbound",
    "external_last_modified": "2025-12-08 08:00:00"
})
event.insert()
```

**Result**:
- Event appears in Sarah's calendar as "Focus Time"
- Sarah remains AVAILABLE for customer bookings (is_blocking_availability = 0)
- Admin/manager can see the focus time for context

### Use Case 5: Sync Failure Handling

**Scenario**: Event modification in external calendar fails to sync due to network error.

```python
# Get existing event
event = frappe.get_doc("MM Calendar Event Sync", "MM-CES-MM-CI-sarah@bestsecurity.com-0001-0012")

# Sync service detects external modification but fails to sync
event.sync_status = "Sync Failed"
event.sync_error_log = """
Sync Error (2025-12-08 12:30:00):
Failed to fetch updated event from Google Calendar API.
Error: 503 Service Unavailable
Retry scheduled for next sync cycle.
"""
event.save()

# Query failed syncs for monitoring
failed_syncs = frappe.get_all(
    "MM Calendar Event Sync",
    filters={"sync_status": "Sync Failed"},
    fields=["name", "event_title", "calendar_integration", "sync_error_log"],
    order_by="modified desc"
)

for sync in failed_syncs:
    print(f"Failed: {sync.event_title} - {sync.sync_error_log[:100]}")
```

**Result**:
- Event marked as "Sync Failed" with detailed error log
- Admin can monitor failed syncs and take corrective action
- Next sync cycle will retry the operation

---

## Validation Rules

The DocType includes comprehensive validation to ensure data integrity and prevent sync conflicts:

### 1. Calendar Integration Validation (`validate_calendar_integration_exists`)

**Validates**:
- Calendar integration field is not empty
- Calendar integration exists in MM Calendar Integration DocType
- Warns if calendar integration is inactive (may not sync properly)

**Error Messages**:
- `"Calendar Integration is required."`
- `"Calendar Integration '{name}' does not exist."`

**Warnings**:
- `"Warning: Calendar Integration '{name}' is not active. This event may not sync properly."` (orange indicator)

### 2. External Event ID Uniqueness (`validate_external_event_id_unique`)

**Validates**:
- External event ID is provided
- External event ID is unique within the calendar integration (prevents duplicates)

**Error Messages**:
- `"External Event ID is required."`
- `"External Event ID '{id}' already exists in calendar integration '{name}'. Each event must have a unique external ID."`

**Example**:
- ✅ Valid: Two events with same external_event_id but different calendar_integration
- ❌ Invalid: Two events with same external_event_id in the same calendar_integration

### 3. Event Timing Validation (`validate_event_timing`)

**Validates**:
- Start and end datetime fields are provided
- Datetimes are in valid format
- End datetime is after start datetime
- Warns about very long events (> 24 hours)
- Warns about very old events (> 2 years in the past)

**Error Messages**:
- `"Start DateTime is required."`
- `"End DateTime is required."`
- `"Invalid datetime format for Start or End DateTime."`
- `"End DateTime must be after Start DateTime."`

**Warnings**:
- `"Warning: This event has a duration of {hours} hours (> 24 hours). Please verify the event timing is correct."` (orange indicator)
- `"Warning: This event started {days} days ago. Very old events may not need to be synced."` (orange indicator)

**Example**:
- ✅ Valid: start: "2025-12-08 10:00:00", end: "2025-12-08 11:00:00"
- ❌ Invalid: start: "2025-12-08 10:00:00", end: "2025-12-08 09:00:00" (end before start)

### 4. Attendees JSON Validation (`validate_attendees_json`)

**Validates**:
- If provided, attendees_json must be valid JSON
- Must be a JSON array (list)
- Each attendee can be:
  - Simple string (email address)
  - Object with at least "email" field
- Email addresses must match valid email format

**Error Messages**:
- `"Invalid JSON format for Attendees."`
- `"Attendees must be a JSON array of email addresses or objects."`
- `"Attendee at index {idx} is missing 'email' field."`
- `"Attendee at index {idx} must be a string or object."`
- `"Invalid email format for attendee: '{email}'"`

**Valid Attendees JSON Examples**:

```json
// Simple email list
["sarah@bestsecurity.com", "john@customer.com"]

// Complex attendee objects
[
  {
    "email": "sarah@bestsecurity.com",
    "response_status": "accepted",
    "display_name": "Sarah Johnson"
  },
  {
    "email": "john@customer.com",
    "response_status": "needs_action",
    "display_name": "John Doe"
  }
]

// Mixed format
[
  "sarah@bestsecurity.com",
  {
    "email": "john@customer.com",
    "response_status": "tentative"
  }
]
```

### 5. Organizer Email Validation (`validate_organizer_email`)

**Validates**:
- If provided, organizer_email must match valid email format

**Error Messages**:
- `"Invalid email format for Organizer Email: '{email}'"`

**Example**:
- ✅ Valid: "sarah@bestsecurity.com"
- ❌ Invalid: "sarah@bestsecurity", "not-an-email", "sarah@"

### 6. Meeting Booking Link Validation (`validate_meeting_booking_link`)

**Validates**:
- If linked, meeting booking must exist
- Warns if meeting booking is already linked to another calendar event (potential sync conflict)
- Warns if event timing differs from booking timing by > 5 minutes (indicates sync issue)

**Error Messages**:
- `"Meeting Booking '{name}' does not exist."`

**Warnings**:
- `"Warning: Meeting Booking '{name}' is already linked to another calendar event. Multiple calendar events for the same booking may cause sync conflicts."` (orange indicator)
- `"Warning: Event timing does not match linked Meeting Booking timing. This may indicate a sync issue."` (orange indicator)

**Timing Tolerance**: 5 minutes allowed for timezone/rounding differences

### 7. Auto-Update Last Synced (`on_update` hook)

**Behavior**:
- When sync_status is set to "Synced", automatically updates last_synced to current datetime
- Does not update modified timestamp (to avoid triggering change detection)

### 8. Deletion Logging (`on_trash` hook)

**Behavior**:
- If event is linked to a meeting booking, logs deletion to error log
- Helps track accidental deletions or sync issues

**Log Entry**:
```
Calendar Event Sync '{name}' linked to Meeting Booking '{booking}' was deleted.
```

---

## Usage Examples

### Example 1: Creating Event from External Calendar Sync

```python
import frappe
from frappe.utils import now_datetime

def create_event_from_google_calendar(calendar_integration, google_event):
    """
    Create MM Calendar Event Sync from Google Calendar API response

    Args:
        calendar_integration: Name of MM Calendar Integration
        google_event: Event object from Google Calendar API
    """
    event = frappe.get_doc({
        "doctype": "MM Calendar Event Sync",
        "calendar_integration": calendar_integration,
        "external_event_id": google_event["id"],
        "event_title": google_event.get("summary", "No Title"),
        "event_type": "All-Day Event" if google_event.get("start", {}).get("date") else "External Event",
        "sync_status": "Synced",
        "start_datetime": google_event["start"].get("dateTime", google_event["start"].get("date")),
        "end_datetime": google_event["end"].get("dateTime", google_event["end"].get("date")),
        "description": google_event.get("description", ""),
        "location": google_event.get("location", ""),
        "attendees_json": [
            {"email": att["email"], "response_status": att.get("responseStatus", "needsAction")}
            for att in google_event.get("attendees", [])
        ],
        "organizer_email": google_event.get("organizer", {}).get("email", ""),
        "is_blocking_availability": 1,
        "sync_direction": "Inbound",
        "external_last_modified": google_event.get("updated")
    })

    try:
        event.insert()
        print(f"Event created: {event.name}")
        return event
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        return None

# Usage
google_event_data = {
    "id": "abc123xyz789",
    "summary": "Team Standup",
    "start": {"dateTime": "2025-12-09T09:00:00Z"},
    "end": {"dateTime": "2025-12-09T09:30:00Z"},
    "description": "Daily standup meeting",
    "location": "Conference Room A",
    "attendees": [
        {"email": "sarah@bestsecurity.com", "responseStatus": "accepted"},
        {"email": "john@bestsecurity.com", "responseStatus": "accepted"}
    ],
    "organizer": {"email": "sarah@bestsecurity.com"},
    "updated": "2025-12-08T10:00:00Z"
}

create_event_from_google_calendar("MM-CI-sarah@bestsecurity.com-0001", google_event_data)
```

### Example 2: Querying User's Blocking Events

```python
import frappe
from frappe.utils import now_datetime, add_days

def get_user_blocking_events(user, start_date=None, end_date=None):
    """
    Get all calendar events that block a user's availability

    Args:
        user: User email address
        start_date: Start of date range (default: today)
        end_date: End of date range (default: 30 days from today)

    Returns:
        List of blocking calendar events
    """
    if not start_date:
        start_date = now_datetime()
    if not end_date:
        end_date = add_days(start_date, 30)

    # Get all active calendar integrations for user
    calendar_integrations = frappe.get_all(
        "MM Calendar Integration",
        filters={"user": user, "is_active": 1},
        pluck="name"
    )

    if not calendar_integrations:
        return []

    # Get blocking events in date range
    events = frappe.get_all(
        "MM Calendar Event Sync",
        filters={
            "calendar_integration": ["in", calendar_integrations],
            "is_blocking_availability": 1,
            "start_datetime": [">=", start_date],
            "end_datetime": ["<=", end_date],
            "sync_status": ["in", ["Synced", "Pending Sync"]]  # Exclude failed/deleted
        },
        fields=[
            "name",
            "event_title",
            "start_datetime",
            "end_datetime",
            "event_type",
            "location"
        ],
        order_by="start_datetime asc"
    )

    return events

# Usage
blocking_events = get_user_blocking_events("sarah@bestsecurity.com")
for event in blocking_events:
    print(f"{event.start_datetime} - {event.end_datetime}: {event.event_title}")
```

### Example 3: Checking Time Slot Availability

```python
import frappe
from frappe.utils import get_datetime

def is_time_slot_available(user, start_datetime, end_datetime):
    """
    Check if a time slot is available (no blocking events)

    Args:
        user: User email address
        start_datetime: Proposed start time
        end_datetime: Proposed end time

    Returns:
        dict: {"available": bool, "conflicting_events": list}
    """
    # Get user's active calendar integrations
    calendar_integrations = frappe.get_all(
        "MM Calendar Integration",
        filters={"user": user, "is_active": 1},
        pluck="name"
    )

    if not calendar_integrations:
        return {"available": True, "conflicting_events": []}

    # Convert to datetime objects
    start_dt = get_datetime(start_datetime)
    end_dt = get_datetime(end_datetime)

    # Find conflicting events
    # Event conflicts if: (start < end_dt) AND (end > start_dt)
    conflicts = frappe.get_all(
        "MM Calendar Event Sync",
        filters={
            "calendar_integration": ["in", calendar_integrations],
            "is_blocking_availability": 1,
            "start_datetime": ["<", end_dt],
            "end_datetime": [">", start_dt],
            "sync_status": ["in", ["Synced", "Pending Sync"]]
        },
        fields=["name", "event_title", "start_datetime", "end_datetime"]
    )

    return {
        "available": len(conflicts) == 0,
        "conflicting_events": conflicts
    }

# Usage
availability = is_time_slot_available(
    "sarah@bestsecurity.com",
    "2025-12-10 14:00:00",
    "2025-12-10 15:00:00"
)

if availability["available"]:
    print("Time slot is available!")
else:
    print("Time slot has conflicts:")
    for conflict in availability["conflicting_events"]:
        print(f"  - {conflict.event_title} ({conflict.start_datetime} - {conflict.end_datetime})")
```

### Example 4: Updating Event After External Modification

```python
import frappe
from frappe.utils import now_datetime

def update_event_from_external(event_name, updated_google_event):
    """
    Update existing calendar event sync after external modification

    Args:
        event_name: Name of MM Calendar Event Sync
        updated_google_event: Updated event from Google Calendar API
    """
    event = frappe.get_doc("MM Calendar Event Sync", event_name)

    # Update fields
    event.event_title = updated_google_event.get("summary", event.event_title)
    event.start_datetime = updated_google_event["start"].get("dateTime", event.start_datetime)
    event.end_datetime = updated_google_event["end"].get("dateTime", event.end_datetime)
    event.description = updated_google_event.get("description", "")
    event.location = updated_google_event.get("location", "")
    event.external_last_modified = updated_google_event.get("updated")
    event.sync_status = "Synced"
    event.sync_error_log = None

    # Update attendees if changed
    if "attendees" in updated_google_event:
        event.attendees_json = [
            {"email": att["email"], "response_status": att.get("responseStatus", "needsAction")}
            for att in updated_google_event.get("attendees", [])
        ]

    try:
        event.save()
        print(f"Event updated: {event.name}")
        return event
    except Exception as e:
        # Mark as sync failed if update fails validation
        event.sync_status = "Sync Failed"
        event.sync_error_log = f"Update failed: {str(e)}"
        event.db_set("sync_status", "Sync Failed", update_modified=False)
        event.db_set("sync_error_log", event.sync_error_log, update_modified=False)
        print(f"Update failed: {str(e)}")
        return None

# Usage (after detecting change in external calendar)
updated_google_event = {
    "id": "abc123xyz789",
    "summary": "Team Standup - RESCHEDULED",
    "start": {"dateTime": "2025-12-09T10:00:00Z"},  # Changed from 9:00 AM
    "end": {"dateTime": "2025-12-09T10:30:00Z"},
    "updated": "2025-12-08T15:30:00Z"
}

update_event_from_external("MM-CES-MM-CI-sarah@bestsecurity.com-0001-0005", updated_google_event)
```

### Example 5: Finding Events Linked to Meeting Bookings

```python
import frappe

def get_meeting_booking_sync_status(booking_name):
    """
    Get sync status for a meeting booking's calendar events

    Args:
        booking_name: Name of MM Meeting Booking

    Returns:
        dict: Sync status information
    """
    # Find all calendar events linked to this booking
    linked_events = frappe.get_all(
        "MM Calendar Event Sync",
        filters={"meeting_booking": booking_name},
        fields=[
            "name",
            "calendar_integration",
            "external_event_id",
            "sync_status",
            "sync_direction",
            "last_synced"
        ]
    )

    if not linked_events:
        return {
            "synced": False,
            "message": "No calendar events found for this booking"
        }

    # Check if all synced successfully
    sync_statuses = [e.sync_status for e in linked_events]
    all_synced = all(status == "Synced" for status in sync_statuses)

    return {
        "synced": all_synced,
        "event_count": len(linked_events),
        "events": linked_events,
        "message": "All events synced successfully" if all_synced else "Some events have sync issues"
    }

# Usage
booking_sync = get_meeting_booking_sync_status("MM-MB-support-0042")
print(f"Sync Status: {booking_sync['message']}")
print(f"Events synced to {booking_sync['event_count']} calendars")

for event in booking_sync["events"]:
    print(f"  - {event.calendar_integration}: {event.sync_status}")
```

---

## Integration with Other DocTypes

### MM Calendar Integration (Parent)

**Relationship**: Many-to-One (many events belong to one calendar integration)

**Flow**:
```
MM Calendar Integration: "Work Google Calendar"
├── MM Calendar Event Sync: "Team Meeting" (2025-12-08 10:00)
├── MM Calendar Event Sync: "Lunch Break" (2025-12-08 12:00)
├── MM Calendar Event Sync: "Client Call" (2025-12-08 14:00)
└── MM Calendar Event Sync: "Project Review" (2025-12-08 16:00)
```

**Cascade Behavior**:
- If calendar integration is deactivated, events remain but may be excluded from availability calculation
- If calendar integration is deleted, consider archiving or deleting associated events

### MM Meeting Booking (Linked)

**Relationship**: One-to-Many (one booking can have multiple calendar events if synced to multiple calendars)

**Flow**:
```
MM Meeting Booking: "Customer Support Call - John Doe"
├── MM Calendar Event Sync: Event in Sarah's Google Calendar
└── MM Calendar Event Sync: Event in John's Outlook Calendar (if he's an attendee)
```

**Integration Points**:
- When booking is created, system creates calendar events in assigned user's external calendars
- When booking is rescheduled, system updates linked calendar events
- When booking is cancelled, system deletes linked calendar events

### Availability Calculation

**Process**:
1. User requests available time slots for booking
2. System queries all calendar integrations for the user
3. Gets all blocking events (`is_blocking_availability = 1`) in date range
4. Excludes time slots with blocking events
5. Returns available slots

**Query**:
```python
# Simplified availability check
blocking_events = frappe.get_all(
    "MM Calendar Event Sync",
    filters={
        "calendar_integration": ["in", user_calendar_integrations],
        "is_blocking_availability": 1,
        "start_datetime": [">=", search_start],
        "end_datetime": ["<=", search_end],
        "sync_status": ["in", ["Synced", "Pending Sync"]]
    },
    fields=["start_datetime", "end_datetime"]
)
```

---

## Sync Architecture

### Event Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                   Calendar Event Sync Lifecycle                  │
└─────────────────────────────────────────────────────────────────┘

1. Event Created in External Calendar
   ↓
2. Sync Service Detects New Event
   ↓
3. Create MM Calendar Event Sync
   - sync_status = "Synced"
   - sync_direction = "Inbound"
   - is_blocking_availability = 1
   ↓
4. Event Appears in User's Availability Calculation
   ↓
5. External Event Modified (time change)
   ↓
6. Sync Service Detects Modification (external_last_modified changed)
   ↓
7. Update MM Calendar Event Sync
   - Update start_datetime, end_datetime
   - Update sync_status = "Synced"
   - Update last_synced timestamp
   ↓
8. Event Deleted in External Calendar
   ↓
9. Sync Service Detects Deletion
   ↓
10. Option A: Soft Delete
    - sync_status = "Deleted Externally"
    - Keep record for audit trail

    Option B: Hard Delete
    - Delete MM Calendar Event Sync record
```

### Bidirectional Sync Flow

```
┌────────────────────────────────────────────────────────────────┐
│            Bidirectional Sync (Meeting Booking)                │
└────────────────────────────────────────────────────────────────┘

1. Customer Books Meeting
   ↓
2. MM Meeting Booking Created
   - assigned_user = "sarah@bestsecurity.com"
   - start_datetime = "2025-12-10 14:00:00"
   - end_datetime = "2025-12-10 14:30:00"
   ↓
3. Sync Service Triggered (on_update hook)
   ↓
4. Get Primary Calendar Integration for Assigned User
   - Sarah's primary calendar: Google Calendar (two-way sync)
   ↓
5. Create Event in Google Calendar (API call)
   - Returns external_event_id = "google_xyz789"
   ↓
6. Create MM Calendar Event Sync
   - calendar_integration = Sarah's Google Calendar
   - external_event_id = "google_xyz789"
   - meeting_booking = MM-MB-support-0042 (link)
   - sync_direction = "Outbound"
   - sync_status = "Synced"
   ↓
7. Event Now Synced Both Ways
   - Changes in Meeting Manager → Update Google Calendar
   - Changes in Google Calendar → Update Meeting Manager
```

---

## Permissions

| Role | Create | Read | Write | Delete | Notes |
|------|--------|------|-------|--------|-------|
| System Manager | ✅ | ✅ | ✅ | ✅ | Full access to all calendar events |
| All | ❌ | ✅ | ❌ | ❌ | Read-only access (typically filtered by user) |

**User-Level Permissions Recommended**:
```python
# Users should only see events from their own calendar integrations
frappe.permissions.add_user_permission("MM Calendar Event Sync", event_name, user_email)
```

---

## Database Schema

### Indexes (Recommended)

```sql
-- Index for finding events by calendar integration
CREATE INDEX idx_calendar_integration ON `tabMM Calendar Event Sync` (calendar_integration, sync_status);

-- Index for external event ID uniqueness check
CREATE UNIQUE INDEX idx_external_event_id ON `tabMM Calendar Event Sync` (calendar_integration, external_event_id);

-- Index for availability queries (time range + blocking)
CREATE INDEX idx_availability_check ON `tabMM Calendar Event Sync`
    (calendar_integration, is_blocking_availability, start_datetime, end_datetime, sync_status);

-- Index for finding events by date range
CREATE INDEX idx_date_range ON `tabMM Calendar Event Sync` (start_datetime, end_datetime);

-- Index for finding events linked to meeting bookings
CREATE INDEX idx_meeting_booking ON `tabMM Calendar Event Sync` (meeting_booking);

-- Index for monitoring sync failures
CREATE INDEX idx_sync_status ON `tabMM Calendar Event Sync` (sync_status, calendar_integration);
```

---

## API Endpoints

### Internal APIs

#### 1. Get User's Blocking Events

```python
@frappe.whitelist()
def get_blocking_events(user, start_date, end_date):
    """
    Get all events that block user's availability in date range

    Args:
        user: User email
        start_date: Start of range (YYYY-MM-DD)
        end_date: End of range (YYYY-MM-DD)

    Returns:
        list: Blocking events
    """
    pass
```

#### 2. Check Time Slot Availability

```python
@frappe.whitelist()
def check_time_slot(user, start_datetime, end_datetime):
    """
    Check if a specific time slot is available

    Args:
        user: User email
        start_datetime: Proposed start time
        end_datetime: Proposed end time

    Returns:
        dict: {"available": bool, "conflicts": list}
    """
    pass
```

#### 3. Sync Single Event

```python
@frappe.whitelist()
def sync_single_event(calendar_event_sync_name):
    """
    Manually trigger sync for a single event

    Args:
        calendar_event_sync_name: Name of event to sync

    Returns:
        dict: {"status": "success", "message": "..."}
    """
    pass
```

---

## Testing Checklist

### Unit Tests

- [ ] **Test calendar integration validation**: Create event with non-existent calendar integration (should fail)
- [ ] **Test external event ID uniqueness**: Create two events with same external_event_id in same integration (should fail)
- [ ] **Test event timing validation**: End before start (should fail), very long event (should warn)
- [ ] **Test attendees JSON validation**: Invalid JSON, non-array, invalid email format (should fail)
- [ ] **Test organizer email validation**: Invalid email format (should fail)
- [ ] **Test meeting booking link validation**: Non-existent booking (should fail), timing mismatch (should warn)
- [ ] **Test auto-update last_synced**: Set sync_status to "Synced", verify last_synced updates

### Integration Tests

- [ ] **Test event import from Google Calendar**: Sync events from Google, verify all fields populated
- [ ] **Test event export to Outlook**: Create booking, verify event appears in Outlook
- [ ] **Test event update sync**: Modify event in external calendar, verify changes reflected in Meeting Manager
- [ ] **Test event deletion sync**: Delete event externally, verify sync_status updates or record deleted
- [ ] **Test all-day event handling**: Sync all-day event, verify it blocks entire day
- [ ] **Test non-blocking event**: Set is_blocking_availability = 0, verify availability not affected
- [ ] **Test availability calculation**: Create multiple blocking events, verify correct availability gaps
- [ ] **Test bidirectional sync**: Create booking, modify in external calendar, verify both sides update

### Manual Tests

- [ ] **User Permissions**: Verify users can only see events from their own calendar integrations
- [ ] **Sync Performance**: Create 100 events, verify availability query completes in < 1 second
- [ ] **Conflict Detection**: Create overlapping events, verify conflicts detected correctly
- [ ] **Timing Tolerance**: Test events with 4-minute time difference from booking (should pass), 6-minute (should warn)
- [ ] **Attendees Display**: Verify complex attendee JSON displays correctly in UI

---

## Best Practices

### For Sync Service Implementation

1. **Batch Processing**:
   - Process events in batches (50-100 at a time)
   - Use `frappe.db.bulk_insert()` for multiple events
   - Avoid N+1 query problems

2. **Error Handling**:
   - Set sync_status = "Sync Failed" on errors
   - Log detailed error messages to sync_error_log
   - Retry failed syncs in next cycle

3. **Change Detection**:
   - Use `external_last_modified` to detect changes
   - Only update if timestamp differs
   - Avoid unnecessary writes

4. **Deletion Strategy**:
   - **Soft delete** (recommended): Set sync_status = "Deleted Externally", keep for audit
   - **Hard delete**: Delete record immediately (may lose history)

5. **Performance Optimization**:
   - Index frequently queried fields (calendar_integration, start_datetime, is_blocking_availability)
   - Use read replicas for availability queries
   - Cache availability calculation results (5-minute TTL)

### For Availability Calculation

1. **Query Optimization**:
   - Only query active calendar integrations
   - Use date range filters to limit results
   - Exclude "Sync Failed" and "Deleted" events

2. **Time Zone Handling**:
   - Store all datetimes in UTC
   - Convert to user's timezone for display
   - Use timezone-aware datetime comparisons

3. **Blocking Logic**:
   - Respect `is_blocking_availability` flag
   - Treat "Pending Sync" as blocking (conservative approach)
   - Exclude "Sync Failed" after retry threshold

---

## Known Limitations

1. **Sync Latency**: Events may take up to `sync_interval_minutes` to sync (not real-time). For critical updates, use manual sync trigger.

2. **Recurring Events**: Current schema stores individual occurrences. Recurring event series may generate many records.

3. **External Event ID Format**: Different providers use different ID formats (Google: alphanumeric, Outlook: long UUID). Ensure field length accommodates all formats.

4. **Timezone Complexity**: All-day events and timezone conversions can be complex. System assumes UTC storage with timezone conversion at query time.

5. **Attendee Response Tracking**: System stores attendee responses but doesn't actively monitor changes. Responses may become stale.

6. **Conflict Resolution**: If same event is modified simultaneously in Meeting Manager and external calendar, last write wins (no merge logic).

7. **Deletion Propagation**: Soft-deleted events (sync_status = "Deleted Externally") remain in database and may affect queries if not filtered properly.

8. **Large Event Sets**: Users with thousands of events may experience slow availability queries. Consider archiving old events (> 1 year past).

---

## See Also

- [MM Calendar Integration](../mm_calendar_integration/README.md) - Parent calendar integration
- [MM Meeting Booking](../mm_meeting_booking/README.md) - Booking system that creates/links calendar events
- [MM User Settings](../mm_user_settings/README.md) - Working hours configuration
- [MM User Availability Rule](../mm_user_availability_rule/README.md) - Availability constraints
- [Meeting Manager Project Description](../../../Meeting_Manager_PD.md) - Overall system architecture

---

## Contributing

When modifying this DocType:

1. **Adding Event Types**:
   - Update `event_type` Select options
   - Add logic to handle new type in availability calculation
   - Document use cases for new type

2. **Changing Sync Logic**:
   - Update sync service implementation
   - Add error handling for new scenarios
   - Update sync_status options if needed

3. **Modifying Validation**:
   - Update validation methods
   - Add test cases for new validations
   - Document new error messages in this README

4. **Adding Metadata Fields**:
   - Use JSON fields for flexible metadata storage
   - Avoid adding too many text fields (impacts query performance)
   - Document JSON structure expectations

---

**Last Updated**: 2025-12-08
**Version**: 1.0
**Maintainer**: Best Security Development Team
