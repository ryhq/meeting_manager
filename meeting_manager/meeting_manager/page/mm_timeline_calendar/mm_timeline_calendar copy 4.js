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

	// Create calendar container
	wrapper.calendar_container = document.createElement('div');
	wrapper.calendar_container.id = 'mm-timeline-calendar';
	wrapper.calendar_container.style.height = '100%';
	wrapper.calendar_container.style.padding = '20px';
	wrapper.calendar_container.style.position = 'relative';

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

		/* Fix for week view - prevent shrinking and vertical text */
		#mm-timeline-calendar .fc-resourceTimeGridWeek-view .fc-timegrid-col {
			min-width: 150px !important;
		}

		#mm-timeline-calendar .fc-resourceTimeGridWeek-view .fc-col-header-cell {
			min-width: 150px !important;
			width: 150px;
		}

		/* Horizontal date formatting in week view */
		#mm-timeline-calendar .fc-col-header-cell-cushion {
			padding: 8px 4px;
			display: block;
			white-space: nowrap !important;
			overflow: hidden;
			text-overflow: ellipsis;
		}

		/* Time column width and styling - CRITICAL */
		#mm-timeline-calendar .fc-timegrid-axis-cushion,
		#mm-timeline-calendar .fc-timegrid-slot-label-cushion {
			min-width: 80px !important;
			width: 80px !important;
			text-align: right;
			padding-right: 10px;
			display: block !important;
		}

		#mm-timeline-calendar .fc-timegrid-axis,
		#mm-timeline-calendar th.fc-timegrid-axis {
			min-width: 80px !important;
			width: 80px !important;
			max-width: 80px !important;
			display: table-cell !important;
			visibility: visible !important;
		}

		#mm-timeline-calendar .fc-timegrid-slot-label,
		#mm-timeline-calendar td.fc-timegrid-slot-label {
			min-width: 80px !important;
			width: 80px !important;
			max-width: 80px !important;
			display: table-cell !important;
			visibility: visible !important;
		}

		/* Force the time column frame to be visible */
		#mm-timeline-calendar .fc-timegrid-axis-frame {
			display: block !important;
			min-width: 80px !important;
		}

		/* CRITICAL: Force time columns in scrollgrid to not be shrunk/hidden */
		#mm-timeline-calendar .fc-scrollgrid-shrink {
			width: 80px !important;
			min-width: 80px !important;
		}

		#mm-timeline-calendar .fc-timegrid-axis.fc-scrollgrid-shrink,
		#mm-timeline-calendar .fc-timegrid-slot-label.fc-scrollgrid-shrink {
			width: 80px !important;
			min-width: 80px !important;
			flex-shrink: 0 !important;
		}

		/* CRITICAL: Ensure the scrollgrid section doesn't clip the time column */
		#mm-timeline-calendar .fc-scrollgrid-section > td {
			overflow: visible !important;
		}

		#mm-timeline-calendar .fc-scrollgrid-section-body > td:first-child,
		#mm-timeline-calendar .fc-scrollgrid-section-header > th:first-child {
			overflow: visible !important;
			position: relative !important;
			z-index: 20 !important;
		}

		/* CRITICAL FIX: Make time column sticky and visible */
		/* Apply to all variations of time column selectors */
		#mm-timeline-calendar .fc-timegrid-axis,
		#mm-timeline-calendar .fc-timegrid-slot-label,
		#mm-timeline-calendar th.fc-timegrid-axis,
		#mm-timeline-calendar td.fc-timegrid-slot-label {
			position: sticky !important;
			left: 0 !important;
			z-index: 15 !important;
			background-color: var(--fc-bg-color) !important;
		}

		/* Ensure header time cell has distinct background and higher z-index */
		#mm-timeline-calendar th.fc-timegrid-axis {
			background-color: var(--fc-neutral-bg-color) !important;
			z-index: 20 !important;
		}

		/* Force visibility of time text */
		#mm-timeline-calendar .fc-timegrid-axis-cushion,
		#mm-timeline-calendar .fc-timegrid-slot-label-cushion {
			visibility: visible !important;
			display: block !important;
			opacity: 1 !important;
		}

		/* CRITICAL: Make column headers sticky at top */
		#mm-timeline-calendar .fc-col-header {
			position: sticky !important;
			top: 0 !important;
			z-index: 12 !important;
			background-color: var(--fc-bg-color) !important;
		}

		/* Ensure all header rows are sticky */
		#mm-timeline-calendar .fc-col-header-cell-cushion {
			background-color: var(--fc-neutral-bg-color) !important;
		}

		/* Resource header (user names) should be sticky */
		#mm-timeline-calendar thead.fc-col-header {
			position: sticky !important;
			top: 0 !important;
			z-index: 12 !important;
		}

		/* Week view: Make sure day headers within resource columns are visible */
		#mm-timeline-calendar .fc-resourceTimeGridWeek-view .fc-col-header {
			position: sticky !important;
			top: 0 !important;
			z-index: 12 !important;
		}

		/* Ensure proper scrolling container setup */
		#mm-timeline-calendar .fc-scroller-liquid-absolute {
			overflow-x: auto !important;
			overflow-y: auto !important;
		}

		#mm-timeline-calendar .fc-scroller-harness {
			overflow: visible !important;
		}

		/* Fix for the scrollable content area */
		#mm-timeline-calendar .fc-timegrid-body {
			overflow-x: auto !important;
		}

		/* Make the time grid container handle scroll properly */
		#mm-timeline-calendar .fc-timegrid-slots,
		#mm-timeline-calendar .fc-timegrid-cols {
			min-width: max-content;
		}

		/* Prevent the header from having its own scroll */
		#mm-timeline-calendar .fc-col-header-cell {
			position: relative;
		}

		/* Ensure the view container allows overflow */
		#mm-timeline-calendar .fc-view-harness {
			overflow: visible !important;
		}

		#mm-timeline-calendar .fc-timegrid {
			overflow: visible !important;
		}

		/* Week view specific: ensure day headers align with columns */
		#mm-timeline-calendar .fc-resourceTimeGridWeek-view .fc-daygrid-day-frame {
			min-height: 30px;
		}

		/* CRITICAL: Ensure proper table layout for headers */
		#mm-timeline-calendar .fc-scrollgrid {
			border-collapse: separate;
		}

		/* Make sure the header table matches body table width */
		#mm-timeline-calendar .fc-scrollgrid-sync-table {
			width: 100%;
		}

		/* Ensure all columns maintain their width during scroll */
		#mm-timeline-calendar .fc-timegrid-col-frame {
			min-width: inherit;
		}

		/* Fix for potential header/body misalignment */
		#mm-timeline-calendar .fc-scrollgrid-section-header > * {
			overflow-x: auto !important;
			overflow-y: hidden !important;
		}

		#mm-timeline-calendar .fc-scrollgrid-section-body > * {
			overflow-x: auto !important;
		}

		/* Remove individual scrollbars from inner elements to prevent double scrolling */
		#mm-timeline-calendar .fc-scrollgrid-section-header .fc-scroller {
			overflow-x: hidden !important;
		}

		/* ULTRA CRITICAL: Prevent scroller from clipping the sticky time column */
		#mm-timeline-calendar .fc-scroller {
			position: relative !important;
		}

		/* Make sure the time column stays above the scroller overflow */
		#mm-timeline-calendar .fc-timegrid-axis,
		#mm-timeline-calendar .fc-timegrid-slot-label {
			position: sticky !important;
			left: 0 !important;
			z-index: 100 !important;
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
 * Setup scroll synchronization between header and body
 */
function setupScrollSync(calendarEl, viewType) {
	// Clean up any existing scroll listeners
	if (calendarEl._scrollSyncHandlers) {
		calendarEl._scrollSyncHandlers.forEach(({scroller, handler}) => {
			scroller.removeEventListener('scroll', handler);
		});
		calendarEl._scrollSyncHandlers = [];
	}

	// Find the scrollable sections in the scrollgrid
	// FullCalendar uses separate scrollers for header and body
	const headerSection = calendarEl.querySelector('.fc-scrollgrid-section-header');
	const bodySection = calendarEl.querySelector('.fc-scrollgrid-section-body');

	if (!headerSection || !bodySection) {
		console.warn('Could not find scrollgrid sections');
		return;
	}

	// Find scrollers within each section
	const headerScroller = headerSection.querySelector('.fc-scroller');
	const bodyScroller = bodySection.querySelector('.fc-scroller');

	if (!headerScroller || !bodyScroller) {
		console.warn('Could not find scrollers in sections');
		console.log('Header scroller:', headerScroller);
		console.log('Body scroller:', bodyScroller);
		return;
	}

	console.log('Setting up scroll sync between header and body scrollers');

	const handlers = [];

	// Sync body scroll to header
	let isSyncingFromBody = false;
	const bodyScrollHandler = function() {
		if (isSyncingFromBody) return;
		isSyncingFromBody = true;

		requestAnimationFrame(() => {
			headerScroller.scrollLeft = bodyScroller.scrollLeft;
			isSyncingFromBody = false;
		});
	};

	bodyScroller.addEventListener('scroll', bodyScrollHandler, { passive: true });
	handlers.push({ scroller: bodyScroller, handler: bodyScrollHandler });

	// Sync header scroll to body (for when user scrolls the header)
	let isSyncingFromHeader = false;
	const headerScrollHandler = function() {
		if (isSyncingFromHeader) return;
		isSyncingFromHeader = true;

		requestAnimationFrame(() => {
			bodyScroller.scrollLeft = headerScroller.scrollLeft;
			isSyncingFromHeader = false;
		});
	};

	headerScroller.addEventListener('scroll', headerScrollHandler, { passive: true });
	handlers.push({ scroller: headerScroller, handler: headerScrollHandler });

	// Store handlers for cleanup
	calendarEl._scrollSyncHandlers = handlers;

	console.log('Scroll synchronization setup completed for view:', viewType);
}

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

		// Week view date format (horizontal layout)
		dayHeaderFormat: {
			weekday: 'short',
			month: 'numeric',
			day: 'numeric',
			omitCommas: true
		},

		// Resource column width settings
		resourceAreaWidth: '150px',

		// Display options
		height: 'auto',
		contentHeight: 'auto',
		expandRows: false,
		handleWindowResize: true,

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
		},

		viewDidMount: function(info) {
			// Apply inline styles to ensure time column is visible
			setTimeout(() => {
				console.log('View mounted:', info.view.type);

				// Debug: Log scrollgrid structure
				const scrollgrid = calendarEl.querySelector('.fc-scrollgrid');
				if (scrollgrid) {
					console.log('Scrollgrid found, examining structure...');
					const shrinkCells = scrollgrid.querySelectorAll('.fc-scrollgrid-shrink');
					console.log('Found', shrinkCells.length, 'shrink cells');
					shrinkCells.forEach((cell, idx) => {
						console.log(`Shrink cell ${idx}:`, cell.className, 'computed width:', window.getComputedStyle(cell).width);
					});
				}

				// Force time column to be visible and sticky
				const timeElements = calendarEl.querySelectorAll('.fc-timegrid-axis, .fc-timegrid-slot-label');
				console.log('Found', timeElements.length, 'time elements');

				timeElements.forEach((el, idx) => {
					// Force visibility and width with MAXIMUM z-index
					el.style.setProperty('z-index', '100', 'important');
					el.style.setProperty('position', 'sticky', 'important');
					el.style.setProperty('left', '0', 'important');
					el.style.setProperty('background-color', '#f3f4f6', 'important');
					el.style.setProperty('display', 'table-cell', 'important');
					el.style.setProperty('min-width', '80px', 'important');
					el.style.setProperty('width', '80px', 'important');
					el.style.setProperty('max-width', '80px', 'important');
					el.style.setProperty('visibility', 'visible', 'important');
					el.style.setProperty('flex-shrink', '0', 'important');
					el.style.setProperty('overflow', 'visible', 'important');

					// Add a visible border for debugging
					el.style.setProperty('border-right', '2px solid #e5e7eb', 'important');

					// Debug: Check if element has content and position
					const content = el.textContent.trim();
					const rect = el.getBoundingClientRect();
					if (idx < 5) {
						console.log(`Time element ${idx}: "${content}", width: ${window.getComputedStyle(el).width}, position: ${rect.left}px, ${rect.top}px`);
					}
				});

				// Make sure time column header is visible
				const timeAxisHeader = calendarEl.querySelector('th.fc-timegrid-axis');
				if (timeAxisHeader) {
					timeAxisHeader.style.setProperty('display', 'table-cell', 'important');
					timeAxisHeader.style.setProperty('width', '80px', 'important');
					timeAxisHeader.style.setProperty('min-width', '80px', 'important');
					timeAxisHeader.style.setProperty('visibility', 'visible', 'important');
					console.log('Time axis header found and styled, content:', timeAxisHeader.textContent);
				} else {
					console.warn('Time axis header NOT found');
				}

				// Make column headers sticky (but not the time column header)
				const headerElements = calendarEl.querySelectorAll('.fc-col-header');
				headerElements.forEach(el => {
					el.style.setProperty('position', 'sticky', 'important');
					el.style.setProperty('top', '0', 'important');
					el.style.setProperty('z-index', '12', 'important');
				});

				// Setup scroll synchronization
				setupScrollSync(calendarEl, info.view.type);

				console.log('Sticky positioning and scroll sync applied');
			}, 100);
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
