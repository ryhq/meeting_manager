#!/usr/bin/env python3
"""
Test 5: Create Customer Booking
Tests the complete booking creation flow
"""

import frappe
from frappe.utils import getdate
from meeting_manager.meeting_manager.api.public import create_customer_booking

print("\n" + "="*80)
print("TEST 5: CREATE CUSTOMER BOOKING")
print("="*80)

try:
    # Booking data
    booking_data = {
        "department_slug": "support",
        "meeting_type_slug": "tech-consultation",
        "scheduled_date": "2025-12-11",
        "scheduled_start_time": "10:00",
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "customer_phone": "+1234567890",
        "customer_notes": "Need help with API integration",
        "visitor_timezone": "America/New_York"
    }

    print(f"\n📋 Booking Request:")
    print(f"   Department: {booking_data['department_slug']}")
    print(f"   Meeting Type: {booking_data['meeting_type_slug']}")
    print(f"   Date: {booking_data['scheduled_date']}")
    print(f"   Time: {booking_data['scheduled_start_time']}")
    print(f"   Customer: {booking_data['customer_name']}")
    print(f"   Email: {booking_data['customer_email']}")

    # Create booking
    result = create_customer_booking(booking_data)

    print(f"\n✅ Booking Created Successfully!")
    print(f"\n📝 Booking Details:")
    print(f"   Booking ID: {result['booking_id']}")
    print(f"   Meeting Type: {result['confirmation']['meeting_type']}")
    print(f"   Date: {result['confirmation']['scheduled_date']}")
    print(f"   Time: {result['confirmation']['scheduled_time']}")
    print(f"   Duration: {result['confirmation']['duration']} minutes")
    print(f"   Status: {result['confirmation']['status']}")
    print(f"   Assigned To: {result['confirmation']['assigned_to_email']}")

    print(f"\n🔗 Customer Self-Service Links:")
    print(f"   Cancel: {result['cancel_url']}")
    print(f"   Reschedule: {result['reschedule_url']}")

    print(f"\n💬 Message: {result['confirmation']['message']}")

    frappe.db.commit()

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    frappe.db.rollback()

print("\n" + "="*80)
