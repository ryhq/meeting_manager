# MM Meeting Type Reminder - Child Table Documentation

## Overview

**MM Meeting Type Reminder** is a child table of **MM Meeting Type** that defines the automated reminder schedule for bookings of that meeting type. Each reminder specifies when (hours before meeting) and how (email, SMS, or both) participants should be reminded about their upcoming meeting.

**Parent DocType**: MM Meeting Type

**Child Table**: Yes (`istable: 1`)

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md), automated reminders are critical for:

1. **Reducing No-Shows**: Timely reminders significantly reduce customer no-show rates by keeping meetings top-of-mind.

2. **Multi-Channel Communication**: Support for email and SMS ensures reminders reach participants through their preferred channels.

3. **Flexible Scheduling**: Different meeting types can have different reminder patterns based on their importance and duration.

4. **Automated Workflow**: Once configured, reminders are sent automatically without manual intervention.

**Key Product Requirements** (Phase 6):
- Configurable reminder timing (hours before meeting)
- Multi-channel support (Email, SMS, Both)
- Multiple reminders per meeting type
- Enable/disable individual reminders
- Prevent duplicate reminder times
- Standard patterns: 24 hours, 1 hour, 15 minutes before

---

## Key Features

### 1. **Flexible Timing**
- Specify exact hours before meeting (0-720 hours)
- Support for fractional hours (e.g., 0.25 hours = 15 minutes)
- Multiple reminders at different intervals

### 2. **Multi-Channel Notifications**
- **Email**: Standard email reminders (default)
- **SMS**: Text message reminders (requires SMS gateway)
- **Both**: Send via both email and SMS simultaneously

### 3. **Active/Inactive Status**
- `is_active` flag to temporarily disable reminders
- Inactive reminders skipped by reminder service
- Useful for testing or temporary suspension

### 4. **Duplicate Prevention**
- Validates no two reminders at same time for same meeting type
- Clear error messages guide configuration
- Prevents confusing duplicate notifications

---

## Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `hours_before_meeting` | Int | Yes | - | Send reminder X hours before meeting (0-720) |
| `notification_type` | Select | Yes | Email | How to send: `Email`, `SMS`, `Both` |
| `is_active` | Check | No | 1 | Enable/disable this reminder |

---

## Validation Rules

The child table includes **3 validation methods** ensuring proper reminder configuration:

### 1. Hours Before Meeting Validation (`validate_hours_before_meeting`)

**Validates**:
- Field is not empty
- Value is not negative
- Warns about very early reminders (> 30 days / 720 hours)
- Provides guidance for 0-hour reminders

**Error Messages**:
- `"Hours Before Meeting is required."`
- `"Hours Before Meeting cannot be negative."`

**Warnings**:
- `"Warning: Reminder scheduled {hours} hours ({days} days) before meeting. Very early reminders may be forgotten by the time of the meeting."` (orange indicator, shown when > 720 hours)

**Info Messages**:
- `"Note: 0-hour reminder means the reminder will be sent at the meeting start time. Consider using at least 15 minutes (0.25 hours) to give participants time to join."` (blue indicator, shown when = 0)

**Reasonable Range**: 0-720 hours (0-30 days)

### 2. Notification Type Validation (`validate_notification_type`)

**Validates**:
- Notification type is selected
- Warns about SMS requirements (gateway configuration needed)

**Error Messages**:
- `"Notification Type is required."`

**Info Messages**:
- `"SMS notifications require SMS gateway configuration. Ensure your SMS provider is properly configured before enabling SMS reminders."` (blue indicator, shown when type = SMS or Both)

### 3. Duplicate Reminder Validation (`validate_duplicate_reminder`)

**Validates**:
- No duplicate `hours_before_meeting` values in same meeting type
- Excludes current row when checking duplicates (allows updates)
- Provides helpful tip for first reminder

**Error Messages**:
- `"A reminder at {hours} hours before meeting already exists. Each reminder time must be unique for this meeting type."`

**Info Messages**:
- `"Tip: Common reminder patterns include: 24 hours + 1 hour before (for important meetings), 24 hours before (standard), 1 hour before (last-minute reminder), 15 minutes before (quick reminder)"` (blue indicator, shown when adding first reminder)

---

## Common Reminder Patterns

### Pattern 1: Standard Meeting (30-60 minutes)

**Example**: Support calls, consultations

```python
reminder_schedule = [
    {
        "hours_before_meeting": 24,  # 1 day before
        "notification_type": "Email",
        "is_active": 1
    },
    {
        "hours_before_meeting": 1,  # 1 hour before
        "notification_type": "Email",
        "is_active": 1
    }
]
```

**Rationale**:
- 24-hour reminder allows rescheduling if needed
- 1-hour reminder ensures participants don't forget
- Email sufficient for most meetings

### Pattern 2: Executive Meeting (High Importance)

**Example**: Executive consultations, board meetings

```python
reminder_schedule = [
    {
        "hours_before_meeting": 72,  # 3 days before
        "notification_type": "Email",
        "is_active": 1
    },
    {
        "hours_before_meeting": 24,  # 1 day before
        "notification_type": "Both",  # Email + SMS
        "is_active": 1
    },
    {
        "hours_before_meeting": 1,  # 1 hour before
        "notification_type": "Both",  # Email + SMS
        "is_active": 1
    }
]
```

**Rationale**:
- 3-day advance warning for busy executives
- Multi-channel reminders (email + SMS) for critical meetings
- Multiple touchpoints ensure attendance

### Pattern 3: Quick Call (15-30 minutes)

**Example**: Quick check-ins, brief consultations

```python
reminder_schedule = [
    {
        "hours_before_meeting": 24,  # 1 day before
        "notification_type": "Email",
        "is_active": 1
    },
    {
        "hours_before_meeting": 0.25,  # 15 minutes before
        "notification_type": "SMS",  # SMS for immediate action
        "is_active": 1
    }
]
```

**Rationale**:
- Light reminder schedule for short meetings
- SMS 15 minutes before for immediate awareness
- No 1-hour reminder (might interrupt other work)

### Pattern 4: All-Day Event

**Example**: Training sessions, workshops

```python
reminder_schedule = [
    {
        "hours_before_meeting": 168,  # 1 week before
        "notification_type": "Email",
        "is_active": 1
    },
    {
        "hours_before_meeting": 24,  # 1 day before
        "notification_type": "Email",
        "is_active": 1
    }
]
```

**Rationale**:
- Week advance notice for calendar blocking
- Day-before reminder for preparation
- No last-minute reminders for all-day events

### Pattern 5: No Reminders (Walk-In)

**Example**: Drop-in hours, open office hours

```python
reminder_schedule = []  # No reminders
```

**Rationale**:
- Informal meetings don't need reminders
- Reduces notification fatigue

---

## Use Cases

### Use Case 1: Standard Support Call Reminders

**Scenario**: Configure reminders for 30-minute support calls.

```python
import frappe

# Create meeting type with standard reminders
meeting_type = frappe.get_doc({
    "doctype": "MM Meeting Type",
    "meeting_type_name": "30-Minute Support Call",
    "meeting_slug": "30-min-support",
    "department": "MM-DEPT-support",
    "duration_minutes": 30,
    "is_active": 1,

    # Reminder schedule
    "reminder_schedule": [
        {
            "hours_before_meeting": 24,
            "notification_type": "Email",
            "is_active": 1
        },
        {
            "hours_before_meeting": 1,
            "notification_type": "Email",
            "is_active": 1
        }
    ]
})

meeting_type.insert()

print(f"Meeting type created with {len(meeting_type.reminder_schedule)} reminders")
```

**Result**:
- Customers receive email 24 hours before meeting
- Customers receive email 1 hour before meeting
- Assigned team member also receives both reminders

### Use Case 2: Adding SMS Reminder for High-Priority Meeting

**Scenario**: Executive consultation needs SMS reminders in addition to email.

```python
import frappe

# Get meeting type
meeting_type = frappe.get_doc("MM Meeting Type", "MM-MT-sales-executive-consultation")

# Add SMS reminder 1 hour before
meeting_type.append("reminder_schedule", {
    "hours_before_meeting": 1,
    "notification_type": "SMS",  # SMS for immediate attention
    "is_active": 1
})

meeting_type.save()

# System will show info message:
# "SMS notifications require SMS gateway configuration.
#  Ensure your SMS provider is properly configured before enabling SMS reminders."

print("SMS reminder added for executive meetings")
```

**Result**:
- Executive meetings now have SMS reminder 1 hour before
- System warns about SMS gateway requirement
- Must configure SMS provider before reminders work

### Use Case 3: Temporarily Disabling Reminders (System Maintenance)

**Scenario**: Email server maintenance scheduled. Temporarily disable email reminders.

```python
import frappe

# Get meeting type
meeting_type = frappe.get_doc("MM Meeting Type", "MM-MT-support-30-min-call")

# Disable all email reminders
for reminder in meeting_type.reminder_schedule:
    if reminder.notification_type in ["Email", "Both"]:
        reminder.is_active = 0
        print(f"Disabled {reminder.hours_before_meeting}-hour {reminder.notification_type} reminder")

meeting_type.save()

print("Email reminders temporarily disabled during maintenance")

# --- After maintenance ---

# Re-enable all reminders
for reminder in meeting_type.reminder_schedule:
    if not reminder.is_active:
        reminder.is_active = 1
        print(f"Re-enabled {reminder.hours_before_meeting}-hour {reminder.notification_type} reminder")

meeting_type.save()

print("All reminders re-enabled")
```

**Result**:
- Email reminders suspended during maintenance
- No errors when email server unavailable
- Easy to re-enable after maintenance complete

### Use Case 4: Preventing Duplicate Reminder Times

**Scenario**: Accidentally trying to add two reminders at 24 hours before.

```python
import frappe

# Get meeting type
meeting_type = frappe.get_doc("MM Meeting Type", "MM-MT-support-30-min-call")

# Already has 24-hour email reminder
# Try to add another 24-hour SMS reminder
meeting_type.append("reminder_schedule", {
    "hours_before_meeting": 24,  # Duplicate!
    "notification_type": "SMS",
    "is_active": 1
})

try:
    meeting_type.save()
except frappe.ValidationError as e:
    print(f"Error: {str(e)}")
    # Output: "A reminder at 24 hours before meeting already exists.
    #          Each reminder time must be unique for this meeting type."

# Solution: Use different time or update existing reminder to "Both"
meeting_type.reminder_schedule = [r for r in meeting_type.reminder_schedule if r.idx != 2]  # Remove failed addition
for reminder in meeting_type.reminder_schedule:
    if reminder.hours_before_meeting == 24:
        reminder.notification_type = "Both"  # Send via both email and SMS
        break

meeting_type.save()
print("Updated existing 24-hour reminder to send via both Email and SMS")
```

**Result**:
- Duplicate prevented by validation
- Solution: Change existing reminder to "Both" instead of adding duplicate
- Maintains clean reminder schedule

### Use Case 5: Custom Reminder Pattern for Urgent Meetings

**Scenario**: Emergency security response meetings need aggressive reminder schedule.

```python
import frappe

# Create urgent meeting type with aggressive reminders
meeting_type = frappe.get_doc({
    "doctype": "MM Meeting Type",
    "meeting_type_name": "Urgent Security Response",
    "meeting_slug": "urgent-security",
    "department": "MM-DEPT-security",
    "duration_minutes": 60,
    "is_active": 1,

    # Aggressive reminder schedule
    "reminder_schedule": [
        {
            "hours_before_meeting": 2,  # 2 hours before
            "notification_type": "Both",
            "is_active": 1
        },
        {
            "hours_before_meeting": 1,  # 1 hour before
            "notification_type": "Both",
            "is_active": 1
        },
        {
            "hours_before_meeting": 0.25,  # 15 minutes before
            "notification_type": "SMS",  # Final SMS reminder
            "is_active": 1
        }
    ]
})

meeting_type.insert()

print("Urgent meeting type created with aggressive reminder schedule")
```

**Result**:
- Reminders at 2 hours, 1 hour, and 15 minutes before
- Multi-channel (email + SMS) for critical communication
- Final SMS ensures immediate awareness

---

## Integration with Other DocTypes

### MM Meeting Type (Parent)

**Relationship**: Child table of MM Meeting Type

**Integration Points**:
- Meeting type defines reminder behavior for all bookings of that type
- Reminders inherited by all `MM Meeting Booking` instances
- Changes to reminder schedule affect future bookings only (not past)

### MM Meeting Booking (Reminder Execution)

**Relationship**: Reminders executed for each booking

**Flow**:
```
MM Meeting Booking created
  ↓
Get MM Meeting Type
  ↓
Get reminder_schedule (active reminders only)
  ↓
For each reminder:
  Calculate reminder send time = (start_datetime - hours_before_meeting)
  Schedule reminder job for send time
  ↓
At send time:
  Send notification via specified channel (Email/SMS/Both)
  Update booking.reminders_sent JSON array
  Update booking.last_reminder_sent timestamp
```

**Reminder Service Logic**:
```python
# Pseudo-code for reminder service
def schedule_booking_reminders(booking):
    meeting_type = frappe.get_doc("MM Meeting Type", booking.meeting_type)

    for reminder in meeting_type.reminder_schedule:
        if not reminder.is_active:
            continue  # Skip inactive reminders

        # Calculate send time
        send_time = booking.start_datetime - timedelta(hours=reminder.hours_before_meeting)

        # Schedule reminder job
        frappe.enqueue(
            method='send_meeting_reminder',
            booking=booking.name,
            notification_type=reminder.notification_type,
            at=send_time
        )
```

---

## Usage Examples

### Example 1: Creating Meeting Type with Reminders

```python
import frappe

def create_meeting_type_with_reminders(department, name, duration, reminders):
    """
    Create meeting type with custom reminder schedule

    Args:
        department: MM Department name
        name: Meeting type name
        duration: Duration in minutes
        reminders: List of reminder dicts

    Returns:
        Created meeting type document
    """
    meeting_type = frappe.get_doc({
        "doctype": "MM Meeting Type",
        "meeting_type_name": name,
        "meeting_slug": name.lower().replace(" ", "-"),
        "department": department,
        "duration_minutes": duration,
        "is_active": 1,
        "reminder_schedule": reminders
    })

    meeting_type.insert()

    print(f"Created '{name}' with {len(reminders)} reminders")

    return meeting_type

# Usage: Standard meeting
standard_reminders = [
    {"hours_before_meeting": 24, "notification_type": "Email", "is_active": 1},
    {"hours_before_meeting": 1, "notification_type": "Email", "is_active": 1}
]

meeting_type = create_meeting_type_with_reminders(
    "MM-DEPT-support",
    "30-Minute Consultation",
    30,
    standard_reminders
)
```

### Example 2: Bulk Update Notification Type

```python
import frappe

def update_all_reminders_to_both(meeting_type_name):
    """
    Change all reminders to send via both Email and SMS

    Args:
        meeting_type_name: Name of MM Meeting Type

    Returns:
        Number of reminders updated
    """
    meeting_type = frappe.get_doc("MM Meeting Type", meeting_type_name)

    updated_count = 0
    for reminder in meeting_type.reminder_schedule:
        if reminder.notification_type != "Both":
            old_type = reminder.notification_type
            reminder.notification_type = "Both"
            print(f"Updated {reminder.hours_before_meeting}-hour reminder: {old_type} → Both")
            updated_count += 1

    if updated_count > 0:
        meeting_type.save()

    return updated_count

# Usage: Upgrade important meeting to multi-channel
updated = update_all_reminders_to_both("MM-MT-sales-executive-consultation")
print(f"Updated {updated} reminders to multi-channel")
```

### Example 3: Get Active Reminders for Booking

```python
import frappe
from datetime import datetime, timedelta

def get_reminder_schedule_for_booking(booking_name):
    """
    Get reminder send times for a specific booking

    Args:
        booking_name: Name of MM Meeting Booking

    Returns:
        List of reminder schedules with send times
    """
    booking = frappe.get_doc("MM Meeting Booking", booking_name)
    meeting_type = frappe.get_doc("MM Meeting Type", booking.meeting_type)

    reminders = []
    for reminder in meeting_type.reminder_schedule:
        if not reminder.is_active:
            continue  # Skip inactive reminders

        # Calculate send time
        start_dt = datetime.fromisoformat(str(booking.start_datetime))
        send_time = start_dt - timedelta(hours=reminder.hours_before_meeting)

        reminders.append({
            "hours_before": reminder.hours_before_meeting,
            "notification_type": reminder.notification_type,
            "send_time": send_time,
            "already_sent": send_time < datetime.now()
        })

    # Sort by send time
    reminders.sort(key=lambda x: x['send_time'])

    return reminders

# Usage
schedule = get_reminder_schedule_for_booking("MM-MB-support-0042")

print("Reminder Schedule:")
for reminder in schedule:
    status = "SENT" if reminder['already_sent'] else "PENDING"
    print(f"  [{status}] {reminder['hours_before']}h before via {reminder['notification_type']} - {reminder['send_time']}")
```

### Example 4: Clone Reminder Schedule to Another Meeting Type

```python
import frappe

def clone_reminder_schedule(source_meeting_type, target_meeting_type):
    """
    Copy reminder schedule from one meeting type to another

    Args:
        source_meeting_type: Name of source MM Meeting Type
        target_meeting_type: Name of target MM Meeting Type

    Returns:
        Number of reminders cloned
    """
    source = frappe.get_doc("MM Meeting Type", source_meeting_type)
    target = frappe.get_doc("MM Meeting Type", target_meeting_type)

    # Clear existing reminders
    target.reminder_schedule = []

    # Clone reminders
    for reminder in source.reminder_schedule:
        target.append("reminder_schedule", {
            "hours_before_meeting": reminder.hours_before_meeting,
            "notification_type": reminder.notification_type,
            "is_active": reminder.is_active
        })

    target.save()

    print(f"Cloned {len(source.reminder_schedule)} reminders from '{source_meeting_type}' to '{target_meeting_type}'")

    return len(source.reminder_schedule)

# Usage: Copy standard pattern to new meeting type
cloned = clone_reminder_schedule(
    "MM-MT-support-30-min-call",
    "MM-MT-sales-demo-call"
)
```

### Example 5: Reminder Effectiveness Report

```python
import frappe

def get_reminder_effectiveness_stats(meeting_type_name):
    """
    Analyze reminder effectiveness for a meeting type

    Args:
        meeting_type_name: Name of MM Meeting Type

    Returns:
        dict: Statistics on reminder performance
    """
    # Get all bookings for this meeting type
    bookings = frappe.get_all(
        "MM Meeting Booking",
        filters={
            "meeting_type": meeting_type_name,
            "booking_status": ["in", ["Completed", "No-Show"]]  # Past bookings only
        },
        fields=["name", "booking_status", "reminders_sent"]
    )

    total_bookings = len(bookings)
    no_shows = len([b for b in bookings if b.booking_status == "No-Show"])
    completed = len([b for b in bookings if b.booking_status == "Completed"])

    # Calculate reminder counts
    with_reminders = len([b for b in bookings if b.reminders_sent])
    without_reminders = total_bookings - with_reminders

    stats = {
        "total_bookings": total_bookings,
        "completed": completed,
        "no_shows": no_shows,
        "no_show_rate": (no_shows / total_bookings * 100) if total_bookings > 0 else 0,
        "with_reminders": with_reminders,
        "without_reminders": without_reminders
    }

    return stats

# Usage
stats = get_reminder_effectiveness_stats("MM-MT-support-30-min-call")

print(f"Reminder Effectiveness Report:")
print(f"  Total Bookings: {stats['total_bookings']}")
print(f"  Completed: {stats['completed']}")
print(f"  No-Shows: {stats['no_shows']} ({stats['no_show_rate']:.1f}%)")
print(f"  With Reminders: {stats['with_reminders']}")
print(f"  Without Reminders: {stats['without_reminders']}")
```

---

## Best Practices

### For Reminder Configuration

1. **Standard Pattern**: Start with 24-hour + 1-hour reminders for most meeting types

2. **Meeting Duration Consideration**:
   - Short meetings (15-30 min): 24h + 15min before
   - Standard meetings (30-60 min): 24h + 1h before
   - Long meetings (1+ hour): 72h + 24h + 1h before

3. **Importance-Based Patterns**:
   - Routine: Email only
   - Important: Email + SMS for last reminder
   - Critical: Email + SMS for all reminders

4. **Avoid Over-Reminding**:
   - Don't exceed 3-4 reminders per meeting
   - Space reminders appropriately (not all within 2 hours)
   - Respect notification fatigue

### For SMS Reminders

1. **Gateway Configuration Required**:
   - Configure SMS gateway before enabling SMS reminders
   - Test SMS delivery before going live
   - Monitor SMS costs and delivery rates

2. **SMS vs Email Guidelines**:
   - Email: Detailed information, calendar invites
   - SMS: Urgent reminders, last-minute notifications
   - Both: Critical meetings, high no-show risk

3. **Character Limits**:
   - Keep SMS content concise (160 characters)
   - Include essential info only: meeting time, type, join link
   - Use URL shorteners for long links

### For Reminder Timing

1. **Business Hours Awareness**:
   - Avoid sending reminders outside business hours (e.g., 2 AM)
   - Use timezone-aware calculations
   - Consider recipient's timezone, not sender's

2. **Fractional Hours**:
   - 0.25 hours = 15 minutes
   - 0.5 hours = 30 minutes
   - Use decimals for precise timing

3. **Very Early Reminders**:
   - > 7 days: Risk of being forgotten
   - Consider confirmation emails instead of reminders
   - Reserve for important, advance-scheduled events

---

## Known Limitations

1. **No Timezone per Reminder**: All reminders use booking's timezone. Can't send different reminders in different timezones.

2. **Static Schedule**: Can't adjust reminder schedule after booking is created (uses meeting type at creation time).

3. **No Conditional Reminders**: Can't send reminders based on conditions (e.g., "only if customer hasn't confirmed").

4. **No Recipient Preferences**: All participants receive same reminders. Can't customize per participant.

5. **Integer Hours Only**: Field type is Int. For 15-minute reminders, must calculate (0.25 hours not directly supported). Consider fractional hour support in future.

6. **No Retry Logic**: If reminder send fails (email bounce, SMS failure), no automatic retry mechanism.

---

## See Also

- [MM Meeting Type](../mm_meeting_type/README.md) - Parent meeting type configuration
- [MM Meeting Booking](../mm_meeting_booking/README.md) - Bookings that receive reminders
- [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md) - Notification requirements

---

## Contributing

When modifying this child table:

1. **Adding Fields**:
   - Update JSON field_order
   - Add validation if needed
   - Update reminder service logic
   - Document in this README

2. **Changing Validation**:
   - Update validation methods
   - Document error messages
   - Add test cases
   - Ensure backward compatibility

3. **Adding Notification Types**:
   - Update notification_type Select options
   - Implement sender in reminder service
   - Update integration documentation
   - Test delivery

4. **Supporting Fractional Hours**:
   - Change field type from Int to Float
   - Update validation for decimal values
   - Test reminder scheduling precision
   - Document in usage examples

---

**Last Updated**: 2025-12-08
**Version**: 1.0
**Maintainer**: Best Security Development Team
