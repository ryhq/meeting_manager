#!/usr/bin/env python3
"""
Test 6: Booking Creation - Validation Failures
Tests various validation failure scenarios
"""

import frappe
from meeting_manager.meeting_manager.api.public import create_customer_booking

print("\n" + "="*80)
print("TEST 6: BOOKING VALIDATION FAILURES")
print("="*80)

test_cases = [
    {
        "name": "Past Date",
        "data": {
            "department_slug": "support",
            "meeting_type_slug": "tech-consultation",
            "scheduled_date": "2024-01-01",  # Past date
            "scheduled_start_time": "10:00",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890"
        },
        "expected_error": "past"
    },
    {
        "name": "Missing Required Field (customer_name)",
        "data": {
            "department_slug": "support",
            "meeting_type_slug": "tech-consultation",
            "scheduled_date": "2025-12-12",
            "scheduled_start_time": "10:00",
            # Missing customer_name
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890"
        },
        "expected_error": "customer_name"
    },
    {
        "name": "Missing Required Field (customer_email)",
        "data": {
            "department_slug": "support",
            "meeting_type_slug": "tech-consultation",
            "scheduled_date": "2025-12-12",
            "scheduled_start_time": "10:00",
            "customer_name": "John Doe",
            # Missing customer_email
            "customer_phone": "+1234567890"
        },
        "expected_error": "customer_email"
    },
    {
        "name": "Invalid Department Slug",
        "data": {
            "department_slug": "nonexistent-dept",  # Invalid
            "meeting_type_slug": "tech-consultation",
            "scheduled_date": "2025-12-12",
            "scheduled_start_time": "10:00",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890"
        },
        "expected_error": "department"
    },
    {
        "name": "Invalid Meeting Type Slug",
        "data": {
            "department_slug": "support",
            "meeting_type_slug": "nonexistent-type",  # Invalid
            "scheduled_date": "2025-12-12",
            "scheduled_start_time": "10:00",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890"
        },
        "expected_error": "meeting type"
    },
    {
        "name": "Conflicting Time Slot (booking on same slot)",
        "data": {
            "department_slug": "support",
            "meeting_type_slug": "tech-consultation",
            "scheduled_date": "2025-12-11",  # Same date as first booking
            "scheduled_start_time": "10:00",  # Same time as first booking
            "customer_name": "Jane Smith",
            "customer_email": "jane@example.com",
            "customer_phone": "+9876543210"
        },
        "expected_error": "available"
    }
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{'─'*80}")
    print(f"Test {i}: {test['name']}")
    print(f"{'─'*80}")

    try:
        result = create_customer_booking(test['data'])
        print(f"   ❌ FAILED - Expected error but booking was created: {result['booking_id']}")
        failed += 1
        frappe.db.rollback()  # Rollback successful bookings in error tests

    except Exception as e:
        error_msg = str(e).lower()
        if test['expected_error'].lower() in error_msg:
            print(f"   ✅ PASSED - Got expected error")
            print(f"   Error: {str(e)}")
            passed += 1
        else:
            print(f"   ⚠️  FAILED - Got different error")
            print(f"   Expected keyword: '{test['expected_error']}'")
            print(f"   Actual error: {str(e)}")
            failed += 1

        frappe.db.rollback()

print(f"\n{'='*80}")
print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print(f"{'='*80}\n")
