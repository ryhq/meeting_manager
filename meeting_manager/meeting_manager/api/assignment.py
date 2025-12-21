# Copyright (c) 2025, Best Security and contributors
# For license information, please see license.txt

"""
Assignment Algorithm Service

This module implements assignment algorithms for automatically
assigning bookings to department members:
- Round Robin: Fair rotation based on last assigned time
- Least Busy: Assign to member with fewest bookings
"""

import frappe
from frappe.utils import getdate, get_time, now_datetime, add_to_date
from datetime import datetime, timedelta
from meeting_manager.meeting_manager.utils.validation import check_member_availability


def assign_to_member(department, meeting_type, scheduled_date, scheduled_start_time, duration_minutes):
	"""
	Automatically assign a booking to an available department member

	Uses the department's assignment algorithm (Round Robin or Least Busy)

	Args:
		department (str): Department ID
		meeting_type (str): Meeting Type ID
		scheduled_date (date or str): Scheduled date
		scheduled_start_time (time or str): Scheduled start time
		duration_minutes (int): Meeting duration

	Returns:
		dict: {
			"assigned_to": user ID,
			"assignment_method": "Round Robin" or "Least Busy",
			"reason": explanation of assignment
		}
	"""
	# Get department configuration
	dept = frappe.get_doc("MM Department", department)

	if not dept.assignment_algorithm:
		frappe.throw("Department does not have an assignment algorithm configured")

	# Get active members
	active_members = [m for m in dept.department_members if m.is_active]

	if not active_members:
		frappe.throw(f"No active members in department '{dept.department_name}'")

	# Check which members are available at the requested time
	available_members = []

	for member in active_members:
		availability = check_member_availability(
			member.member,
			scheduled_date,
			scheduled_start_time,
			duration_minutes
		)

		if availability["available"]:
			available_members.append(member)

	if not available_members:
		frappe.throw(
			f"No members available in department '{dept.department_name}' at the requested time. "
			"Please choose a different time slot."
		)

	# Apply assignment algorithm
	if dept.assignment_algorithm == "Round Robin":
		assigned_member = assign_round_robin(available_members)
		assignment_method = "Round Robin"
	elif dept.assignment_algorithm == "Least Busy":
		assigned_member = assign_least_busy(available_members, scheduled_date)
		assignment_method = "Least Busy"
	else:
		# Default to round robin
		assigned_member = assign_round_robin(available_members)
		assignment_method = "Round Robin (default)"

	# Update member assignment tracking
	update_member_assignment_tracking(dept.name, assigned_member.member)

	return {
		"assigned_to": assigned_member.member,
		"assignment_method": assignment_method,
		"reason": f"Assigned using {assignment_method} algorithm"
	}


def assign_round_robin(available_members):
	"""
	Assign to member with oldest last_assigned_datetime

	This ensures fair rotation among all members

	Args:
		available_members (list): List of MM Department Member objects

	Returns:
		MM Department Member: Selected member
	"""
	# Sort by last_assigned_datetime (oldest first)
	# Members who have never been assigned (None) should come first
	sorted_members = sorted(
		available_members,
		key=lambda m: m.last_assigned_datetime or datetime(1970, 1, 1)
	)

	return sorted_members[0]


def assign_least_busy(available_members, scheduled_date):
	"""
	Assign to member with fewest confirmed/pending bookings in next 7 days

	This balances workload across team members

	Args:
		available_members (list): List of MM Department Member objects
		scheduled_date (date): Date of the new booking

	Returns:
		MM Department Member: Selected member
	"""
	scheduled_date = getdate(scheduled_date)
	week_end = scheduled_date + timedelta(days=7)

	# Count bookings for each member
	member_booking_counts = []

	for member in available_members:
		# Query the child table for assigned bookings
		assigned_bookings = frappe.get_all(
			"MM Meeting Booking Assigned User",
			filters={
				"user": member.member
			},
			fields=["parent"]
		)

		booking_ids = [b.parent for b in assigned_bookings]

		# Count bookings in the date range with confirmed/pending status
		booking_count = 0
		if booking_ids:
			booking_count = frappe.db.count(
				"MM Meeting Booking",
				filters={
					"name": ["in", booking_ids],
					"start_datetime": ["between", [scheduled_date, week_end]],
					"booking_status": ["in", ["Confirmed", "Pending"]]
				}
			)

		member_booking_counts.append({
			"member": member,
			"booking_count": booking_count
		})

	# Sort by booking count (lowest first)
	# If tied, use last_assigned_datetime as tiebreaker
	sorted_members = sorted(
		member_booking_counts,
		key=lambda m: (
			m["booking_count"],
			m["member"].last_assigned_datetime or datetime(1970, 1, 1)
		)
	)

	return sorted_members[0]["member"]


def assign_weighted(available_members):
	"""
	Assign based on assignment_priority field (higher priority = more assignments)

	This is for future implementation - weighted random selection

	Args:
		available_members (list): List of MM Department Member objects

	Returns:
		MM Department Member: Selected member
	"""
	import random

	# Create weighted list based on assignment_priority
	weighted_choices = []
	for member in available_members:
		priority = member.assignment_priority or 1
		# Add member to list 'priority' times (higher priority = more chances)
		weighted_choices.extend([member] * priority)

	# Random selection from weighted list
	return random.choice(weighted_choices)


def update_member_assignment_tracking(department, member):
	"""
	Update assignment tracking fields in department member record

	Args:
		department (str): Department ID
		member (str): User ID
	"""
	# Find the member row in department
	dept = frappe.get_doc("MM Department", department)

	for dept_member in dept.department_members:
		if dept_member.member == member:
			# Update tracking fields
			dept_member.last_assigned_datetime = now_datetime()
			dept_member.total_assignments = (dept_member.total_assignments or 0) + 1
			break

	# Save department (which saves child table)
	dept.save(ignore_permissions=True)


def get_assignment_statistics(department, days=30):
	"""
	Get assignment statistics for a department

	Args:
		department (str): Department ID
		days (int): Number of days to look back

	Returns:
		dict: Assignment statistics by member
	"""
	start_date = getdate() - timedelta(days=days)

	# Get all members
	members = frappe.get_all(
		"MM Department Member",
		filters={
			"parent": department,
			"parenttype": "MM Department"
		},
		fields=["member", "total_assignments", "last_assigned_datetime", "is_active"]
	)

	statistics = []

	for member in members:
		# Get recent bookings count
		recent_bookings = frappe.db.count(
			"MM Meeting Booking",
			filters={
				"department": department,
				"assigned_to": member.member,
				"scheduled_date": [">=", start_date],
				"status": ["in", ["Confirmed", "Pending", "Completed"]]
			}
		)

		# Get member name
		member_name = frappe.get_value("User", member.member, "full_name")

		statistics.append({
			"member": member.member,
			"member_name": member_name,
			"is_active": member.is_active,
			"total_assignments": member.total_assignments or 0,
			"recent_bookings": recent_bookings,
			"last_assigned": member.last_assigned_datetime
		})

	# Sort by recent bookings (descending)
	statistics.sort(key=lambda x: x["recent_bookings"], reverse=True)

	return {
		"department": department,
		"period_days": days,
		"statistics": statistics
	}


def rebalance_assignments(department, dry_run=True):
	"""
	Analyze and suggest rebalancing of assignments

	Useful for identifying if assignment algorithm is working correctly

	Args:
		department (str): Department ID
		dry_run (bool): If True, only return suggestions without making changes

	Returns:
		dict: Rebalancing analysis and suggestions
	"""
	stats = get_assignment_statistics(department, days=30)

	active_members = [s for s in stats["statistics"] if s["is_active"]]

	if not active_members:
		return {
			"status": "no_active_members",
			"message": "No active members in department"
		}

	# Calculate average assignments
	total_assignments = sum(m["recent_bookings"] for m in active_members)
	avg_assignments = total_assignments / len(active_members)

	# Find imbalances (members with significantly more/fewer assignments)
	threshold = avg_assignments * 0.3  # 30% deviation threshold

	overloaded = [m for m in active_members if m["recent_bookings"] > avg_assignments + threshold]
	underloaded = [m for m in active_members if m["recent_bookings"] < avg_assignments - threshold]

	return {
		"status": "balanced" if not (overloaded or underloaded) else "imbalanced",
		"average_assignments": avg_assignments,
		"total_assignments": total_assignments,
		"active_members_count": len(active_members),
		"overloaded_members": overloaded,
		"underloaded_members": underloaded,
		"suggestions": generate_rebalancing_suggestions(overloaded, underloaded, avg_assignments)
	}


def generate_rebalancing_suggestions(overloaded, underloaded, avg_assignments):
	"""
	Generate suggestions for rebalancing workload

	Args:
		overloaded (list): Members with too many assignments
		underloaded (list): Members with too few assignments
		avg_assignments (float): Average assignments per member

	Returns:
		list: List of suggestion strings
	"""
	suggestions = []

	if not overloaded and not underloaded:
		suggestions.append("✓ Assignments are well-balanced across all members")
		return suggestions

	if overloaded:
		for member in overloaded:
			diff = member["recent_bookings"] - avg_assignments
			suggestions.append(
				f"⚠ {member['member_name']} has {diff:.0f} more assignments than average. "
				"Consider checking their availability rules or calendar sync."
			)

	if underloaded:
		for member in underloaded:
			diff = avg_assignments - member["recent_bookings"]
			suggestions.append(
				f"ℹ {member['member_name']} has {diff:.0f} fewer assignments than average. "
				"This may indicate limited availability or they may have recently joined."
			)

	suggestions.append(
		"💡 Tip: Ensure all members have similar working hours and availability rules for best balance."
	)

	return suggestions
