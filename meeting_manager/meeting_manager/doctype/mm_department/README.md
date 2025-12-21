# MM Department DocType

## Overview

The **MM Department** DocType is the central management entity for department-based booking in the Meeting Manager system. It enables organizations to set up departments (e.g., Support, Sales, HR) that customers can book meetings with, while the system automatically assigns bookings to available department members using configurable assignment algorithms.

## Business Context

From the [Meeting Manager Project Description](../../../../Meeting_Manager_PD.md):

> **Department-based public booking** - Customers book with departments, not individuals; system auto-assigns to available members using round-robin or least-busy algorithms.

This DocType implements the core requirement that customers interact with departments rather than specific individuals, ensuring even distribution of bookings across team members and preventing overload on any single person.

## Key Features

### 1. Department Configuration
- **Department Name**: Human-readable name (e.g., "Support Department", "Sales Team")
- **Department Slug**: URL-friendly identifier for public booking pages (e.g., "support", "sales")
- **Description**: Rich text description shown on public booking pages
- **Active Status**: Enable/disable public booking for the department

### 2. Assignment Algorithms
The system supports two booking assignment methods:

- **Round Robin**: Distributes bookings evenly by rotating through members based on `last_assigned_datetime`
- **Least Busy**: Assigns to the member with fewest bookings in the next 7 days

### 3. Department Members Management
Child table tracking:
- Member (Link to User)
- Active status
- Assignment priority (for future weighted assignment)
- Last assigned datetime (auto-updated)
- Total assignments count (auto-updated)

### 4. Notification Settings
- **Notify Leader on Booking**: Send email to department leader when new bookings are created
- **Notify Admin on Booking**: Send email to system administrators on new bookings

### 5. Public Booking URL
Auto-generated URL for customer-facing booking page:
```
{site_url}/book/{department_slug}
```

## Field Reference

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `department_name` | Data | Yes | Display name of the department |
| `department_slug` | Data | Yes, Unique | URL-safe identifier (auto-cleaned) |
| `is_active` | Check | No (Default: 1) | Enable/disable public booking |
| `description` | Text Editor | No | Rich text description for public pages |
| `department_leader` | Link (User) | No | Must be an active department member |
| `timezone` | Select | No (Default: Europe/Copenhagen) | Department timezone for all operations |
| `assignment_algorithm` | Select | No (Default: Round Robin) | "Round Robin" or "Least Busy" |
| `notify_leader_on_booking` | Check | No (Default: 1) | Email leader on new bookings |
| `notify_admin_on_booking` | Check | No (Default: 0) | Email admin on new bookings |
| `department_members` | Table | Yes | Child table of department members |
| `public_booking_url` | Data | No (Read-only) | Auto-generated booking URL |

## Child Table: MM Department Member

| Field Name | Type | Description |
|------------|------|-------------|
| `member` | Link (User) | User belonging to this department |
| `is_active` | Check | Only active members receive booking assignments |
| `assignment_priority` | Int | For future weighted assignment (must be > 0) |
| `last_assigned_datetime` | Datetime | Tracks last assignment for round-robin |
| `total_assignments` | Int | Count of all-time assignments |

## Validation Rules

The DocType implements comprehensive validation in [mm_department.py](mm_department.py):

### 1. Department Leader Validation
**Method**: `validate_department_leader()`

- If a department leader is specified, they **must** be present in the Department Members child table
- The leader **must** have `is_active` enabled
- **Error Messages**:
  - "Department Leader '{user}' must be added as a member in the Department Members table."
  - "Department Leader '{user}' must be an active member. Please enable the 'Is Active' checkbox for this member."

**Example**:
```python
# This will fail validation:
department.department_leader = "john@example.com"
department.department_members = []  # Leader not in members list

# This will pass:
department.department_leader = "john@example.com"
department.department_members = [
    {"member": "john@example.com", "is_active": 1}
]
```

### 2. Active Members Validation
**Method**: `validate_active_members()`

- Department **must** have at least one member
- No duplicate members allowed (same user can't be added twice)
- All members must exist as valid Users in the system
- Assignment priority (if set) must be greater than 0
- At least one member must have `is_active` enabled
- **Error Messages**:
  - "Department must have at least one member."
  - "Duplicate members found. Each user can only be added once to the department."
  - "User '{user}' does not exist."
  - "Assignment Priority for member '{user}' must be greater than 0."
  - "Assignment Priority for member '{user}' must be less or equal to 10."
  - "Department must have at least one active member. Please enable 'Is Active' for at least one member."

### 3. Department Slug Validation
**Method**: `validate_department_slug()`

The department slug is automatically cleaned and validated:

**Cleaning Process**:
1. Convert to lowercase
2. Strip leading/trailing whitespace
3. Replace spaces with hyphens
4. Remove any character that isn't: lowercase letter, number, or hyphen
5. Replace consecutive hyphens with single hyphen
6. Remove leading/trailing hyphens

**Validation**:
- Slug must not be empty after cleaning
- Slug must be unique across all departments
- **Error Messages**:
  - "Department Slug is required."
  - "Department Slug must contain at least one letter or number."
  - "Department Slug '{slug}' already exists. Please use a unique slug."

**Examples**:
```python
# Input → Output after cleaning
"Support Team" → "support-team"
"Sales - EMEA" → "sales-emea"
"HR@Department!" → "hrdepartment"
"   dev---ops   " → "dev-ops"
```

### 4. Public Booking URL Generation
**Method**: `set_public_booking_url()`

Automatically generates the public-facing booking URL:
```python
self.public_booking_url = f"{site_url}/book/{self.department_slug}"
```

**Example**:
- Site URL: `https://bestsecurity.local`
- Department Slug: `support`
- Generated URL: `https://bestsecurity.local/book/support`

## Usage Examples

### Creating a Support Department

```python
# Create new department
support_dept = frappe.get_doc({
    "doctype": "MM Department",
    "department_name": "Support Department",
    "department_slug": "support",
    "description": "<p>Our support team is here to help you!</p>",
    "is_active": 1,
    "department_leader": "support-lead@example.com",
    "timezone": "Europe/Copenhagen",
    "assignment_algorithm": "Round Robin",
    "notify_leader_on_booking": 1,
    "notify_admin_on_booking": 0,
    "department_members": [
        {
            "member": "support-lead@example.com",
            "is_active": 1,
            "assignment_priority": 1
        },
        {
            "member": "agent1@example.com",
            "is_active": 1,
            "assignment_priority": 1
        },
        {
            "member": "agent2@example.com",
            "is_active": 1,
            "assignment_priority": 1
        }
    ]
})
support_dept.insert()
```

### Querying Active Departments

```python
# Get all active departments
active_departments = frappe.get_all(
    "MM Department",
    filters={"is_active": 1},
    fields=["name", "department_name", "department_slug", "public_booking_url"]
)

# Get department with members
department = frappe.get_doc("MM Department", "support")
active_members = [m.member for m in department.department_members if m.is_active]
```

### Updating Assignment Count

```python
# After assigning a booking to a member
department = frappe.get_doc("MM Department", "support")
for member in department.department_members:
    if member.member == assigned_user:
        member.last_assigned_datetime = frappe.utils.now_datetime()
        member.total_assignments += 1
        break
department.save()
```

## Integration with Other DocTypes

### Related DocTypes
- **[MM Department Meeting Type](../mm_meeting_type/README.md)**: Meeting types offered by this department
- **[MM Meeting Booking](../mm_meeting_booking/README.md)**: Bookings assigned to department members
- **[MM User Settings](../mm_user_settings/README.md)**: Individual member availability settings
- **[MM User Availability Rule](../mm_user_availability_rule/README.md)**: Member availability constraints

### Assignment Flow
1. Customer selects department on public booking page
2. Customer chooses meeting type (filtered by department)
3. System calculates aggregate availability across all active department members
4. Customer selects date and time
5. System uses `assignment_algorithm` to assign booking to a member:
   - **Round Robin**: Member with oldest `last_assigned_datetime` who is available
   - **Least Busy**: Member with fewest bookings in next 7 days who is available
6. System updates `last_assigned_datetime` and `total_assignments` for assigned member

## Permissions

| Role | Create | Read | Write | Delete | Notes |
|------|--------|------|-------|--------|-------|
| System Manager | ✓ | ✓ | ✓ | ✓ | Full access to all departments |
| Department Leader | - | ✓ | ✓ | - | Read/Write access to their own department(s) |
| Department Member | - | ✓ | - | - | Read-only access to their department(s) |
| Guest | - | ✓ | - | - | Public read access for booking pages |

*Note: Department Leader permissions need to be configured with permission rules based on `department_leader` field.*


### Track Changes
Track changes is **enabled** (`"track_changes": 1`) to maintain audit trail of:
- Member additions/removals
- Assignment algorithm changes
- Leader changes
- Active status changes

## API Endpoints

### Public API
```python
# Get all active departments (public booking)
@frappe.whitelist(allow_guest=True)
def get_departments():
    """Returns all active departments for public booking page"""
    return frappe.get_all(
        "MM Department",
        filters={"is_active": 1},
        fields=["department_name", "department_slug", "description", "public_booking_url"]
    )
```

### Internal API
```python
# Get department members for assignment
@frappe.whitelist()
def get_active_members(department_slug):
    """Returns active members of a department"""
    department = frappe.get_doc("MM Department", department_slug)
    return [
        {
            "member": m.member,
            "last_assigned": m.last_assigned_datetime,
            "total_assignments": m.total_assignments
        }
        for m in department.department_members
        if m.is_active
    ]
```

## Testing Checklist

### Unit Tests
- [ ] Validate department leader must be active member
- [ ] Validate at least one active member required
- [ ] Validate no duplicate members allowed
- [ ] Validate department slug cleaning and uniqueness
- [ ] Validate public booking URL generation
- [ ] Validate assignment priority must be positive

### Integration Tests
- [ ] Test round-robin assignment across multiple bookings
- [ ] Test least-busy assignment with varying member workloads
- [ ] Test notification triggers for leader and admin
- [ ] Test member deactivation doesn't break leader validation
- [ ] Test slug collision handling on concurrent inserts

## Known Limitations

1. **Assignment Algorithm**: Currently only supports Round Robin and Least Busy. Weighted assignment using `assignment_priority` is planned for future release.
2. **Multi-Department Members**: A user can belong to multiple departments, but there's no cross-department coordination of assignments.
3. **Timezone Handling**: All department members work under the department's timezone. Individual member timezone preferences are not yet supported.

**Module**: Meeting Manager
**App**: meeting_manager
