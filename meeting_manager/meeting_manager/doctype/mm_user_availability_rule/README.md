# MM User Availability Rule DocType

## Overview

The **MM User Availability Rule** DocType defines advanced availability constraints and scheduling parameters for users in the Meeting Manager system. While [MM User Settings](../mm_user_settings/README.md) provides basic weekly working hours, this DocType adds buffer times, booking limits, scheduling constraints, and date-specific overrides to ensure users maintain control over their booking capacity and schedule.

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md):

> **MM User Availability Rule** - Define availability constraints and preferences for users including buffer times, maximum bookings, advance booking window, minimum notice, and date-specific overrides (vacations, special availability).

This DocType implements sophisticated scheduling logic that prevents overbooking, maintains work-life balance, and handles real-world scheduling scenarios like vacations, buffer times between meetings, and advance booking limits.

## Key Features

### 1. Buffer Times

- **Before meetings**: Preparation time (e.g., 15 minutes before)
- **After meetings**: Wrap-up time, breaks (e.g., 15 minutes after)
- Prevents back-to-back meetings
- Ensures time for transitions

### 2. Booking Capacity Limits

- **Per day**: Maximum bookings allowed in a single day
- **Per week**: Maximum bookings allowed in a rolling 7-day period
- 0 = unlimited bookings
- Prevents burnout and overwork

### 3. Scheduling Constraints

- **Minimum notice**: Prevent last-minute bookings (e.g., require 2 hours notice)
- **Maximum advance**: Limit how far ahead bookings can be made (e.g., 60 days)
- Balances availability with planning flexibility

### 4. Date-Specific Overrides

- [MM User Date Overrides](../mm_user_date_overrides/README.md) child table
- Handle vacations, holidays, half-days
- Override standard working hours for specific dates

### 5. Rule Management

- **Multiple rules per user**: Different rules for different scenarios
- **Default rule**: One rule marked as default for standard calculations
- **Active/Inactive**: Enable/disable rules without deleting

### 6. Auto-Naming

Format: `MM-UAR-{user}-{####}` (e.g., `MM-UAR-john@example.com-0001`)

## Field Reference

| Field Name              | Type        | Required | Default | Description                                      |
| ----------------------- | ----------- | -------- | ------- | ------------------------------------------------ |
| `user`                  | Link (User) | Yes      | -       | User these rules apply to                        |
| `rule_name`             | Data        | Yes      | -       | Descriptive name (e.g., "Standard Availability") |
| `is_default`            | Check       | No       | 0       | Default rule for this user                       |
| `is_active`             | Check       | No       | 1       | Enable/disable this rule                         |
| `buffer_time_before`    | Int         | No       | 0       | Minutes before meeting (max 240)                 |
| `buffer_time_after`     | Int         | No       | 0       | Minutes after meeting (max 240)                  |
| `max_bookings_per_day`  | Int         | No       | 0       | Max bookings per day (0 = unlimited, max 50)     |
| `max_bookings_per_week` | Int         | No       | 0       | Max bookings per week (0 = unlimited, max 200)   |
| `min_notice_hours`      | Int         | Yes      | 2       | Minimum hours notice required (max 720)          |
| `max_days_advance`      | Int         | Yes      | 60      | Maximum days ahead bookings allowed (max 365)    |
| `date_overrides`        | Table       | No       | -       | Child table: MM User Date Overrides              |

## Field Constraints

### Buffer Times

- Must be ≥ 0 (non-negative)
- Maximum: 240 minutes (4 hours)
- Reasonable range: 0-60 minutes
- **Error**: "Buffer Time Before cannot be negative."
- **Error**: "Buffer Time Before cannot exceed 240 minutes (4 hours)."

### Booking Limits

- Must be ≥ 0 (non-negative, 0 = unlimited)
- Max per day: 50 bookings
- Max per week: 200 bookings
- Weekly limit consistency: `daily × 7 ≥ weekly` (if both set)
- **Error**: "Max Bookings Per Day cannot be negative. Use 0 for unlimited."
- **Error**: "Max Bookings Per Day cannot exceed 50. Use 0 for unlimited."
- **Error**: "Max Bookings Per Week seems inconsistent with Max Bookings Per Day."

### Scheduling Constraints

- `min_notice_hours`: 0-720 hours (0-30 days)
- `max_days_advance`: 1-365 days (must be > 0)
- Logical check: min_notice < max_advance
- **Error**: "Minimum Notice Hours must be at least 0."
- **Error**: "Minimum Notice Hours cannot exceed 720 hours (30 days)."
- **Error**: "Maximum Days in Advance must be greater than 0."
- **Error**: "Minimum Notice Hours must be less than Maximum Days in Advance."

## Use Cases & Examples

### Use Case 1: Standard Availability Rule

**Scenario**: Default rule for a full-time employee with reasonable constraints.

```python
{
    "user": "john@example.com",
    "rule_name": "Standard Availability",
    "is_default": 1,
    "is_active": 1,
    "buffer_time_before": 15,  # 15 min prep time
    "buffer_time_after": 15,   # 15 min wrap-up
    "max_bookings_per_day": 8, # Max 8 meetings per day
    "max_bookings_per_week": 0, # Unlimited weekly (managed by daily)
    "min_notice_hours": 2,     # 2 hours minimum notice
    "max_days_advance": 60     # Can book up to 60 days ahead
}
```

**Effect**:

- 15 minutes blocked before/after each meeting
- Maximum 8 meetings per day
- Cannot book meetings within 2 hours
- Cannot book beyond 60 days ahead

### Use Case 2: Executive with Limited Availability

**Scenario**: Senior executive with strict booking limits to prevent overload.

```python
{
    "user": "ceo@example.com",
    "rule_name": "Executive Availability",
    "is_default": 1,
    "is_active": 1,
    "buffer_time_before": 30,  # 30 min prep (review materials)
    "buffer_time_after": 30,   # 30 min follow-up
    "max_bookings_per_day": 4, # Max 4 meetings per day
    "max_bookings_per_week": 15, # Max 15 meetings per week
    "min_notice_hours": 24,    # 24 hours minimum notice
    "max_days_advance": 90     # Can book up to 90 days ahead
}
```

**Effect**:

- 30 minutes blocked before/after for preparation
- Strictly limited to 4 meetings/day, 15/week
- Requires full day notice (24 hours)
- Allows quarterly planning (90 days)

### Use Case 3: Customer Support with High Volume

**Scenario**: Support agent handling many short calls with minimal buffer.

```python
{
    "user": "support@example.com",
    "rule_name": "Support Availability",
    "is_default": 1,
    "is_active": 1,
    "buffer_time_before": 5,   # 5 min buffer
    "buffer_time_after": 5,    # 5 min buffer
    "max_bookings_per_day": 16, # Up to 16 calls per day
    "max_bookings_per_week": 80, # Max 80 calls per week
    "min_notice_hours": 0,     # Same-day booking allowed
    "max_days_advance": 14     # 2 weeks ahead
}
```

**Effect**:

- Minimal 5-minute buffer
- High capacity (16 meetings/day)
- Immediate bookings allowed
- Short booking window (2 weeks)

### Use Case 4: Part-Time Consultant

**Scenario**: Consultant working limited hours with longer meetings.

```python
{
    "user": "consultant@example.com",
    "rule_name": "Consultant Availability",
    "is_default": 1,
    "is_active": 1,
    "buffer_time_before": 20,  # 20 min prep
    "buffer_time_after": 10,   # 10 min wrap-up
    "max_bookings_per_day": 3, # Max 3 consultations per day
    "max_bookings_per_week": 12, # Max 12 per week
    "min_notice_hours": 48,    # 2 days notice required
    "max_days_advance": 30     # 1 month ahead
}
```

**Effect**:

- Adequate buffer times for thorough meetings
- Limited to 3 meetings/day (part-time)
- Requires 2 days advance notice
- 30-day booking window

### Use Case 5: Seasonal Availability Rule

**Scenario**: Different rule for busy season vs. off-season.

```python
# Busy Season Rule (Active December-February)
{
    "user": "sales@example.com",
    "rule_name": "Busy Season - High Capacity",
    "is_default": 0,  # Manually activated during season
    "is_active": 1,
    "buffer_time_before": 10,
    "buffer_time_after": 10,
    "max_bookings_per_day": 10,  # Higher capacity
    "max_bookings_per_week": 50,
    "min_notice_hours": 1,       # Short notice OK
    "max_days_advance": 30
}

# Off Season Rule (Active rest of year)
{
    "user": "sales@example.com",
    "rule_name": "Standard Season",
    "is_default": 1,  # Default rule
    "is_active": 1,
    "buffer_time_before": 15,
    "buffer_time_after": 15,
    "max_bookings_per_day": 6,   # Normal capacity
    "max_bookings_per_week": 30,
    "min_notice_hours": 4,       # More notice required
    "max_days_advance": 60
}
```

## Validation Rules

The DocType implements comprehensive validation in [mm_user_availability_rule.py](mm_user_availability_rule.py):

### 1. User Validation (`validate_user_exists()`)

- User field is required
- User must exist in User doctype
- **Error**: "User is required."
- **Error**: "User '{user}' does not exist."

### 2. Buffer Times Validation (`validate_buffer_times()`)

- Must be non-negative (≥ 0)
- Maximum: 240 minutes (4 hours)
- **Error**: "Buffer Time Before cannot be negative."
- **Error**: "Buffer Time After cannot exceed 240 minutes (4 hours)."

### 3. Booking Limits Validation (`validate_booking_limits()`)

- Must be non-negative (≥ 0, where 0 = unlimited)
- Maximum per day: 50
- Maximum per week: 200
- Consistency check: `daily ≤ weekly` (when both set)
- **Error**: "Max Bookings Per Day cannot exceed 50. Use 0 for unlimited."
- **Error**: "Max Bookings Per Day cannot exceed Max Bookings Per Week. Daily limit must be less than or equal to weekly limit."

**Example of invalid configuration**:

```python
# This will FAIL validation:
{
    "max_bookings_per_day": 15,  # 15 per day
    "max_bookings_per_week": 10  # 10 per week
    # 15 > 10 - INVALID! Daily limit exceeds weekly limit
}

# This will PASS:
{
    "max_bookings_per_day": 5,   # 5 per day
    "max_bookings_per_week": 30  # 30 per week
    # 5 ≤ 30 - VALID! Daily limit does not exceed weekly limit
}

# This will also PASS:
{
    "max_bookings_per_day": 10,  # 10 per day
    "max_bookings_per_week": 20  # 20 per week
    # 10 ≤ 20 - VALID! You can have up to 10 per day, but only 20 total for the week
}
```

### 4. Scheduling Constraints Validation (`validate_scheduling_constraints()`)

- `min_notice_hours`: Required, 0-720 hours (30 days)
- `max_days_advance`: Required, 1-365 days
- Logical check: min_notice < max_advance
- **Error**: "Minimum Notice Hours is required."
- **Error**: "Maximum Days in Advance cannot exceed 365 days (1 year)."
- **Error**: "Minimum Notice Hours must be less than Maximum Days in Advance."

**Example of logical error**:

```python
# This will FAIL validation:
{
    "min_notice_hours": 72,  # 72 hours = 3 days
    "max_days_advance": 2    # 2 days ahead
    # Cannot require 3 days notice but only allow 2 days advance!
}

# This will PASS:
{
    "min_notice_hours": 24,  # 24 hours = 1 day
    "max_days_advance": 30   # 30 days ahead
}
```

### 5. Default Rule Validation (`validate_default_rule()`)

- Only one default rule allowed per user
- **Error**: "A default availability rule already exists for user '{user}'. Please uncheck 'Is Default' on the existing rule first, or uncheck it on this rule."

### 6. Date Overrides Validation (`validate_date_overrides()`)

- No duplicate dates allowed in child table
- Custom hours consistency (both start and end required if available)
- End time must be after start time
- **Error**: "Duplicate date override found for {date}. Each date can only appear once."
- **Error**: "Custom End Time must be after Custom Start Time for date {date}."
- **Error**: "Custom Start Time is required when Custom End Time is provided for date {date}."

## Usage Examples

### Creating an Availability Rule

```python
# Create availability rule with moderate constraints
availability_rule = frappe.get_doc({
    "doctype": "MM User Availability Rule",
    "user": "john@example.com",
    "rule_name": "Standard Availability",
    "is_default": 1,
    "is_active": 1,
    "buffer_time_before": 15,
    "buffer_time_after": 15,
    "max_bookings_per_day": 8,
    "max_bookings_per_week": 0,  # Unlimited weekly
    "min_notice_hours": 2,
    "max_days_advance": 60
})
availability_rule.insert()
# Auto-named as: MM-UAR-john@example.com-0001
```

### Adding Date Overrides (Vacation)

```python
# Add vacation dates
availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")

# Add Christmas vacation
availability_rule.append("date_overrides", {
    "date": "2025-12-24",
    "available": 0,
    "reason": "Christmas Eve"
})
availability_rule.append("date_overrides", {
    "date": "2025-12-25",
    "available": 0,
    "reason": "Christmas Day"
})
availability_rule.append("date_overrides", {
    "date": "2025-12-26",
    "available": 0,
    "reason": "Boxing Day"
})

availability_rule.save()
```

### Querying Active Rules

```python
# Get default active rule for a user
default_rule = frappe.get_value(
    "MM User Availability Rule",
    {"user": "john@example.com", "is_active": 1, "is_default": 1},
    ["name", "rule_name", "min_notice_hours", "max_days_advance"],
    as_dict=True
)

if default_rule:
    print(f"Rule: {default_rule.rule_name}")
    print(f"Min Notice: {default_rule.min_notice_hours} hours")
    print(f"Max Advance: {default_rule.max_days_advance} days")
```

### Checking Booking Limits

```python
from datetime import datetime, timedelta
from frappe.utils import add_days, nowdate

def can_accept_more_bookings(user_email, check_date):
    """Check if user can accept more bookings on a specific date"""
    # Get active rule
    rule = frappe.get_doc(
        "MM User Availability Rule",
        {"user": user_email, "is_active": 1, "is_default": 1}
    )

    if not rule:
        return True  # No rule, no limit

    # Check daily limit
    if rule.max_bookings_per_day > 0:
        daily_bookings = frappe.db.count(
            "MM Meeting Booking",
            {
                "assigned_to": user_email,
                "scheduled_date": check_date,
                "status": ["in", ["Confirmed", "Pending"]]
            }
        )

        if daily_bookings >= rule.max_bookings_per_day:
            return False

    # Check weekly limit
    if rule.max_bookings_per_week > 0:
        week_start = add_days(check_date, -6)  # Rolling 7-day window

        weekly_bookings = frappe.db.count(
            "MM Meeting Booking",
            {
                "assigned_to": user_email,
                "scheduled_date": ["between", [week_start, check_date]],
                "status": ["in", ["Confirmed", "Pending"]]
            }
        )

        if weekly_bookings >= rule.max_bookings_per_week:
            return False

    return True
```

### Applying Buffer Times

```python
from datetime import datetime, timedelta

def get_available_slots_with_buffer(user_email, check_date, slot_duration=30):
    """Generate available slots considering buffer times"""
    # Get availability rule
    rule = frappe.get_value(
        "MM User Availability Rule",
        {"user": user_email, "is_active": 1, "is_default": 1},
        ["buffer_time_before", "buffer_time_after"],
        as_dict=True
    )

    buffer_before = rule.buffer_time_before if rule else 0
    buffer_after = rule.buffer_time_after if rule else 0

    # Get existing bookings for the day
    bookings = frappe.get_all(
        "MM Meeting Booking",
        filters={
            "assigned_to": user_email,
            "scheduled_date": check_date,
            "status": ["in", ["Confirmed", "Pending"]]
        },
        fields=["scheduled_start_time", "scheduled_end_time"]
    )

    # Block out time slots including buffer times
    blocked_periods = []
    for booking in bookings:
        start = datetime.combine(check_date, booking.scheduled_start_time)
        end = datetime.combine(check_date, booking.scheduled_end_time)

        # Add buffer before and after
        buffered_start = start - timedelta(minutes=buffer_before)
        buffered_end = end + timedelta(minutes=buffer_after)

        blocked_periods.append((buffered_start, buffered_end))

    # Generate available slots avoiding blocked periods
    # (implementation continues...)
```

## Integration with Other DocTypes

### Related DocTypes

- **[MM User Settings](../mm_user_settings/README.md)**: Provides base weekly working hours
- **[MM User Date Overrides](../mm_user_date_overrides/README.md)** (Child): Date-specific availability exceptions
- **[MM Meeting Booking](../mm_meeting_booking/README.md)**: Respects availability rules for assignment
- **[MM Department](../mm_department/README.md)**: Department members have individual rules
- **[MM Calendar Event Sync](../mm_calendar_event_sync/README.md)**: External calendar conflicts also apply

### Availability Calculation Hierarchy

```
1. MM User Settings (working_hours_json)
   └─> Base weekly schedule (Mon-Fri 9-5)

2. MM User Availability Rule
   ├─> Buffer times (15 min before/after)
   ├─> Booking limits (8 per day)
   ├─> Scheduling constraints (2h notice, 60 days advance)
   └─> Date Overrides (child table)
       └─> Vacation days, custom hours

3. MM Calendar Event Sync
   └─> External calendar conflicts (Google, Outlook)

4. MM Meeting Booking
   └─> Existing confirmed bookings

Final Result: Available time slots
```

### Complete Availability Check

```python
def calculate_available_slots(user, date, meeting_duration=30):
    """
    Complete availability calculation considering all factors
    Returns list of available time slots
    """
    from datetime import datetime, timedelta

    # Step 1: Get base working hours from MM User Settings
    user_settings = frappe.get_doc("MM User Settings", f"MM-USER-{user}")
    working_hours = json.loads(user_settings.working_hours_json)
    day_name = date.strftime("%A").lower()

    if not working_hours[day_name]["enabled"]:
        return []  # Not working on this day

    # Step 2: Check date overrides in MM User Availability Rule
    rule = frappe.get_doc(
        "MM User Availability Rule",
        {"user": user, "is_active": 1, "is_default": 1}
    )

    # Check if date has override
    for override in rule.date_overrides:
        if str(override.date) == str(date):
            if not override.available:
                return []  # User unavailable on this date

            if override.custom_hours_start and override.custom_hours_end:
                start_time = override.custom_hours_start
                end_time = override.custom_hours_end
                break
    else:
        # No override - use standard working hours
        start_time = working_hours[day_name]["start"]
        end_time = working_hours[day_name]["end"]

    # Step 3: Check scheduling constraints
    from frappe.utils import now_datetime, add_days

    current_datetime = now_datetime()
    check_datetime = datetime.combine(date, datetime.min.time())

    # Check minimum notice
    hours_until = (check_datetime - current_datetime).total_seconds() / 3600
    if hours_until < rule.min_notice_hours:
        return []  # Too soon

    # Check maximum advance
    days_until = (check_datetime.date() - current_datetime.date()).days
    if days_until > rule.max_days_advance:
        return []  # Too far ahead

    # Step 4: Check booking limits
    if not can_accept_more_bookings(user, date):
        return []  # Booking limit reached

    # Step 5: Generate time slots with buffer times
    slots = generate_slots_with_buffer(
        user, date, start_time, end_time,
        meeting_duration,
        rule.buffer_time_before,
        rule.buffer_time_after
    )

    # Step 6: Remove slots blocked by external calendar events
    slots = remove_external_conflicts(user, date, slots)

    # Step 7: Remove slots blocked by existing bookings
    slots = remove_existing_booking_conflicts(user, date, slots)

    return slots
```

## Permissions

| Role                   | Create | Read | Write | Delete | Notes                        |
| ---------------------- | ------ | ---- | ----- | ------ | ---------------------------- |
| System Manager         | ✓      | ✓    | ✓     | ✓      | Full access to all rules     |
| All                    | -      | ✓    | -     | -      | All users can read any rules |
| Self (User Permission) | ✓      | ✓    | ✓     | -      | Users manage their own rules |

## Database Schema

### Indexes

```sql
-- Query optimization for default active rules
CREATE INDEX idx_user_default_active
ON `tabMM User Availability Rule` (user, is_default, is_active);

-- Query optimization for user lookups
CREATE INDEX idx_user ON `tabMM User Availability Rule` (user);
```

### Auto-Naming

Format: `MM-UAR-{user}-{####}`

**Examples**:

- User: `john@example.com` → `MM-UAR-john@example.com-0001`, `MM-UAR-john@example.com-0002`, etc.
- User: `support@company.com` → `MM-UAR-support@company.com-0001`

### Track Changes

Track changes is **enabled** (`"track_changes": 1`) to maintain audit trail of:

- Buffer time changes
- Booking limit modifications
- Scheduling constraint updates
- Default rule switches
- Rule activation/deactivation

## Testing Checklist

### Unit Tests

- [ ] Validate user exists
- [ ] Validate buffer times (non-negative, max 240)
- [ ] Validate booking limits (non-negative, daily vs weekly consistency)
- [ ] Validate min notice < max advance
- [ ] Validate only one default rule per user
- [ ] Validate no duplicate dates in overrides
- [ ] Validate custom hours in date overrides

### Integration Tests

- [ ] Test buffer times prevent back-to-back bookings
- [ ] Test booking limits block new assignments
- [ ] Test min notice prevents same-day bookings
- [ ] Test max advance limits future bookings
- [ ] Test date overrides take precedence over working hours
- [ ] Test multiple rules per user (default selection)
- [ ] Test rule deactivation stops using rule

### Edge Cases

- [ ] User with multiple rules (only default is active)
- [ ] Rule with 0 buffer times (back-to-back allowed)
- [ ] Rule with 0 booking limits (unlimited)
- [ ] Rule with 0 min notice (immediate booking allowed)
- [ ] Date override on already-booked date
- [ ] Switching default rule mid-day
- [ ] Inactive default rule (fallback behavior)

## Best Practices

### 1. Start with Conservative Limits

```python
# Good starting point for most users
{
    "buffer_time_before": 15,
    "buffer_time_after": 15,
    "max_bookings_per_day": 8,
    "max_bookings_per_week": 0,  # Unlimited weekly
    "min_notice_hours": 2,
    "max_days_advance": 60
}
```

### 2. One Default Rule Per User

- Always have one active default rule
- Use additional rules for special scenarios
- Switch default when changing primary schedule

### 3. Reasonable Buffer Times

- 10-15 minutes: Good for most meetings
- 30+ minutes: For preparation-heavy meetings
- 5 minutes: Only for high-volume, short calls

### 4. Consistent Booking Limits

- Set daily OR weekly, not both (unless intentional)
- If both: ensure `daily × 7 ≥ weekly`
- Use 0 for unlimited

### 5. Document Rule Purpose

- Use descriptive `rule_name`
- Examples: "Standard Availability", "Executive Schedule", "Busy Season"

## Known Limitations

1. **No Time-of-Day Limits**: Cannot limit bookings to specific hours (e.g., "max 2 morning meetings"). Use working hours in MM User Settings instead.

2. **No Per-Meeting-Type Limits**: Cannot set different limits for different meeting types. All meeting types count toward the same daily/weekly limit.

3. **Rolling Weekly Window**: Weekly limit uses a rolling 7-day window, not calendar weeks (Monday-Sunday).

4. **Single Default Rule**: Only one default rule per user. Cannot have multiple default rules for different contexts.

5. **No Automatic Rule Switching**: System doesn't auto-switch between rules based on date ranges. Must manually change default rule.

## See Also

- [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md) - Full system requirements
- [MM User Settings](../mm_user_settings/README.md) - Base weekly working hours
- [MM User Date Overrides](../mm_user_date_overrides/README.md) - Child table for date exceptions
- [MM Meeting Booking](../mm_meeting_booking/README.md) - Booking assignments
- [Phase 1: Foundation Setup](../../../../Meeting_Manager_PD.md#phase-1-foundation-setup-week-1) - Implementation context
- [Phase 2: Availability Engine](../../../../Meeting_Manager_PD.md#phase-2-availability-engine--calendar-sync-week-2) - Availability calculation details

## Contributing

When modifying this DocType:

1. Ensure all validation rules pass, especially consistency checks
2. Update this README if field structure or constraints change
3. Test availability calculation with new constraints
4. Test buffer time application in slot generation
5. Test booking limit enforcement
6. Consider backward compatibility when changing validation rules

---

**DocType Version**: 1.0
**Last Updated**: 2025-12-08
**Module**: Meeting Manager
**App**: meeting_manager
