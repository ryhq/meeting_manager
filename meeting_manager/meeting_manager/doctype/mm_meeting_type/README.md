# MM Meeting Type DocType

## Overview

The **MM Meeting Type** DocType defines the types of meetings that departments offer to customers and internal staff. Each meeting type specifies duration, location settings, availability flags (public/internal), approval requirements, and automated reminder schedules. This is a key DocType that bridges departments with the booking system.

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md):

> **MM Department Meeting Type** - Meeting types offered by a specific department including duration, location type, video platform, approval requirements, public/internal availability flags, and reminder schedules.

Meeting types are what customers see and select on public booking pages. A department might offer "30-min Support Call", "Technical Consultation", "Demo Session", etc. Each type has specific settings that determine how bookings are created and managed.

## Key Features

### 1. Department Association
- Each meeting type belongs to one department
- Department must be active
- Automatically inherits department timezone and assignment algorithm

### 2. Meeting Configuration
- **Name**: Human-readable name (e.g., "30-min Support Call")
- **Slug**: URL-friendly identifier (e.g., "30-min-support-call")
- **Duration**: Meeting length in minutes (15, 30, 45, 60, 90, 120, etc.)
- **Description**: Rich text explanation for customers

### 3. Availability Flags
- **Public**: Available for customer booking via public pages
- **Internal**: Available for internal meetings between employees
- Must have at least one flag enabled

### 4. Location Settings
- **Video Call**: Google Meet, Zoom, Microsoft Teams, Custom
- **Phone Call**: Phone-based meetings
- **Physical Location**: In-person meetings with address
- **Custom**: Other meeting formats

### 5. Booking Behavior
- **Requires Approval**: Manual approval before confirming customer bookings
- **Public Booking URL**: Auto-generated URL for direct booking

### 6. Reminder Schedule
- [MM Meeting Type Reminder](../mm_meeting_type_reminder/) child table
- Configure multiple reminders (24h, 1h, etc.)
- Email, SMS, or both notification types

### 7. Auto-Naming
Format: `MM-MT-{department}-{meeting_slug}`
Example: `MM-MT-support-30-min-call`

## Field Reference

| Field Name | Type | Required | Default | Description |
|------------|------|----------|---------|-------------|
| `department` | Link (MM Department) | Yes | - | Parent department offering this meeting |
| `meeting_name` | Data | Yes | - | Display name (e.g., "30-min Support Call") |
| `meeting_slug` | Data | Yes | - | URL-safe identifier (auto-cleaned) |
| `is_active` | Check | No | 1 | Enable/disable this meeting type |
| `duration` | Int | Yes | - | Duration in minutes (max 480) |
| `is_public` | Check | No | 1 | Available for public/customer booking |
| `is_internal` | Check | No | 0 | Available for internal meetings |
| `description` | Text Editor | No | - | Rich text description |
| `location_type` | Select | No | Video Call | Type of meeting location |
| `video_platform` | Select | No | - | Platform for video calls |
| `custom_location` | Small Text | No | - | Address or custom instructions |
| `requires_approval` | Check | No | 0 | Manual approval needed for customers |
| `public_booking_url` | Data | No (Read-only) | - | Auto-generated booking URL |
| `created_by` | Link (User) | No (Auto-set) | - | User who created this meeting type |
| `reminder_schedule` | Table | No | - | Child table: MM Meeting Type Reminder |

## Field Constraints

### Duration
- Must be > 0 minutes
- Maximum: 480 minutes (8 hours)
- **Error**: "Duration must be greater than 0 minutes."
- **Error**: "Duration cannot exceed 480 minutes (8 hours)."

### Availability Flags
- At least one must be checked: `is_public` OR `is_internal`
- **Error**: "At least one availability flag must be checked: 'Available for Public/Customer Booking' or 'Available for Internal Meetings'."

### Meeting Slug
- Automatically cleaned to URL-safe format
- Must be unique within the department
- Same cleaning rules as MM Department slug
- **Error**: "Meeting Slug '{slug}' already exists in department '{department}'. Please use a unique slug within this department."

## Use Cases & Examples

### Use Case 1: Standard Support Call

**Scenario**: 30-minute support call for customers, video-based, immediate approval.

```python
{
    "department": "support",
    "meeting_name": "30-min Support Call",
    "meeting_slug": "30-min-call",  # Auto-cleaned
    "is_active": 1,
    "duration": 30,
    "is_public": 1,  # Available to customers
    "is_internal": 0,  # Not for internal use
    "description": "<p>Quick support session to resolve your issues.</p>",
    "location_type": "Video Call",
    "video_platform": "Google Meet",
    "requires_approval": 0,  # Instant booking
    "reminder_schedule": [
        {"hours_before_meeting": 24, "notification_type": "Email", "is_active": 1},
        {"hours_before_meeting": 1, "notification_type": "Both", "is_active": 1}
    ]
}
```

**Generated URL**: `https://bestsecurity.local/book/support/30-min-call`

**Booking Flow**:
1. Customer visits URL
2. Selects date/time
3. Enters details
4. Booking instantly confirmed
5. Reminders sent 24h and 1h before

### Use Case 2: Executive Consultation (Requires Approval)

**Scenario**: High-value consultation requiring manual approval, longer duration.

```python
{
    "department": "sales",
    "meeting_name": "Executive Consultation",
    "meeting_slug": "executive-consultation",
    "is_active": 1,
    "duration": 90,  # 1.5 hours
    "is_public": 1,
    "is_internal": 0,
    "description": "<p>In-depth consultation with our senior executives about enterprise solutions.</p>",
    "location_type": "Video Call",
    "video_platform": "Zoom",
    "requires_approval": 1,  # Must be approved
    "reminder_schedule": [
        {"hours_before_meeting": 48, "notification_type": "Email", "is_active": 1},
        {"hours_before_meeting": 24, "notification_type": "Email", "is_active": 1},
        {"hours_before_meeting": 2, "notification_type": "Both", "is_active": 1}
    ]
}
```

**Booking Flow**:
1. Customer submits booking request
2. Booking status: "Pending"
3. Department leader reviews and approves
4. Status changes to "Confirmed"
5. Reminders sent at 48h, 24h, 2h before

### Use Case 3: Internal Team Meeting

**Scenario**: Internal meeting type for team standups, not visible to customers.

```python
{
    "department": "engineering",
    "meeting_name": "Team Standup",
    "meeting_slug": "team-standup",
    "is_active": 1,
    "duration": 15,  # Quick standup
    "is_public": 0,  # Not for customers
    "is_internal": 1,  # Only internal
    "description": "<p>Daily team standup meeting.</p>",
    "location_type": "Video Call",
    "video_platform": "Microsoft Teams",
    "requires_approval": 0,
    "reminder_schedule": [
        {"hours_before_meeting": 0.25, "notification_type": "Email", "is_active": 1}  # 15 min before
    ]
}
```

**Usage**:
- Only visible to internal users
- Not shown on public booking pages
- Used by managers to schedule team meetings
- No customer access

### Use Case 4: Physical Meeting

**Scenario**: In-person meeting at office location.

```python
{
    "department": "sales",
    "meeting_name": "Office Visit",
    "meeting_slug": "office-visit",
    "is_active": 1,
    "duration": 60,
    "is_public": 1,
    "is_internal": 0,
    "description": "<p>Visit our office for a face-to-face meeting.</p>",
    "location_type": "Physical Location",
    "video_platform": None,  # Not needed for physical
    "custom_location": "Best Security HQ\nMulvadvej 8A, 6000 Kolding, Denmark\nParking available at rear entrance",
    "requires_approval": 1,  # Verify availability of physical space
    "reminder_schedule": [
        {"hours_before_meeting": 24, "notification_type": "Both", "is_active": 1},
        {"hours_before_meeting": 2, "notification_type": "SMS", "is_active": 1}
    ]
}
```

### Use Case 5: Dual-Purpose Meeting Type

**Scenario**: Meeting type available for both customers and internal use.

```python
{
    "department": "training",
    "meeting_name": "Product Training Session",
    "meeting_slug": "product-training",
    "is_active": 1,
    "duration": 120,  # 2 hours
    "is_public": 1,  # Customers can book
    "is_internal": 1,  # Internal team can also use
    "description": "<p>Comprehensive product training covering all features.</p>",
    "location_type": "Video Call",
    "video_platform": "Zoom",
    "requires_approval": 0,
    "reminder_schedule": [
        {"hours_before_meeting": 72, "notification_type": "Email", "is_active": 1},
        {"hours_before_meeting": 24, "notification_type": "Email", "is_active": 1},
        {"hours_before_meeting": 1, "notification_type": "Both", "is_active": 1}
    ]
}
```

## Validation Rules

The DocType implements comprehensive validation in [mm_meeting_type.py](mm_meeting_type.py):

### 1. Created By Auto-Set (`set_created_by()`)
- Automatically sets `created_by` to current user on creation
- Only applies to new records

### 2. Department Validation (`validate_department_exists()`)
- Department field is required
- Department must exist
- Department must be active
- **Error**: "Department is required."
- **Error**: "Department '{department}' is not active. Please select an active department."

### 3. Meeting Slug Validation (`validate_meeting_slug()`)
- Automatically cleans slug to URL-safe format
- Must be unique within the department (not globally)
- Same cleaning process as MM Department:
  - Converts to lowercase
  - Replaces spaces with hyphens
  - Removes non-alphanumeric characters (except hyphens)
  - Removes consecutive hyphens
  - Removes leading/trailing hyphens

**Slug Cleaning Examples**:
```python
"30-min Call" → "30-min-call"
"Technical & Consultation" → "technical-consultation"
"Sales Demo!" → "sales-demo"
"  Team  --  Standup  " → "team-standup"
```

**Error Messages**:
- "Meeting Slug is required."
- "Meeting Slug must contain at least one letter or number."
- "Meeting Slug '{slug}' already exists in department '{department}'. Please use a unique slug within this department."

### 4. Availability Flags Validation (`validate_availability_flags()`)
- At least one of `is_public` or `is_internal` must be checked
- Prevents creating inaccessible meeting types
- **Error**: "At least one availability flag must be checked: 'Available for Public/Customer Booking' or 'Available for Internal Meetings'."

**Valid Combinations**:
```python
# Valid: Public only
is_public=1, is_internal=0  ✓

# Valid: Internal only
is_public=0, is_internal=1  ✓

# Valid: Both
is_public=1, is_internal=1  ✓

# Invalid: Neither
is_public=0, is_internal=0  ✗ ERROR
```

### 5. Duration Validation (`validate_duration()`)
- Must be > 0 minutes
- Maximum: 480 minutes (8 hours)
- **Error**: "Duration is required."
- **Error**: "Duration must be greater than 0 minutes."
- **Error**: "Duration cannot exceed 480 minutes (8 hours)."

### 6. Reminder Schedule Validation (`validate_reminder_schedule()`)
- Each reminder must have `hours_before_meeting` set
- Hours must be ≥ 0 (non-negative)
- Maximum: 720 hours (30 days)
- No duplicate reminder times allowed
- **Error**: "Hours Before Meeting is required for all reminder schedule entries."
- **Error**: "Hours Before Meeting cannot be negative."
- **Error**: "Hours Before Meeting cannot exceed 720 hours (30 days)."
- **Error**: "Duplicate reminder found for {hours} hours before meeting. Each reminder time must be unique."

**Valid Reminder Schedule**:
```python
[
    {"hours_before_meeting": 24, "notification_type": "Email"},
    {"hours_before_meeting": 1, "notification_type": "Both"}
]  ✓
```

**Invalid Reminder Schedule**:
```python
[
    {"hours_before_meeting": 24, "notification_type": "Email"},
    {"hours_before_meeting": 24, "notification_type": "SMS"}  # Duplicate 24h
]  ✗ ERROR
```

### 7. Location Settings Validation (`validate_location_settings()`)
- If `location_type` = "Video Call", `video_platform` is required
- If `location_type` = "Physical Location" or "Custom", `custom_location` recommended (warning only)
- **Error**: "Video Platform is required when Location Type is 'Video Call'."
- **Warning**: "Custom Location is recommended when Location Type is '{type}'."

### 8. Public Booking URL Generation (`set_public_booking_url()`)
- Automatically generates booking URL
- Format: `{site_url}/book/{department_slug}/{meeting_slug}`
- Requires both department and meeting_slug to be set
- Updates automatically when slug changes

## Usage Examples

### Creating a Meeting Type

```python
# Create a standard support call meeting type
meeting_type = frappe.get_doc({
    "doctype": "MM Meeting Type",
    "department": "support",
    "meeting_name": "30-min Support Call",
    "meeting_slug": "30-min-call",
    "is_active": 1,
    "duration": 30,
    "is_public": 1,
    "is_internal": 0,
    "description": "<p>Quick support session to resolve your issues.</p>",
    "location_type": "Video Call",
    "video_platform": "Google Meet",
    "requires_approval": 0
})
meeting_type.insert()
# Auto-named as: MM-MT-support-30-min-call
# Auto-generated URL: https://site.com/book/support/30-min-call
```

### Adding Reminder Schedule

```python
# Add reminders to existing meeting type
meeting_type = frappe.get_doc("MM Meeting Type", "MM-MT-support-30-min-call")

meeting_type.append("reminder_schedule", {
    "hours_before_meeting": 24,
    "notification_type": "Email",
    "is_active": 1
})

meeting_type.append("reminder_schedule", {
    "hours_before_meeting": 1,
    "notification_type": "Both",
    "is_active": 1
})

meeting_type.save()
```

### Querying Public Meeting Types for a Department

```python
# Get all active public meeting types for a department
public_meetings = frappe.get_all(
    "MM Meeting Type",
    filters={
        "department": "support",
        "is_active": 1,
        "is_public": 1
    },
    fields=[
        "name",
        "meeting_name",
        "meeting_slug",
        "duration",
        "description",
        "public_booking_url"
    ]
)

for meeting in public_meetings:
    print(f"{meeting.meeting_name} ({meeting.duration} min)")
    print(f"Book at: {meeting.public_booking_url}")
```

### Querying Internal Meeting Types

```python
# Get internal meeting types for a department
internal_meetings = frappe.get_all(
    "MM Meeting Type",
    filters={
        "department": "engineering",
        "is_active": 1,
        "is_internal": 1
    },
    fields=["meeting_name", "duration", "location_type"]
)
```

### Deactivating a Meeting Type

```python
# Temporarily disable a meeting type (keeps data, just hides from booking)
meeting_type = frappe.get_doc("MM Meeting Type", "MM-MT-support-30-min-call")
meeting_type.is_active = 0
meeting_type.save()

# Later, re-activate
meeting_type.is_active = 1
meeting_type.save()
```

## Child Table: MM Meeting Type Reminder

| Field Name | Type | Required | Default | Description |
|------------|------|----------|---------|-------------|
| `hours_before_meeting` | Int | Yes | - | Send reminder X hours before (non-negative) |
| `notification_type` | Select | Yes | Email | Email, SMS, or Both |
| `is_active` | Check | No | 1 | Enable/disable this reminder |

### Common Reminder Patterns

```python
# Standard Pattern (24h + 1h)
[
    {"hours_before_meeting": 24, "notification_type": "Email"},
    {"hours_before_meeting": 1, "notification_type": "Both"}
]

# Executive Pattern (3 days, 1 day, 2 hours)
[
    {"hours_before_meeting": 72, "notification_type": "Email"},
    {"hours_before_meeting": 24, "notification_type": "Email"},
    {"hours_before_meeting": 2, "notification_type": "Both"}
]

# Quick Call Pattern (15 min only)
[
    {"hours_before_meeting": 0.25, "notification_type": "Email"}  # 15 minutes
]

# High-Touch Pattern (1 week, 3 days, 1 day, 2 hours, 15 min)
[
    {"hours_before_meeting": 168, "notification_type": "Email"},  # 1 week
    {"hours_before_meeting": 72, "notification_type": "Email"},   # 3 days
    {"hours_before_meeting": 24, "notification_type": "Email"},   # 1 day
    {"hours_before_meeting": 2, "notification_type": "Both"},     # 2 hours
    {"hours_before_meeting": 0.25, "notification_type": "SMS"}    # 15 min
]
```

## Integration with Other DocTypes

### Related DocTypes
- **[MM Department](../mm_department/)** (Parent): Provides members for assignment
- **[MM Meeting Booking](../mm_meeting_booking/)**: Uses meeting type settings
- **[MM Meeting Type Reminder](../mm_meeting_type_reminder/)** (Child): Reminder schedule
- **[MM User Availability Rule](../mm_user_availability_rule/)**: Applied during booking

### Booking Flow Integration

```
Customer visits public booking URL
              ↓
Load MM Meeting Type details
(duration, description, location_type)
              ↓
Display available dates/times
(using department member availability)
              ↓
Customer selects slot and submits
              ↓
Create MM Meeting Booking
├─> Copy: duration, location_type
├─> Set: requires_approval status
└─> Apply: reminder_schedule

If requires_approval = 1:
    Booking status = "Pending"
    Notify department leader
    Wait for approval
Else:
    Booking status = "Confirmed"
    Auto-assign to available member

Schedule reminders from reminder_schedule
```

## Permissions

| Role | Create | Read | Write | Delete | Notes |
|------|--------|------|-------|--------|-------|
| System Manager | ✓ | ✓ | ✓ | ✓ | Full access |
| MM Department Leader | - | ✓ | ✓ | - | Can modify their department's meeting types |
| All Users | - | ✓ | - | - | Read access for internal booking |
| Guest | - | ✓ | - | - | Read public meeting types only |

**Note**: Department Leaders need permission rules configured to limit access to their own department's meeting types.

## Database Schema

### Indexes
```sql
-- Query optimization for public booking pages
CREATE INDEX idx_department_active_public
ON `tabMM Meeting Type` (department, is_active, is_public);

-- Query optimization for internal meeting selection
CREATE INDEX idx_department_active_internal
ON `tabMM Meeting Type` (department, is_active, is_internal);

-- Unique slug within department
CREATE UNIQUE INDEX idx_department_slug
ON `tabMM Meeting Type` (department, meeting_slug);
```

### Auto-Naming
Format: `MM-MT-{department}-{meeting_slug}`

**Examples**:
- Department: `support`, Slug: `30-min-call` → `MM-MT-support-30-min-call`
- Department: `sales`, Slug: `demo` → `MM-MT-sales-demo`

### Track Changes
Track changes is **enabled** (`"track_changes": 1`) to maintain audit trail of:
- Meeting type configuration changes
- Duration modifications
- Approval requirement changes
- Activation/deactivation

## API Endpoints

### Public API

```python
@frappe.whitelist(allow_guest=True)
def get_department_meeting_types(department_slug):
    """Get all active public meeting types for a department"""
    # Get department
    department = frappe.get_value("MM Department", {"department_slug": department_slug}, "name")

    if not department:
        return []

    # Get public meeting types
    meeting_types = frappe.get_all(
        "MM Meeting Type",
        filters={
            "department": department,
            "is_active": 1,
            "is_public": 1
        },
        fields=[
            "name",
            "meeting_name",
            "meeting_slug",
            "duration",
            "description",
            "location_type",
            "public_booking_url"
        ]
    )

    return meeting_types
```

### Internal API

```python
@frappe.whitelist()
def get_internal_meeting_types(department):
    """Get internal meeting types for a department"""
    return frappe.get_all(
        "MM Meeting Type",
        filters={
            "department": department,
            "is_active": 1,
            "is_internal": 1
        },
        fields=["name", "meeting_name", "duration", "location_type"]
    )

@frappe.whitelist()
def clone_meeting_type(source_name, new_department=None):
    """Clone a meeting type to another department"""
    source = frappe.get_doc("MM Meeting Type", source_name)

    # Create copy
    new_doc = frappe.copy_doc(source)

    if new_department:
        new_doc.department = new_department

    # Will auto-generate new slug and URL
    new_doc.insert()

    return new_doc.name
```

## Testing Checklist

### Unit Tests
- [ ] Validate department must exist and be active
- [ ] Validate meeting slug cleaning and uniqueness within department
- [ ] Validate at least one availability flag (public/internal) required
- [ ] Validate duration (positive, max 480 minutes)
- [ ] Validate no duplicate reminder times
- [ ] Validate video platform required when location_type = Video Call
- [ ] Validate public booking URL generation

### Integration Tests
- [ ] Test meeting type appears on public booking page
- [ ] Test internal meeting type NOT visible publicly
- [ ] Test booking inherits meeting type settings (duration, location)
- [ ] Test approval workflow when requires_approval = 1
- [ ] Test reminder schedule triggers notifications
- [ ] Test deactivated meeting types hidden from booking
- [ ] Test department deactivation affects meeting types

### Edge Cases
- [ ] Meeting type with both public and internal flags
- [ ] Meeting type with 480-minute duration (8 hours)
- [ ] Meeting type with 0.25 hour reminder (15 minutes)
- [ ] Meeting type slug collision in different departments (should allow)
- [ ] Meeting type with custom video platform
- [ ] Meeting type with no reminder schedule (valid)
- [ ] Changing department slug updates booking URLs

## Best Practices

### 1. Clear Meeting Names
```python
# Good
"30-min Support Call"
"Technical Consultation (1 hour)"
"Executive Demo Session"

# Poor
"Call"
"Meeting"
"Session 1"
```

### 2. Descriptive Slugs
```python
# Good
"30-min-support-call"
"tech-consultation"
"executive-demo"

# Poor (but will be auto-cleaned)
"meeting1"
"session"
"call"
```

### 3. Appropriate Durations
- 15 min: Quick check-ins, standups
- 30 min: Standard calls, support
- 45-60 min: Consultations, demos
- 90-120 min: Training, workshops
- 120+ min: Full-day workshops (consider breaking up)

### 4. Smart Reminder Schedules
- Always include at least one reminder
- Use 24h for standard meetings
- Add 1h reminder for time-sensitive meetings
- Use SMS for high-priority or same-day reminders
- Consider timezone when setting reminder times

### 5. Location Type Selection
- Video Call: Most flexible, use for remote
- Phone Call: When video not needed
- Physical Location: Verify space availability, consider approval
- Custom: Special formats (webinars, etc.)

## Known Limitations

1. **Single Department**: Each meeting type belongs to only one department. Cannot share meeting types across departments (must clone).

2. **Fixed Duration**: Duration is fixed per meeting type. Cannot allow customers to choose duration (e.g., 30 or 60 min options).

3. **No Time-of-Day Restrictions**: Cannot limit booking to specific times (e.g., "only morning slots"). Use MM User Availability Rule for this.

4. **No Capacity Limits**: Meeting type doesn't limit total bookings. Use MM User Availability Rule for capacity management.

5. **No Dynamic Pricing**: No built-in support for paid meetings or varying prices by time/day.

## See Also

- [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md) - Full system requirements
- [MM Department](../mm_department/) - Parent department DocType
- [MM Meeting Type Reminder](../mm_meeting_type_reminder/) - Child table for reminders
- [MM Meeting Booking](../mm_meeting_booking/) - Bookings created from meeting types
- [Phase 1: Foundation Setup](../../../../Meeting_Manager_PD.md#phase-1-foundation-setup-week-1) - Implementation context
- [Phase 3: Public Booking Interface](../../../../Meeting_Manager_PD.md#phase-3-public-booking-interface---6-step-department-flow-week-3) - How meeting types are displayed

## Contributing

When modifying this DocType:
1. Ensure all validation rules pass, especially slug uniqueness within department
2. Update this README if field structure changes
3. Test public booking page integration
4. Test reminder schedule processing
5. Consider backward compatibility for existing meeting types
6. Update API documentation if endpoints change

---

**DocType Version**: 1.0
**Last Updated**: 2025-12-08
**Module**: Meeting Manager
**App**: meeting_manager
