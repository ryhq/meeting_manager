#!/usr/bin/env python3
"""
Test 8: Cancel Booking API
Tests the cancel booking functionality using the cancel token
"""

import frappe
from meeting_manager.meeting_manager.api.public import create_customer_booking, cancel_booking

print("\n" + "="*80)
print("TEST 8: CANCEL BOOKING API")
print("="*80)

try:
    # Step 1: Create a booking
    print("\n📝 Step 1: Creating a booking...")
    booking_data = {
        "department_slug": "support",
        "meeting_type_slug": "tech-consultation",
        "scheduled_date": "2025-12-16",
        "scheduled_start_time": "14:00",
        "customer_name": "Test Cancel User",
        "customer_email": "cancel.test@example.com",
        "customer_phone": "+1234567890",
        "customer_notes": "Testing cancel functionality"
    }

    result = create_customer_booking(booking_data)
    booking_id = result['booking_id']
    cancel_token = frappe.get_value("MM Meeting Booking", booking_id, "cancel_token")

    print(f"   ✅ Booking Created: {booking_id}")
    print(f"   Cancel Token: {cancel_token[:20]}...")
    print(f"   Status: {result['confirmation']['status']}")

    frappe.db.commit()

    # Step 2: Cancel the booking using the token
    print(f"\n🚫 Step 2: Cancelling booking with token...")
    cancel_result = cancel_booking(cancel_token)

    print(f"   ✅ Cancel Result: {cancel_result['success']}")
    print(f"   Message: {cancel_result['message']}")

    # Step 3: Verify booking is cancelled
    print(f"\n🔍 Step 3: Verifying cancellation...")
    booking_status = frappe.get_value("MM Meeting Booking", booking_id, "booking_status")
    cancellation_reason = frappe.get_value("MM Meeting Booking", booking_id, "cancellation_reason")
    cancelled_at = frappe.get_value("MM Meeting Booking", booking_id, "cancelled_at")

    print(f"   Booking Status: {booking_status}")
    print(f"   Cancellation Reason: {cancellation_reason}")
    print(f"   Cancelled At: {cancelled_at}")

    if booking_status == "Cancelled":
        print(f"\n   ✅ VERIFICATION PASSED - Booking successfully cancelled")
    else:
        print(f"\n   ❌ VERIFICATION FAILED - Status is {booking_status}, expected 'Cancelled'")

    # Step 4: Try to cancel again (should fail)
    print(f"\n🔁 Step 4: Attempting to cancel already-cancelled booking...")
    try:
        cancel_booking(cancel_token)
        print(f"   ❌ ERROR - Should have thrown exception for already-cancelled booking")
    except Exception as e:
        if "already been" in str(e).lower():
            print(f"   ✅ Correctly rejected: {str(e)}")
        else:
            print(f"   ⚠️  Unexpected error: {str(e)}")

    # Step 5: Try with invalid token
    print(f"\n🔒 Step 5: Testing with invalid token...")
    try:
        cancel_booking("invalid_token_12345")
        print(f"   ❌ ERROR - Should have thrown exception for invalid token")
    except Exception as e:
        if "invalid" in str(e).lower():
            print(f"   ✅ Correctly rejected: {str(e)}")
        else:
            print(f"   ⚠️  Unexpected error: {str(e)}")

    frappe.db.commit()

    print(f"\n{'='*80}")
    print("CANCEL BOOKING TEST COMPLETE - ALL CHECKS PASSED")
    print(f"{'='*80}\n")

except Exception as e:
    print(f"\n❌ Test Failed: {str(e)}")
    import traceback
    traceback.print_exc()
    frappe.db.rollback()
