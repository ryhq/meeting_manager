# MM User Settings DocType

## Overview

The **MM User Settings** DocType extends the core Frappe User doctype with calendar-specific settings and working hours configuration. It stores user preferences for timezone, profile information, and working hours that are used throughout the Meeting Manager system for availability calculation and booking assignment.

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md):

> **MM User Settings** - Extends User doctype with calendar-specific settings including timezone, profile picture, bio, and working hours configuration (JSON serialized).

This DocType provides the foundation for individual user availability by defining when team members are available to accept bookings. The working hours configuration directly impacts the availability calculation engine and determines which time slots are offered to customers on public booking pages.

## Key Features

### 1. User Profile Information
- **Profile Picture**: User photo displayed on internal interfaces
- **Bio**: Short biography for internal reference
- **Timezone**: User's preferred timezone (can be overridden by department timezone)

### 2. Working Hours Configuration
JSON-based flexible schedule defining:
- Which days of the week the user is available
- Start and end times for each day
- Disabled days (weekends, days off)
- Per-day granularity for different schedules

### 3. Auto-Naming
Format: `MM-USER-{user}` (e.g., `MM-USER-john@example.com`)

### 4. Default Working Hours
Standard Monday-Friday, 9:00-17:00 schedule automatically applied on creation

## Field Reference

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `user` | Link (User) | Yes, Unique | Foreign key to User doctype |
| `timezone` | Select | No (Default: Europe/Copenhagen) | User's timezone for availability |
| `profile_picture` | Attach Image | No | User's profile photo |
| `bio` | Small Text | No | Short biography for internal use |
| `working_hours_json` | JSON | No (Default provided) | Weekly schedule configuration |

## Working Hours JSON Structure

### Schema

```json
{
  "monday": {
    "enabled": true,
    "start": "09:00",
    "end": "17:00"
  },
  "tuesday": {
    "enabled": true,
    "start": "09:00",
    "end": "17:00"
  },
  "wednesday": {
    "enabled": true,
    "start": "09:00",
    "end": "17:00"
  },
  "thursday": {
    "enabled": true,
    "start": "09:00",
    "end": "17:00"
  },
  "friday": {
    "enabled": true,
    "start": "09:00",
    "end": "17:00"
  },
  "saturday": {
    "enabled": false
  },
  "sunday": {
    "enabled": false
  }
}
```

### Field Definitions

**For each day of the week:**
- `enabled` (boolean, required): Whether the user is available on this day
- `start` (string, required if enabled): Start time in HH:MM format (24-hour)
- `end` (string, required if enabled): End time in HH:MM format (24-hour)

**Requirements:**
- All 7 days must be present in the JSON object
- At least one day must be enabled
- If `enabled: true`, both `start` and `end` are required
- If `enabled: false`, `start` and `end` can be omitted
- Time format: HH:MM (e.g., "09:00", "17:00")
- End time must be after start time

### Example Configurations

#### Standard Business Hours (Mon-Fri, 9-5)
```json
{
  "monday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "tuesday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "wednesday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "thursday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "friday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "saturday": {"enabled": false},
  "sunday": {"enabled": false}
}
```

#### Part-Time Schedule (Mon/Wed/Fri mornings)
```json
{
  "monday": {"enabled": true, "start": "09:00", "end": "13:00"},
  "tuesday": {"enabled": false},
  "wednesday": {"enabled": true, "start": "09:00", "end": "13:00"},
  "thursday": {"enabled": false},
  "friday": {"enabled": true, "start": "09:00", "end": "13:00"},
  "saturday": {"enabled": false},
  "sunday": {"enabled": false}
}
```

#### Flexible Hours (Different schedule each day)
```json
{
  "monday": {"enabled": true, "start": "08:00", "end": "16:00"},
  "tuesday": {"enabled": true, "start": "10:00", "end": "18:00"},
  "wednesday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "thursday": {"enabled": true, "start": "10:00", "end": "18:00"},
  "friday": {"enabled": true, "start": "08:00", "end": "14:00"},
  "saturday": {"enabled": false},
  "sunday": {"enabled": false}
}
```

#### 24/7 Support Schedule (with night shifts)
```json
{
  "monday": {"enabled": true, "start": "00:00", "end": "23:59"},
  "tuesday": {"enabled": true, "start": "00:00", "end": "23:59"},
  "wednesday": {"enabled": true, "start": "00:00", "end": "23:59"},
  "thursday": {"enabled": true, "start": "00:00", "end": "23:59"},
  "friday": {"enabled": true, "start": "00:00", "end": "23:59"},
  "saturday": {"enabled": true, "start": "00:00", "end": "23:59"},
  "sunday": {"enabled": true, "start": "00:00", "end": "23:59"}
}
```

## Validation Rules

The DocType implements comprehensive validation in [mm_user_settings.py](mm_user_settings.py):

### 1. User Validation
**Method**: `validate_user_exists()`

- User field is required
- User must exist in the User doctype
- **Error Messages**:
  - "User is required."
  - "User '{user}' does not exist."

### 2. Working Hours JSON Validation
**Method**: `validate_working_hours_json()`

This is the most complex validation, ensuring data integrity:

#### JSON Structure Validation
- Must be valid JSON format
- Must be a JSON object (not array or primitive)
- **Error Messages**:
  - "Invalid JSON format for Working Hours."
  - "Working Hours must be a JSON object."

#### Day Configuration Validation
For each day of the week:
- All 7 days must be present: monday, tuesday, wednesday, thursday, friday, saturday, sunday
- Each day must be a JSON object
- Each day must have an `enabled` field (boolean)
- **Error Messages**:
  - "Missing configuration for '{day}' in Working Hours."
  - "Configuration for '{day}' must be an object."
  - "Missing 'enabled' field for '{day}'."
  - "'enabled' field for '{day}' must be true or false."

#### Time Format Validation (for enabled days)
- `start` and `end` fields are required when `enabled: true`
- Time format: HH:MM (24-hour format)
- Valid hours: 00-23
- Valid minutes: 00-59
- End time must be after start time
- **Error Messages**:
  - "'{day}' is enabled but missing 'start' or 'end' time."
  - "Invalid start time format for '{day}'. Use HH:MM format (e.g., 09:00)."
  - "Invalid end time format for '{day}'. Use HH:MM format (e.g., 17:00)."
  - "End time must be after start time for '{day}'."

**Valid Time Examples**:
- `"09:00"` ✓
- `"17:30"` ✓
- `"00:00"` ✓
- `"23:59"` ✓
- `"9:00"` ✗ (missing leading zero)
- `"09:0"` ✗ (missing minute digit)
- `"25:00"` ✗ (invalid hour)
- `"09:60"` ✗ (invalid minute)

#### Business Logic Validation
- At least one day must be enabled
- **Error Message**:
  - "At least one day must be enabled in Working Hours."

**Examples**:
```python
# This will fail - no days enabled:
{
  "monday": {"enabled": false},
  "tuesday": {"enabled": false},
  # ... all days disabled
}

# This will pass - at least one day enabled:
{
  "monday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "tuesday": {"enabled": false},
  # ... other days
}
```

#### Default Working Hours
If `working_hours_json` is empty or not provided, the system automatically sets default working hours:
- Monday-Friday: 09:00-17:00 (enabled)
- Saturday-Sunday: disabled

## Usage Examples

### Creating User Settings

```python
# Create user settings with default working hours
user_settings = frappe.get_doc({
    "doctype": "MM User Settings",
    "user": "john@example.com",
    "timezone": "Europe/Copenhagen",
    "bio": "Senior Support Engineer"
})
user_settings.insert()
# Auto-naming will create: MM-USER-john@example.com
# Default working hours applied automatically
```

### Creating User Settings with Custom Schedule

```python
import json

# Create user settings with custom working hours
custom_hours = {
    "monday": {"enabled": True, "start": "08:00", "end": "16:00"},
    "tuesday": {"enabled": True, "start": "08:00", "end": "16:00"},
    "wednesday": {"enabled": True, "start": "08:00", "end": "16:00"},
    "thursday": {"enabled": True, "start": "08:00", "end": "16:00"},
    "friday": {"enabled": True, "start": "08:00", "end": "14:00"},
    "saturday": {"enabled": False},
    "sunday": {"enabled": False}
}

user_settings = frappe.get_doc({
    "doctype": "MM User Settings",
    "user": "jane@example.com",
    "timezone": "America/New_York",
    "bio": "Sales Representative",
    "working_hours_json": json.dumps(custom_hours)
})
user_settings.insert()
```

### Querying User Settings

```python
# Get user settings for a specific user
user_settings = frappe.get_doc("MM User Settings", "MM-USER-john@example.com")

# Or query by user email
user_settings = frappe.get_value(
    "MM User Settings",
    {"user": "john@example.com"},
    ["name", "timezone", "working_hours_json"],
    as_dict=True
)

# Parse working hours
import json
working_hours = json.loads(user_settings.working_hours_json)

# Check if user is available on Monday
if working_hours["monday"]["enabled"]:
    start_time = working_hours["monday"]["start"]
    end_time = working_hours["monday"]["end"]
    print(f"Available Monday: {start_time} - {end_time}")
```

### Updating Working Hours

```python
import json

# Load existing user settings
user_settings = frappe.get_doc("MM User Settings", "MM-USER-john@example.com")

# Parse current working hours
working_hours = json.loads(user_settings.working_hours_json)

# Modify schedule (e.g., add Saturday availability)
working_hours["saturday"] = {
    "enabled": True,
    "start": "10:00",
    "end": "14:00"
}

# Save updated working hours
user_settings.working_hours_json = json.dumps(working_hours)
user_settings.save()
```

### Checking User Availability

```python
import json
from datetime import datetime, time

def is_user_available(user_email, datetime_obj):
    """Check if user is available at a given datetime"""
    # Get user settings
    user_settings = frappe.get_value(
        "MM User Settings",
        {"user": user_email},
        ["working_hours_json"],
        as_dict=True
    )

    if not user_settings:
        return False

    # Parse working hours
    working_hours = json.loads(user_settings.working_hours_json)

    # Get day of week (monday, tuesday, etc.)
    day_name = datetime_obj.strftime("%A").lower()

    # Check if day is enabled
    if not working_hours[day_name]["enabled"]:
        return False

    # Get start and end times
    start_time_str = working_hours[day_name]["start"]
    end_time_str = working_hours[day_name]["end"]

    # Parse times
    start_hour, start_min = map(int, start_time_str.split(":"))
    end_hour, end_min = map(int, end_time_str.split(":"))

    start_time = time(start_hour, start_min)
    end_time = time(end_hour, end_min)

    # Check if datetime falls within working hours
    check_time = datetime_obj.time()

    return start_time <= check_time < end_time

# Example usage
from datetime import datetime
check_datetime = datetime(2025, 12, 8, 10, 30)  # Monday, 10:30 AM
is_available = is_user_available("john@example.com", check_datetime)
print(f"User available: {is_available}")
```

## Integration with Other DocTypes

### Related DocTypes
- **[User](https://frappeframework.com/docs/user/en/basics/doctypes/user)**: Core Frappe User doctype (foreign key)
- **[MM User Availability Rule](../mm_user_availability_rule/README.md)**: Advanced availability constraints and date overrides
- **[MM Department](../mm_department/README.md)**: Department membership and timezone inheritance
- **[MM Meeting Booking](../mm_meeting_booking/README.md)**: Booking assignments respect working hours
- **[MM Calendar Integration](../mm_calendar_integration/README.md)**: External calendar sync

### Availability Calculation Flow

The working hours defined in MM User Settings are used in the availability calculation:

1. **Base Availability**: Working hours from MM User Settings
2. **Constraints**: Buffer times, max bookings from MM User Availability Rule
3. **Overrides**: Date-specific overrides from MM User Availability Rule
4. **External Conflicts**: Busy times from MM Calendar Event Sync
5. **Existing Bookings**: Confirmed bookings from MM Meeting Booking

**Pseudo-code**:
```python
def calculate_available_slots(user, date):
    # Step 1: Get base working hours
    user_settings = get_user_settings(user)
    day_name = date.strftime("%A").lower()
    working_hours = user_settings.working_hours_json[day_name]

    if not working_hours["enabled"]:
        return []  # User not available on this day

    # Step 2: Generate time slots based on working hours
    slots = generate_slots(
        working_hours["start"],
        working_hours["end"],
        slot_duration=30  # minutes
    )

    # Step 3: Apply availability rules (buffer times, max bookings)
    slots = apply_availability_rules(user, date, slots)

    # Step 4: Remove date-specific overrides (vacations, etc.)
    slots = apply_date_overrides(user, date, slots)

    # Step 5: Remove external calendar conflicts
    slots = remove_external_conflicts(user, date, slots)

    # Step 6: Remove existing booking conflicts
    slots = remove_booking_conflicts(user, date, slots)

    return slots
```

### Timezone Handling

**User Timezone vs Department Timezone**:
- MM User Settings stores individual user timezone preference
- MM Department stores department-level timezone
- **Priority**: Department timezone takes precedence for booking operations
- **Use Case**: User timezone is for personal preferences, department timezone ensures team coordination

**Example**:
```python
# User in New York joins London-based support department
user_settings = frappe.get_doc("MM User Settings", "MM-USER-john@example.com")
user_settings.timezone = "America/New_York"  # Personal preference

department = frappe.get_doc("MM Department", "support")
department.timezone = "Europe/London"  # Team operates in London time

# For booking calculations, London time is used
# But user may see times displayed in their personal timezone in some interfaces
```

## Permissions

| Role | Create | Read | Write | Delete | Notes |
|------|--------|------|-------|--------|-------|
| System Manager | ✓ | ✓ | ✓ | ✓ | Full access to all user settings |
| All | - | ✓ | - | - | All users can read any user settings |
| Self (User Permission) | ✓ | ✓ | ✓ | - | Users can manage their own settings |

**User Permission Note**: Users should be able to create and edit their own MM User Settings. This requires setting up User Permissions:

```python
# Create user permission allowing users to manage their own settings
frappe.share.add_docshare(
    "MM User Settings",
    "MM-USER-john@example.com",
    user="john@example.com",
    read=1,
    write=1,
    share=0
)
```

## Database Schema

### Indexes
```sql
-- Unique constraint on user field
CREATE UNIQUE INDEX idx_user ON `tabMM User Settings` (user);

-- Query optimization for timezone lookups
CREATE INDEX idx_timezone ON `tabMM User Settings` (timezone);
```

### Auto-Naming
Format: `MM-USER-{user}`

**Examples**:
- User: `john@example.com` → Name: `MM-USER-john@example.com`
- User: `support@company.com` → Name: `MM-USER-support@company.com`

## API Endpoints

### Public API
```python
# Get user's working hours (public booking page)
@frappe.whitelist(allow_guest=True)
def get_user_working_hours(user_email):
    """Returns working hours for availability calculation"""
    user_settings = frappe.get_value(
        "MM User Settings",
        {"user": user_email},
        ["working_hours_json", "timezone"],
        as_dict=True
    )

    if not user_settings:
        return None

    return {
        "working_hours": json.loads(user_settings.working_hours_json),
        "timezone": user_settings.timezone
    }
```

### Internal API
```python
# Update user working hours
@frappe.whitelist()
def update_working_hours(user_email, working_hours_json):
    """Update user's working hours"""
    user_settings = frappe.get_doc("MM User Settings", f"MM-USER-{user_email}")
    user_settings.working_hours_json = working_hours_json
    user_settings.save()
    return {"success": True}

# Get users by timezone
@frappe.whitelist()
def get_users_by_timezone(timezone):
    """Get all users in a specific timezone"""
    return frappe.get_all(
        "MM User Settings",
        filters={"timezone": timezone},
        fields=["user", "name"]
    )
```

## Frontend Integration

### Working Hours Editor Component

For a user-friendly interface to edit working hours, consider creating a Vue.js component:

```vue
<!-- WorkingHoursEditor.vue -->
<template>
  <div class="working-hours-editor">
    <div v-for="day in days" :key="day" class="day-config">
      <label>
        <input type="checkbox" v-model="workingHours[day].enabled">
        {{ capitalize(day) }}
      </label>
      <div v-if="workingHours[day].enabled" class="time-inputs">
        <input type="time" v-model="workingHours[day].start">
        <span>to</span>
        <input type="time" v-model="workingHours[day].end">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
      workingHours: {
        monday: { enabled: true, start: '09:00', end: '17:00' },
        // ... other days
      }
    }
  },
  methods: {
    capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    },
    saveWorkingHours() {
      frappe.call({
        method: 'meeting_manager.api.update_working_hours',
        args: {
          user_email: frappe.session.user,
          working_hours_json: JSON.stringify(this.workingHours)
        }
      });
    }
  }
}
</script>
```

## Testing Checklist

### Unit Tests
- [ ] Validate user must exist in User doctype
- [ ] Validate JSON structure (all 7 days present)
- [ ] Validate time format (HH:MM)
- [ ] Validate end time after start time
- [ ] Validate at least one day enabled
- [ ] Validate default working hours applied when empty
- [ ] Validate invalid JSON throws error
- [ ] Validate missing day throws error
- [ ] Validate invalid time format throws error

### Integration Tests
- [ ] Test availability calculation respects working hours
- [ ] Test timezone conversion in availability slots
- [ ] Test working hours override with date-specific rules
- [ ] Test multiple users with different schedules
- [ ] Test 24/7 schedule edge cases (00:00, 23:59)
- [ ] Test part-time schedule calculations
- [ ] Test department timezone vs user timezone priority

### Edge Cases
- [ ] User with no enabled days (should fail validation)
- [ ] Working hours crossing midnight (not supported, document limitation)
- [ ] Same start and end time (should fail validation)
- [ ] Invalid day name in JSON (should fail validation)
- [ ] Missing `enabled` field (should fail validation)
- [ ] Non-boolean `enabled` value (should fail validation)

## Known Limitations

1. **No Midnight Crossing**: Working hours cannot cross midnight. For overnight shifts, use separate days:
   ```json
   // NOT SUPPORTED: 22:00 to 02:00 (crosses midnight)

   // WORKAROUND: Split across days
   "monday": {"enabled": true, "start": "22:00", "end": "23:59"},
   "tuesday": {"enabled": true, "start": "00:00", "end": "02:00"}
   ```

2. **Single Schedule Per Day**: Each day can only have one continuous time block. Multiple time ranges per day (e.g., morning and evening shifts with lunch break) are not supported. Use buffer times in MM User Availability Rule instead.

3. **No Lunch Breaks**: Working hours define continuous availability. For breaks, use buffer times or date-specific overrides.

4. **Timezone Stored as String**: Timezone is stored as select field, not linked to system timezone data. Daylight Saving Time (DST) transitions must be handled by application logic.

## Contributing

When modifying this DocType:
1. Ensure all validation rules pass, especially working hours JSON validation
2. Update this README if field structure changes
3. Test timezone handling thoroughly
4. Test working hours edge cases (midnight, weekends, part-time)
5. Update API documentation if methods change
6. Consider backward compatibility when changing JSON structure

---

**DocType Version**: 1.0
**Last Updated**: 2025-12-08
**Module**: Meeting Manager
**App**: meeting_manager
