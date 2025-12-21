import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";

/**
 * Meeting Management Dashboard
 * A proof-of-concept React page for managing meetings in Frappe
 */
function ManageMeetings() {
	const [meetings, setMeetings] = useState([]);
	const [loading, setLoading] = useState(true);
	const [filter, setFilter] = useState("all");
	const [searchTerm, setSearchTerm] = useState("");
	const [stats, setStats] = useState({
		total: 0,
		confirmed: 0,
		pending: 0,
		completed: 0,
	});

	// Fetch meetings on component mount
	useEffect(() => {
		loadMeetings();
	}, [filter]);

	const loadMeetings = () => {
		setLoading(true);

		frappe.call({
			method: "meeting_manager.meeting_manager.page.mm_manage_meetings.api.get_meetings",
			args: {
				status: filter === "all" ? null : filter,
			},
			callback: (r) => {
				if (r.message) {
					setMeetings(r.message.meetings || []);
					setStats(r.message.stats || {});
				}
				setLoading(false);
			},
			error: () => {
				setLoading(false);
				frappe.msgprint("Failed to load meetings");
			},
		});
	};

	const handleViewMeeting = (meetingId) => {
		frappe.set_route("Form", "MM Meeting Booking", meetingId);
	};

	const handleStatusUpdate = (meetingId, newStatus) => {
		frappe.call({
			method: "meeting_manager.meeting_manager.api.booking.update_booking_status",
			args: {
				booking_id: meetingId,
				new_status: newStatus,
				notes: `Status updated from Manage Meetings page`,
			},
			callback: (r) => {
				if (r.message && r.message.success) {
					frappe.show_alert({
						message: `Meeting status updated to ${newStatus}`,
						indicator: "green",
					});
					loadMeetings();
				}
			},
		});
	};

	const getStatusColor = (status) => {
		const colors = {
			Confirmed: "bg-green-100 text-green-800 border-green-200",
			Pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
			Cancelled: "bg-red-100 text-red-800 border-red-200",
			Completed: "bg-blue-100 text-blue-800 border-blue-200",
			"No-show": "bg-gray-100 text-gray-800 border-gray-200",
		};
		return colors[status] || "bg-gray-100 text-gray-800 border-gray-200";
	};

	const filteredMeetings = meetings.filter((meeting) => {
		if (!searchTerm) return true;
		const search = searchTerm.toLowerCase();
		return (
			meeting.booking_reference?.toLowerCase().includes(search) ||
			meeting.customer_name?.toLowerCase().includes(search) ||
			meeting.meeting_type_name?.toLowerCase().includes(search)
		);
	});

	return (
		<div style={{ padding: "20px", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
			{/* Header */}
			<div style={{ marginBottom: "24px" }}>
				<h1 style={{ fontSize: "28px", fontWeight: "700", color: "#1f2937", marginBottom: "8px" }}>
					Manage Meetings
				</h1>
				<p style={{ color: "#6b7280", fontSize: "14px" }}>
					View and manage all your meeting bookings
				</p>
			</div>

			{/* Stats Cards */}
			<div
				style={{
					display: "grid",
					gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
					gap: "16px",
					marginBottom: "24px",
				}}
			>
				<StatCard
					title="Total Meetings"
					value={stats.total}
					icon="📅"
					color="#3b82f6"
				/>
				<StatCard
					title="Confirmed"
					value={stats.confirmed}
					icon="✅"
					color="#10b981"
				/>
				<StatCard
					title="Pending"
					value={stats.pending}
					icon="⏳"
					color="#f59e0b"
				/>
				<StatCard
					title="Completed"
					value={stats.completed}
					icon="🎯"
					color="#8b5cf6"
				/>
			</div>

			{/* Filters and Search */}
			<div
				style={{
					backgroundColor: "white",
					padding: "20px",
					borderRadius: "8px",
					boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
					marginBottom: "24px",
				}}
			>
				<div
					style={{
						display: "flex",
						gap: "16px",
						flexWrap: "wrap",
						alignItems: "center",
					}}
				>
					{/* Search */}
					<div style={{ flex: "1", minWidth: "250px" }}>
						<input
							type="text"
							placeholder="Search by reference, customer, or meeting type..."
							value={searchTerm}
							onChange={(e) => setSearchTerm(e.target.value)}
							style={{
								width: "100%",
								padding: "10px 14px",
								border: "1px solid #d1d5db",
								borderRadius: "6px",
								fontSize: "14px",
							}}
						/>
					</div>

					{/* Status Filter */}
					<div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
						{["all", "Confirmed", "Pending", "Completed", "Cancelled"].map((status) => (
							<button
								key={status}
								onClick={() => setFilter(status)}
								className={`btn ${filter === status ? "btn-primary" : "btn-default"}`}
								style={{
									padding: "8px 16px",
									fontSize: "13px",
									textTransform: "capitalize",
								}}
							>
								{status}
							</button>
						))}
					</div>

					{/* Refresh Button */}
					<button
						onClick={loadMeetings}
						className="btn btn-secondary"
						style={{ padding: "8px 16px" }}
					>
						🔄 Refresh
					</button>
				</div>
			</div>

			{/* Meetings List */}
			{loading ? (
				<LoadingSpinner />
			) : filteredMeetings.length === 0 ? (
				<EmptyState searchTerm={searchTerm} />
			) : (
				<div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
					{filteredMeetings.map((meeting) => (
						<MeetingCard
							key={meeting.name}
							meeting={meeting}
							onView={handleViewMeeting}
							onStatusUpdate={handleStatusUpdate}
							getStatusColor={getStatusColor}
						/>
					))}
				</div>
			)}
		</div>
	);
}

// Stat Card Component
function StatCard({ title, value, icon, color }) {
	return (
		<div
			style={{
				backgroundColor: "white",
				padding: "20px",
				borderRadius: "8px",
				boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
				border: "1px solid #e5e7eb",
			}}
		>
			<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
				<div>
					<p style={{ fontSize: "13px", color: "#6b7280", marginBottom: "4px" }}>{title}</p>
					<p style={{ fontSize: "28px", fontWeight: "700", color: "#1f2937" }}>{value}</p>
				</div>
				<div
					style={{
						fontSize: "32px",
						opacity: 0.7,
					}}
				>
					{icon}
				</div>
			</div>
		</div>
	);
}

// Meeting Card Component
function MeetingCard({ meeting, onView, onStatusUpdate, getStatusColor }) {
	const [showActions, setShowActions] = useState(false);

	return (
		<div
			style={{
				backgroundColor: "white",
				padding: "20px",
				borderRadius: "8px",
				boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
				border: "1px solid #e5e7eb",
				transition: "all 0.2s",
			}}
			onMouseEnter={() => setShowActions(true)}
			onMouseLeave={() => setShowActions(false)}
		>
			<div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
				{/* Left Side - Meeting Info */}
				<div style={{ flex: 1 }}>
					<div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
						<h3 style={{ fontSize: "16px", fontWeight: "600", color: "#1f2937", margin: 0 }}>
							{meeting.customer_name || meeting.booking_reference}
						</h3>
						<span
							style={{
								padding: "4px 12px",
								borderRadius: "12px",
								fontSize: "12px",
								fontWeight: "600",
								border: "1px solid",
							}}
							className={getStatusColor(meeting.status)}
						>
							{meeting.status}
						</span>
					</div>

					<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", marginTop: "12px" }}>
						<InfoItem label="Reference" value={meeting.booking_reference} />
						<InfoItem label="Meeting Type" value={meeting.meeting_type_name} />
						<InfoItem label="Date" value={meeting.scheduled_date} />
						<InfoItem label="Time" value={`${meeting.scheduled_start_time} - ${meeting.scheduled_end_time}`} />
						<InfoItem label="Assigned To" value={meeting.assigned_to_name} />
						<InfoItem label="Department" value={meeting.department_name} />
					</div>
				</div>

				{/* Right Side - Actions */}
				<div style={{ display: "flex", gap: "8px", marginLeft: "16px" }}>
					<button
						onClick={() => onView(meeting.name)}
						className="btn btn-primary btn-sm"
						style={{ padding: "6px 12px", fontSize: "13px" }}
					>
						View Details
					</button>

					{showActions && meeting.status === "Confirmed" && (
						<div style={{ display: "flex", gap: "4px" }}>
							<button
								onClick={() => onStatusUpdate(meeting.name, "Completed")}
								className="btn btn-success btn-sm"
								style={{ padding: "6px 12px", fontSize: "13px" }}
								title="Mark as Completed"
							>
								✓
							</button>
							<button
								onClick={() => onStatusUpdate(meeting.name, "Cancelled")}
								className="btn btn-danger btn-sm"
								style={{ padding: "6px 12px", fontSize: "13px" }}
								title="Cancel Meeting"
							>
								✕
							</button>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

// Info Item Component
function InfoItem({ label, value }) {
	return (
		<div>
			<p style={{ fontSize: "12px", color: "#6b7280", marginBottom: "2px" }}>{label}</p>
			<p style={{ fontSize: "14px", color: "#1f2937", fontWeight: "500" }}>{value || "N/A"}</p>
		</div>
	);
}

// Loading Spinner Component
function LoadingSpinner() {
	return (
		<div style={{ textAlign: "center", padding: "60px" }}>
			<div
				style={{
					border: "4px solid #f3f4f6",
					borderTop: "4px solid #3b82f6",
					borderRadius: "50%",
					width: "48px",
					height: "48px",
					animation: "spin 1s linear infinite",
					margin: "0 auto 16px",
				}}
			/>
			<p style={{ color: "#6b7280", fontSize: "14px" }}>Loading meetings...</p>
		</div>
	);
}

// Empty State Component
function EmptyState({ searchTerm }) {
	return (
		<div
			style={{
				backgroundColor: "white",
				padding: "60px 20px",
				borderRadius: "8px",
				textAlign: "center",
				boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
			}}
		>
			<div style={{ fontSize: "64px", marginBottom: "16px" }}>📭</div>
			<h3 style={{ fontSize: "18px", fontWeight: "600", color: "#1f2937", marginBottom: "8px" }}>
				{searchTerm ? "No meetings found" : "No meetings yet"}
			</h3>
			<p style={{ color: "#6b7280", fontSize: "14px" }}>
				{searchTerm
					? "Try adjusting your search or filter criteria"
					: "Create your first meeting to get started"}
			</p>
		</div>
	);
}

/**
 * Mount function
 * Called by Frappe to mount the React component
 */
export function mount(wrapper) {
	const root = createRoot(wrapper);
	root.render(<ManageMeetings />);
	return root;
}
