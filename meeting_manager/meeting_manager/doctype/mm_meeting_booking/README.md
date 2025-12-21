# MM Meeting Booking - DocType Documentation

## Overview

**MM Meeting Booking** is the central DocType of the Meeting Manager system. It represents a single meeting/booking between department members and customers (or between internal team members). This is where all the system's functionality converges: customer bookings from the public interface, internal meeting creation, calendar synchronization, assignment tracking, approval workflows, and comprehensive audit trails.

**Auto-naming Format**: `MM-MB-{meeting_type}-{####}`

Example: `MM-MB-MM-MT-support-30-min-call-0042`

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md), the booking system is the heart of the entire application:

### Core Business Requirements

1. **Customer Booking Flow**: Customers book meetings with departments through a public interface. The system automatically assigns bookings to available department members using round-robin or least-busy algorithms.

2. **Internal Meeting Creation**: System Managers and Department Leaders can create internal meetings directly with specific employees, respecting their availability schedules.

3. **Assignment Management**: Automatic assignment with ability for manual reassignment via drag-and-drop interface.

4. **Approval Workflow**: Certain meeting types require approval before confirmation (e.g., executive meetings, high-value consultations).

5. **Calendar Integration**: Bookings are automatically synced to assigned users' external calendars (Google, Outlook).

6. **Comprehensive Tracking**: Full audit trail of all booking changes, assignments, and customer interactions.

**Key Product Requirements** (Phases 1-6):
- Support both customer bookings and internal meetings
- Automatic assignment based on availability and department rules
- Manual reassignment with notification cascade
- Approval workflow for restricted meeting types
- Bidirectional calendar sync
- Email confirmations and reminders
- Cancellation and rescheduling capability
- Complete audit history

---

## Key Features

### 1. **Dual Booking Modes**
- **Customer Bookings** (`is_internal = 0`): External customers booking through public interface
- **Internal Meetings** (`is_internal = 1`): Internal team meetings between employees

### 2. **Comprehensive Status Management**
Six booking statuses tracking the complete lifecycle:
- **Pending**: Initial state, awaiting confirmation/approval
- **Confirmed**: Booking is confirmed and scheduled
- **Cancelled**: Booking was cancelled (tracks who, when, why)
- **Completed**: Meeting took place successfully
- **No-Show**: Customer/participant didn't attend
- **Rescheduled**: Booking was moved to new time (links to new booking)

### 3. **Assignment System**
- **Multiple Assigned Users**: Support for multiple team members per booking
- **Primary Host**: Designate one user as the main host
- **Assignment History**: Complete audit trail of all assignment changes
- **Assignment Tracking**: Who assigned, when, why (reassignment notes)

### 4. **Approval Workflow**
- **Conditional Approval**: Some meeting types require approval
- **Three Approval States**: Pending, Approved, Rejected
- **Approval Tracking**: Who approved/rejected, when, with reason
- **Auto-confirmation**: Approved bookings auto-transition to Confirmed status

### 5. **Participant Management**
- **Internal Participants**: Link to system users
- **External Participants**: Customer and guest details
- **Response Tracking**: Accepted, Declined, Tentative, Pending
- **RSVP Timeline**: Track when each participant responded

### 6. **Calendar Synchronization**
- **Bidirectional Sync**: Create events in external calendars (Google, Outlook)
- **Event Linking**: Link to `MM Calendar Event Sync` records
- **External Calendar Links**: Direct links to events in Google/Outlook
- **Sync Status Tracking**: Know if calendar sync succeeded or failed

### 7. **Location Management**
Four location types with appropriate fields:
- **Video Call**: Video meeting URL (Zoom, Meet, Teams)
- **Phone Call**: Phone number in customer details
- **Physical Location**: Address or room details
- **Custom**: Flexible location description

### 8. **Reminder System**
- **Configurable Reminders**: Based on meeting type reminder schedule
- **Reminder Tracking**: JSON array of sent reminder timestamps
- **Last Reminder Sent**: Quick reference for last reminder
- **Multiple Recipients**: Reminders to assigned users and customer

### 9. **Complete Audit Trail**
Three levels of history tracking:
- **Booking History**: All booking events (created, confirmed, cancelled, etc.)
- **Assignment History**: All assignment changes (assigned, unassigned, primary changed)
- **Status Changes**: Tracked via before_save hook with descriptions

### 10. **Customer Details**
For external bookings (`is_internal = 0`):
- **Customer Name**: Full name (required)
- **Customer Email**: Email address with validation (required)
- **Customer Phone**: Phone number with format validation
- **Customer Notes**: Special requests, accessibility needs, etc.

---

## Field Reference

### Booking Information Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meeting_type` | Link (MM Meeting Type) | Yes | Type of meeting being booked |
| `booking_status` | Select | Yes | Status: `Pending`, `Confirmed`, `Cancelled`, `Completed`, `No-Show`, `Rescheduled` (default: Pending) |
| `booking_date` | Date | Auto | Date when booking was created (read-only, default: Today) |
| `booking_reference` | Data | Auto | Unique reference for customer communication (read-only, auto-generated) |
| `is_internal` | Check | No | Is this an internal meeting between employees (default: 0) |
| `booking_source` | Select | No | How booking was created: `Public Booking Page`, `Internal System`, `Manual Entry`, `API Integration`, `Google Calendar`, `Outlook Calendar` (default: Public Booking Page) |

### Meeting Details Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meeting_title` | Data | Yes | Meeting title/subject |
| `meeting_description` | Text Editor | No | Meeting agenda or description |
| `meeting_location` | Data | No | Physical address or instructions |
| `video_meeting_url` | Data | No | Video conference URL (must start with http:// or https://) |
| `location_type` | Select | No | Type: `Video Call`, `Phone Call`, `Physical Location`, `Custom` |

### Timing Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_datetime` | Datetime | Yes | Meeting start date and time |
| `end_datetime` | Datetime | Yes | Meeting end date and time |
| `duration` | Int | Auto | Duration in minutes (auto-calculated, read-only) |

### Assigned Users Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assigned_users` | Table (MM Meeting Booking Assigned User) | Yes | Currently assigned team members (at least one required) |
| `assignment_history` | Table (MM Meeting Booking Assignment History) | Auto | Historical record of assignment changes (read-only) |

### Customer Details Section

*Only visible when `is_internal = 0`*

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customer_name` | Data | Conditional* | Customer full name |
| `customer_email` | Data | Conditional* | Customer email address (validated) |
| `customer_phone` | Data | No | Customer phone number (validated) |
| `customer_notes` | Text | No | Customer's notes or special requests |

*Required when `is_internal = 0`

### Participants Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `participants` | Table (MM Meeting Booking Participant) | No | All meeting participants (internal and external) |

### Approval Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requires_approval` | Check | No | Does this booking require manual approval (default: 0, set from meeting type) |
| `approval_status` | Select | Conditional | Status: `Pending`, `Approved`, `Rejected` (default: Pending, visible if requires_approval) |
| `approved_by` | Link (User) | Auto | User who approved/rejected (read-only) |
| `approval_date` | Datetime | Auto | When approval decision was made |
| `rejection_reason` | Text | Conditional | Reason for rejection (required if approval_status = Rejected) |

### Calendar Sync Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `calendar_event_synced` | Check | No | Has this been synced to calendar (default: 0) |
| `calendar_event` | Link (MM Calendar Event Sync) | No | Link to synced calendar event |
| `external_calendar_link` | Data | Auto | External calendar event URL (read-only) |

### Reminders Section

| Field | Type | Description |
|-------|------|-------------|
| `reminders_sent` | JSON | JSON array of reminder timestamps sent (read-only) |
| `last_reminder_sent` | Datetime | Last reminder sent timestamp (read-only) |

### Booking History Section

| Field | Type | Description |
|-------|------|-------------|
| `booking_history` | Table (MM Meeting Booking History) | Log of all booking changes and events (auto-populated) |

### Metadata Section

| Field | Type | Description |
|-------|------|-------------|
| `created_by` | Link (User) | User who created this booking (read-only, auto-set) |
| `cancelled_at` | Datetime | When booking was cancelled (read-only, visible if status = Cancelled) |
| `cancellation_reason` | Text | Reason for cancellation (visible if status = Cancelled) |

---

## Child Table Structures

### 1. MM Meeting Booking Assigned User

Currently assigned team members hosting this meeting.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user` | Link (User) | Yes | Team member assigned to this booking |
| `is_primary_host` | Check | No | Is this the primary host (default: 0) |
| `assigned_at` | Datetime | Auto | When user was assigned (default: Now, read-only) |
| `assigned_by` | Link (User) | Auto | Who assigned this user (read-only) |

**Key Rules**:
- At least one assigned user required
- At least one must be marked as primary host
- No duplicate users allowed
- Automatically tracks assignment timestamp and assigner

### 2. MM Meeting Booking Assignment History

Audit trail of all assignment changes (reassignments, unassignments).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action_type` | Select | Yes | Type: `Assigned`, `Unassigned`, `Reassigned`, `Primary Changed` |
| `user` | Link (User) | Yes | User affected by this action |
| `action_datetime` | Datetime | Auto | When action occurred (default: Now, read-only) |
| `action_by` | Link (User) | Auto | Who performed this action (read-only) |
| `notes` | Small Text | No | Additional notes about this action |

**Auto-populated by system** via `track_assignment_changes()` method.

### 3. MM Meeting Booking Participant

All meeting participants (both internal team members and external guests).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `participant_type` | Select | Yes | Type: `Internal`, `External` (default: External) |
| `user` | Link (User) | Conditional* | Internal user (required if participant_type = Internal) |
| `name1` | Data | Conditional** | Participant name (required if participant_type = External) |
| `email` | Data | Yes | Participant email address (validated) |
| `response_status` | Select | No | Response: `Pending`, `Accepted`, `Declined`, `Tentative` (default: Pending) |
| `response_datetime` | Datetime | Auto | When participant responded (read-only) |

*Required when `participant_type = Internal`
**Required when `participant_type = External`

**Key Rules**:
- Email must be unique per participant
- Internal participants must have valid user link
- External participants must have name
- Email format validation applied

### 4. MM Meeting Booking History

Complete audit log of all booking events and changes.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_type` | Select | Yes | Type: `Created`, `Confirmed`, `Rescheduled`, `Cancelled`, `Completed`, `No-Show`, `Approved`, `Rejected`, `Reminder Sent`, `Calendar Synced`, `Assignment Changed`, `Customer Updated` |
| `event_datetime` | Datetime | Auto | When event occurred (default: Now, read-only) |
| `event_by` | Link (User) | Auto | User who triggered this event (read-only) |
| `event_description` | Text | No | Detailed description of the event |

**Auto-populated by system** via hooks and `add_history_entry()` method.

---

## Use Cases

### Use Case 1: Customer Books Meeting via Public Interface

**Scenario**: John Doe (customer) books a 30-minute support call through the public booking page.

```python
# System creates booking (public booking API)
booking = frappe.get_doc({
    "doctype": "MM Meeting Booking",
    "meeting_type": "MM-MT-support-30-min-call",
    "meeting_title": "Support Call - Account Setup Issues",
    "meeting_description": "Need help setting up multi-factor authentication",
    "booking_status": "Pending",  # Will auto-confirm if no approval required
    "is_internal": 0,
    "booking_source": "Public Booking Page",
    "start_datetime": "2025-12-10 14:00:00",
    "end_datetime": "2025-12-10 14:30:00",
    "location_type": "Video Call",
    "video_meeting_url": "https://meet.google.com/abc-defg-hij",

    # Customer details
    "customer_name": "John Doe",
    "customer_email": "john@customer.com",
    "customer_phone": "+1-555-123-4567",
    "customer_notes": "Prefer email follow-up after call",

    # Assignment (auto-assigned by system using round-robin)
    "assigned_users": [{
        "user": "sarah@bestsecurity.com",
        "is_primary_host": 1
    }]
})

booking.insert()

# System automatically:
# 1. Generates booking_reference: "BK-A7F92K1X"
# 2. Sets booking_date to today
# 3. Calculates duration: 30 minutes
# 4. Validates customer email format
# 5. Checks Sarah's availability
# 6. Sets created_by to system user (API)
# 7. Adds "Created" entry to booking_history
# 8. Triggers calendar sync to Sarah's Google Calendar
# 9. Sends confirmation emails to John and Sarah

print(f"Booking created: {booking.name}")
print(f"Reference: {booking.booking_reference}")
print(f"Status: {booking.booking_status}")
```

**Result**:
- Booking: `MM-MB-MM-MT-support-30-min-call-0042`
- Reference: `BK-A7F92K1X`
- Sarah receives email with customer details
- John receives email with booking details and meeting link
- Event created in Sarah's Google Calendar
- Booking appears in department dashboard

### Use Case 2: Internal Team Meeting Creation

**Scenario**: Department leader creates internal planning meeting with 3 team members.

```python
# Leader creates internal meeting
booking = frappe.get_doc({
    "doctype": "MM Meeting Booking",
    "meeting_type": "MM-MT-support-internal-planning",
    "meeting_title": "Q1 Planning Meeting",
    "meeting_description": "<h3>Agenda</h3><ul><li>Review Q4 metrics</li><li>Set Q1 goals</li><li>Resource allocation</li></ul>",
    "booking_status": "Confirmed",  # Internal meetings auto-confirm
    "is_internal": 1,
    "booking_source": "Internal System",
    "start_datetime": "2025-12-15 10:00:00",
    "end_datetime": "2025-12-15 11:30:00",
    "location_type": "Physical Location",
    "meeting_location": "Conference Room A, 3rd Floor",

    # Multiple assigned users (all team members)
    "assigned_users": [
        {
            "user": "sarah@bestsecurity.com",
            "is_primary_host": 1  # Sarah is leading the meeting
        },
        {
            "user": "mike@bestsecurity.com",
            "is_primary_host": 0
        },
        {
            "user": "jane@bestsecurity.com",
            "is_primary_host": 0
        }
    ],

    # Internal participants (for RSVP tracking)
    "participants": [
        {
            "participant_type": "Internal",
            "user": "sarah@bestsecurity.com",
            "email": "sarah@bestsecurity.com",
            "response_status": "Accepted"
        },
        {
            "participant_type": "Internal",
            "user": "mike@bestsecurity.com",
            "email": "mike@bestsecurity.com",
            "response_status": "Pending"
        },
        {
            "participant_type": "Internal",
            "user": "jane@bestsecurity.com",
            "email": "jane@bestsecurity.com",
            "response_status": "Tentative"
        }
    ]
})

booking.insert()

# System automatically:
# 1. Skips customer_name/email validation (is_internal = 1)
# 2. Validates all 3 users exist and are available
# 3. Calculates duration: 90 minutes
# 4. Creates calendar events in all 3 users' calendars
# 5. Sends meeting invites to all participants
# 6. Adds all 3 users to assignment_history

print(f"Internal meeting created: {booking.name}")
```

**Result**:
- No customer details required
- All 3 team members receive calendar invites
- Meeting appears in Conference Room A booking system (if integrated)
- Department dashboard shows internal meeting

### Use Case 3: Booking Requires Approval

**Scenario**: Customer books executive consultation (requires approval before confirmation).

```python
# Customer books executive meeting
booking = frappe.get_doc({
    "doctype": "MM Meeting Booking",
    "meeting_type": "MM-MT-sales-executive-consultation",  # This type requires_approval = 1
    "meeting_title": "Executive Consultation - Enterprise Account",
    "meeting_description": "Discussing enterprise security package for 500+ employees",
    "booking_status": "Pending",
    "is_internal": 0,
    "booking_source": "Public Booking Page",
    "start_datetime": "2025-12-12 15:00:00",
    "end_datetime": "2025-12-12 16:00:00",
    "location_type": "Video Call",
    "video_meeting_url": "https://zoom.us/j/123456789",

    "customer_name": "Alice Johnson",
    "customer_email": "alice@bigcorp.com",
    "customer_phone": "+1-555-987-6543",
    "customer_notes": "Referred by John Smith, existing customer",

    "assigned_users": [{
        "user": "ceo@bestsecurity.com",
        "is_primary_host": 1
    }]
})

booking.insert()

# System automatically:
# 1. Sets requires_approval = 1 (from meeting type)
# 2. Sets approval_status = "Pending"
# 3. Booking status remains "Pending"
# 4. Does NOT send confirmation to customer yet
# 5. Sends approval request to department leader/admin

print(f"Booking pending approval: {booking.name}")
print(f"Approval status: {booking.approval_status}")

# --- Later: Department leader approves ---
booking = frappe.get_doc("MM Meeting Booking", booking.name)
booking.approval_status = "Approved"
booking.rejection_reason = ""  # Clear any previous rejection
booking.save()

# System automatically (via validate_approval_workflow):
# 1. Sets approved_by = current user
# 2. Sets approval_date = now
# 3. Changes booking_status from "Pending" to "Confirmed"
# 4. Sends confirmation email to customer
# 5. Creates calendar event in CEO's calendar
# 6. Adds "Approved" entry to booking_history

print(f"Booking approved and confirmed!")
```

**Result**:
- Booking requires manual approval
- Customer notified that booking is pending approval
- Department leader receives approval request email
- After approval, customer receives confirmation
- CEO's calendar updated with event

### Use Case 4: Booking Reassignment (Drag-and-Drop)

**Scenario**: Sarah is sick. Department leader reassigns her booking to Mike.

```python
# Get existing booking
booking = frappe.get_doc("MM Meeting Booking", "MM-MB-MM-MT-support-30-min-call-0042")

print(f"Current assigned user: {booking.assigned_users[0].user}")  # sarah@bestsecurity.com

# Reassign to Mike
booking.assigned_users = []  # Clear current assignments
booking.append("assigned_users", {
    "user": "mike@bestsecurity.com",
    "is_primary_host": 1
})

booking.save()

# System automatically (via track_assignment_changes):
# 1. Detects Sarah was removed from assigned_users
# 2. Detects Mike was added to assigned_users
# 3. Adds "Unassigned" entry to assignment_history for Sarah
# 4. Adds "Assigned" entry to assignment_history for Mike
# 5. Adds "Primary Changed" entry (primary changed from Sarah to Mike)
# 6. Deletes calendar event from Sarah's Google Calendar
# 7. Creates calendar event in Mike's Google Calendar
# 8. Sends notification emails:
#    - To Customer: "Your meeting host has changed to Mike"
#    - To Sarah: "Booking reassigned away from you"
#    - To Mike: "New booking assigned to you"
#    - To Department Leader: "Booking reassigned from Sarah to Mike"

print(f"Booking reassigned to: {booking.assigned_users[0].user}")
print(f"Assignment history entries: {len(booking.assignment_history)}")
```

**Result**:
- Complete audit trail in assignment_history
- All parties notified via email
- Calendar events updated in both Sarah's and Mike's calendars
- Customer sees updated host information

### Use Case 5: Booking Cancellation

**Scenario**: Customer cancels booking 2 days before scheduled time.

```python
# Customer cancels via cancellation link
booking = frappe.get_doc("MM Meeting Booking", "MM-MB-MM-MT-support-30-min-call-0042")

booking.booking_status = "Cancelled"
booking.cancellation_reason = "Customer: Schedule conflict - need to reschedule for next week"
booking.save()

# System automatically (via validate_booking_status):
# 1. Sets cancelled_at = now
# 2. Warns if cancellation_reason not provided (but allows save)
# 3. Adds "Cancelled" entry to booking_history
# 4. Deletes calendar event from assigned user's calendar
# 5. Sends cancellation emails:
#    - To Customer: "Your booking has been cancelled" + link to rebook
#    - To Assigned User (Sarah): "Customer cancelled booking"
#    - To Department Leader: "Booking cancelled"

print(f"Booking cancelled at: {booking.cancelled_at}")
print(f"Reason: {booking.cancellation_reason}")
```

**Result**:
- Booking marked as Cancelled with timestamp
- Calendar event removed from Sarah's calendar
- Time slot becomes available for new bookings
- Customer can rebook if needed

### Use Case 6: Marking as No-Show

**Scenario**: Meeting time passed but customer didn't attend.

```python
# After meeting time passes, assigned user marks as no-show
booking = frappe.get_doc("MM Meeting Booking", "MM-MB-MM-MT-support-30-min-call-0042")

# Validate that meeting is in the past
from frappe.utils import get_datetime, now_datetime
if get_datetime(booking.start_datetime) < now_datetime():
    booking.booking_status = "No-Show"
    booking.save()

    # System automatically:
    # 1. Adds "No-Show" entry to booking_history
    # 2. Triggers follow-up email to customer (optional reschedule)
    # 3. Updates department statistics (no-show rate)
    # 4. May trigger auto-blacklist if repeated no-shows (configurable)

    print(f"Booking marked as No-Show")
else:
    print("Cannot mark future booking as No-Show")
    # System validation will throw error
```

**Result**:
- Booking marked as No-Show (only allowed after meeting start time)
- No-show tracked in department analytics
- Optional follow-up automation triggered

---

## Validation Rules

The DocType includes **15 validation methods** ensuring comprehensive data integrity:

### 1. Meeting Type Validation (`validate_meeting_type_exists`)

**Validates**:
- Meeting type exists and is active
- `is_internal` flag matches meeting type availability:
  - Internal booking requires `meeting_type.is_internal = 1`
  - Public booking requires `meeting_type.is_public = 1`
- Auto-sets `requires_approval` from meeting type
- Copies location settings from meeting type

**Error Messages**:
- `"Meeting Type is required."`
- `"Meeting Type '{name}' is not active. Please select an active meeting type."`
- `"Meeting Type '{name}' is not available for internal meetings. Please select a meeting type that allows internal meetings."`
- `"Meeting Type '{name}' is not available for public bookings. Please select a meeting type that allows public bookings."`

### 2. Timing Validation (`validate_timing`)

**Validates**:
- Start and end datetime are provided and valid
- End is after start
- New bookings are not in the past
- Booking meets assigned users' availability rules:
  - Respects `max_days_advance` (maximum advance booking window)
  - Respects `min_notice_hours` (minimum notice before booking)

**Error Messages**:
- `"Start DateTime is required."`
- `"End DateTime is required."`
- `"Invalid datetime format for Start or End DateTime."`
- `"End DateTime must be after Start DateTime."`
- `"Cannot create a booking in the past. Please select a future date and time."`
- `"Booking is too far in advance for user '{user}'. Maximum advance booking is {days} days."`
- `"Booking does not meet minimum notice requirement for user '{user}'. Minimum notice is {hours} hours."`

### 3. Duration Calculation (`calculate_duration`)

**Behavior**:
- Automatically calculates duration in minutes from start and end times
- Updates `duration` field (read-only)
- Example: 10:00 AM - 10:30 AM = 30 minutes

### 4. Customer Details Validation (`validate_customer_details`)

**Validates** (only for external bookings, `is_internal = 0`):
- `customer_name` is provided
- `customer_email` is provided and valid email format
- `customer_phone` has valid format (if provided):
  - At least 7 digits after removing formatting characters
  - Only digits allowed (after removing spaces, dashes, parentheses, plus)

**Error Messages**:
- `"Customer Name is required for external bookings."`
- `"Customer Email is required for external bookings."`
- `"Invalid email format for Customer Email: '{email}'"`
- `"Invalid phone number format. Please provide a valid phone number."`

**Example Phone Validation**:
- ✅ Valid: "+1-555-123-4567", "(555) 123-4567", "555-123-4567", "+44 20 7123 4567"
- ❌ Invalid: "123-456" (< 7 digits), "call me" (not numeric)

### 5. Assigned Users Validation (`validate_assigned_users`)

**Validates**:
- At least one user is assigned
- No duplicate users in assigned_users list
- All assigned users exist in User DocType
- At least one user is marked as primary host
- Warns if multiple primary hosts (recommends one)
- Auto-sets `assigned_by` if not already set

**Error Messages**:
- `"At least one user must be assigned to this booking."`
- `"Duplicate users found in assigned users. Each user can only be assigned once."`
- `"User '{user}' does not exist."`
- `"At least one assigned user must be marked as Primary Host."`

**Warnings**:
- `"Warning: Multiple users are marked as Primary Host. Consider having only one primary host."` (orange indicator)

### 6. Participants Validation (`validate_participants`)

**Validates**:
- No duplicate participant emails
- All participant emails have valid format
- Internal participants have `user` field set
- External participants have `name1` field set
- Internal participant's user exists
- Auto-populates email from user if not set (for internal participants)
- Warns if no participants for confirmed bookings

**Error Messages**:
- `"Duplicate participants found. Each participant email must be unique."`
- `"Invalid email format for participant: '{email}'"`
- `"Internal participant must have a User selected: '{email}'"`
- `"External participant must have a Name: '{email}'"`
- `"User '{user}' does not exist."`

**Warnings**:
- `"Warning: No participants added to this confirmed booking. Consider adding participants for better tracking."` (orange indicator)

### 7. Approval Workflow Validation (`validate_approval_workflow`)

**Validates**:
- Clears approval fields if `requires_approval = 0`
- Auto-sets `approval_status = "Pending"` if not set
- Auto-sets `approved_by` and `approval_date` for approved/rejected bookings
- Auto-transitions `booking_status`:
  - Approved + Pending → Confirmed
  - Rejected → Cancelled
- Requires `rejection_reason` for rejected bookings

**Error Messages**:
- `"Rejection Reason is required when rejecting a booking."`

**Auto-behavior**:
- Sets `approved_by = current_user` if not set
- Sets `approval_date = now` if not set
- Updates `booking_status` based on `approval_status`

### 8. Calendar Sync Validation (`validate_calendar_sync`)

**Validates**:
- Warns if `calendar_event_synced` checked but no `calendar_event` linked
- Auto-checks `calendar_event_synced` if `calendar_event` is linked
- Validates linked calendar event exists

**Error Messages**:
- `"Calendar Event '{name}' does not exist."`

**Warnings**:
- `"Warning: Calendar Event Synced is checked but no Calendar Event is linked."` (orange indicator)

### 9. Location Settings Validation (`validate_location_settings`)

**Validates**:
- Warns if `location_type = "Video Call"` but no `video_meeting_url`
- Warns if `location_type = "Physical Location"` but no `meeting_location`
- Video meeting URL must start with `http://` or `https://`

**Error Messages**:
- `"Video Meeting URL must start with http:// or https://"`

**Warnings**:
- `"Video Meeting URL is recommended when Location Type is 'Video Call'."` (orange indicator)
- `"Meeting Location is recommended when Location Type is 'Physical Location'."` (orange indicator)

### 10. Booking Status Validation (`validate_booking_status`)

**Validates**:
- Auto-sets `cancelled_at` for cancelled bookings
- Warns if `cancellation_reason` not provided (recommended)
- Validates `No-Show` and `Completed` statuses are only for past bookings

**Error Messages**:
- `"Cannot mark a future booking as '{status}'. This status can only be set for past bookings."`

**Warnings**:
- `"Cancellation Reason is recommended when cancelling a booking."` (orange indicator)

### 11. Booking Reference Generation (`set_booking_reference`)

**Behavior**:
- Auto-generates unique 8-character reference code for new bookings
- Format: `BK-{8 random uppercase letters/digits}`
- Example: `BK-A7F92K1X`, `BK-3K9QW2M5`
- Used in customer emails and cancellation links

### 12. Created By Auto-Set (`set_created_by`)

**Behavior**:
- Auto-sets `created_by` to current user for new bookings
- Used for audit trail and permission filtering

### 13. Status Change Tracking (`before_save` hook)

**Behavior**:
- Detects booking_status changes
- Automatically adds history entry with old and new status
- Example: "Booking status changed from Pending to Confirmed"

### 14. Assignment Change Tracking (`track_assignment_changes`)

**Behavior** (called in `on_update` hook):
- Detects users added to assigned_users (creates "Assigned" history entry)
- Detects users removed from assigned_users (creates "Unassigned" history entry)
- Detects primary host changes (creates "Primary Changed" history entry)
- All entries include timestamp, actor, and notes

### 15. Creation History Entry (`on_update` hook)

**Behavior**:
- For new bookings, automatically adds "Created" entry to booking_history
- Includes meeting title in description

---

## Usage Examples

### Example 1: Creating Customer Booking with Full Details

```python
import frappe
from frappe.utils import add_days, now_datetime, get_time

def create_customer_booking(meeting_type, customer_details, booking_datetime):
    """
    Create a complete customer booking

    Args:
        meeting_type: Name of MM Meeting Type
        customer_details: Dict with name, email, phone, notes
        booking_datetime: Tuple of (start_datetime, end_datetime)

    Returns:
        MM Meeting Booking document
    """
    booking = frappe.get_doc({
        "doctype": "MM Meeting Booking",
        "meeting_type": meeting_type,
        "meeting_title": f"Support Call - {customer_details['name']}",
        "meeting_description": customer_details.get('notes', ''),
        "booking_status": "Pending",
        "is_internal": 0,
        "booking_source": "Public Booking Page",
        "start_datetime": booking_datetime[0],
        "end_datetime": booking_datetime[1],
        "location_type": "Video Call",

        # Customer details
        "customer_name": customer_details['name'],
        "customer_email": customer_details['email'],
        "customer_phone": customer_details.get('phone', ''),
        "customer_notes": customer_details.get('notes', ''),

        # Assignment (from assignment algorithm)
        "assigned_users": [{
            "user": customer_details['assigned_user'],
            "is_primary_host": 1
        }],

        # Add customer as external participant
        "participants": [{
            "participant_type": "External",
            "name1": customer_details['name'],
            "email": customer_details['email'],
            "response_status": "Pending"
        }]
    })

    booking.insert()
    frappe.db.commit()

    return booking

# Usage
customer = {
    "name": "John Doe",
    "email": "john@customer.com",
    "phone": "+1-555-123-4567",
    "notes": "Needs help with account setup",
    "assigned_user": "sarah@bestsecurity.com"
}

start = add_days(now_datetime(), 2).replace(hour=14, minute=0, second=0)
end = start.replace(hour=14, minute=30)

booking = create_customer_booking(
    "MM-MT-support-30-min-call",
    customer,
    (start, end)
)

print(f"Booking created: {booking.name}")
print(f"Reference: {booking.booking_reference}")
```

### Example 2: Querying Bookings with Filters

```python
import frappe
from frappe.utils import today, add_days

def get_department_bookings(department, start_date=None, end_date=None, status=None):
    """
    Get bookings for a department with optional filters

    Args:
        department: MM Department name
        start_date: Start of date range (default: today)
        end_date: End of date range (default: 30 days from start)
        status: Filter by booking_status (optional)

    Returns:
        List of bookings
    """
    if not start_date:
        start_date = today()
    if not end_date:
        end_date = add_days(start_date, 30)

    # Get department's meeting types
    meeting_types = frappe.get_all(
        "MM Meeting Type",
        filters={"department": department, "is_active": 1},
        pluck="name"
    )

    if not meeting_types:
        return []

    # Build filters
    filters = {
        "meeting_type": ["in", meeting_types],
        "start_datetime": [">=", start_date],
        "end_datetime": ["<=", end_date]
    }

    if status:
        filters["booking_status"] = status

    # Get bookings
    bookings = frappe.get_all(
        "MM Meeting Booking",
        filters=filters,
        fields=[
            "name",
            "meeting_title",
            "booking_status",
            "booking_reference",
            "start_datetime",
            "end_datetime",
            "duration",
            "customer_name",
            "customer_email",
            "is_internal"
        ],
        order_by="start_datetime asc"
    )

    # Enrich with assigned users
    for booking in bookings:
        booking['assigned_users'] = frappe.get_all(
            "MM Meeting Booking Assigned User",
            filters={"parent": booking.name},
            fields=["user", "is_primary_host"]
        )

    return bookings

# Usage examples

# Get all confirmed bookings for Support department
confirmed = get_department_bookings("MM-DEPT-support", status="Confirmed")
print(f"Confirmed bookings: {len(confirmed)}")

# Get all bookings (any status) for next week
from frappe.utils import add_weeks
next_week = get_department_bookings(
    "MM-DEPT-support",
    start_date=add_weeks(today(), 1),
    end_date=add_weeks(today(), 2)
)
print(f"Next week bookings: {len(next_week)}")
```

### Example 3: Reassigning Booking with Notifications

```python
import frappe
from frappe.utils import now_datetime

def reassign_booking(booking_name, old_user, new_user, reason=""):
    """
    Reassign booking from one user to another

    Args:
        booking_name: Name of MM Meeting Booking
        old_user: Current assigned user email
        new_user: New assigned user email
        reason: Reason for reassignment

    Returns:
        Updated booking document
    """
    booking = frappe.get_doc("MM Meeting Booking", booking_name)

    # Verify old_user is currently assigned
    current_users = [au.user for au in booking.assigned_users]
    if old_user not in current_users:
        frappe.throw(f"User '{old_user}' is not currently assigned to this booking.")

    # Check new user availability
    from frappe.utils import get_datetime
    start_dt = get_datetime(booking.start_datetime)
    end_dt = get_datetime(booking.end_datetime)

    # TODO: Add availability check logic here

    # Remove old user
    booking.assigned_users = [au for au in booking.assigned_users if au.user != old_user]

    # Add new user
    booking.append("assigned_users", {
        "user": new_user,
        "is_primary_host": 1  # New user becomes primary host
    })

    # Add reassignment note to booking history
    booking.add_history_entry(
        event_type="Assignment Changed",
        description=f"Booking reassigned from {old_user} to {new_user}. Reason: {reason or 'Not provided'}"
    )

    booking.save()

    # Send notifications (would be handled by email hooks in production)
    print(f"Reassignment notifications sent to:")
    print(f"  - Customer: {booking.customer_email}")
    print(f"  - Old user: {old_user}")
    print(f"  - New user: {new_user}")

    return booking

# Usage
reassigned = reassign_booking(
    "MM-MB-MM-MT-support-30-min-call-0042",
    "sarah@bestsecurity.com",
    "mike@bestsecurity.com",
    "Sarah is out sick"
)

print(f"Booking reassigned to: {reassigned.assigned_users[0].user}")
print(f"Assignment history entries: {len(reassigned.assignment_history)}")
```

### Example 4: Handling Approval Workflow

```python
import frappe
from frappe.utils import now_datetime

def approve_booking(booking_name, approver_comment=""):
    """
    Approve a booking that requires approval

    Args:
        booking_name: Name of MM Meeting Booking
        approver_comment: Optional comment from approver

    Returns:
        Approved booking document
    """
    booking = frappe.get_doc("MM Meeting Booking", booking_name)

    # Check if approval is required
    if not booking.requires_approval:
        frappe.msgprint("This booking does not require approval.")
        return booking

    # Check current approval status
    if booking.approval_status != "Pending":
        frappe.msgprint(f"Booking already {booking.approval_status}.")
        return booking

    # Approve booking
    booking.approval_status = "Approved"
    booking.rejection_reason = ""  # Clear any previous rejection

    # Add approver comment to history if provided
    if approver_comment:
        booking.add_history_entry(
            event_type="Approved",
            description=f"Booking approved. Comment: {approver_comment}"
        )

    booking.save()

    # System will automatically:
    # 1. Set approved_by to current user
    # 2. Set approval_date to now
    # 3. Change booking_status from "Pending" to "Confirmed"
    # 4. Trigger confirmation emails
    # 5. Trigger calendar sync

    print(f"Booking approved!")
    print(f"Approved by: {booking.approved_by}")
    print(f"New status: {booking.booking_status}")

    return booking

def reject_booking(booking_name, rejection_reason):
    """
    Reject a booking that requires approval

    Args:
        booking_name: Name of MM Meeting Booking
        rejection_reason: Reason for rejection (required)

    Returns:
        Rejected booking document
    """
    if not rejection_reason:
        frappe.throw("Rejection reason is required.")

    booking = frappe.get_doc("MM Meeting Booking", booking_name)

    if not booking.requires_approval:
        frappe.msgprint("This booking does not require approval.")
        return booking

    # Reject booking
    booking.approval_status = "Rejected"
    booking.rejection_reason = rejection_reason

    booking.save()

    # System will automatically:
    # 1. Set approved_by to current user
    # 2. Set approval_date to now
    # 3. Change booking_status to "Cancelled"
    # 4. Trigger rejection email to customer with reason

    print(f"Booking rejected!")
    print(f"Reason: {booking.rejection_reason}")

    return booking

# Usage

# Approve booking
approved = approve_booking(
    "MM-MB-MM-MT-sales-executive-consultation-0003",
    "Approved - High-value enterprise client"
)

# Reject booking
rejected = reject_booking(
    "MM-MB-MM-MT-sales-executive-consultation-0004",
    "Rejected - Requested time slot conflicts with board meeting. Please suggest alternative times."
)
```

### Example 5: Marking Booking Status (Completed/No-Show)

```python
import frappe
from frappe.utils import get_datetime, now_datetime

def mark_booking_completed(booking_name, completion_notes=""):
    """
    Mark booking as completed (after meeting took place)

    Args:
        booking_name: Name of MM Meeting Booking
        completion_notes: Optional notes about meeting outcome

    Returns:
        Updated booking document
    """
    booking = frappe.get_doc("MM Meeting Booking", booking_name)

    # Verify meeting is in the past
    start_dt = get_datetime(booking.start_datetime)
    if start_dt > now_datetime():
        frappe.throw("Cannot mark future booking as Completed.")

    # Update status
    booking.booking_status = "Completed"

    # Add completion notes to history
    if completion_notes:
        booking.add_history_entry(
            event_type="Completed",
            description=f"Meeting completed. Notes: {completion_notes}"
        )

    booking.save()

    print(f"Booking marked as Completed")
    return booking

def mark_booking_no_show(booking_name, no_show_notes=""):
    """
    Mark booking as no-show (customer didn't attend)

    Args:
        booking_name: Name of MM Meeting Booking
        no_show_notes: Optional notes about no-show

    Returns:
        Updated booking document
    """
    booking = frappe.get_doc("MM Meeting Booking", booking_name)

    # Verify meeting is in the past
    start_dt = get_datetime(booking.start_datetime)
    if start_dt > now_datetime():
        frappe.throw("Cannot mark future booking as No-Show.")

    # Update status
    booking.booking_status = "No-Show"

    # Add no-show notes to history
    booking.add_history_entry(
        event_type="No-Show",
        description=f"Customer did not attend. {no_show_notes}"
    )

    booking.save()

    # Trigger follow-up automation
    print(f"Booking marked as No-Show")
    print(f"Follow-up email will be sent to: {booking.customer_email}")

    return booking

# Usage

# Mark as completed
completed = mark_booking_completed(
    "MM-MB-MM-MT-support-30-min-call-0042",
    "Successfully helped customer set up MFA. No follow-up needed."
)

# Mark as no-show
no_show = mark_booking_no_show(
    "MM-MB-MM-MT-support-30-min-call-0043",
    "Customer did not join video call. Attempted to call phone number - no answer."
)
```

---

## Integration with Other DocTypes

### MM Meeting Type (Parent Configuration)

**Relationship**: Many-to-One (many bookings use one meeting type)

**Integration Points**:
- Meeting type defines booking behavior:
  - Duration (copied to start/end calculation)
  - Location type (copied to booking)
  - Requires approval flag
  - Reminder schedule
- Meeting type must be active for new bookings
- Meeting type department determines which members can be assigned

### MM Department (via Meeting Type)

**Relationship**: Bookings are associated with departments through meeting types

**Flow**:
```
MM Department: "Support"
└── MM Meeting Type: "30-min Support Call"
    └── MM Meeting Booking: Customer booking assigned to support member
```

**Integration Points**:
- Department assignment algorithm (Round Robin, Least Busy) determines which member is assigned
- Department members are eligible for assignment
- Department leader receives notifications for bookings

### MM Calendar Integration & MM Calendar Event Sync

**Relationship**: Bookings create/link to calendar events

**Flow**:
```
MM Meeting Booking: "Customer Support Call"
├── Creates event in Sarah's Google Calendar
│   └── MM Calendar Event Sync (linked)
└── Creates event in Mike's Outlook Calendar (if co-host)
    └── MM Calendar Event Sync (linked)
```

**Integration Points**:
- On booking creation/confirmation: Create calendar events in assigned users' calendars
- On booking reschedule: Update calendar events
- On booking cancellation: Delete calendar events
- On reassignment: Delete old user's event, create new user's event

### MM User Settings & MM User Availability Rule

**Relationship**: Bookings respect user availability constraints

**Availability Check Process**:
1. Get user's MM User Settings (working hours)
2. Get user's MM User Availability Rule (buffer times, booking limits, constraints)
3. Get user's MM User Date Overrides (specific date exceptions)
4. Get user's MM Calendar Event Sync (external calendar busy times)
5. Calculate available time slots
6. Only allow booking if slot is available

**Validation Integration**:
- `validate_timing()` checks `max_days_advance` and `min_notice_hours` from availability rule
- Assignment algorithm excludes users who don't meet these constraints

---

## API Endpoints

### Public Booking APIs

#### 1. Create Customer Booking

```python
@frappe.whitelist(allow_guest=True)
def create_customer_booking(meeting_type, start_datetime, end_datetime, customer_details):
    """
    Create customer booking via public API

    Args:
        meeting_type: MM Meeting Type name
        start_datetime: Booking start time
        end_datetime: Booking end time
        customer_details: Dict with name, email, phone, notes

    Returns:
        dict: {"booking_name": "...", "booking_reference": "...", "status": "..."}
    """
    pass
```

#### 2. Cancel Booking

```python
@frappe.whitelist(allow_guest=True)
def cancel_booking(booking_reference, cancellation_reason=""):
    """
    Cancel booking using customer booking reference

    Args:
        booking_reference: Unique booking reference (e.g., BK-A7F92K1X)
        cancellation_reason: Reason for cancellation

    Returns:
        dict: {"status": "cancelled", "message": "..."}
    """
    pass
```

### Internal APIs

#### 3. Reassign Booking

```python
@frappe.whitelist()
def reassign_booking(booking_name, new_user, reassignment_reason=""):
    """
    Reassign booking to different user

    Args:
        booking_name: MM Meeting Booking name
        new_user: New assigned user email
        reassignment_reason: Reason for reassignment

    Returns:
        dict: {"status": "success", "new_assigned_user": "..."}
    """
    pass
```

#### 4. Approve/Reject Booking

```python
@frappe.whitelist()
def approve_reject_booking(booking_name, action, reason=""):
    """
    Approve or reject booking requiring approval

    Args:
        booking_name: MM Meeting Booking name
        action: "approve" or "reject"
        reason: Reason (required for reject)

    Returns:
        dict: {"status": "approved/rejected", "booking_status": "..."}
    """
    pass
```

#### 5. Get User's Bookings

```python
@frappe.whitelist()
def get_user_bookings(user=None, start_date=None, end_date=None, status=None):
    """
    Get bookings assigned to a user

    Args:
        user: User email (default: current user)
        start_date: Start of date range
        end_date: End of date range
        status: Filter by status

    Returns:
        list: Bookings with details
    """
    pass
```

---

## Permissions

| Role | Create | Read | Write | Delete | Notes |
|------|--------|------|-------|--------|-------|
| System Manager | ✅ | ✅ | ✅ | ✅ | Full access to all bookings |
| MM Department Leader | ✅ | ✅ | ✅ | ❌ | Can create, view, and edit bookings for their department |
| MM Department Member | ❌ | ✅* | ✅* | ❌ | Can view and edit only their assigned bookings |
| Customer (Guest) | ✅** | ✅** | ❌ | ❌ | Can create bookings via public API, view own bookings via reference |

*Requires user-level permissions (see own bookings only)
**Via public API with booking reference

**Recommended User-Level Permissions**:
```python
# Department members see bookings assigned to them
frappe.permissions.add_user_permission("MM Meeting Booking", booking_name, user_email)

# Department leaders see all bookings for their department's meeting types
frappe.permissions.add_user_permission("MM Meeting Type", meeting_type_name, leader_email)
```

---

## Database Schema

### Indexes (Recommended)

```sql
-- Index for finding bookings by meeting type
CREATE INDEX idx_meeting_type ON `tabMM Meeting Booking` (meeting_type, booking_status);

-- Index for finding bookings by date range
CREATE INDEX idx_datetime_range ON `tabMM Meeting Booking` (start_datetime, end_datetime);

-- Index for finding bookings by customer email
CREATE INDEX idx_customer_email ON `tabMM Meeting Booking` (customer_email, booking_status);

-- Index for finding bookings by booking reference (customer lookup)
CREATE UNIQUE INDEX idx_booking_reference ON `tabMM Meeting Booking` (booking_reference);

-- Index for finding bookings by status
CREATE INDEX idx_booking_status ON `tabMM Meeting Booking` (booking_status, booking_date);

-- Index for finding bookings requiring approval
CREATE INDEX idx_approval ON `tabMM Meeting Booking` (requires_approval, approval_status);

-- Index for calendar sync lookup
CREATE INDEX idx_calendar_sync ON `tabMM Meeting Booking` (calendar_event_synced, calendar_event);

-- Child table indexes
CREATE INDEX idx_assigned_user ON `tabMM Meeting Booking Assigned User` (user, parent);
CREATE INDEX idx_participant_email ON `tabMM Meeting Booking Participant` (email, parent);
```

---

## Testing Checklist

### Unit Tests

- [ ] **Test meeting type validation**: Create booking with inactive meeting type (should fail)
- [ ] **Test is_internal flag validation**: Internal booking with public-only meeting type (should fail)
- [ ] **Test timing validation**: End before start (should fail), booking in past (should fail for new)
- [ ] **Test advance booking limits**: Booking beyond max_days_advance (should fail)
- [ ] **Test minimum notice**: Booking within min_notice_hours (should fail)
- [ ] **Test customer details validation**: Invalid email, invalid phone (should fail)
- [ ] **Test assigned users validation**: No assigned users (should fail), duplicate users (should fail)
- [ ] **Test primary host requirement**: No primary host (should fail)
- [ ] **Test participants validation**: Duplicate emails (should fail), invalid email (should fail)
- [ ] **Test approval workflow**: Approval without rejection reason (should allow), rejection without reason (should fail)
- [ ] **Test status validation**: Mark future booking as completed/no-show (should fail)
- [ ] **Test booking reference generation**: Verify unique 8-character reference created

### Integration Tests

- [ ] **Test customer booking flow**: Create booking via public API, verify assignment, verify emails sent
- [ ] **Test internal meeting creation**: Create internal meeting, verify no customer fields required
- [ ] **Test approval flow**: Create booking requiring approval, approve, verify status changes
- [ ] **Test rejection flow**: Reject booking, verify cancellation, verify customer notified
- [ ] **Test reassignment**: Reassign booking, verify assignment_history updated, verify emails sent
- [ ] **Test cancellation**: Cancel booking, verify calendar event deleted, verify emails sent
- [ ] **Test calendar sync**: Create booking, verify calendar event created, verify external_calendar_link set
- [ ] **Test status transitions**: Move through all statuses, verify history tracking works
- [ ] **Test no-show marking**: Mark past booking as no-show, verify validation for future bookings
- [ ] **Test reminder sending**: Trigger reminders, verify reminders_sent JSON updated

### Manual Tests

- [ ] **Test public booking page**: Complete end-to-end booking flow as customer
- [ ] **Test drag-and-drop reassignment**: Reassign booking in calendar view
- [ ] **Test approval workflow**: Approve and reject bookings from department leader account
- [ ] **Test email notifications**: Verify all emails sent (confirmation, reminder, cancellation, reassignment)
- [ ] **Test calendar integration**: Verify events appear in Google/Outlook calendars
- [ ] **Test booking reference lookup**: Use booking reference to view/cancel booking
- [ ] **Test history tracking**: Make various changes, verify complete audit trail

---

## Best Practices

### For Booking Creation

1. **Always Validate Availability First**:
   - Check user's working hours
   - Check user's availability rules
   - Check user's date overrides
   - Check user's external calendar events
   - Only create booking if all checks pass

2. **Use Assignment Algorithms**:
   - Don't manually assign unless required
   - Use department's assignment algorithm (Round Robin, Least Busy)
   - Respect user booking limits (max_bookings_per_day/week)

3. **Provide Complete Customer Details**:
   - Always collect name and email (minimum)
   - Phone number highly recommended for no-show follow-up
   - Customer notes help provide better service

4. **Set Appropriate Location Type**:
   - Always provide `video_meeting_url` for Video Call
   - Always provide `meeting_location` for Physical Location
   - Include phone number in description for Phone Call

### For Booking Management

1. **Track All Changes in History**:
   - Use `add_history_entry()` for significant events
   - Include descriptive event_description
   - Always set event_by for accountability

2. **Handle Reassignments Carefully**:
   - Check new user's availability before reassigning
   - Provide reassignment reason
   - Send notifications to all parties (customer, old user, new user)
   - Update calendar events immediately

3. **Approval Workflow Best Practices**:
   - Always provide rejection_reason for rejected bookings
   - Approve/reject promptly (don't leave customers waiting)
   - Consider auto-approval for low-risk meeting types

4. **Status Management**:
   - Only mark as Completed/No-Show after meeting time passes
   - Always provide cancellation_reason for cancelled bookings
   - Use Rescheduled status with link to new booking

### For Calendar Sync

1. **Ensure Calendar Integration Active**:
   - Verify assigned users have active calendar integrations
   - Check calendar_event_synced flag after creation
   - Monitor sync failures and retry

2. **Handle Sync Errors Gracefully**:
   - Don't block booking creation on sync failure
   - Log sync errors for later retry
   - Notify admins of repeated sync failures

3. **Maintain Event Links**:
   - Always link booking to calendar event (calendar_event field)
   - Store external_calendar_link for easy access
   - Update links when events are rescheduled

### For Performance

1. **Use Indexes Effectively**:
   - Query by indexed fields (meeting_type, start_datetime, booking_status)
   - Avoid full table scans
   - Use date range filters in queries

2. **Batch Operations**:
   - Send reminder emails in batches
   - Bulk update statuses when appropriate
   - Use background jobs for heavy operations

3. **Cache Frequently Accessed Data**:
   - Cache meeting type configurations
   - Cache department member lists
   - Cache user availability rules (with short TTL)

---

## Known Limitations

1. **Booking Reference Uniqueness**: 8-character reference code provides 2.8 trillion combinations, but collisions are theoretically possible. System should validate uniqueness on generation.

2. **Multiple Primary Hosts**: System allows multiple primary hosts with only a warning. Some integrations may expect exactly one primary host.

3. **Timezone Handling**: All datetimes stored in UTC. Timezone conversion must be handled at query/display time. Mixed-timezone bookings can be confusing.

4. **Assignment History Retroactive**: Assignment history is only tracked via hooks. Assignments made before this feature was implemented have no history.

5. **Participant Response Tracking**: System stores response_status but doesn't actively sync with external calendar responses (accepted/declined in Google/Outlook).

6. **Rescheduling**: No built-in reschedule function. Must cancel and create new booking manually. Consider building dedicated reschedule API.

7. **Recurring Bookings**: No support for recurring meetings. Each occurrence must be created as separate booking.

8. **Conflict Detection Timing**: Availability checked at booking creation, but user might become unavailable between booking and meeting time.

---

## See Also

- [MM Meeting Type](../mm_meeting_type/README.md) - Meeting type configuration
- [MM Department](../mm_department/README.md) - Department management and assignment algorithms
- [MM Calendar Event Sync](../mm_calendar_event_sync/README.md) - Calendar synchronization
- [MM User Settings](../mm_user_settings/README.md) - User working hours
- [MM User Availability Rule](../mm_user_availability_rule/README.md) - Availability constraints
- [MM User Date Overrides](../mm_user_date_overrides/README.md) - Date-specific exceptions
- [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md) - Overall system architecture

---

## Contributing

When modifying this DocType:

1. **Adding Fields**:
   - Update field_order in JSON
   - Add validation in appropriate validate method
   - Update this README with field description
   - Add test cases

2. **Changing Validation Logic**:
   - Update validation methods
   - Document error messages in README
   - Update test cases
   - Consider backward compatibility

3. **Modifying Child Tables**:
   - Update child table JSON files
   - Update validation for child table data
   - Document changes in Child Table Structures section
   - Test parent-child relationship integrity

4. **Adding Status Values**:
   - Update booking_status Select options
   - Add validation for new status transitions
   - Update status change tracking logic
   - Document new status meaning and usage

5. **Enhancing History Tracking**:
   - Add new event_type values to booking_history
   - Use `add_history_entry()` consistently
   - Include descriptive event_description
   - Update history tracking documentation

---

**Last Updated**: 2025-12-08
**Version**: 1.0
**Maintainer**: Best Security Development Team
