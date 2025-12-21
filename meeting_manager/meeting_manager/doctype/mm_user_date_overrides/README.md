# MM User Date Overrides DocType (Child Table)

## Overview

The **MM User Date Overrides** DocType is a child table that stores date-specific availability exceptions for users. It allows users to override their regular working hours defined in MM User Settings for specific dates, such as vacations, conferences, public holidays, or days with different working hours.

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md):

> **Child Table - MM User Date Overrides**:
> - `date` (Date)
> - `available` (Check)
> - `custom_hours_start` (Time)
> - `custom_hours_end` (Time)
> - `reason` (Small Text) - e.g., "Vacation", "Conference", "Out of Office"

This child table is part of the [MM User Availability Rule](../mm_user_availability_rule/README.md) DocType and provides the flexibility to handle real-world scheduling scenarios where users need to deviate from their standard weekly schedule.

## Key Features

### 1. Date-Specific Overrides
- Override availability for specific dates
- Mark dates as unavailable (vacations, sick days, holidays)
- Set custom working hours for specific dates (half-days, special schedules)

### 2. Reason Tracking
- Document why the override exists
- Common reasons: Vacation, Conference, Out of Office, Half Day, Public Holiday

### 3. Flexible Scheduling
- Complete day off (available = 0)
- Modified hours (available = 1, with custom start/end times)
- Overrides standard weekly schedule from MM User Settings

### 4. Child Table Structure
- Belongs to MM User Availability Rule (parent)
- Editable grid for easy bulk entry
- Sorted by date for chronological viewing

## Field Reference

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `date` | Date | Yes | Specific date for override |
| `available` | Check | No (Default: 0) | Is user available on this date |
| `custom_hours_start` | Time | No | Custom start time for this date |
| `custom_hours_end` | Time | No | Custom end time for this date |
| `reason` | Small Text | Yes | Explanation for the override |

## Parent DocType Relationship

**Parent**: [MM User Availability Rule](../mm_user_availability_rule/)

The MM User Date Overrides child table is accessed through the parent availability rule:

```python
# Access via parent
availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")
date_overrides = availability_rule.date_overrides  # Child table rows

# Each row is an MM User Date Overrides record
for override in date_overrides:
    print(f"Date: {override.date}, Available: {override.available}, Reason: {override.reason}")
```

## Use Cases & Examples

### Use Case 1: Full Day Off (Vacation)

**Scenario**: User is on vacation and completely unavailable.

```python
{
    "date": "2025-12-25",
    "available": 0,  # Not available
    "custom_hours_start": None,  # Not needed when unavailable
    "custom_hours_end": None,    # Not needed when unavailable
    "reason": "Christmas Holiday"
}
```

**Effect**: User will not be shown as available for any time slots on December 25, 2025, regardless of their standard working hours.

### Use Case 2: Half Day (Morning Only)

**Scenario**: User working half-day, leaving at noon.

```python
{
    "date": "2025-12-20",
    "available": 1,  # Available with custom hours
    "custom_hours_start": "09:00:00",
    "custom_hours_end": "12:00:00",
    "reason": "Half Day - Personal Appointment"
}
```

**Effect**: User available 9:00 AM - 12:00 PM on December 20, 2025, instead of their standard 9:00 AM - 5:00 PM schedule.

### Use Case 3: Conference Day (Different Schedule)

**Scenario**: User attending conference but available during lunch break.

```python
{
    "date": "2025-12-22",
    "available": 1,
    "custom_hours_start": "12:00:00",
    "custom_hours_end": "13:00:00",
    "reason": "Conference - Available during lunch"
}
```

**Effect**: User only available 12:00 PM - 1:00 PM on December 22, 2025.

### Use Case 4: Extended Hours (Special Event)

**Scenario**: User working late for a product launch.

```python
{
    "date": "2025-12-18",
    "available": 1,
    "custom_hours_start": "09:00:00",
    "custom_hours_end": "20:00:00",
    "reason": "Product Launch Day - Extended Hours"
}
```

**Effect**: User available 9:00 AM - 8:00 PM on December 18, 2025, instead of standard 9:00 AM - 5:00 PM.

### Use Case 5: Public Holiday (Team-Wide)

**Scenario**: Company observing a public holiday.

```python
{
    "date": "2026-01-01",
    "available": 0,
    "custom_hours_start": None,
    "custom_hours_end": None,
    "reason": "New Year's Day - Public Holiday"
}
```

**Effect**: User completely unavailable on January 1, 2026.

### Use Case 6: Preventing Duplicate Dates

**Scenario**: Accidentally trying to add a second override for the same date.

```python
# Existing override
availability_rule.date_overrides = [
    {
        "date": "2025-12-25",
        "available": 0,
        "reason": "Christmas Day"
    }
]

# Try to add another override for same date
availability_rule.append("date_overrides", {
    "date": "2025-12-25",  # DUPLICATE!
    "available": 1,
    "custom_hours_start": "10:00:00",
    "custom_hours_end": "12:00:00",
    "reason": "Forgot I marked this as unavailable"
})

try:
    availability_rule.save()
except frappe.ValidationError as e:
    print(str(e))
    # Output: "A date override for 2025-12-25 already exists.
    #          Each date can only have one override entry.
    #          Please update the existing override instead of creating a new one."
```

**Solution**: Update the existing override instead:
```python
# Find and update existing override
for override in availability_rule.date_overrides:
    if str(override.date) == "2025-12-25":
        override.available = 1
        override.custom_hours_start = "10:00:00"
        override.custom_hours_end = "12:00:00"
        override.reason = "Christmas Day - Working limited hours"
        break

availability_rule.save()  # ✅ Success!
```

**Effect**: Duplicate prevented, user guided to update existing override instead.

## Logic & Behavior

### Availability Calculation Priority

When calculating user availability for a specific date, the system follows this priority:

1. **Check Date Overrides First** (this child table)
   - If override exists for the date, use override settings
   - If `available = 0`, user is completely unavailable
   - If `available = 1`, use `custom_hours_start` and `custom_hours_end`

2. **Fall Back to Standard Working Hours** (from MM User Settings)
   - If no override exists, use weekly schedule
   - Check working_hours_json for the day of week

3. **Apply Availability Rule Constraints** (from parent MM User Availability Rule)
   - Buffer times (before/after meetings)
   - Maximum bookings per day/week
   - Minimum notice hours
   - Maximum advance booking days

4. **Check External Calendar Conflicts** (from MM Calendar Event Sync)
   - Existing events from Google Calendar, Outlook, etc.

5. **Check Existing Bookings** (from MM Meeting Booking)
   - Already confirmed meetings

### Pseudo-code for Availability Check

```python
def is_user_available_at_datetime(user, check_datetime):
    """Check if user is available at a specific datetime"""
    check_date = check_datetime.date()
    check_time = check_datetime.time()

    # Step 1: Check for date-specific override
    override = get_date_override(user, check_date)

    if override:
        # Override exists - use override settings
        if not override.available:
            return False  # User marked as unavailable for entire day

        # User available with custom hours
        if override.custom_hours_start and override.custom_hours_end:
            if not (override.custom_hours_start <= check_time < override.custom_hours_end):
                return False  # Outside custom hours
    else:
        # No override - use standard working hours from MM User Settings
        working_hours = get_working_hours(user, check_datetime.strftime("%A").lower())

        if not working_hours["enabled"]:
            return False  # Not working on this day of week

        if not (working_hours["start"] <= check_time < working_hours["end"]):
            return False  # Outside standard working hours

    # Step 2: Apply buffer times, max bookings, etc.
    if not check_availability_rules(user, check_datetime):
        return False

    # Step 3: Check external calendar conflicts
    if has_external_conflict(user, check_datetime):
        return False

    # Step 4: Check existing bookings
    if has_existing_booking(user, check_datetime):
        return False

    return True
```

## Validation Rules

The child table includes **5 validation methods** ensuring data integrity and preventing conflicts:

### 1. Date Required Validation (`validate_date_required`)

**Validates**:
- Date field is not empty

**Error Messages**:
- `"Date is required for date override."`

### 2. Duplicate Date Validation (`validate_duplicate_date`)

**Validates**:
- No duplicate dates within the same user availability rule
- Each date can only have one override entry
- Excludes current row when checking duplicates (allows updates)

**Error Messages**:
- `"A date override for {date} already exists. Each date can only have one override entry. Please update the existing override instead of creating a new one."`

**Example**:
- ✅ Valid: Overrides for 2025-12-24 and 2025-12-25 (different dates)
- ❌ Invalid: Two overrides for 2025-12-24 in same availability rule

### 3. Custom Hours Validation (`validate_custom_hours`)

**Validates**:
- If `available = 1` (checked), both `custom_hours_start` and `custom_hours_end` are required
- End time must be after start time
- Duration cannot exceed 24 hours
- Warns if duration exceeds 12 hours
- If `available = 0` (unchecked), custom hours are cleared automatically

**Error Messages**:
- `"Custom Start Hours and Custom End Hours are required when Available is checked."`
- `"Custom End Hours must be after Custom Start Hours."`
- `"Custom hours duration cannot exceed 24 hours."`

**Warnings**:
- `"Warning: Custom hours span {hours} hours (more than 12 hours). Please verify this is correct."` (orange indicator, shown when > 12 hours)

**Example**:
```python
# Valid
{
    "available": 1,
    "custom_hours_start": "09:00:00",
    "custom_hours_end": "12:00:00"  # 3 hours - OK
}

# Invalid
{
    "available": 1,
    "custom_hours_start": "14:00:00",
    "custom_hours_end": "10:00:00"  # End before start - FAIL
}

# Auto-cleared
{
    "available": 0,  # Unavailable - custom hours will be cleared
    "custom_hours_start": None,  # Automatically set to None
    "custom_hours_end": None     # Automatically set to None
}
```

### 4. Past Date Warning (`validate_date_not_in_past`)

**Validates**:
- Warns (but allows) creation of overrides for past dates
- Past overrides don't affect already-created bookings

**Warnings**:
- `"Warning: You are creating an override for a past date ({date}). This will not affect past bookings."` (orange indicator)

**Behavior**:
- Warning only - does not block save
- Useful for historical record-keeping
- Prevents confusion about past bookings

### 5. Custom Hours Format Validation (`validate_custom_hours_format`)

**Validates**:
- Start and end times are in HH:MM format
- Hour must be 0-23
- Minute must be 0-59

**Error Messages**:
- `"Custom Start Hours must be in HH:MM format (e.g., 09:00)."`
- `"Custom End Hours must be in HH:MM format (e.g., 17:00)."`
- `"Custom Start Hours: Hour must be between 0 and 23."`
- `"Custom Start Hours: Minute must be between 0 and 59."`
- `"Custom End Hours: Hour must be between 0 and 23."`
- `"Custom End Hours: Minute must be between 0 and 59."`

**Example**:
- ✅ Valid: "09:00", "14:30", "23:59"
- ❌ Invalid: "25:00" (hour > 23), "14:60" (minute > 59), "9:00" (should be "09:00"), "14-30" (wrong separator)

## Usage Examples

### Adding Date Overrides via Parent DocType

```python
# Get or create user availability rule
availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")

# Add vacation dates
vacation_dates = [
    {
        "date": "2025-12-24",
        "available": 0,
        "reason": "Christmas Eve"
    },
    {
        "date": "2025-12-25",
        "available": 0,
        "reason": "Christmas Day"
    },
    {
        "date": "2025-12-26",
        "available": 0,
        "reason": "Boxing Day"
    }
]

for vacation in vacation_dates:
    availability_rule.append("date_overrides", vacation)

availability_rule.save()
```

### Adding Half-Day Override

```python
# Add half-day override
availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")

availability_rule.append("date_overrides", {
    "date": "2025-12-20",
    "available": 1,
    "custom_hours_start": "09:00:00",
    "custom_hours_end": "12:00:00",
    "reason": "Half Day - Dentist Appointment"
})

availability_rule.save()
```

### Bulk Adding Public Holidays

```python
# Add multiple public holidays for 2025
public_holidays_2025 = [
    ("2025-01-01", "New Year's Day"),
    ("2025-04-18", "Good Friday"),
    ("2025-04-21", "Easter Monday"),
    ("2025-05-16", "Ascension Day"),
    ("2025-06-05", "Constitution Day"),
    ("2025-12-24", "Christmas Eve"),
    ("2025-12-25", "Christmas Day"),
    ("2025-12-26", "Boxing Day"),
]

availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")

for date, reason in public_holidays_2025:
    availability_rule.append("date_overrides", {
        "date": date,
        "available": 0,
        "reason": reason
    })

availability_rule.save()
```

### Querying Date Overrides

```python
# Get all overrides for a user
availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")
date_overrides = availability_rule.date_overrides

# Filter unavailable dates (vacations, holidays)
unavailable_dates = [
    override for override in date_overrides
    if not override.available
]

# Filter dates with custom hours (half days)
custom_hours_dates = [
    override for override in date_overrides
    if override.available and override.custom_hours_start
]

# Check if specific date has override
from frappe.utils import getdate

def has_override_for_date(availability_rule, check_date):
    """Check if user has override for a specific date"""
    for override in availability_rule.date_overrides:
        if getdate(override.date) == getdate(check_date):
            return override
    return None

override = has_override_for_date(availability_rule, "2025-12-25")
if override:
    print(f"Override found: {override.reason}")
```

### Removing Past Overrides (Cleanup)

```python
from frappe.utils import today, getdate

# Remove overrides for dates in the past
availability_rule = frappe.get_doc("MM User Availability Rule", "MM-UAR-john@example.com-0001")

current_date = getdate(today())
overrides_to_keep = []

for override in availability_rule.date_overrides:
    if getdate(override.date) >= current_date:
        overrides_to_keep.append(override)

# Clear all and re-add only future overrides
availability_rule.date_overrides = []
for override in overrides_to_keep:
    availability_rule.append("date_overrides", override.as_dict())

availability_rule.save()
print(f"Removed {len(availability_rule.date_overrides) - len(overrides_to_keep)} past overrides")
```

## Integration with Other DocTypes

### Availability Calculation Flow

```
Customer selects date/time on booking page
              ↓
Check MM User Date Overrides for this date
              ↓
         Override exists?
         /              \
       Yes               No
        ↓                ↓
  Use override    Use MM User Settings
    settings        working_hours_json
        ↓                ↓
        └────────┬───────┘
                 ↓
      Apply MM User Availability Rule
      (buffer times, max bookings, etc.)
                 ↓
      Check MM Calendar Event Sync
      (external calendar conflicts)
                 ↓
      Check MM Meeting Booking
      (existing confirmed bookings)
                 ↓
      Return available time slots
```

## UI/UX Considerations

### Form Display

The date overrides are displayed in an editable grid within the MM User Availability Rule form:

```
┌─────────────────────────────────────────────────────────────┐
│ Date-Specific Overrides                                     │
├──────────┬───────────┬──────────────┬────────────┬─────────┤
│ Date     │ Available │ Custom Start │ Custom End │ Reason  │
├──────────┼───────────┼──────────────┼────────────┼─────────┤
│ 12/24/25 │ ☐         │              │            │ Xmas Eve│
│ 12/25/25 │ ☐         │              │            │ Xmas Day│
│ 12/20/25 │ ☑         │ 09:00:00     │ 12:00:00   │ Half Day│
└──────────┴───────────┴──────────────┴────────────┴─────────┘
```

### Recommended UI Improvements

1. **Calendar View**: Add a calendar picker showing overrides visually
2. **Color Coding**:
   - Red for unavailable dates
   - Yellow for dates with custom hours
   - Green for extended hours
3. **Quick Add Templates**: Buttons for "Add Vacation Week", "Add Holiday", "Add Half Day"
4. **Bulk Import**: CSV import for multiple overrides
5. **Conflict Warnings**: Show if override conflicts with existing bookings

## API Endpoints

### Public API

```python
@frappe.whitelist(allow_guest=True)
def check_date_availability(user_email, check_date):
    """Check if user has override for a specific date"""
    availability_rule = frappe.get_value(
        "MM User Availability Rule",
        {"user": user_email, "is_active": 1, "is_default": 1},
        "name"
    )

    if not availability_rule:
        return {"has_override": False}

    rule_doc = frappe.get_doc("MM User Availability Rule", availability_rule)

    for override in rule_doc.date_overrides:
        if str(override.date) == str(check_date):
            return {
                "has_override": True,
                "available": override.available,
                "custom_hours_start": override.custom_hours_start,
                "custom_hours_end": override.custom_hours_end,
                "reason": override.reason
            }

    return {"has_override": False}
```

### Internal API

```python
@frappe.whitelist()
def add_vacation_period(user_email, start_date, end_date, reason="Vacation"):
    """Add date overrides for a vacation period"""
    from frappe.utils import getdate, add_days

    availability_rule = frappe.get_value(
        "MM User Availability Rule",
        {"user": user_email, "is_active": 1, "is_default": 1},
        "name"
    )

    if not availability_rule:
        frappe.throw(f"No active availability rule found for user {user_email}")

    rule_doc = frappe.get_doc("MM User Availability Rule", availability_rule)

    current_date = getdate(start_date)
    end = getdate(end_date)

    while current_date <= end:
        rule_doc.append("date_overrides", {
            "date": current_date,
            "available": 0,
            "reason": reason
        })
        current_date = add_days(current_date, 1)

    rule_doc.save()
    return {"success": True, "days_added": len(rule_doc.date_overrides)}
```

## Testing Checklist

### Unit Tests
- [ ] Validate date field is required
- [ ] Validate reason field is required
- [ ] Validate custom hours required when available = 1
- [ ] Validate end time after start time
- [ ] Validate duplicate dates prevented in same parent
- [ ] Test clearing custom hours when available = 0

### Integration Tests
- [ ] Test availability calculation respects overrides
- [ ] Test override takes precedence over working hours
- [ ] Test bookings cannot be made on unavailable override dates
- [ ] Test custom hours limit available time slots correctly
- [ ] Test past overrides don't affect past bookings
- [ ] Test multiple users with overlapping overrides

### Edge Cases
- [ ] Override on date that falls on standard day off (e.g., Sunday)
- [ ] Override with custom hours same as standard hours (redundant)
- [ ] Override for date far in future (e.g., 1 year ahead)
- [ ] Override with start time 00:00 and end time 23:59 (full day)
- [ ] Multiple overrides for same date (should prevent duplicates)
- [ ] Override on leap day (February 29)

## Best Practices

### 1. Use Clear Reasons
Always provide descriptive reasons for overrides:
- **Good**: "Vacation - Family trip to Spain"
- **Good**: "Conference - React Summit 2025"
- **Good**: "Half Day - Doctor's appointment"
- **Poor**: "Off"
- **Poor**: "Unavailable"

### 2. Clean Up Past Overrides
Run periodic cleanup to remove overrides for past dates:
```python
# Recommended: Monthly cleanup job
def cleanup_past_date_overrides():
    """Remove date overrides older than 30 days"""
    from frappe.utils import add_days, today

    cutoff_date = add_days(today(), -30)
    # Cleanup logic here
```

### 3. Batch Add Vacation Periods
Use helper functions to add multiple consecutive days:
```python
add_vacation_period(
    user_email="john@example.com",
    start_date="2025-07-01",
    end_date="2025-07-14",
    reason="Summer Vacation"
)
```

### 4. Document Custom Hours Clearly
When using custom hours, be explicit in the reason:
```python
{
    "date": "2025-12-20",
    "available": 1,
    "custom_hours_start": "13:00:00",
    "custom_hours_end": "17:00:00",
    "reason": "Available afternoon only - Morning training session"
}
```

### 5. Consider Team Holidays
For company-wide holidays, consider setting overrides at the department level or using a template.

## Known Limitations

1. **No Recurring Overrides**: Each override is for a single specific date. For recurring patterns (e.g., "every Friday in December"), you must add each date individually.

2. **No Time Range Validation**: Currently no validation prevents overlapping time ranges or ensures custom hours are within 24-hour period.

3. **No Booking Conflict Check**: System doesn't warn if creating an override for a date with existing bookings.

4. **Single Override Per Date**: Each date can only have one override. Cannot have multiple time ranges for the same date (e.g., morning and evening availability with afternoon off).

5. **No Automatic Cleanup**: Past overrides are not automatically deleted and must be manually cleaned up.

## Contributing

When modifying this DocType:
1. Add validation logic to mm_user_date_overrides.py (currently empty)
2. Validate custom hours consistency when available flag changes
3. Test override priority in availability calculation
4. Update this README if field structure changes
5. Consider UI improvements for bulk date entry
6. Test edge cases around midnight and DST transitions

---

**DocType Version**: 1.0
**Last Updated**: 2025-12-08
**Module**: Meeting Manager
**App**: meeting_manager
**Type**: Child Table (belongs to MM User Availability Rule)
