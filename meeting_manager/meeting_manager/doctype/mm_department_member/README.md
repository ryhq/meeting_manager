# MM Department Member - Child Table Documentation

## Overview

**MM Department Member** is a child table of **MM Department** that represents individual team members who are part of a department. Each member can receive automatic booking assignments based on the department's assignment algorithm (Round Robin or Least Busy). This child table tracks assignment statistics and priorities for each member.

**Parent DocType**: MM Department

**Child Table**: Yes (`istable: 1`)

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md), department members are the users who:

1. **Receive Automatic Assignments**: When customers book meetings with a department, the system automatically assigns bookings to available members based on the department's assignment algorithm.

2. **Have Individual Availability**: Each member has their own working hours, availability rules, date overrides, and calendar integrations; That determine when they can receive bookings.

3. **Track Assignment History**: The system tracks how many bookings each member has received and when they were last assigned, enabling fair distribution.

4. **Priority-Based Assignment**: Members can have different assignment priorities (1-10) for future weighted assignment algorithms.

**Key Product Requirements**:
- Track which users belong to which departments
- Support multiple departments per user (users can be in Sales AND Support)
- Track assignment statistics (total assignments, last assigned time)
- Enable/disable members without removing them
- Support future weighted assignment based on priority

---

## Key Features

### 1. **Member Tracking**
- Links to system User (frappe User DocType)
- Validates user exists and is enabled
- Prevents duplicate members in same department

### 2. **Active/Inactive Status**
- `is_active` flag to temporarily disable member
- Inactive members excluded from assignment algorithms
- Useful for temporary absences or role changes

### 3. **Assignment Priority**
- Integer value 1-10 (default: 1)
- Higher priority = more likely to receive assignments (in weighted algorithms)
- Currently informational, will be used in future weighted assignment feature

### 4. **Assignment Tracking**
- `total_assignments`: Count of bookings assigned to this member
- `last_assigned_datetime`: Timestamp of most recent assignment
- Auto-updated by assignment algorithm
- Used for Round Robin and Least Busy calculations

---

## Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `member` | Link (User) | Yes | - | Team member user account |
| `is_active` | Check | No | 1 | Enable/disable this member for assignments |
| `assignment_priority` | Int | No | 1 | Priority for weighted assignment (1-10, higher = more assignments) |
| `total_assignments` | Int | No | 0 | Total bookings assigned to this member (read-only, auto-updated) |
| `last_assigned_datetime` | Datetime | No | - | Last time member was assigned a booking (read-only, auto-updated) |

---

## Validation Rules

The child table includes **3 validation methods** ensuring data integrity:

### 1. Member Existence Validation (`validate_member_exists`)

**Validates**:
- Member field is not empty
- User exists in User DocType
- Warns if user is disabled (not enabled)

**Error Messages**:
- `"Member is required."`
- `"User '{member}' does not exist."`

**Warnings**:
- `"Warning: User '{member}' is disabled. Consider removing them from the department or enabling their account."` (orange indicator)

### 2. Member Uniqueness Validation (`validate_member_unique`)

**Validates**:
- Member is not already in the department
- Checks all rows in parent's members table
- Excludes current row when checking duplicates (allows updates)

**Error Messages**:
- `"Member '{member}' is already in this department. Each user can only be added once per department."`

**Example**:
- ✅ Valid: User in Support department only (once)
- ✅ Valid: User in both Support department and Sales department (different departments)
- ❌ Invalid: User added twice to Support department

### 3. Assignment Priority Validation (`validate_assignment_priority`)

**Validates**:
- Priority is within acceptable range (1-10)
- Auto-sets to 1 if not provided
- Provides guidance for high priority values

**Error Messages**:
- `"Assignment Priority must be at least 1."`
- `"Assignment Priority cannot exceed 10."`

**Info Messages**:
- `"High assignment priority ({priority}) - This member will be favored for assignment in weighted algorithms."` (blue indicator, shown when priority > 5)

**Priority Guidelines**:
- **1-3**: Lower priority (junior team members, part-time)
- **4-6**: Normal priority (standard team members)
- **7-10**: High priority (senior team members, specialists)

---

## Use Cases

### Use Case 1: Adding Members to New Department

**Scenario**: Creating a Support department with 3 team members.

```python
import frappe

# Create department with members
department = frappe.get_doc({
    "doctype": "MM Department",
    "department_name": "Support Team",
    "slug": "support",
    "assignment_algorithm": "Round Robin",
    "members": [
        {
            "member": "sarah@bestsecurity.com",
            "is_active": 1,
            "assignment_priority": 5  # Normal priority
        },
        {
            "member": "mike@bestsecurity.com",
            "is_active": 1,
            "assignment_priority": 3  # Lower priority (junior)
        },
        {
            "member": "jane@bestsecurity.com",
            "is_active": 1,
            "assignment_priority": 8  # High priority (senior)
        }
    ]
})

department.insert()

print(f"Department created with {len(department.members)} members")
```

**Result**:
- All 3 members added to Support department
- Jane has highest priority (8) - will get more assignments in weighted algorithms
- Mike has lowest priority (3) - will get fewer assignments
- All members active and ready to receive bookings

### Use Case 2: Temporarily Disabling Member (Vacation)

**Scenario**: Sarah is going on vacation for 2 weeks. Temporarily disable her without removing from department.

```python
import frappe

# Get department
department = frappe.get_doc("MM Department", "MM-DEPT-support")

# Find Sarah's member row
for member in department.members:
    if member.member == "sarah@bestsecurity.com":
        member.is_active = 0  # Disable during vacation
        break

department.save()

print("Sarah disabled from assignment during vacation")

# --- 2 weeks later ---

# Re-enable Sarah
for member in department.members:
    if member.member == "sarah@bestsecurity.com":
        member.is_active = 1  # Re-enable after vacation
        break

department.save()

print("Sarah re-enabled for assignments")
```

**Result**:
- Sarah excluded from assignment algorithm while `is_active = 0`
- All bookings go to Mike and Jane during vacation
- Sarah's assignment history preserved
- Easy to re-enable when back from vacation

### Use Case 3: Tracking Assignment Statistics

**Scenario**: View assignment distribution across department members.

```python
import frappe

def get_department_assignment_stats(department_name):
    """
    Get assignment statistics for all department members

    Args:
        department_name: Name of MM Department

    Returns:
        list: Members with assignment stats
    """
    department = frappe.get_doc("MM Department", department_name)

    stats = []
    for member in department.members:
        # Get user details
        user_details = frappe.get_value(
            "User",
            member.member,
            ["full_name", "email"],
            as_dict=True
        )

        stats.append({
            "member": member.member,
            "full_name": user_details.full_name,
            "is_active": member.is_active,
            "priority": member.assignment_priority,
            "total_assignments": member.total_assignments,
            "last_assigned": member.last_assigned_datetime,
            "status": "Active" if member.is_active else "Inactive"
        })

    # Sort by total assignments (descending)
    stats.sort(key=lambda x: x['total_assignments'], reverse=True)

    return stats

# Usage
stats = get_department_assignment_stats("MM-DEPT-support")

print("Department Assignment Statistics:")
print(f"{'Member':<30} {'Status':<10} {'Priority':<10} {'Assignments':<15} {'Last Assigned'}")
print("-" * 100)

for member in stats:
    print(f"{member['full_name']:<30} {member['status']:<10} {member['priority']:<10} "
          f"{member['total_assignments']:<15} {member['last_assigned'] or 'Never'}")
```

**Output Example**:
```
Department Assignment Statistics:
Member                         Status     Priority   Assignments     Last Assigned
----------------------------------------------------------------------------------------------------
Sarah Johnson                  Active     5          42              2025-12-08 14:30:00
Jane Smith                     Active     8          38              2025-12-08 13:15:00
Mike Brown                     Active     3          25              2025-12-08 11:00:00
```

### Use Case 4: Adjusting Priority for Senior Member

**Scenario**: Jane is promoted to senior support specialist. Increase her priority to receive more complex cases.

```python
import frappe

# Get department
department = frappe.get_doc("MM Department", "MM-DEPT-support")

# Update Jane's priority
for member in department.members:
    if member.member == "jane@bestsecurity.com":
        old_priority = member.assignment_priority
        member.assignment_priority = 9  # Increase to high priority
        print(f"Jane's priority updated: {old_priority} → 9")
        break

department.save()

# System will show info message:
# "High assignment priority (9) - This member will be favored for assignment in weighted algorithms."
```

**Result**:
- Jane's priority increased from 8 to 9
- In future weighted assignment algorithm, Jane will receive more bookings
- Blue info message shown to confirm high priority

### Use Case 5: Preventing Duplicate Member Addition

**Scenario**: Accidentally trying to add Sarah to Support department twice.

```python
import frappe

# Get department
department = frappe.get_doc("MM Department", "MM-DEPT-support")

# Try to add Sarah again (she's already a member)
department.append("members", {
    "member": "sarah@bestsecurity.com",
    "is_active": 1,
    "assignment_priority": 5
})

try:
    department.save()
except frappe.ValidationError as e:
    print(f"Error: {str(e)}")
    # Output: "Member 'sarah@bestsecurity.com' is already in this department.
    #          Each user can only be added once per department."
```

**Result**:
- Validation prevents duplicate
- Error message clearly explains the issue
- Sarah remains in department once (not duplicated)

---

## Integration with Other DocTypes

### MM Department (Parent)

**Relationship**: Child table of MM Department

**Integration Points**:
- Department's `assignment_algorithm` determines how members are selected for bookings
- Department's `leader` must be one of the members (validated in parent)
- Active members only considered for assignment

**Assignment Algorithms**:

1. **Round Robin**:
   - Uses `last_assigned_datetime` to track rotation
   - Assigns to member who was assigned longest ago
   - Ensures equal distribution

2. **Least Busy**:
   - Uses `total_assignments` to find least loaded member
   - Assigns to member with fewest current bookings
   - Balances workload

### MM Meeting Booking (Assignment Target)

**Relationship**: Members receive booking assignments

**Flow**:
```
Customer books meeting
  ↓
MM Department: "Support"
  ↓
Assignment Algorithm (Round Robin or Least Busy)
  ↓
Select MM Department Member (active members only)
  ↓
MM Meeting Booking assigned to selected member
  ↓
Update member's total_assignments++
Update member's last_assigned_datetime
```

### User (System DocType)

**Relationship**: Each member links to a Frappe User

**Integration Points**:
- Member must be valid, existing user
- User's enabled status affects assignment eligibility
- User's full_name displayed in department lists
- User's availability settings (MM User Settings, MM User Availability Rule) checked during assignment

---

## Usage Examples

### Example 1: Adding New Member to Department

```python
import frappe

def add_member_to_department(department_name, user_email, priority=5):
    """
    Add a new member to a department

    Args:
        department_name: Name of MM Department
        user_email: Email of user to add
        priority: Assignment priority (1-10, default 5)

    Returns:
        Updated department document
    """
    # Verify user exists
    if not frappe.db.exists("User", user_email):
        frappe.throw(f"User '{user_email}' does not exist.")

    # Get department
    department = frappe.get_doc("MM Department", department_name)

    # Check if already a member
    for member in department.members:
        if member.member == user_email:
            frappe.throw(f"User '{user_email}' is already a member of this department.")

    # Add member
    department.append("members", {
        "member": user_email,
        "is_active": 1,
        "assignment_priority": priority,
        "total_assignments": 0  # Start at zero
    })

    department.save()

    print(f"Added {user_email} to {department.department_name} (Priority: {priority})")

    return department

# Usage
add_member_to_department("MM-DEPT-support", "alex@bestsecurity.com", priority=5)
```

### Example 2: Bulk Update Member Status

```python
import frappe

def bulk_disable_members(department_name, user_emails, reason=""):
    """
    Disable multiple members at once (useful for team absences)

    Args:
        department_name: Name of MM Department
        user_emails: List of user emails to disable
        reason: Reason for disabling (for logging)

    Returns:
        Number of members disabled
    """
    department = frappe.get_doc("MM Department", department_name)

    disabled_count = 0
    for member in department.members:
        if member.member in user_emails and member.is_active:
            member.is_active = 0
            disabled_count += 1
            print(f"Disabled {member.member} - {reason}")

    if disabled_count > 0:
        department.save()

    return disabled_count

# Usage: Disable entire team for company holiday
team_emails = [
    "sarah@bestsecurity.com",
    "mike@bestsecurity.com",
    "jane@bestsecurity.com"
]

disabled = bulk_disable_members(
    "MM-DEPT-support",
    team_emails,
    "Company holiday - Dec 25-26"
)

print(f"Disabled {disabled} members for holiday")
```

### Example 3: Get Next Available Member (Round Robin)

```python
import frappe
from frappe.utils import now_datetime

def get_next_member_round_robin(department_name):
    """
    Get next member for assignment using round robin algorithm

    Args:
        department_name: Name of MM Department

    Returns:
        Email of next member to assign
    """
    department = frappe.get_doc("MM Department", department_name)

    # Filter active members only
    active_members = [m for m in department.members if m.is_active]

    if not active_members:
        frappe.throw("No active members in this department.")

    # Find member who was assigned longest ago (or never assigned)
    next_member = None
    oldest_assignment = now_datetime()

    for member in active_members:
        if not member.last_assigned_datetime:
            # Never assigned - highest priority
            next_member = member
            break
        elif member.last_assigned_datetime < oldest_assignment:
            oldest_assignment = member.last_assigned_datetime
            next_member = member

    if not next_member:
        # All have same timestamp or no assignments - pick first
        next_member = active_members[0]

    return next_member.member

# Usage
next_user = get_next_member_round_robin("MM-DEPT-support")
print(f"Next member for assignment: {next_user}")
```

### Example 4: Get Least Busy Member

```python
import frappe

def get_least_busy_member(department_name):
    """
    Get member with fewest current assignments (Least Busy algorithm)

    Args:
        department_name: Name of MM Department

    Returns:
        Email of least busy member
    """
    department = frappe.get_doc("MM Department", department_name)

    # Filter active members only
    active_members = [m for m in department.members if m.is_active]

    if not active_members:
        frappe.throw("No active members in this department.")

    # Find member with lowest total_assignments
    least_busy = min(active_members, key=lambda m: m.total_assignments or 0)

    print(f"Least busy member: {least_busy.member} ({least_busy.total_assignments} assignments)")

    return least_busy.member

# Usage
least_busy_user = get_least_busy_member("MM-DEPT-support")
print(f"Assign next booking to: {least_busy_user}")
```

### Example 5: Reset Assignment Statistics (New Period)

```python
import frappe

def reset_department_assignments(department_name, reason=""):
    """
    Reset assignment statistics for all members (e.g., start of new quarter)

    Args:
        department_name: Name of MM Department
        reason: Reason for reset (for logging)

    Returns:
        Number of members reset
    """
    department = frappe.get_doc("MM Department", department_name)

    reset_count = 0
    for member in department.members:
        if member.total_assignments > 0 or member.last_assigned_datetime:
            old_total = member.total_assignments
            member.total_assignments = 0
            member.last_assigned_datetime = None
            print(f"Reset {member.member}: {old_total} assignments → 0")
            reset_count += 1

    if reset_count > 0:
        department.save()
        print(f"Reset {reset_count} members - {reason}")

    return reset_count

# Usage: Reset at start of new quarter
reset = reset_department_assignments(
    "MM-DEPT-support",
    "Q1 2026 - Starting fresh assignment tracking"
)
```

---

## Best Practices

### For Department Management

1. **Active Status Management**:
   - Use `is_active = 0` for temporary absences (vacations, sick leave)
   - Don't delete members - disable them to preserve history
   - Re-enable members when they return

2. **Assignment Priority Guidelines**:
   - Start all members at priority 5 (normal)
   - Adjust based on seniority, expertise, capacity
   - Use 1-3 for part-time or junior members
   - Use 7-10 for senior or specialized members

3. **Member Validation**:
   - Always verify user exists before adding
   - Check for duplicates before manual additions
   - Ensure user has proper availability settings configured

### For Assignment Tracking

1. **Round Robin**:
   - Track `last_assigned_datetime` accurately
   - Update immediately after assignment
   - Handle null values (never assigned) with highest priority

2. **Least Busy**:
   - Increment `total_assignments` after each booking
   - Decrement when bookings are cancelled (optional)
   - Consider implementing periodic resets (monthly/quarterly)

3. **Weighted Assignment (Future)**:
   - Use `assignment_priority` to weight random selection
   - Higher priority = proportionally more assignments
   - Combine with availability checks

### For Performance

1. **Filtering Active Members**:
   - Always filter `is_active = 1` before assignment logic
   - Cache active member list if queried frequently
   - Update cache when members added/removed

2. **Assignment Statistics**:
   - Update asynchronously if possible (background job)
   - Avoid blocking booking creation on stat updates
   - Index `last_assigned_datetime` for Round Robin queries

---

## Known Limitations

1. **No Built-in Assignment Logic**: This child table only stores data. Assignment algorithm logic must be implemented separately in assignment service.

2. **Total Assignments Never Decrements**: If bookings are cancelled, `total_assignments` doesn't automatically decrease. Consider manual resets or periodic reconciliation.

3. **No Time-Based Priority**: Current priority is static. Consider implementing time-weighted priority (e.g., recent assignments decrease effective priority temporarily).

4. **Single Department View**: To see all departments a user belongs to, must query all departments (not optimized for "user's departments" lookup).

5. **No Capacity Limits**: Assignment priority and statistics don't enforce capacity limits. Must check `MM User Availability Rule` separately for `max_bookings_per_day/week`.

---

## See Also

- [MM Department](../mm_department/README.md) - Parent department configuration
- [MM Meeting Booking](../mm_meeting_booking/README.md) - Booking assignments
- [MM User Settings](../mm_user_settings/README.md) - Member working hours
- [MM User Availability Rule](../mm_user_availability_rule/README.md) - Member availability constraints
- [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md) - Assignment algorithm specifications

---

## Contributing

When modifying this child table:

1. **Adding Fields**:
   - Update JSON field_order
   - Add validation if needed
   - Update this README
   - Consider impact on assignment algorithms

2. **Changing Validation**:
   - Update validation methods
   - Document error messages
   - Add test cases
   - Ensure backward compatibility

3. **Assignment Statistics**:
   - If changing how statistics are tracked, provide migration script
   - Update assignment algorithm implementations
   - Document calculation methodology

---

**Last Updated**: 2025-12-08
**Version**: 1.0
**Maintainer**: Best Security Development Team
