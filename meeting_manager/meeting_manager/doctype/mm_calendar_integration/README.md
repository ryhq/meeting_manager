# MM Calendar Integration - DocType Documentation

## Overview

**MM Calendar Integration** is the bridge between the Meeting Manager system and external calendar services (Google Calendar, Outlook Calendar, and iCal). This DocType manages OAuth authentication, sync settings, and bidirectional calendar synchronization to ensure that bookings created in Meeting Manager appear in users' external calendars and that external events block availability in the booking system.

**Auto-naming Format**: `MM-CI-{user}-{####}`

Example: `MM-CI-administrator@example.com-0001`

## Business Context

From the [Meeting Manager Project Description](../../../Meeting_Manager_PD.md), calendar integration is essential for:

1. **Availability Accuracy**: External calendar events (personal appointments, existing meetings) should block availability in the Meeting Manager booking system
2. **Calendar Sync**: Meetings booked through Meeting Manager should automatically appear in users' external calendars (Google, Outlook, iCal)
3. **Conflict Prevention**: Before assigning a booking to a department member, the system checks their external calendar for conflicts
4. **User Convenience**: Users maintain a single source of truth for all their meetings across multiple systems

**Key Product Requirements** (Phase 2 & 4):
- Support for Google Calendar, Outlook Calendar, and iCal integrations
- OAuth 2.0 authentication for Google and Outlook
- Read-only sync from iCal feeds
- Bidirectional sync (read and write) for OAuth-based integrations
- Configurable sync frequency (5-1440 minutes)
- Automatic token refresh for expired OAuth tokens
- Primary calendar designation for availability checking

---

## Key Features

### 1. **Multi-Provider Support**
- **Google Calendar**: OAuth 2.0 integration with full read/write access
- **Outlook Calendar**: OAuth 2.0 integration with Microsoft Graph API
- **iCal**: Read-only sync from iCal feeds (Apple Calendar, other services)

### 2. **Authentication Management**
- Secure storage of OAuth tokens (encrypted Password fields)
- Automatic token expiry detection and warning
- Refresh token support for seamless re-authentication
- iCal URL support for read-only integrations

### 3. **Flexible Sync Configuration**
- **Sync Direction**: One-way (read-only) or Two-way (read & write)
- **Sync Window**: Configurable past (0-365 days) and future (1-730 days) sync ranges
- **Auto Sync**: Periodic automatic synchronization (5-1440 minutes interval)
- **Manual Sync**: On-demand sync capability

### 4. **Primary Calendar Designation**
- Mark one calendar per user as "primary" for availability checking
- Automatic unmarking of previous primary when a new one is set
- Only active calendars can be primary

### 5. **Sync Status Tracking**
- Real-time sync status (Pending, Success, Failed, In Progress)
- Last sync timestamp tracking
- Error log for troubleshooting failed syncs

---

## Field Reference

### Basic Information Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user` | Link (User) | Yes | User who owns this calendar integration |
| `integration_type` | Select | Yes | Type of calendar service: `Google Calendar`, `Outlook Calendar`, `iCal` |
| `integration_name` | Data | Yes | Friendly name (e.g., "Work Google Calendar", "Personal Outlook") |
| `is_active` | Check | No | Enable/disable this integration (default: 1) |
| `is_primary` | Check | No | Use as primary calendar for availability (default: 0) |
| `calendar_id` | Data | No | Calendar ID from external service (for OAuth types) |

### Authentication Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_token` | Password | Conditional* | OAuth 2.0 access token (encrypted) |
| `refresh_token` | Password | No | OAuth 2.0 refresh token for automatic renewal |
| `token_expiry` | Datetime | No | When the access token expires |

*Required for active Google/Outlook integrations

### iCal Settings Section

*Only visible when `integration_type == 'iCal'`*

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ical_url` | Data | Yes (for iCal) | iCal feed URL (must start with http://, https://, or webcal://) |

### Sync Settings Section

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sync_direction` | Select | Two-way (Read & Write) | `One-way (Read Only)` or `Two-way (Read & Write)` |
| `sync_past_days` | Int | 30 | Number of days in past to sync (0-365) |
| `sync_future_days` | Int | 90 | Number of days in future to sync (1-730) |
| `auto_sync_enabled` | Check | 1 | Enable automatic periodic syncing |
| `sync_interval_minutes` | Int | 15 | How often to sync (5-1440 minutes) |

### Sync Status Section

*Read-only fields managed by the system*

| Field | Type | Description |
|-------|------|-------------|
| `last_sync` | Datetime | Last successful sync timestamp |
| `sync_status` | Select | `Pending`, `Success`, `Failed`, `In Progress` |
| `sync_error_log` | Text | Error details from last sync attempt |

---

## Use Cases

### Use Case 1: Google Calendar Integration (Primary)

**Scenario**: Sarah, a support team member, integrates her work Google Calendar as her primary calendar.

```python
# Create Google Calendar integration
calendar = frappe.get_doc({
    "doctype": "MM Calendar Integration",
    "user": "sarah@bestsecurity.com",
    "integration_type": "Google Calendar",
    "integration_name": "Work Google Calendar",
    "is_active": 1,
    "is_primary": 1,  # This is her primary calendar for availability
    "calendar_id": "sarah@bestsecurity.com",
    "access_token": "ya29.a0AfH6SMBx...",  # From OAuth flow
    "refresh_token": "1//0gHYqJ...",
    "token_expiry": "2025-12-08 14:30:00",
    "sync_direction": "Two-way (Read & Write)",
    "sync_past_days": 7,
    "sync_future_days": 60,
    "auto_sync_enabled": 1,
    "sync_interval_minutes": 15
})
calendar.insert()
```

**Result**:
- Sarah's Google Calendar events appear as busy times in Meeting Manager
- Bookings assigned to Sarah are automatically created in her Google Calendar
- System syncs every 15 minutes
- If another calendar was primary, it's automatically unmarked

### Use Case 2: Personal Outlook Calendar (Secondary)

**Scenario**: Sarah also adds her personal Outlook calendar to block personal appointments, but not as primary.

```python
# Add secondary Outlook calendar
outlook = frappe.get_doc({
    "doctype": "MM Calendar Integration",
    "user": "sarah@bestsecurity.com",
    "integration_type": "Outlook Calendar",
    "integration_name": "Personal Outlook",
    "is_active": 1,
    "is_primary": 0,  # Not primary - work calendar is primary
    "calendar_id": "sarah.personal@outlook.com",
    "access_token": "EwBoA8l6BAA...",
    "refresh_token": "M.R3_BAY.-...",
    "token_expiry": "2025-12-08 15:00:00",
    "sync_direction": "One-way (Read Only)",  # Only read from personal calendar
    "sync_past_days": 0,  # No past sync needed
    "sync_future_days": 90,
    "auto_sync_enabled": 1,
    "sync_interval_minutes": 30
})
outlook.insert()
```

**Result**:
- Personal Outlook events block Sarah's availability
- Meeting Manager bookings are NOT written to personal calendar
- System syncs every 30 minutes
- Work Google Calendar remains primary for writing events

### Use Case 3: iCal Feed (Read-Only)

**Scenario**: John uses Apple Calendar and wants to block his availability based on his iCal feed.

```python
# Add iCal integration
ical = frappe.get_doc({
    "doctype": "MM Calendar Integration",
    "user": "john@bestsecurity.com",
    "integration_type": "iCal",
    "integration_name": "Apple Calendar",
    "is_active": 1,
    "is_primary": 0,  # iCal is read-only, so not suitable as primary
    "ical_url": "https://calendar.google.com/calendar/ical/john%40bestsecurity.com/private-abc123/basic.ics",
    "sync_direction": "One-way (Read Only)",  # iCal is always read-only
    "sync_past_days": 30,
    "sync_future_days": 90,
    "auto_sync_enabled": 1,
    "sync_interval_minutes": 60  # Less frequent for read-only
})
ical.insert()
```

**Result**:
- System reads events from iCal feed and blocks availability
- Events are NOT written to iCal (not supported)
- Warning displayed if user tries to set two-way sync
- System syncs every 60 minutes

### Use Case 4: Expired Token Handling

**Scenario**: Sarah's Google Calendar access token expires. System detects and alerts.

```python
# Get expired integration
calendar = frappe.get_doc("MM Calendar Integration", "MM-CI-sarah@bestsecurity.com-0001")

# Check token expiry (automatic validation)
# If token_expiry < now_datetime() and is_active == 1:
#   System shows warning: "Access Token has expired on 2025-12-08 14:30:00. Please re-authenticate."

# Check last sync status
if calendar.sync_status == "Failed":
    print(f"Last sync failed: {calendar.sync_error_log}")
    # Example error: "401 Unauthorized - Access token expired"

# User re-authenticates through OAuth flow
calendar.access_token = "ya29.a0AfH6SMBx_NEW_TOKEN..."
calendar.token_expiry = "2025-12-09 14:30:00"
calendar.sync_status = "Pending"
calendar.save()
```

**Result**:
- System detects expired token during validation
- Alert shown to user with red indicator
- Sync status set to "Failed" with error details
- User can re-authenticate and update tokens

### Use Case 5: Primary Calendar Switch

**Scenario**: Sarah decides to make her Outlook calendar primary instead of Google.

```python
# Get Outlook calendar
outlook = frappe.get_doc("MM Calendar Integration", "MM-CI-sarah@bestsecurity.com-0002")

# Set as primary
outlook.is_primary = 1
outlook.save()

# System automatically:
# 1. Validates that no other active primary exists for this user
# 2. On save (on_update hook), unmarks Google calendar as primary
# 3. Shows message: "Unmarked 'Work Google Calendar' as primary calendar."
```

**Result**:
- Outlook becomes primary calendar for availability
- Google calendar is automatically unmarked as primary
- User receives confirmation message
- Future bookings are written to Outlook

---

## Validation Rules

The DocType includes comprehensive validation to ensure data integrity and proper configuration:

### 1. User Validation (`validate_user_exists`)

**Validates**:
- User field is not empty
- User exists in the User DocType

**Error Messages**:
- `"User is required."`
- `"User '{user}' does not exist."`

### 2. Integration Name Uniqueness (`validate_integration_name_unique`)

**Validates**:
- Integration name is provided
- Integration name is unique per user (case-sensitive)

**Error Messages**:
- `"Integration Name is required."`
- `"Integration Name '{name}' already exists for user '{user}'. Please use a unique name for each integration."`

**Example**:
- ✅ Valid: User has "Work Google Calendar" and "Personal Outlook"
- ❌ Invalid: User tries to create two integrations both named "Work Google Calendar"

### 3. Integration Type Requirements (`validate_integration_type_requirements`)

**Validates**:

**For iCal**:
- `ical_url` is required
- URL must start with `http://`, `https://`, or `webcal://`
- Clears OAuth fields (access_token, refresh_token, token_expiry)
- Warns if sync direction is "Two-way" (iCal typically read-only)

**For Google Calendar / Outlook Calendar**:
- `access_token` is required (if integration is active)
- Clears `ical_url`
- Warns if `calendar_id` is not provided (will use primary calendar by default)

**Error Messages**:
- `"Integration Type is required."`
- `"iCal URL is required for iCal integration type."`
- `"iCal URL must start with http://, https://, or webcal://"`
- `"{type} requires an Access Token. Please authenticate with {type} first."`

**Warnings**:
- `"Warning: iCal integrations typically support only one-way (read-only) sync. Two-way sync may not work as expected."`
- `"Calendar ID is recommended for {type} integration. Without it, the primary calendar will be used by default."`

### 4. Sync Settings Validation (`validate_sync_settings`)

**Validates**:

**sync_past_days**:
- Must be >= 0 (use 0 for no past sync)
- Must be <= 365 days (1 year)

**sync_future_days**:
- Must be > 0
- Must be <= 730 days (2 years)

**sync_interval_minutes**:
- Must be >= 5 minutes (avoid excessive API calls)
- Must be <= 1440 minutes (24 hours)

**Error Messages**:
- `"Sync Past Days cannot be negative. Use 0 for no past sync."`
- `"Sync Past Days cannot exceed 365 days (1 year)."`
- `"Sync Future Days must be greater than 0."`
- `"Sync Future Days cannot exceed 730 days (2 years)."`
- `"Sync Interval cannot be less than 5 minutes to avoid excessive API calls."`
- `"Sync Interval cannot exceed 1440 minutes (24 hours)."`

### 5. Token Expiry Validation (`validate_token_expiry`)

**Validates**:
- If `token_expiry` is set, it must be valid datetime format
- If token has expired and integration is active, shows warning

**Error Messages**:
- `"Invalid Token Expiry datetime format."`

**Warnings**:
- `"Warning: Access Token has expired on {expiry}. Please re-authenticate to continue syncing."` (red indicator)

### 6. Primary Calendar Validation (`validate_primary_calendar`)

**Validates**:
- Only one active primary calendar per user
- Checks existing primary calendars (excluding current document if updating)

**Error Messages**:
- `"A primary calendar integration already exists for user '{user}': '{name}'. Please uncheck 'Is Primary Calendar' on the existing integration first, or uncheck it on this integration."`

### 7. Auto-Unmarking Primary Calendars (`unmark_other_primary_calendars`)

**Behavior** (on_update hook):
- If this calendar is marked as primary and active
- Automatically unmarks all other calendars for this user as primary
- Shows confirmation message for each unmarked calendar

**Messages**:
- `"Unmarked '{name}' as primary calendar."` (alert)

---

## Usage Examples

### Example 1: Creating Google Calendar Integration

```python
import frappe

# Step 1: User authenticates via OAuth (handled by frontend)
# This returns access_token, refresh_token, and expiry

# Step 2: Create integration record
calendar = frappe.get_doc({
    "doctype": "MM Calendar Integration",
    "user": "john@bestsecurity.com",
    "integration_type": "Google Calendar",
    "integration_name": "Work Google Calendar",
    "is_active": 1,
    "is_primary": 1,
    "calendar_id": "john@bestsecurity.com",
    "access_token": "ya29.a0AfH6SMBx...",
    "refresh_token": "1//0gHYqJ...",
    "token_expiry": "2025-12-08 14:30:00",
    "sync_direction": "Two-way (Read & Write)",
    "sync_past_days": 7,
    "sync_future_days": 90,
    "auto_sync_enabled": 1,
    "sync_interval_minutes": 15
})

try:
    calendar.insert()
    print(f"Calendar integration created: {calendar.name}")
except Exception as e:
    print(f"Error: {str(e)}")
```

### Example 2: Querying User's Active Calendars

```python
import frappe

def get_user_active_calendars(user):
    """Get all active calendar integrations for a user"""
    calendars = frappe.get_all(
        "MM Calendar Integration",
        filters={
            "user": user,
            "is_active": 1
        },
        fields=[
            "name",
            "integration_type",
            "integration_name",
            "is_primary",
            "sync_status",
            "last_sync"
        ],
        order_by="is_primary desc, creation desc"
    )
    return calendars

# Usage
user_calendars = get_user_active_calendars("sarah@bestsecurity.com")
for cal in user_calendars:
    print(f"{cal.integration_name} ({cal.integration_type}) - Primary: {cal.is_primary}")
```

### Example 3: Getting Primary Calendar

```python
import frappe

def get_primary_calendar(user):
    """Get the primary calendar integration for a user"""
    primary = frappe.get_value(
        "MM Calendar Integration",
        filters={
            "user": user,
            "is_primary": 1,
            "is_active": 1
        },
        fieldname=["name", "integration_type", "calendar_id", "sync_direction"],
        as_dict=True
    )

    if not primary:
        frappe.log_error(f"No primary calendar found for user {user}")
        return None

    return primary

# Usage
primary_cal = get_primary_calendar("john@bestsecurity.com")
if primary_cal:
    print(f"Primary calendar: {primary_cal.name} ({primary_cal.integration_type})")
```

### Example 4: Checking Sync Status

```python
import frappe
from frappe.utils import now_datetime, time_diff_in_seconds

def check_sync_status(calendar_name):
    """Check if calendar needs syncing"""
    calendar = frappe.get_doc("MM Calendar Integration", calendar_name)

    if not calendar.is_active:
        return {"status": "inactive", "message": "Calendar integration is inactive"}

    if not calendar.auto_sync_enabled:
        return {"status": "manual", "message": "Auto-sync is disabled"}

    if calendar.sync_status == "In Progress":
        return {"status": "syncing", "message": "Sync currently in progress"}

    if calendar.sync_status == "Failed":
        return {
            "status": "failed",
            "message": f"Last sync failed: {calendar.sync_error_log}"
        }

    # Check if sync is due
    if calendar.last_sync:
        last_sync = calendar.last_sync
        now = now_datetime()
        seconds_since_sync = time_diff_in_seconds(now, last_sync)
        interval_seconds = calendar.sync_interval_minutes * 60

        if seconds_since_sync >= interval_seconds:
            return {
                "status": "due",
                "message": f"Sync overdue by {int((seconds_since_sync - interval_seconds) / 60)} minutes"
            }
        else:
            return {
                "status": "ok",
                "message": f"Next sync in {int((interval_seconds - seconds_since_sync) / 60)} minutes"
            }
    else:
        return {"status": "pending", "message": "Never synced, initial sync pending"}

# Usage
status = check_sync_status("MM-CI-sarah@bestsecurity.com-0001")
print(status["message"])
```

### Example 5: Updating Access Token

```python
import frappe
from frappe.utils import add_to_date, now_datetime

def update_access_token(calendar_name, new_access_token, expires_in_seconds):
    """Update access token after refresh"""
    calendar = frappe.get_doc("MM Calendar Integration", calendar_name)

    # Update token
    calendar.access_token = new_access_token

    # Calculate new expiry
    calendar.token_expiry = add_to_date(now_datetime(), seconds=expires_in_seconds)

    # Reset sync status
    calendar.sync_status = "Pending"
    calendar.sync_error_log = None

    calendar.save(ignore_permissions=True)

    frappe.msgprint(f"Access token updated. New expiry: {calendar.token_expiry}")

# Usage (after OAuth token refresh)
update_access_token(
    "MM-CI-john@bestsecurity.com-0001",
    "ya29.a0AfH6SMBx_NEW_TOKEN...",
    3600  # Expires in 1 hour
)
```

---

## Integration with Other DocTypes

### MM Calendar Event Sync

**Relationship**: Child table/linked DocType

**Purpose**: Tracks individual events synced from external calendars

**Flow**:
```
MM Calendar Integration (Parent)
└── MM Calendar Event Sync (Child records)
    ├── Event 1: "Team Meeting" (2025-12-08 10:00)
    ├── Event 2: "Dentist Appointment" (2025-12-10 14:00)
    └── Event 3: "Project Review" (2025-12-12 09:00)
```

**Integration Points**:
- Each synced event references its parent `MM Calendar Integration`
- Events are used to calculate user availability
- Sync service creates/updates/deletes event records based on external calendar changes

### MM User Settings

**Relationship**: Same user link

**Purpose**: Calendar integration complements working hours settings

**Availability Calculation Hierarchy**:
```
1. MM User Settings: Working hours (e.g., Mon-Fri 9-5)
2. MM User Availability Rule: Buffer times, booking limits
3. MM User Date Overrides: Specific date exceptions
4. MM Calendar Integration: External calendar events (blocks availability)
```

### MM Meeting Booking

**Relationship**: Calendar integration provides availability data for booking assignment

**Flow**:
1. Customer creates booking request
2. System checks department member availability:
   - Working hours (MM User Settings)
   - Availability rules (MM User Availability Rule)
   - Date overrides (MM User Date Overrides)
   - **External calendar events (MM Calendar Integration)**
3. Assign to available member
4. Write booking to member's primary calendar (if two-way sync enabled)

---

## Sync Architecture

### Sync Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Sync Process Flow                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Scheduler Job   │ (Runs every 5 minutes)
│  or Manual Sync  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  1. Get Due Calendar Integrations                │
│     - is_active = 1                              │
│     - auto_sync_enabled = 1                      │
│     - (now - last_sync) >= sync_interval_minutes │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  2. For Each Calendar Integration:               │
│     - Set sync_status = "In Progress"            │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  3. Check Token Validity                         │
│     - If expired, attempt refresh                │
│     - If refresh fails, set status = "Failed"    │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  4. Fetch Events from External Calendar          │
│     - Date range: (now - sync_past_days) to      │
│                   (now + sync_future_days)       │
│     - Use Calendar API (Google/Outlook/iCal)     │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  5. Compare with MM Calendar Event Sync          │
│     - Create new events                          │
│     - Update modified events                     │
│     - Delete removed events                      │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  6. Write Local Events to External Calendar      │
│     (Only if sync_direction = "Two-way")         │
│     - Get new MM Meeting Bookings since last sync│
│     - Create events in external calendar         │
│     - Store external event ID for future updates │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  7. Update Sync Status                           │
│     - last_sync = now                            │
│     - sync_status = "Success" or "Failed"        │
│     - sync_error_log = error details (if failed) │
└──────────────────────────────────────────────────┘
```

---

## Permissions

| Role | Create | Read | Write | Delete | Notes |
|------|--------|------|-------|--------|-------|
| System Manager | ✅ | ✅ | ✅ | ✅ | Full access to all calendar integrations |
| All | ❌ | ✅ | ❌ | ❌ | Read-only access (can view their own) |

**User-Level Permissions Recommended**:
```python
# Users should only see their own calendar integrations
frappe.permissions.add_user_permission("MM Calendar Integration", calendar_name, user_email)
```

---

## Database Schema

### Indexes (Recommended)

```sql
-- Index for finding user's active calendars
CREATE INDEX idx_user_active ON `tabMM Calendar Integration` (user, is_active);

-- Index for finding primary calendar per user
CREATE INDEX idx_user_primary ON `tabMM Calendar Integration` (user, is_primary, is_active);

-- Index for finding due syncs
CREATE INDEX idx_sync_due ON `tabMM Calendar Integration` (is_active, auto_sync_enabled, last_sync);

-- Index for integration name uniqueness per user
CREATE UNIQUE INDEX idx_user_integration_name ON `tabMM Calendar Integration` (user, integration_name);
```

---

## API Endpoints

### Internal APIs

#### 1. Initiate OAuth Flow

```python
@frappe.whitelist()
def initiate_oauth_flow(integration_type, redirect_uri):
    """
    Start OAuth authentication flow for Google/Outlook

    Args:
        integration_type: "Google Calendar" or "Outlook Calendar"
        redirect_uri: URL to redirect after authentication

    Returns:
        dict: {"auth_url": "https://..."}
    """
    pass
```

#### 2. Handle OAuth Callback

```python
@frappe.whitelist()
def handle_oauth_callback(code, state, integration_type):
    """
    Handle OAuth callback and exchange code for tokens

    Args:
        code: Authorization code from OAuth provider
        state: State parameter for CSRF protection
        integration_type: "Google Calendar" or "Outlook Calendar"

    Returns:
        dict: {
            "access_token": "...",
            "refresh_token": "...",
            "expires_in": 3600,
            "calendar_id": "user@example.com"
        }
    """
    pass
```

#### 3. Trigger Manual Sync

```python
@frappe.whitelist()
def trigger_manual_sync(calendar_integration_name):
    """
    Manually trigger a sync for a specific calendar

    Args:
        calendar_integration_name: Name of MM Calendar Integration

    Returns:
        dict: {"status": "success", "message": "Sync completed"}
    """
    pass
```

#### 4. Refresh Access Token

```python
@frappe.whitelist()
def refresh_access_token(calendar_integration_name):
    """
    Refresh expired access token using refresh token

    Args:
        calendar_integration_name: Name of MM Calendar Integration

    Returns:
        dict: {
            "new_access_token": "...",
            "expires_in": 3600,
            "status": "success"
        }
    """
    pass
```

---

## Testing Checklist

### Unit Tests

- [ ] **Test user existence validation**: Create integration with non-existent user (should fail)
- [ ] **Test integration name uniqueness**: Create two integrations with same name for same user (should fail)
- [ ] **Test iCal URL validation**: Test invalid URLs (no protocol, invalid format)
- [ ] **Test OAuth token requirement**: Create active Google/Outlook integration without access_token (should fail)
- [ ] **Test sync settings ranges**: Test negative sync_past_days, excessive sync_future_days
- [ ] **Test sync interval bounds**: Test sync_interval_minutes < 5 and > 1440 (should fail)
- [ ] **Test token expiry validation**: Set expired token_expiry on active integration (should warn)
- [ ] **Test primary calendar enforcement**: Create two primary calendars for same user (should fail)
- [ ] **Test auto-unmarking primary**: Set calendar as primary, verify others are unmarked

### Integration Tests

- [ ] **Test Google Calendar OAuth flow**: Complete authentication and create integration
- [ ] **Test Outlook Calendar OAuth flow**: Complete authentication and create integration
- [ ] **Test iCal feed parsing**: Add iCal URL and verify events are synced
- [ ] **Test two-way sync**: Create booking in Meeting Manager, verify it appears in external calendar
- [ ] **Test one-way sync**: Create event in external calendar, verify it blocks availability
- [ ] **Test token refresh**: Simulate expired token, verify automatic refresh works
- [ ] **Test sync error handling**: Simulate API failure, verify error log is populated
- [ ] **Test primary calendar switch**: Change primary calendar, verify availability calculation uses new primary
- [ ] **Test inactive calendar**: Deactivate integration, verify it's excluded from sync
- [ ] **Test multiple calendars**: Create Google + Outlook for same user, verify both sync independently

### Manual Tests

- [ ] **User Permissions**: Verify users can only see their own calendar integrations
- [ ] **OAuth Security**: Verify tokens are encrypted in database
- [ ] **Sync Performance**: Verify sync completes within reasonable time (< 30 seconds for 100 events)
- [ ] **Conflict Detection**: Create overlapping events in external calendar, verify availability is blocked
- [ ] **Calendar ID Handling**: Test with and without calendar_id (should use primary calendar if not provided)

---

## Best Practices

### For Administrators

1. **Primary Calendar Strategy**:
   - Use two-way sync calendar as primary (Google or Outlook)
   - Use one-way sync for secondary calendars (personal, iCal feeds)
   - Only one primary per user

2. **Sync Interval Tuning**:
   - Start with 15 minutes for most users
   - Reduce to 5 minutes for high-priority users (executives)
   - Increase to 60 minutes for read-only calendars (iCal feeds)

3. **Sync Window Configuration**:
   - `sync_past_days`: 7-30 days (enough to update recent events)
   - `sync_future_days`: 60-90 days (matches typical booking horizon)
   - Adjust based on API rate limits

4. **Token Management**:
   - Monitor `token_expiry` dates
   - Set up alerts for tokens expiring within 7 days
   - Use refresh tokens for automatic renewal

5. **Error Monitoring**:
   - Check `sync_status = "Failed"` daily
   - Review `sync_error_log` for patterns
   - Set up email notifications for repeated failures

### For Users

1. **Integration Setup**:
   - Use work calendar as primary (two-way sync)
   - Add personal calendar as secondary (one-way sync)
   - Use descriptive integration names

2. **Maintaining Accuracy**:
   - Keep external calendar up to date
   - Don't delete events created by Meeting Manager
   - Use consistent timezone settings across systems

3. **Troubleshooting**:
   - Check sync status regularly
   - Re-authenticate if sync fails repeatedly
   - Contact admin if errors persist

---

## Known Limitations

1. **OAuth Token Expiry**: Tokens typically expire after 1 hour and require refresh. If refresh token is invalid, user must re-authenticate.

2. **iCal Limitations**: iCal feeds are read-only. Two-way sync is not supported regardless of `sync_direction` setting.

3. **Sync Latency**: Events may take up to `sync_interval_minutes` to sync. Not real-time.

4. **API Rate Limits**: Google and Outlook have API rate limits. Excessive sync frequency may result in throttling.

5. **Calendar ID Discovery**: For Google/Outlook, if `calendar_id` is not provided, system uses primary calendar. This may not be the intended calendar for some users.

6. **Timezone Handling**: System assumes all events use the user's timezone. Events in different timezones may require manual adjustment.

7. **Deleted Event Handling**: If an event is deleted in external calendar, it may take one sync cycle to reflect in Meeting Manager availability.

8. **OAuth Redirect URI**: OAuth flow requires publicly accessible redirect URI. Localhost development may require ngrok or similar tunneling.

---

## See Also

- [MM Calendar Event Sync](../mm_calendar_event_sync/README.md) - Individual event sync records
- [MM User Settings](../mm_user_settings/README.md) - Working hours configuration
- [MM User Availability Rule](../mm_user_availability_rule/README.md) - Availability constraints
- [MM Meeting Booking](../mm_meeting_booking/README.md) - Booking system that uses calendar data
- [Meeting Manager Project Description](../../../Meeting_Manager_PD.md) - Overall system architecture

---

## Contributing

When modifying this DocType:

1. **Adding New Integration Type**:
   - Update `integration_type` Select options
   - Add validation logic in `validate_integration_type_requirements`
   - Implement sync service for new provider

2. **Changing Validation Rules**:
   - Update validation methods
   - Update this README with new error messages
   - Add test cases for new validations

3. **Adding Sync Features**:
   - Update sync service implementation
   - Add new fields to track sync metadata
   - Update sync status options if needed

4. **Modifying Token Handling**:
   - Ensure tokens remain encrypted (Password field type)
   - Update refresh logic in sync service
   - Test token expiry handling

---

**Last Updated**: 2025-12-08
**Version**: 1.0
**Maintainer**: Best Security Development Team
