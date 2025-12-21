/**
 * Timeline Calendar Page - Resource-Based Calendar View
 * Displays meetings in a day/week/month view with team members as columns
 */

frappe.pages['mm-timeline-calendar'].on_page_load = function(wrapper) {
	// Create the Frappe app page
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Timeline Meeting Calendar',
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

		/* Style for week view day headers */
		#mm-timeline-calendar .fc-resourceTimeGridWeek-view .fc-col-header-cell {
			font-size: 14px;
		}

		/* Time axis styling (left column) - Frozen/Sticky */
		#mm-timeline-calendar .fc-timegrid-axis {
			background-color: var(--fc-neutral-bg-color);
			font-weight: 600;
			position: sticky;
			left: 0;
			// z-index: 3;
		}

		#mm-timeline-calendar .fc-timegrid-slot-label {
			border-color: var(--fc-border-color);
			position: sticky;
			left: 0;
			z-index: 3;
			background-color: var(--fc-neutral-bg-color);
		}

		/* Make the time column header sticky too */
		#mm-timeline-calendar .fc-timegrid-axis-frame {
			position: sticky;
			left: 0;
			z-index: 4;
			background-color: var(--fc-neutral-bg-color);
		}

		/* Ensure the corner header cell is also sticky */
		#mm-timeline-calendar .fc-col-header .fc-timegrid-axis {
			position: sticky;
			left: 0;
			z-index: 5;
			background-color: var(--fc-neutral-bg-color);
		}

		/* Event Styling */
		#mm-timeline-calendar .fc-event {
			border-radius: 6px;
			padding: 0;
			font-size: 12px;
			cursor: pointer;
			border: none;
			overflow: hidden;
		}

		/* Draggable events - show move cursor */
		#mm-timeline-calendar .fc-event.draggable-event {
			cursor: move;
		}

		/* Non-draggable events - show not-allowed cursor */
		#mm-timeline-calendar .fc-event.non-draggable-event {
			cursor: not-allowed;
			opacity: 0.7;
		}

		#mm-timeline-calendar .fc-event-main {
			padding: 0;
			height: 100%;
		}

		/* Force time slot height */
		#mm-timeline-calendar .fc-timegrid-slot {
			height: 40px !important;
			min-height: 40px !important;
		}

		#mm-timeline-calendar .fc-timegrid-slot-lane {
			height: 40px !important;
		}

		/* Current Time Indicator */
		#mm-timeline-calendar .fc-timegrid-now-indicator-line {
			border-color: #ef4444;
			border-width: 0.5%;
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

		/* Frappe-styled buttons */
		#mm-timeline-calendar .fc-button {
			background-color: var(--fc-bg-color);
			border: 1px solid var(--fc-border-color);
			color: var(--fc-text-color);
			border-radius: 6px;
			padding: 6px 12px;
			font-size: 13px;
			font-weight: 500;
			transition: all 0.2s ease;
			box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
			display: inline-flex;
			align-items: center;
			justify-content: center;
			text-align: center;
		}

		#mm-timeline-calendar .fc-button:hover {
			background-color: var(--fc-neutral-bg-color);
			border-color: var(--fc-border-color);
			box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
		}

		#mm-timeline-calendar .fc-button:focus {
			box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
			outline: none;
		}

		#mm-timeline-calendar .fc-button-active {
			background-color: #3b82f6 !important;
			color: white !important;
			border-color: #3b82f6 !important;
		}

		#mm-timeline-calendar .fc-button-active:hover {
			background-color: #2563eb !important;
			border-color: #2563eb !important;
		}

		/* Button group styling */
		#mm-timeline-calendar .fc-button-group {
			gap: 4px;
			display: inline-flex;
		}

		#mm-timeline-calendar .fc-button-group .fc-button {
			border-radius: 6px;
			margin: 0;
		}

		/* Navigation buttons (prev/next) */
		#mm-timeline-calendar .fc-prev-button,
		#mm-timeline-calendar .fc-next-button {
			padding: 6px 10px;
			min-width: 36px;
		}

		/* Today button */
		#mm-timeline-calendar .fc-today-button {
			padding: 6px 16px;
		}

		/* Toolbar styling */
		#mm-timeline-calendar .fc-toolbar {
			margin-bottom: 20px;
			padding: 12px 0;
		}

		#mm-timeline-calendar .fc-toolbar-title {
			font-size: 18px;
			font-weight: 600;
			color: var(--fc-text-color);
		}

		#mm-timeline-calendar .fc-toolbar-chunk {
			display: flex;
			align-items: center;
			gap: 8px;
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

			#mm-timeline-calendar .fc-toolbar-title {
				font-size: 16px;
			}
		}
	`;
	document.head.appendChild(style);

	// Create filters section
	const filters_html = `
		<div class="frappe-control" style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; padding: 21px">
			<div style="flex: 1; min-width: 180px;">
				<label style="font-size: 12px; color: #6b7280; margin-bottom: 4px; display: block;">Department</label>
				<select id="department-filter" class="form-control" style="height: 32px; font-size: 13px;">
					<option value="">All Departments</option>
				</select>
			</div>
			<div style="flex: 1; min-width: 180px;">
				<label style="font-size: 12px; color: #6b7280; margin-bottom: 4px; display: block;">Meeting Type</label>
				<select id="meeting-type-filter" class="form-control" style="height: 32px; font-size: 13px;" disabled>
					<option value="">All Meeting Types</option>
				</select>
			</div>
			<div style="flex: 1; min-width: 160px;">
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
			<div style="flex: 1; min-width: 160px;">
				<label style="font-size: 12px; color: #6b7280; margin-bottom: 4px; display: block;">Service</label>
				<select id="service-filter" class="form-control" style="height: 32px; font-size: 13px;">
					<option value="">All Services</option>
					<option value="Business">Business</option>
					<option value="Business Extended">Business Extended</option>
					<option value="Business Rebook">Business Rebook</option>
					<option value="New Setup Business">New Setup Business</option>
					<option value="Private / Business Customer">Private / Business Customer</option>
					<option value="Private New Sale">Private New Sale</option>
					<option value="Private Self Book">Private Self Book</option>
				</select>
			</div>
			<div style="flex: 1; min-width: 140px;">
				<label style="font-size: 12px; color: #6b7280; margin-bottom: 4px; display: block;">Status Color</label>
				<select id="status-color-filter" class="form-control" style="height: 32px; font-size: 13px;">
					<option value="">All Colors</option>
					<option value="Red">Red</option>
					<option value="Blue">Blue</option>
					<option value="Green">Green</option>
					<option value="Orange">Orange</option>
					<option value="Yellow">Yellow</option>
					<option value="Indigo">Indigo</option>
					<option value="Purple">Purple</option>
					<option value="Pink">Pink</option>
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

		// Customize button text
		buttonText: {
			today: 'Current',
			day: 'day',
			week: 'week',
			month: 'month'
		},

		// Custom day header format for week view - show single letter day names with tooltips
		dayHeaderContent: function(arg) {
			const view = wrapper.calendar?.view;
			const date = arg.date;

			// Only apply custom formatting to week view
			if (view && view.type === 'resourceTimeGridWeek') {
				const dayNames = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
				const dayOfWeek = date.getDay();
				const dayLetter = dayNames[dayOfWeek];

				// Format full date for tooltip
				const fullDate = date.toLocaleDateString('en-US', {
					weekday: 'long',
					year: 'numeric',
					month: 'long',
					day: 'numeric'
				});

				return {
					html: `<div title="${fullDate}" style="cursor: help; font-weight: 600; text-align: center;">
						${dayLetter}
					</div>`
				};
			}

			// Return default for other views (let FullCalendar handle it)
			return null;
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

		// slotLabelFormat: function(date) {
		// 	// Format time with 'T' prefix: T07:00, T08:00, etc.
		// 	const hours = String(date.date.hour).padStart(2, '0');
		// 	const minutes = String(date.date.minute).padStart(2, '0');
		// 	return `T ${hours}:${minutes}`;
		// },
		allDaySlot: false,
		nowIndicator: true,

		// Resource column width settings
		resourceAreaWidth: '150px',

		// Display options
		height: 'auto',
		contentHeight: 'auto',
		expandRows: false,  // Don't expand to fill height
		handleWindowResize: true,

		// Enable horizontal scrolling when needed
		stickyHeaderDates: true,
		stickyFooterScrollbar: true,

		// Enable drag-and-drop functionality
		// Note: editability will be controlled per-event based on status
		editable: true,
		droppable: true,
		eventResourceEditable: true,  // Allow dragging between resources (hosts)
		eventDurationEditable: true,   // Allow resizing event duration
		eventStartEditable: true,       // Allow changing start time

		// Control which events can be dragged/resized
		eventAllow: function(dropInfo, draggedEvent) {
			// Check if event status allows editing
			const status = draggedEvent.extendedProps.status;
			if (status === 'Cancelled' || status === 'Completed') {
				return false; // Cannot drag cancelled or completed events
			}

			// For resource changes (reassignment), check if department is selected
			if (dropInfo.resource) {
				const department = document.getElementById('department-filter')?.value;
				if (!department) {
					// No department selected, don't allow resource change
					frappe.show_alert({
						message: 'Please select a department first to reassign meetings',
						indicator: 'orange'
					}, 3);
					return false;
				}
			}

			return true;
		},

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
			const meetingType = document.getElementById('meeting-type-filter')?.value || null;
			const status = document.getElementById('status-filter')?.value || null;
			const service = document.getElementById('service-filter')?.value || null;
			const statusColor = document.getElementById('status-color-filter')?.value || null;

			frappe.call({
				method: 'meeting_manager.meeting_manager.page.mm_timeline_calendar.api.get_events',
				args: {
					start: info.startStr,
					end: info.endStr,
					department: department,
					status: status,
					meeting_type: meetingType,
					service: service,
					status_color: statusColor
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

		// Custom event content rendering
		eventContent: function(arg) {
			const event = arg.event;
			const props = event.extendedProps;

			const title = arg?.event?.title;
			
			// Format times
			const startTime = event.start.toLocaleTimeString('en-US', {
				hour: 'numeric',
				minute: '2-digit',
				hour12: true
			});
			const endTime = event.end.toLocaleTimeString('en-US', {
				hour: 'numeric',
				minute: '2-digit',
				hour12: true
			});

			// Status icon based on location type
			const locationIcon = props.location_type === 'Video Call' ? '📹' :
								props.location_type === 'Phone Call' ? '📞' :
								props.location_type === 'In-Person' ? '📍' : '💼';

			return {
				html: `
				<div style="padding: 4px 6px; height: 100%; display: flex; flex-direction: column; gap: 2px;">
						<div style="font-weight: 500; font-size: 12px; white-space: nowrap; text-overflow: ellipsis;">
							${title}
						</div>
						<div style="font-weight: 600; font-size: 10px; opacity: 0.9;">
							${startTime} - ${endTime}
						</div>
						<div style="font-size: 10px; opacity: 0.8; display: flex; gap: 4px; align-items: center;">
							<span>${locationIcon}</span>
							<span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
								${props.meeting_type || 'Meeting'}
							</span>
						</div>
					</div>
				`
			};
		},

		eventDidMount: function(info) {
			// Add tooltip with event details
			const props = info.event.extendedProps;

			const event = info.event;

			// Format times
			const startTime = event.start.toLocaleTimeString('en-US', {
				hour: 'numeric',
				minute: '2-digit',
				hour12: true
			});
			const endTime = event.end.toLocaleTimeString('en-US', {
				hour: 'numeric',
				minute: '2-digit',
				hour12: true
			});

			// Build tooltip
			let tooltip = `${info.event.title}\nTime: ${startTime} - ${endTime}\nStatus: ${props.status || 'N/A'}`;
			if (props.customer_email) {
				tooltip += `\nEmail: ${props.customer_email}`;
			}

			// Check if event is draggable
			const status = props.status;
			const isDraggable = status !== 'Cancelled' && status !== 'Completed';

			if (isDraggable) {
				$(info.el).addClass('draggable-event');
				tooltip += '\n\n✓ Drag to reschedule or reassign';
			} else {
				$(info.el).addClass('non-draggable-event');
				tooltip += `\n\n✗ Cannot modify ${status.toLowerCase()} meetings`;
			}

			$(info.el).attr('title', tooltip);
		},

		// Handle event drop (drag and drop - both time change and resource change)
		eventDrop: function(info) {
			handleEventDrop(info, wrapper);
		},

		// Handle event resize (duration change)
		eventResize: function(info) {
			handleEventResize(info, wrapper);
		}
	});

	wrapper.calendar.render();

	// Set dynamic tooltips for buttons after render
	setTimeout(() => {
		const updateTooltips = () => {
			const currentView = wrapper.calendar.view;
			const viewName = currentView.type.includes('Day') ? 'Day' :
							currentView.type.includes('Week') ? 'Week' : 'Month';

			// Update Current button tooltip
			const todayBtn = document.querySelector('#mm-timeline-calendar .fc-today-button');
			if (todayBtn) {
				todayBtn.setAttribute('title', `Current ${viewName}`);
			}

			// Set other button tooltips
			const prevBtn = document.querySelector('#mm-timeline-calendar .fc-prev-button');
			if (prevBtn) prevBtn.setAttribute('title', 'Previous');

			const nextBtn = document.querySelector('#mm-timeline-calendar .fc-next-button');
			if (nextBtn) nextBtn.setAttribute('title', 'Next');

			const dayBtn = document.querySelector('#mm-timeline-calendar .fc-resourceTimeGridDay-button');
			if (dayBtn) dayBtn.setAttribute('title', 'Day view');

			const weekBtn = document.querySelector('#mm-timeline-calendar .fc-resourceTimeGridWeek-button');
			if (weekBtn) weekBtn.setAttribute('title', 'Week view');

			const monthBtn = document.querySelector('#mm-timeline-calendar .fc-dayGridMonth-button');
			if (monthBtn) monthBtn.setAttribute('title', 'Month view');
		};

		// Initial tooltip setup
		updateTooltips();

		// Update tooltips when view changes
		wrapper.calendar.on('viewDidMount', updateTooltips);
	}, 200);
}

/**
 * Setup event handlers for filters and controls
 */
function setupEventHandlers(wrapper) {
	// Department filter - also loads meeting types for that department
	$('#department-filter').off('change').on('change', function() {
		const department = $(this).val();

		// Load meeting types for selected department
		loadMeetingTypes(department);

		// Refetch resources and events
		if (wrapper.calendar) {
			wrapper.calendar.refetchResources();
			wrapper.calendar.refetchEvents();
		}
	});

	// Meeting Type filter
	$('#meeting-type-filter').off('change').on('change', function() {
		if (wrapper.calendar) {
			wrapper.calendar.refetchEvents();
		}
	});

	// Status filter
	$('#status-filter').off('change').on('change', function() {
		if (wrapper.calendar) {
			wrapper.calendar.refetchEvents();
		}
	});

	// Service filter
	$('#service-filter').off('change').on('change', function() {
		if (wrapper.calendar) {
			wrapper.calendar.refetchEvents();
		}
	});

	// Status Color filter
	$('#status-color-filter').off('change').on('change', function() {
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
 * Handle event drop (drag and drop)
 * Detects whether it's a reschedule (time change) or reassignment (resource/host change)
 */
function handleEventDrop(info, wrapper) {
	const event = info.event;
	const oldEvent = info.oldEvent;
	const oldResource = info.oldResource;
	const newResource = info.newResource || event.getResources()[0];
	const status = event.extendedProps.status;

	// Check if event status allows editing
	if (status === 'Cancelled' || status === 'Completed') {
		frappe.show_alert({
			message: `Cannot modify ${status.toLowerCase()} meetings`,
			indicator: 'red'
		}, 3);
		info.revert();
		return;
	}

	// Check if resource (host) changed
	const resourceChanged = oldResource && newResource && (oldResource.id !== newResource.id);

	// Check if time changed
	const timeChanged = oldEvent.start.getTime() !== event.start.getTime() ||
						oldEvent.end.getTime() !== event.end.getTime();

	if (!resourceChanged && !timeChanged) {
		// Nothing changed, just revert
		info.revert();
		return;
	}

	// For resource changes, verify department is selected
	if (resourceChanged) {
		const department = document.getElementById('department-filter')?.value;
		if (!department) {
			frappe.show_alert({
				message: 'Please select a department first to reassign meetings',
				indicator: 'orange'
			}, 4);
			info.revert();
			return;
		}
	}

	// Format dates for display
	const newStart = event.start.toLocaleString('en-US', {
		weekday: 'short',
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: '2-digit',
		hour12: true
	});
	const newEnd = event.end.toLocaleString('en-US', {
		hour: 'numeric',
		minute: '2-digit',
		hour12: true
	});

	// Build confirmation message
	let message = '';
	if (resourceChanged && timeChanged) {
		message = `Reschedule AND reassign this meeting?<br><br>` +
				  `<strong>New Host:</strong> ${newResource.title}<br>` +
				  `<strong>New Time:</strong> ${newStart} - ${newEnd}`;
	} else if (resourceChanged) {
		message = `Reassign this meeting to <strong>${newResource.title}</strong>?`;
	} else {
		message = `Reschedule this meeting to:<br><strong>${newStart} - ${newEnd}</strong>?`;
	}

	// Show confirmation dialog
	frappe.confirm(
		message,
		() => {
			// User confirmed - update the booking
			updateBooking(event, newResource, resourceChanged, timeChanged, info, wrapper);
		},
		() => {
			// User cancelled - revert the change
			info.revert();
		}
	);
}

/**
 * Handle event resize (duration change)
 */
function handleEventResize(info, wrapper) {
	const event = info.event;
	const status = event.extendedProps.status;

	// Check if event status allows editing
	if (status === 'Cancelled' || status === 'Completed') {
		frappe.show_alert({
			message: `Cannot modify ${status.toLowerCase()} meetings`,
			indicator: 'red'
		}, 3);
		info.revert();
		return;
	}

	// Format new end time for display
	const newEnd = event.end.toLocaleString('en-US', {
		hour: 'numeric',
		minute: '2-digit',
		hour12: true
	});

	const duration = Math.round((event.end - event.start) / (1000 * 60)); // Duration in minutes

	// Show confirmation dialog
	frappe.confirm(
		`Change meeting duration to <strong>${duration} minutes</strong>?<br>` +
		`New end time: <strong>${newEnd}</strong>`,
		() => {
			// User confirmed - update the booking
			updateBooking(event, null, false, true, info, wrapper);
		},
		() => {
			// User cancelled - revert the change
			info.revert();
		}
	);
}

/**
 * Update booking via API
 */
function updateBooking(event, newResource, resourceChanged, timeChanged, info, wrapper) {
	const bookingId = event.id;

	// Prepare update data
	const updateData = {
		booking_id: bookingId
	};

	if (timeChanged) {
		updateData.start_datetime = event.start.toISOString();
		updateData.end_datetime = event.end.toISOString();
	}

	if (resourceChanged && newResource) {
		updateData.new_host = newResource.id;
		// Include department for validation
		updateData.department = document.getElementById('department-filter')?.value;
	}

	// Show loading indicator
	frappe.show_alert({
		message: 'Updating booking...',
		indicator: 'blue'
	}, 2);

	// Call API to update booking
	frappe.call({
		method: 'meeting_manager.meeting_manager.page.mm_timeline_calendar.api.update_booking',
		args: updateData,
		callback: (r) => {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: r.message.message || 'Booking updated successfully',
					indicator: 'green'
				}, 3);

				// Refetch events to ensure calendar is in sync
				if (wrapper.calendar) {
					wrapper.calendar.refetchEvents();
				}
			} else {
				// Update failed, revert the change
				frappe.show_alert({
					message: r.message?.message || 'Failed to update booking',
					indicator: 'red'
				}, 5);
				info.revert();
			}
		},
		error: (error) => {
			// Error occurred, revert the change
			frappe.show_alert({
				message: 'Error updating booking: ' + (error.message || 'Unknown error'),
				indicator: 'red'
			}, 5);
			info.revert();
		}
	});
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

/**
 * Load meeting types for filter dropdown (dependent on department)
 */
function loadMeetingTypes(department) {
	const select = document.getElementById('meeting-type-filter');

	// Reset the dropdown
	select.innerHTML = '<option value="">All Meeting Types</option>';

	if (!department) {
		// If no department selected, disable the meeting type filter
		select.disabled = true;
		return;
	}

	// Enable the dropdown
	select.disabled = false;

	// Load meeting types for the selected department
	frappe.call({
		method: 'meeting_manager.meeting_manager.page.mm_timeline_calendar.api.get_meeting_types',
		args: { department: department },
		callback: (r) => {
			if (r.message && r.message.length > 0) {
				r.message.forEach(mt => {
					const option = document.createElement('option');
					option.value = mt.name;
					option.textContent = mt.meeting_name;
					select.appendChild(option);
				});
			} else {
				// No meeting types found for this department
				const option = document.createElement('option');
				option.value = '';
				option.textContent = 'No meeting types available';
				option.disabled = true;
				select.appendChild(option);
			}
		},
		error: () => {
			frappe.show_alert({
				message: 'Failed to load meeting types',
				indicator: 'red'
			});
		}
	});
}
