/**
 * Timeline Calendar Page - Resource-Based Calendar View
 * Displays meetings in a day/week/month view with team members as columns
 */

frappe.pages['mm-timeline-calendar'].on_page_load = function(wrapper) {
	// Create the Frappe app page
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Timeline Calendar',
		single_column: true
	});

	// Store page reference
	wrapper.page = page;

	// Create calendar container with horizontal scroll support
	wrapper.calendar_container = document.createElement('div');
	wrapper.calendar_container.id = 'mm-timeline-calendar';
	wrapper.calendar_container.style.height = '100%';
	wrapper.calendar_container.style.padding = '20px';
	wrapper.calendar_container.style.overflowX = 'auto';  // Enable horizontal scroll
	wrapper.calendar_container.style.overflowY = 'auto';  // Enable vertical scroll

	// Append to the layout main section
	page.main.append(wrapper.calendar_container);

	// Add custom CSS for FullCalendar theming
	const style = document.createElement('style');
	style.textContent = `
		/* Light Theme (Default) */
		#mm-timeline-calendar {
			--fc-bg-color: #ffffff;
			--fc-border-color: #e5e7eb;
			--fc-text-color: #1f2937;
			--fc-neutral-bg-color: #f3f4f6;
			--fc-neutral-text-color: #6b7280;
		}

		/* Dark Theme */
		[data-theme="dark"] #mm-timeline-calendar {
			--fc-bg-color: #1f2937;
			--fc-border-color: #374151;
			--fc-text-color: #f9fafb;
			--fc-neutral-bg-color: #111827;
			--fc-neutral-text-color: #9ca3af;
		}

		/* Calendar Styling */
		#mm-timeline-calendar .fc {
			background-color: var(--fc-bg-color);
			color: var(--fc-text-color);
		}

		#mm-timeline-calendar .fc-theme-standard td,
		#mm-timeline-calendar .fc-theme-standard th {
			border-color: var(--fc-border-color);
		}

		#mm-timeline-calendar .fc-col-header-cell {
			background-color: var(--fc-neutral-bg-color);
			font-weight: 600;
			padding: 8px;
		}

		/* Time axis styling (left column) */
		#mm-timeline-calendar .fc-timegrid-axis {
			background-color: var(--fc-neutral-bg-color);
			font-weight: 600;
		}

		#mm-timeline-calendar .fc-timegrid-slot-label {
			border-color: var(--fc-border-color);
		}

		/* Event Styling */
		#mm-timeline-calendar .fc-event {
			border-radius: 4px;
			padding: 2px 4px;
			font-size: 12px;
			cursor: pointer;
			border: none;
		}

		#mm-timeline-calendar .fc-event-main {
			padding: 2px 4px;
		}

		/* Current Time Indicator */
		#mm-timeline-calendar .fc-timegrid-now-indicator-line {
			border-color: #ef4444;
			border-width: 2px;
		}

		#mm-timeline-calendar .fc-timegrid-now-indicator-arrow {
			border-color: #ef4444;
		}

		/* Resource column headers */
		#mm-timeline-calendar .fc-resource-timeline .fc-resource-cell {
			background-color: var(--fc-neutral-bg-color);
		}

		/* Fixed minimum width for resource columns */
		#mm-timeline-calendar .fc-timegrid-col {
			min-width: 180px !important;
			width: 180px;
		}

		#mm-timeline-calendar .fc-col-header-cell {
			min-width: 180px !important;
			width: 180px;
		}

		/* Enable horizontal scrolling */
		#mm-timeline-calendar .fc-scroller {
			overflow-x: auto !important;
		}

		#mm-timeline-calendar .fc-scroller-harness {
			overflow: visible !important;
		}

		/* Fix for week view - prevent shrinking */
		#mm-timeline-calendar .fc-resourceTimeGridWeek-view .fc-timegrid-col {
			min-width: 150px !important;
			width: auto;
		}

		/* Ensure calendar doesn't shrink content */
		#mm-timeline-calendar .fc-view-harness {
			min-width: fit-content;
		}

		/* Resource header styling */
		#mm-timeline-calendar .fc-col-header-cell-cushion {
			padding: 8px 4px;
			display: block;
			white-space: normal;
			word-wrap: break-word;
		}

		/* Responsive adjustments */
		@media (max-width: 768px) {
			#mm-timeline-calendar .fc-button {
				font-size: 11px;
				padding: 4px 8px;
			}

			#mm-timeline-calendar .fc-timegrid-col {
				min-width: 120px !important;
			}
		}
	`;
	document.head.appendChild(style);

	// Create filters section
	const filters_html = `
		<div class="frappe-control" style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
			<div style="flex: 1; min-width: 200px;">
				<label style="font-size: 12px; color: #6b7280; margin-bottom: 4px; display: block;">Department</label>
				<select id="department-filter" class="form-control" style="height: 32px; font-size: 13px;">
					<option value="">All Departments</option>
				</select>
			</div>
			<div style="flex: 1; min-width: 200px;">
				<label style="font-size: 12px; color: #6b7280; margin-bottom: 4px; display: block;">Status</label>
				<select id="status-filter" class="form-control" style="height: 32px; font-size: 13px;">
					<option value="">All Statuses</option>
					<option value="Confirmed">Confirmed</option>
					<option value="Pending">Pending</option>
					<option value="Completed">Completed</option>
					<option value="Cancelled">Cancelled</option>
					<option value="No-Show">No-Show</option>
					<option value="Rescheduled">Rescheduled</option>
				</select>
			</div>
			<div style="display: flex; gap: 8px; align-items: flex-end;">
				<button id="theme-toggle" class="btn btn-default btn-sm" title="Toggle Theme">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
						<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
					</svg>
				</button>
			</div>
		</div>
	`;
	page.main.prepend($(filters_html));

	// Load departments
	loadDepartments();
};

frappe.pages['mm-timeline-calendar'].on_page_show = function(wrapper) {
	// Load FullCalendar Scheduler Bundle from CDN if not already loaded
	const loadFullCalendar = () => {
		if (window.FullCalendar && window.FullCalendar.Calendar) {
			return Promise.resolve();
		}

		return new Promise((resolve, reject) => {
			// Load CSS for scheduler bundle
			const css = document.createElement('link');
			css.rel = 'stylesheet';
			css.href = 'https://cdn.jsdelivr.net/npm/fullcalendar-scheduler@6.1.10/index.global.min.css';
			document.head.appendChild(css);

			// Load FullCalendar Scheduler bundle (includes all plugins)
			const script = document.createElement('script');
			script.src = 'https://cdn.jsdelivr.net/npm/fullcalendar-scheduler@6.1.10/index.global.min.js';
			script.crossOrigin = 'anonymous';

			script.onload = () => {
				console.log('FullCalendar Scheduler loaded successfully');
				resolve();
			};

			script.onerror = (error) => {
				console.error('Failed to load FullCalendar Scheduler:', error);
				reject(error);
			};

			document.head.appendChild(script);
		});
	};

	// Initialize calendar after loading FullCalendar
	loadFullCalendar().then(() => {
		// Give it a moment for the script to fully initialize
		setTimeout(() => {
			initializeCalendar(wrapper);
			setupEventHandlers(wrapper);
		}, 100);
	}).catch((error) => {
		console.error('Error loading FullCalendar:', error);
		frappe.msgprint('Failed to load calendar library. Please refresh and try again.');
	});
};

frappe.pages['mm-timeline-calendar'].on_page_hide = function(wrapper) {
	// Cleanup calendar instance
	if (wrapper.calendar) {
		wrapper.calendar.destroy();
		wrapper.calendar = null;
	}
};

/**
 * Initialize FullCalendar instance
 */
function initializeCalendar(wrapper) {
	if (wrapper.calendar) {
		wrapper.calendar.destroy();
	}

	const calendarEl = wrapper.calendar_container;

	wrapper.calendar = new FullCalendar.Calendar(calendarEl, {
		// Calendar view - Time Grid with resources as columns
		initialView: 'resourceTimeGridDay',
		schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',

		// Header toolbar
		headerToolbar: {
			left: 'prev,next today',
			center: 'title',
			right: 'resourceTimeGridDay,resourceTimeGridWeek,dayGridMonth'
		},

		// Time configuration (vertical time axis on left)
		slotMinTime: '07:00:00',
		slotMaxTime: '23:00:00',
		slotDuration: '00:30:00',
		slotLabelInterval: '01:00:00',
		slotLabelFormat: {
			hour: '2-digit',
			minute: '2-digit',
			hour12: false
		},
		allDaySlot: false,
		nowIndicator: true,

		// Resource column width settings
		resourceAreaWidth: '150px',
		resourceMinWidth: 180,  // Minimum width for each resource column

		// Display options
		height: 'auto',
		contentHeight: 'auto',
		expandRows: false,  // Don't expand to fill height
		handleWindowResize: true,

		// Enable horizontal scrolling when needed
		stickyHeaderDates: true,
		stickyFooterScrollbar: true,

		// Dynamic resource loading
		resources: function(info, successCallback, failureCallback) {
			const department = document.getElementById('department-filter')?.value || null;

			frappe.call({
				method: 'meeting_manager.meeting_manager.page.mm_timeline_calendar.api.get_resources',
				args: { department: department },
				callback: (r) => {
					if (r.message) {
						successCallback(r.message);
					} else {
						failureCallback('Failed to load resources');
					}
				},
				error: failureCallback
			});
		},

		// Dynamic event loading
		events: function(info, successCallback, failureCallback) {
			const department = document.getElementById('department-filter')?.value || null;
			const status = document.getElementById('status-filter')?.value || null;

			frappe.call({
				method: 'meeting_manager.meeting_manager.page.mm_timeline_calendar.api.get_events',
				args: {
					start: info.startStr,
					end: info.endStr,
					department: department,
					status: status
				},
				callback: (r) => {
					if (r.message) {
						successCallback(r.message);
					} else {
						failureCallback('Failed to load events');
					}
				},
				error: failureCallback
			});
		},

		// Event handlers
		eventClick: function(info) {
			// Open meeting booking form
			frappe.set_route('Form', 'MM Meeting Booking', info.event.id);
		},

		eventDidMount: function(info) {
			// Add tooltip with event details
			const props = info.event.extendedProps;
			const tooltip = `
				<b>${info.event.title}</b><br>
				Status: ${props.status || 'N/A'}<br>
				Time: ${info.event.startStr} - ${info.event.endStr}<br>
				${props.customer_email ? 'Email: ' + props.customer_email : ''}
			`;
			$(info.el).attr('title', tooltip);
		}
	});

	wrapper.calendar.render();
}

/**
 * Setup event handlers for filters and controls
 */
function setupEventHandlers(wrapper) {
	// Department filter
	$('#department-filter').off('change').on('change', function() {
		if (wrapper.calendar) {
			wrapper.calendar.refetchResources();
			wrapper.calendar.refetchEvents();
		}
	});

	// Status filter
	$('#status-filter').off('change').on('change', function() {
		if (wrapper.calendar) {
			wrapper.calendar.refetchEvents();
		}
	});

	// Theme toggle
	$('#theme-toggle').off('click').on('click', function() {
		const container = document.getElementById('mm-timeline-calendar');
		const currentTheme = container.getAttribute('data-theme');

		if (currentTheme === 'dark') {
			container.removeAttribute('data-theme');
			localStorage.setItem('mm-calendar-theme', 'light');
		} else {
			container.setAttribute('data-theme', 'dark');
			localStorage.setItem('mm-calendar-theme', 'dark');
		}
	});

	// Apply saved theme
	const savedTheme = localStorage.getItem('mm-calendar-theme');
	if (savedTheme === 'dark') {
		document.getElementById('mm-timeline-calendar').setAttribute('data-theme', 'dark');
	}
}

/**
 * Load departments for filter dropdown
 */
function loadDepartments() {
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'MM Department',
			filters: { is_active: 1 },
			fields: ['name', 'department_name'],
			order_by: 'department_name asc'
		},
		callback: (r) => {
			if (r.message) {
				const select = document.getElementById('department-filter');
				r.message.forEach(dept => {
					const option = document.createElement('option');
					option.value = dept.name;
					option.textContent = dept.department_name;
					select.appendChild(option);
				});
			}
		}
	});
}
