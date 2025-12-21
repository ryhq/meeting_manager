# Reschedule & Cancel Booking Flow

## Overview

This document describes the complete customer self-service flow for rescheduling and canceling bookings using secure token-based authentication.

## Security Model

### Token Generation
- **Cancel Token**: 32-byte URL-safe random token generated at booking creation
- **Reschedule Token**: 32-byte URL-safe random token generated at booking creation
- Both tokens are regenerated after each reschedule to prevent token reuse

### Token Lifecycle
1. **Initial Booking**: Tokens generated and included in confirmation email
2. **Reschedule**: Old tokens invalidated, new tokens generated and sent via email
3. **Cancel**: Tokens become invalid after cancellation (booking status = Cancelled)

### Security Features
- Tokens are unique per booking
- Tokens are invalidated after use (reschedule) or status change (cancel)
- No authentication required - token serves as bearer credential
- Tokens are long and random (256 bits of entropy)

## Reschedule Flow

### User Journey

1. **Email Link Click**
   - Customer receives confirmation email with reschedule link
   - Link format: `https://yoursite.com/reschedule-booking?token={reschedule_token}`

2. **Reschedule Page**
   - Page: `/reschedule-booking/index.py`
   - Validates token and loads current booking details
   - Shows current booking information
   - Displays date picker for new date
   - Loads available time slots for selected date via AJAX

3. **Date Selection**
   - Customer selects new date (must be today or future)
   - JavaScript calls `get_available_time_slots` API
   - Time slots are populated dynamically based on availability

4. **Time Selection**
   - Customer selects from available time slots
   - Submit button becomes enabled

5. **Reschedule Submission**
   - Form submits to `reschedule_booking` API
   - API validates token, date, and time
   - Checks member availability
   - Reassigns to different member if needed
   - **Regenerates both tokens**
   - Updates booking record
   - Logs action in booking history
   - Sends new confirmation email with new tokens

6. **Success Page**
   - Shows old vs new date/time
   - Indicates if member was reassigned
   - Confirms new email will be sent

### Backend Functions

#### `get_booking_details(token)`
**File**: `api/public.py:475`

**Purpose**: Retrieve booking details for reschedule form

**Parameters**:
- `token` (str): Reschedule token

**Returns**:
```python
{
    "booking_id": str,
    "department": {
        "department_name": str,
        "department_slug": str,
        "timezone": str
    },
    "meeting_type": {
        "meeting_name": str,
        "meeting_slug": str
    },
    "current_date": str (YYYY-MM-DD),
    "current_time": str (HH:MM),
    "duration": int (minutes),
    "customer_name": str,
    "customer_email": str,
    "status": str
}
```

**Validation**:
- Token must exist in database
- Booking status must not be Cancelled or Completed

#### `reschedule_booking(token, new_date, new_time)`
**File**: `api/public.py:528`

**Purpose**: Reschedule a booking to new date/time

**Parameters**:
- `token` (str): Reschedule token
- `new_date` (str): New date in YYYY-MM-DD format
- `new_time` (str): New time in HH:MM format

**Process**:
1. Validate token and booking status
2. Validate new date (not in past)
3. Check current assigned member availability
4. If unavailable, auto-assign to another member
5. Update booking datetime
6. **Regenerate cancel_token and reschedule_token** ✓
7. Add entry to booking_history
8. Save booking
9. **Send confirmation email with new tokens** ✓
10. Return success response

**Returns**:
```python
{
    "success": True,
    "message": str,
    "booking_id": str,
    "old_datetime": {
        "date": str,
        "time": str
    },
    "new_datetime": {
        "date": str,
        "time": str
    },
    "member_changed": bool (optional),
    "old_assigned_to": str (optional),
    "new_assigned_to": str (optional)
}
```

**Token Regeneration Code**:
```python
# Regenerate security tokens for new booking
import secrets
booking.cancel_token = secrets.token_urlsafe(32)
booking.reschedule_token = secrets.token_urlsafe(32)
```

## Cancel Flow

### User Journey

1. **Email Link Click**
   - Customer receives confirmation email with cancel link
   - Link format: `https://yoursite.com/cancel-booking?token={cancel_token}`

2. **Confirmation Page**
   - Page: `/cancel-booking/index.py`
   - Validates token and loads booking details
   - Shows full booking information
   - Displays warning about cancellation being permanent
   - Shows "Confirm Cancellation" button

3. **Cancel Confirmation**
   - Customer clicks "Confirm Cancellation"
   - Form submits with `?confirmed=1` parameter
   - Calls `cancel_booking` API

4. **Cancellation Processing**
   - API validates token
   - Updates booking status to "Cancelled"
   - Sets cancellation_reason and cancelled_at
   - Sends cancellation emails to customer and team
   - Returns success response

5. **Success Page**
   - Shows cancellation confirmation
   - Indicates email will be sent

### Backend Functions

#### `cancel_booking(token)`
**File**: `api/public.py:417`

**Purpose**: Cancel a booking using cancel token

**Parameters**:
- `token` (str): Cancel token

**Process**:
1. Validate token exists
2. Check booking not already cancelled/completed
3. Update booking status to "Cancelled"
4. Set cancellation_reason = "Customer Cancelled"
5. Set cancelled_at timestamp
6. Save booking
7. Send cancellation emails to customer and team
8. Return success response

**Returns**:
```python
{
    "success": True,
    "message": "Your booking has been cancelled successfully. A confirmation email has been sent."
}
```

**Email Notifications**:
- Calls `send_cancellation_email(booking.name)`
- Sends to customer (confirmation)
- Sends to assigned team members (notification)
- Uses template: `templates/emails/booking_cancellation.html`

## Email Notifications

### Confirmation Email (After Reschedule)
**Template**: `templates/emails/booking_confirmation_customer.html`

**Contains**:
- Updated booking reference
- New date/time
- Assigned team member(s)
- **New cancel link** with new cancel_token
- **New reschedule link** with new reschedule_token

### Cancellation Email
**Template**: `templates/emails/booking_cancellation.html`

**Contains**:
- Cancelled booking details
- Cancellation confirmation
- Link to book another meeting

## Web Routes

### Reschedule Page
- **Path**: `/reschedule-booking`
- **File**: `www/reschedule-booking/index.py`
- **Template**: `www/reschedule-booking/index.html`
- **Method**: GET (form display), POST (reschedule submission)
- **Authentication**: Token-based (no login required)

### Cancel Page
- **Path**: `/cancel-booking`
- **File**: `www/cancel-booking/index.py`
- **Template**: `www/cancel-booking/index.html`
- **Method**: GET
- **Authentication**: Token-based (no login required)

## Testing

### Manual Test Steps

1. **Create a booking** through the public API
2. **Check confirmation email** for reschedule and cancel links
3. **Click reschedule link** and verify:
   - Token is valid
   - Current booking details are shown
   - Date picker works
   - Time slots load dynamically
4. **Reschedule the booking** and verify:
   - Booking is updated in database
   - Status changes to "Rescheduled"
   - New tokens are generated
   - Old tokens are invalid
   - New confirmation email is sent
   - Email contains new tokens
5. **Click cancel link** (from new email) and verify:
   - Token is valid
   - Confirmation page shows
   - Cancellation processes correctly
   - Status changes to "Cancelled"
   - Cancellation emails are sent

### Automated Test Script
Run: `bench --site bestsecurity.local console < test_reschedule_cancel_flow.py`

### Security Tests

1. **Old Token Invalidation**
   - After reschedule, old reschedule_token should fail
   - Old cancel_token should fail

2. **Token Reuse Prevention**
   - Using same token twice for reschedule should fail
   - Using cancel token after cancellation should fail

3. **Status Validation**
   - Cannot reschedule cancelled booking
   - Cannot cancel completed booking
   - Cannot cancel already cancelled booking

## Database Schema

### Token Fields (MM Meeting Booking)
```json
{
  "fieldname": "cancel_token",
  "fieldtype": "Data",
  "label": "Cancel Token",
  "read_only": 1
}
```

```json
{
  "fieldname": "reschedule_token",
  "fieldtype": "Data",
  "label": "Reschedule Token",
  "read_only": 1
}
```

### Booking History (Child Table)
Logs all reschedule actions:
```json
{
  "action": "Rescheduled",
  "action_by": "Guest",
  "action_datetime": "2025-12-11 17:00:00",
  "old_value": "2025-12-13 10:00",
  "new_value": "2025-12-15 14:00",
  "notes": "Customer rescheduled via reschedule link"
}
```

## API Endpoints

All endpoints in `meeting_manager.meeting_manager.api.public`

### Get Booking Details
```python
@frappe.whitelist(allow_guest=True)
def get_booking_details(token)
```

### Reschedule Booking
```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def reschedule_booking(token, new_date, new_time)
```

### Cancel Booking
```python
@frappe.whitelist(allow_guest=True)
def cancel_booking(token)
```

## Error Handling

### Common Errors

1. **Invalid Token**
   - Message: "Invalid or expired link"
   - Cause: Token doesn't exist in database
   - Solution: User must use latest email link

2. **Booking Already Cancelled**
   - Message: "This booking has already been cancelled"
   - Cause: Booking status is "Cancelled"
   - Solution: No action needed, inform user

3. **Date in Past**
   - Message: "Cannot reschedule to a date in the past"
   - Cause: Selected date < today
   - Solution: User must select future date

4. **No Available Members**
   - Message: "No members are available at the requested time"
   - Cause: All department members are busy
   - Solution: User must select different time slot

## Best Practices

1. **Always regenerate tokens** after reschedule
2. **Always send confirmation email** with new tokens after reschedule
3. **Log all actions** in booking history for audit trail
4. **Validate tokens** before any state change
5. **Check booking status** before allowing reschedule/cancel
6. **Use HTTPS** for all token-based URLs
7. **Set email to send immediately** (`now=True`) for better UX

## Future Enhancements

1. **Rate Limiting**: Limit reschedules per booking (e.g., max 3 times)
2. **Reschedule Deadline**: Prevent reschedule within X hours of meeting
3. **Cancel Deadline**: Prevent cancel within X hours of meeting
4. **SMS Notifications**: Send SMS in addition to email
5. **Calendar Invites**: Attach ICS files to emails
6. **Multi-language Support**: Translate emails and pages
7. **Custom Cancellation Reasons**: Allow customer to provide reason
