# Timezone Utilities Documentation

**File:** `meeting_manager/meeting_manager/utils/timezone.py`
**Purpose:** Timezone conversion, validation, and display formatting for the Meeting Manager system
**Dependencies:** `frappe`, `pytz`, `datetime`

---

## Table of Contents

1. [Overview](#overview)
2. [Core Algorithms](#core-algorithms)
3. [Function Reference](#function-reference)
4. [Use Cases](#use-cases)
5. [Edge Cases Handled](#edge-cases-handled)
6. [Best Practices](#best-practices)

---

## Overview

The timezone utilities module provides a comprehensive set of functions for handling timezone-related operations in a global meeting scheduling system. It addresses the complex challenges of:

- Converting times between different timezones
- Handling Daylight Saving Time (DST) transitions
- Displaying times in multiple timezones simultaneously
- Validating timezone strings
- Managing timezone information for users and departments

### Key Design Principles

1. **UTC-First Approach**: All datetime conversions route through UTC as an intermediary
2. **Pytz Integration**: Uses the robust `pytz` library for timezone database (IANA/Olson)
3. **Graceful Degradation**: Defaults to UTC when timezone information is unavailable
4. **Type Flexibility**: Accepts both `datetime` objects and ISO string representations
5. **DST Awareness**: Explicitly handles ambiguous and non-existent times during DST transitions

---

## Core Algorithms

### 1. Timezone Retrieval Hierarchy

**Function:** `get_user_timezone(user)`

**Algorithm:**

```
1. Query MM User Settings for user-specific timezone
2. If not found, fallback to Frappe User timezone
3. If still not found, return "UTC" as safe default
```

**Rationale:** Prioritizes Meeting Manager-specific settings over global Frappe settings, ensuring system-specific timezone preferences.

**Function:** `get_department_timezone(department)`

**Algorithm:**

```
1. Query MM Department for department timezone
2. If not found, return "UTC" as safe default
```

**Use Case:** Department-based scheduling where all members default to the department's timezone.

---

### 2. Timezone Conversion Algorithm

**Function:** `convert_to_timezone(dt, from_tz, to_tz)`

**Step-by-Step Process:**

```python
Input: datetime (dt), source timezone (from_tz), target timezone (to_tz)

Step 1: Type Normalization
    IF dt is string THEN
        dt = parse_datetime(dt)
    END IF

Step 2: Create Timezone Objects
    from_timezone = pytz.timezone(from_tz)  # e.g., "UTC"
    to_timezone = pytz.timezone(to_tz)      # e.g., "Europe/Copenhagen"

Step 3: Handle Naive Datetime (No Timezone Info)
    IF dt.tzinfo is None THEN
        dt = from_timezone.localize(dt)  # Attach source timezone
    ELSE
        dt = dt.astimezone(from_timezone)  # Convert to source timezone
    END IF

Step 4: Convert to Target Timezone
    result = dt.astimezone(to_timezone)

Output: datetime in target timezone
```

**Why Localize vs Astimezone?**

- `localize()`: Used for **naive** datetimes (no timezone info) to attach timezone info
- `astimezone()`: Used for **aware** datetimes (has timezone info) to convert between timezones

**Example:**

```python
# Naive datetime: 2025-12-11 14:00 (no timezone)
dt = datetime(2025, 12, 11, 14, 0)

# Localize to Copenhagen time
cph_tz = pytz.timezone("Europe/Copenhagen")
dt_cph = cph_tz.localize(dt)  # 2025-12-11 14:00+01:00 CET

# Convert to New York time
ny_tz = pytz.timezone("America/New_York")
dt_ny = dt_cph.astimezone(ny_tz)  # 2025-12-11 08:00-05:00 EST
```

---

### 3. UTC Conversion (Specialized Cases)

**Function:** `convert_to_utc(dt, source_tz)`

**Algorithm:**

```
convert_to_timezone(dt, source_tz, "UTC")
```

**Use Case:** Storing meeting times in the database (always stored in UTC)

**Function:** `convert_from_utc(dt, target_tz)`

**Algorithm:**

```
convert_to_timezone(dt, "UTC", target_tz)
```

**Use Case:** Displaying UTC-stored times in user's local timezone

---

### 4. Time Slot Display Formatting

**Function:** `format_time_slot_display(start_time, end_time, timezone, visitor_timezone=None)`

**Algorithm:**

```
Input: start_time, end_time, meeting_timezone, visitor_timezone (optional)

Step 1: Input Validation & Type Conversion
    FOR each time in [start_time, end_time] DO
        IF time is string THEN
            time = parse_datetime(time)
        END IF

        IF time is time object (not datetime) THEN
            time = combine_with_today_date(time)  # Graceful handling
        END IF
    END FOR

Step 2: Localize to Meeting Timezone
    meeting_tz = pytz.timezone(timezone)

    FOR each time in [start_time, end_time] DO
        IF time has timezone info THEN
            localized_time = time.astimezone(meeting_tz)
        ELSE
            localized_time = meeting_tz.localize(time)
        END IF
    END FOR

    meeting_str = format("{start} - {end} {timezone}")

Step 3: Add Visitor Timezone (if different)
    IF visitor_timezone exists AND visitor_timezone ≠ meeting_timezone THEN
        visitor_tz = pytz.timezone(visitor_timezone)

        FOR each time in [start_time, end_time] DO
            IF time has timezone info THEN
                visitor_time = time.astimezone(visitor_tz)
            ELSE
                visitor_time = convert_to_timezone(time, meeting_tz, visitor_tz)
            END IF
        END FOR

        visitor_str = format("{start} - {end} {visitor_timezone}")

        RETURN "{meeting_str} ({visitor_str} your time)"
    END IF

Output: "09:00 - 09:30 Europe/Copenhagen (03:00 - 03:30 America/New_York your time)"
```

**Dual-Timezone Display Strategy:**

- **Primary:** Always show time in meeting/department timezone
- **Secondary:** Show visitor's local time in parentheses for clarity
- **Conditional:** Only show visitor timezone if different from meeting timezone

**Example Output:**

```
"14:00 - 14:30 Europe/Copenhagen (08:00 - 08:30 America/New_York your time)"
```

---

### 5. DST Transition Detection

**Function:** `is_dst_transition(dt, tz)`

**Algorithm:**

```
Input: datetime (dt), timezone (tz)

Step 1: Get Timezone Object
    timezone = pytz.timezone(tz)

Step 2: Attempt Localization
    TRY
        timezone.localize(dt)
        RETURN False  # No DST issue
    CATCH pytz.AmbiguousTimeError
        # Time occurs twice (clocks fall back)
        RETURN True
    CATCH pytz.NonExistentTimeError
        # Time doesn't exist (clocks spring forward)
        RETURN True
    END TRY

Output: boolean indicating DST transition
```

**DST Transition Types:**

1. **Spring Forward (NonExistentTimeError)**

   - Example: In US, 2:00 AM → 3:00 AM
   - Time between 2:00-2:59 AM doesn't exist

2. **Fall Back (AmbiguousTimeError)**
   - Example: In US, 2:00 AM → 1:00 AM
   - Time between 1:00-1:59 AM occurs twice

**Handling Strategy:**

- Detect transitions before scheduling
- Alert users when booking times that may be affected
- Use `is_dst=True/False` parameter in `localize()` for explicit disambiguation

**Example:**

```python
# March 13, 2025, 2:30 AM doesn't exist in America/New_York (spring forward)
dt = datetime(2025, 3, 13, 2, 30)
is_dst_transition(dt, "America/New_York")  # Returns: True
```

---

### 6. UTC Offset Calculation

**Function:** `get_timezone_offset(tz, dt=None)`

**Algorithm:**

```
Input: timezone (tz), optional datetime (dt)

Step 1: Initialize
    IF dt is None THEN
        dt = current_datetime()
    END IF

Step 2: Localize to Timezone
    timezone = pytz.timezone(tz)

    IF dt has timezone info THEN
        localized = dt.astimezone(timezone)
    ELSE
        localized = timezone.localize(dt)
    END IF

Step 3: Extract Offset
    offset_raw = localized.strftime("%z")  # e.g., "+0100"

Step 4: Format as +HH:MM
    formatted = offset_raw[0:3] + ":" + offset_raw[3:]
    # "+0100" → "+01:00"

Output: "+01:00" or "-05:00"
```

**Use Cases:**

- Displaying timezone information to users
- Debugging timezone conversions
- API responses requiring offset information

**Important Note:** Offset varies with DST. Same timezone can have different offsets:

- Europe/Copenhagen: `+01:00` (CET) in winter, `+02:00` (CEST) in summer

---

### 7. Next Occurrence Algorithm

**Function:** `get_next_occurrence_in_timezone(time_str, tz, from_datetime=None)`

**Algorithm:**

```
Input: time string (e.g., "14:30"), timezone (tz), optional start datetime

Step 1: Initialize Start Time
    IF from_datetime is None THEN
        from_datetime = current_datetime()
    END IF

Step 2: Convert to Target Timezone
    timezone = pytz.timezone(tz)

    IF from_datetime has timezone info THEN
        local_dt = from_datetime.astimezone(timezone)
    ELSE
        local_dt = timezone.localize(from_datetime)
    END IF

Step 3: Parse Target Time
    hour, minute = parse(time_str)  # "14:30" → 14, 30

Step 4: Create Target Datetime (Today)
    target = local_dt.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

Step 5: Check if Time Has Passed
    IF target <= local_dt THEN
        target = target + 1 day
    END IF

Output: Next occurrence datetime in target timezone
```

**Use Case:** Scheduling recurring meetings - finding the next occurrence of "2:00 PM CET" from current time.

**Example:**

```python
# Current time: 2025-12-11 15:00 CET
# Looking for: Next "14:30"
get_next_occurrence_in_timezone("14:30", "Europe/Copenhagen")
# Returns: 2025-12-12 14:30 CET (tomorrow)
```

---

## Function Reference

### Configuration Functions

| Function                              | Purpose                                     | Return Type |
| ------------------------------------- | ------------------------------------------- | ----------- |
| `get_department_timezone(department)` | Get department's timezone                   | `str`       |
| `get_user_timezone(user)`             | Get user's timezone with fallback hierarchy | `str`       |
| `validate_timezone(tz)`               | Check if timezone string is valid           | `bool`      |
| `get_common_timezones()`              | List all common timezone names              | `list[str]` |

### Conversion Functions

| Function                                  | Purpose                     | Algorithm Complexity |
| ----------------------------------------- | --------------------------- | -------------------- |
| `convert_to_timezone(dt, from_tz, to_tz)` | Generic timezone conversion | O(1)                 |
| `convert_to_utc(dt, source_tz)`           | Convert any timezone to UTC | O(1)                 |
| `convert_from_utc(dt, target_tz)`         | Convert UTC to any timezone | O(1)                 |

### Display Functions

| Function                                               | Purpose                       | Output Format                                    |
| ------------------------------------------------------ | ----------------------------- | ------------------------------------------------ |
| `format_datetime_with_timezone(dt, tz, format)`        | Format datetime with timezone | Customizable                                     |
| `format_time_slot_display(start, end, tz, visitor_tz)` | Dual-timezone slot display    | "HH:MM - HH:MM TZ (HH:MM - HH:MM TZ2 your time)" |
| `get_timezone_offset(tz, dt)`                          | Get UTC offset                | "+HH:MM" or "-HH:MM"                             |

### Utility Functions

| Function                                             | Purpose                      | Use Case                        |
| ---------------------------------------------------- | ---------------------------- | ------------------------------- |
| `is_dst_transition(dt, tz)`                          | Detect DST transitions       | Booking validation              |
| `get_next_occurrence_in_timezone(time, tz, from_dt)` | Find next time occurrence    | Recurring meetings              |
| `detect_visitor_timezone(request)`                   | Auto-detect visitor timezone | (Placeholder) Public booking UI |

---

## Use Cases

### Use Case 1: Public Booking Flow

**Scenario:** Customer in New York books with Copenhagen-based support team

```python
# Step 1: Customer views available slots
department_tz = get_department_timezone("Support Department")  # "Europe/Copenhagen"
visitor_tz = "America/New_York"

# Step 2: Display slot with dual timezones
slot_display = format_time_slot_display(
    start_time=datetime(2025, 12, 11, 14, 0),  # 2 PM Copenhagen time
    end_time=datetime(2025, 12, 11, 14, 30),
    timezone=department_tz,
    visitor_timezone=visitor_tz
)
# Output: "14:00 - 14:30 Europe/Copenhagen (08:00 - 08:30 America/New_York your time)"

# Step 3: Store booking in UTC
booking_start_utc = convert_to_utc(
    datetime(2025, 12, 11, 14, 0),
    department_tz
)
# Stored: 2025-12-11 13:00:00 UTC
```

---

### Use Case 2: Team Member Availability Check

**Scenario:** Check if team member in Berlin is available at 3 PM Copenhagen time

```python
# Member's timezone
member_tz = get_user_timezone("alice@example.com")  # "Europe/Berlin"

# Meeting time in Copenhagen
meeting_time_cph = datetime(2025, 12, 11, 15, 0)  # 3 PM CET

# Convert to member's timezone
meeting_time_berlin = convert_to_timezone(
    meeting_time_cph,
    from_tz="Europe/Copenhagen",
    to_tz=member_tz
)
# Result: 2025-12-11 15:00 (same time, both CET)

# Check member's working hours in their local time
# Working hours: 9 AM - 5 PM Berlin time
```

---

### Use Case 3: DST-Safe Scheduling

**Scenario:** Schedule weekly meeting avoiding DST transition issues

```python
# Proposed meeting time
proposed_time = datetime(2025, 3, 13, 2, 30)  # DST transition day in US

# Check if this time is problematic
if is_dst_transition(proposed_time, "America/New_York"):
    # Alert: This time doesn't exist (spring forward)
    # Suggest alternative: 3:30 AM or 1:30 AM
    pass
```

---

### Use Case 4: Multi-Timezone Team Meeting

**Scenario:** Display meeting time for globally distributed team

```python
meeting_utc = datetime(2025, 12, 11, 14, 0)  # Stored in UTC

# Display for each team member
for member in team:
    member_tz = get_user_timezone(member.email)
    local_time = convert_from_utc(meeting_utc, member_tz)

    display = format_datetime_with_timezone(
        local_time,
        member_tz,
        "%H:%M %Z on %B %d"
    )
    # Alice (Copenhagen): "15:00 CET on December 11"
    # Bob (New York): "09:00 EST on December 11"
    # Carol (Tokyo): "23:00 JST on December 11"
```

---

## Edge Cases Handled

### 1. Naive Datetime Objects

**Problem:** Python datetime without timezone info

**Solution:**

```python
def convert_to_timezone(dt, from_tz, to_tz):
    # ...
    if dt.tzinfo is None:
        dt = from_timezone.localize(dt)  # Assume source timezone
    else:
        dt = dt.astimezone(from_timezone)
```

### 2. String Date Inputs

**Problem:** ISO string vs datetime object

**Solution:**

```python
if isinstance(dt, str):
    dt = get_datetime(dt)  # Frappe's parser
```

### 3. Time Objects (Not Datetime)

**Problem:** Function receives `time(14, 30)` instead of full datetime

**Solution:**

```python
from datetime import time
if isinstance(start_time, time):
    start_time = datetime.combine(datetime.today(), start_time)
```

### 4. Missing Timezone Configuration

**Problem:** User/department has no timezone set

**Solution:** Always fallback to UTC

```python
return timezone or "UTC"
```

### 5. DST Ambiguity

**Problem:** Time occurs twice (fall back) or doesn't exist (spring forward)

**Solution:** Use `is_dst` parameter

```python
try:
    tz.localize(dt)
except pytz.AmbiguousTimeError:
    # Use is_dst=True for first occurrence, is_dst=False for second
    dt_first = tz.localize(dt, is_dst=True)
    dt_second = tz.localize(dt, is_dst=False)
except pytz.NonExistentTimeError:
    # Advance to next valid time
    pass
```

### 6. Invalid Timezone Strings

**Problem:** User enters "PST" or invalid timezone

**Solution:**

```python
def validate_timezone(tz):
    try:
        pytz.timezone(tz)
        return True
    except pytz.UnknownTimeZoneError:
        return False
```

---

## Best Practices

### 1. Always Store in UTC

**Database Layer:**

```python
# CORRECT: Store in UTC
booking.start_datetime = convert_to_utc(local_time, user_tz)

# WRONG: Store in local timezone
booking.start_datetime = local_time
```

**Rationale:** UTC never changes (no DST), ensures consistent sorting/querying.

---

### 2. Convert at Display Time

**Presentation Layer:**

```python
# Retrieve from database (UTC)
booking_utc = frappe.get_value("MM Meeting Booking", booking_id, "start_datetime")

# Convert to user's timezone for display
user_tz = get_user_timezone(frappe.session.user)
display_time = convert_from_utc(booking_utc, user_tz)
```

---

### 3. Use Explicit Timezone Names

**CORRECT:**

```python
tz = "Europe/Copenhagen"  # IANA timezone name
tz = "America/New_York"
```

**WRONG:**

```python
tz = "CET"   # Ambiguous - doesn't handle DST
tz = "EST"   # Ambiguous - multiple regions
tz = "+01:00"  # Offset - changes with DST
```

---

### 4. Validate User Input

**Before Conversion:**

```python
if not validate_timezone(user_input_tz):
    frappe.throw("Invalid timezone. Please select from the list.")
```

---

### 5. Handle DST Transitions

**Before Scheduling:**

```python
if is_dst_transition(proposed_datetime, timezone):
    frappe.msgprint("Warning: This time falls during DST transition")
```

---

### 6. Provide Dual-Timezone Display for Public Bookings

**Public API:**

```python
# Always show both department and visitor timezone
display = format_time_slot_display(
    start_time,
    end_time,
    department_timezone,
    visitor_timezone  # Don't skip this
)
```

---

## Testing Considerations

### Critical Test Cases

1. **Basic Conversion**

   - UTC → Local
   - Local → UTC
   - Local A → Local B

2. **DST Transitions**

   - Spring forward (non-existent time)
   - Fall back (ambiguous time)
   - Scheduling across DST boundary

3. **Edge Timezones**

   - UTC+14 (Kiribati)
   - UTC-12 (Baker Island)
   - UTC+00:00 (London - switches to BST)

4. **Date Line Crossing**

   - Tokyo (UTC+9) → Honolulu (UTC-10)
   - Verify date changes correctly

5. **Input Validation**
   - Naive datetimes
   - String inputs
   - Time objects
   - Invalid timezone strings

---

## Performance Considerations

### Pytz Caching

Pytz caches timezone objects internally. Repeated calls are efficient:

```python
# First call: Loads timezone from database
tz1 = pytz.timezone("Europe/Copenhagen")

# Subsequent calls: Retrieved from cache (fast)
tz2 = pytz.timezone("Europe/Copenhagen")
```

### Optimization Tips

1. **Batch Conversions:** Convert once, reuse

   ```python
   # GOOD
   tz = pytz.timezone("Europe/Copenhagen")
   for dt in datetime_list:
       converted = tz.localize(dt)

   # BAD
   for dt in datetime_list:
       tz = pytz.timezone("Europe/Copenhagen")  # Repeated lookup
       converted = tz.localize(dt)
   ```

2. **Avoid String Parsing in Loops**

   ```python
   # GOOD
   dt = get_datetime(dt_string)
   for tz in timezone_list:
       convert_to_timezone(dt, "UTC", tz)

   # BAD
   for tz in timezone_list:
       convert_to_timezone(dt_string, "UTC", tz)  # Parses string every time
   ```

---

## Dependencies

### External Libraries

- **pytz** (v2024.1+): IANA timezone database
  - Comprehensive timezone rules
  - DST handling
  - Historical timezone changes

### Frappe Framework

- **frappe.utils.get_datetime**: ISO string parser
- **frappe.utils.now_datetime**: Current datetime in system timezone
- **frappe.get_value**: Database queries for user/department settings

---

## Future Enhancements

### 1. Browser-Based Timezone Detection

**Current:** Placeholder function returns "UTC"

**Future Implementation:**

```javascript
// Frontend (JavaScript)
const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

// Send to backend via API
frappe.call({
  method: "meeting_manager.api.public.create_customer_booking",
  args: {
    visitor_timezone: userTimezone, // "America/New_York"
  },
});
```

### 2. IP Geolocation Fallback

Use IP address to detect approximate timezone when JavaScript detection fails:

```python
import geoip2.database

def detect_visitor_timezone(request):
    ip = frappe.local.request_ip

    try:
        reader = geoip2.database.Reader('/path/to/GeoLite2-City.mmdb')
        response = reader.city(ip)
        return response.location.time_zone  # "Europe/Copenhagen"
    except:
        return "UTC"
```

### 3. Smart DST Transition Handling

Automatically adjust proposed times during DST transitions:

```python
def smart_schedule(dt, tz):
    if is_dst_transition(dt, tz):
        # Non-existent time: Add 1 hour
        # Ambiguous time: Ask user preference
        return dt + timedelta(hours=1)
    return dt
```

### 4. Recurring Meeting Timezone Stability

For recurring meetings, maintain "2 PM local time" even when DST changes:

```python
def get_next_recurring(base_time, tz):
    # Always 14:00 local, even if UTC offset changes
    return get_next_occurrence_in_timezone("14:00", tz)
```

---

## Conclusion

The timezone utilities module provides a robust, production-ready solution for handling global time scheduling challenges. By leveraging pytz's comprehensive timezone database and implementing careful edge case handling, it ensures accurate time conversions across all scenarios, including DST transitions.

**Key Strengths:**

- UTC-first storage strategy
- Dual-timezone display for clarity
- Comprehensive DST handling
- Graceful fallback mechanisms
- Type-flexible APIs

**Production Checklist:**

- ✅ Handles naive and aware datetimes
- ✅ Validates timezone strings
- ✅ Detects DST transitions
- ✅ Provides user-friendly displays
- ✅ Maintains UTC consistency
- ✅ Optimized for performance

This module forms the foundation for reliable global meeting scheduling in the Meeting Manager system.
