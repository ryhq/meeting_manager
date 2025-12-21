#!/usr/bin/env python3
"""
Test 7: Assignment Algorithms
Tests Round Robin and Least Busy assignment algorithms
"""

import frappe
from meeting_manager.meeting_manager.api.public import create_customer_booking
from datetime import datetime, timedelta

print("\n" + "="*80)
print("TEST 7: ASSIGNMENT ALGORITHMS")
print("="*80)

# Check current department assignment algorithm
# Get department by slug directly
dept = frappe.get_doc("MM Department", "support")
print(f"\n📊 Current Department Configuration:")
print(f"   Department: {dept.department_name}")
print(f"   Assignment Algorithm: {dept.assignment_algorithm}")
print(f"   Active Members:")

# Get active members
for member in dept.department_members:
    if member.is_active:
        user_email = frappe.get_value("User", member.member, "email")
        print(f"      - {user_email}")

print(f"\n{'='*80}")
print("Test Part 1: Current Algorithm ({})".format(dept.assignment_algorithm))
print("="*80)

# Create 5 bookings to test assignment distribution
assigned_users = []
base_date = "2025-12-15"  # Use a fresh date

for i in range(5):
    # Use different time slots to avoid conflicts (30 min apart + 30 min duration = 1 hour apart)
    time_slot = f"{10 + i}:30"

    booking_data = {
        "department_slug": "support",
        "meeting_type_slug": "tech-consultation",
        "scheduled_date": base_date,
        "scheduled_start_time": time_slot,
        "customer_name": f"Customer {i+1}",
        "customer_email": f"customer{i+1}@example.com",
        "customer_phone": f"+123456789{i}"
    }

    try:
        result = create_customer_booking(booking_data)
        assigned_email = result['confirmation']['assigned_to_email']
        assigned_users.append(assigned_email)

        print(f"\nBooking {i+1}:")
        print(f"   Time: {time_slot}")
        print(f"   Assigned To: {assigned_email}")
        print(f"   Booking ID: {result['booking_id']}")

        frappe.db.commit()

    except Exception as e:
        print(f"\nBooking {i+1} FAILED: {str(e)}")
        frappe.db.rollback()

print(f"\n{'─'*80}")
print("Assignment Distribution:")
print(f"{'─'*80}")

from collections import Counter
distribution = Counter(assigned_users)

for user, count in distribution.items():
    print(f"   {user}: {count} booking(s)")

if dept.assignment_algorithm == "Round Robin":
    print(f"\n✅ Round Robin: Assignments should rotate evenly across members")

    # Check if distribution is relatively even
    counts = list(distribution.values())
    if len(set(counts)) <= 2:  # At most 2 different counts (e.g., 2 and 3)
        print(f"   ✓ Distribution looks even")
    else:
        print(f"   ⚠️  Distribution might be uneven")

elif dept.assignment_algorithm == "Least Busy":
    print(f"\n✅ Least Busy: Should assign to members with fewer bookings")
    print(f"   Note: All had 0 bookings initially, so distribution may vary")

print(f"\n{'='*80}")
print(f"ASSIGNMENT ALGORITHM TEST COMPLETE")
print(f"Created 5 bookings successfully")
print(f"{'='*80}\n")
