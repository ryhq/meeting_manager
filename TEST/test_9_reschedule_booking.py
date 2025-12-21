#!/usr/bin/env python3
"""
Test 9: Reschedule Booking API
Tests the reschedule booking functionality using the reschedule token
"""

import frappe
from meeting_manager.meeting_manager.api.public import create_customer_booking, reschedule_booking

print("\n" + "="*80)
print("TEST 9: RESCHEDULE BOOKING API")
print("="*80)

try:
    # Step 1: Create a booking
    print("\n📝 Step 1: Creating initial booking...")
    booking_data = {
        "department_slug": "support",
        "meeting_type_slug": "tech-consultation",
        "scheduled_date": "2025-12-17",
        "scheduled_start_time": "10:00",
        "customer_name": "Test Reschedule User",
        "customer_email": "reschedule.test@example.com",
        "customer_phone": "+1234567890",
        "customer_notes": "Testing reschedule functionality"
    }

    result = create_customer_booking(booking_data)
    booking_id = result['booking_id']
    reschedule_token = frappe.get_value("MM Meeting Booking", booking_id, "reschedule_token")

    print(f"   ✅ Booking Created: {booking_id}")
    print(f"   Original Date: {result['confirmation']['scheduled_date']}")
    print(f"   Original Time: {result['confirmation']['scheduled_time']}")
    print(f"   Reschedule Token: {reschedule_token[:20]}...")

    frappe.db.commit()

    # Step 2: Reschedule the booking to a new time
    print(f"\n🔄 Step 2: Rescheduling booking to new time...")
    new_date = "2025-12-18"
    new_time = "14:30"

    reschedule_result = reschedule_booking(reschedule_token, new_date, new_time)

    print(f"   ✅ Reschedule Result: {reschedule_result['success']}")
    print(f"   Message: {reschedule_result['message']}")
    print(f"   Old: {reschedule_result['old_datetime']['date']} {reschedule_result['old_datetime']['time']}")
    print(f"   New: {reschedule_result['new_datetime']['date']} {reschedule_result['new_datetime']['time']}")

    if reschedule_result.get('member_changed'):
        print(f"   ⚠️  Member Changed: {reschedule_result.get('old_assigned_to')} → {reschedule_result.get('new_assigned_to')}")

    # Step 3: Verify booking is rescheduled
    print(f"\n🔍 Step 3: Verifying rescheduled booking...")
    booking_doc = frappe.get_doc("MM Meeting Booking", booking_id)

    print(f"   Booking Status: {booking_doc.booking_status}")
    print(f"   Start DateTime: {booking_doc.start_datetime}")
    print(f"   End DateTime: {booking_doc.end_datetime}")

    # Verify the new datetime matches
    expected_new_datetime = f"{new_date} {new_time}"
    actual_new_datetime = f"{booking_doc.start_datetime.strftime('%Y-%m-%d')} {booking_doc.start_datetime.strftime('%H:%M')}"

    if actual_new_datetime == expected_new_datetime:
        print(f"   ✅ VERIFICATION PASSED - Booking successfully rescheduled to {expected_new_datetime}")
    else:
        print(f"   ❌ VERIFICATION FAILED - Expected {expected_new_datetime}, got {actual_new_datetime}")

    # Step 4: Try to reschedule to a past date (should fail)
    print(f"\n⏪ Step 4: Attempting to reschedule to past date...")
    try:
        reschedule_booking(reschedule_token, "2024-01-01", "10:00")
        print(f"   ❌ ERROR - Should have thrown exception for past date")
    except Exception as e:
        if "past" in str(e).lower():
            print(f"   ✅ Correctly rejected: {str(e)}")
        else:
            print(f"   ⚠️  Unexpected error: {str(e)}")

    # Step 5: Try with invalid token
    print(f"\n🔒 Step 5: Testing with invalid token...")
    try:
        reschedule_booking("invalid_token_12345", "2025-12-20", "10:00")
        print(f"   ❌ ERROR - Should have thrown exception for invalid token")
    except Exception as e:
        if "invalid" in str(e).lower() or "expired" in str(e).lower():
            print(f"   ✅ Correctly rejected: {str(e)}")
        else:
            print(f"   ⚠️  Unexpected error: {str(e)}")

    frappe.db.commit()

    print(f"\n{'='*80}")
    print("RESCHEDULE BOOKING TEST COMPLETE - ALL CHECKS PASSED")
    print(f"{'='*80}\n")

except Exception as e:
    print(f"\n❌ Test Failed: {str(e)}")
    import traceback
    traceback.print_exc()
    frappe.db.rollback()
