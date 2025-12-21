/**
 * Manage Meetings Page - React Integration
 * This page loads a React component for managing meeting bookings
 */

frappe.pages['mm-manage-meetings'].on_page_load = function(wrapper) {
	// Create the Frappe app page
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Manage Meetings',
		single_column: true
	});

	// Create a root div for React
	wrapper.meeting_root = document.createElement('div');
	wrapper.meeting_root.id = 'mm-manage-meetings-root';
	wrapper.meeting_root.style.height = '100%';

	// Append to the layout main section
	wrapper.querySelector('.layout-main-section').appendChild(wrapper.meeting_root);

	// Add custom CSS for animations and Tailwind-like utilities
	const style = document.createElement('style');
	style.textContent = `
		@keyframes spin {
			0% { transform: rotate(0deg); }
			100% { transform: rotate(360deg); }
		}

		#mm-manage-meetings-root .bg-green-100 {
			background-color: #d1fae5;
		}
		#mm-manage-meetings-root .text-green-800 {
			color: #065f46;
		}
		#mm-manage-meetings-root .border-green-200 {
			border-color: #a7f3d0;
		}

		#mm-manage-meetings-root .bg-yellow-100 {
			background-color: #fef3c7;
		}
		#mm-manage-meetings-root .text-yellow-800 {
			color: #92400e;
		}
		#mm-manage-meetings-root .border-yellow-200 {
			border-color: #fde68a;
		}

		#mm-manage-meetings-root .bg-red-100 {
			background-color: #fee2e2;
		}
		#mm-manage-meetings-root .text-red-800 {
			color: #991b1b;
		}
		#mm-manage-meetings-root .border-red-200 {
			border-color: #fecaca;
		}

		#mm-manage-meetings-root .bg-blue-100 {
			background-color: #dbeafe;
		}
		#mm-manage-meetings-root .text-blue-800 {
			color: #1e40af;
		}
		#mm-manage-meetings-root .border-blue-200 {
			border-color: #bfdbfe;
		}

		#mm-manage-meetings-root .bg-gray-100 {
			background-color: #f3f4f6;
		}
		#mm-manage-meetings-root .text-gray-800 {
			color: #1f2937;
		}
		#mm-manage-meetings-root .border-gray-200 {
			border-color: #e5e7eb;
		}
	`;
	document.head.appendChild(style);
};

frappe.pages['mm-manage-meetings'].on_page_show = function(wrapper) {
	// Load and mount React component
	frappe.require('mm_manage_meetings/bundle.js').then(() => {
		if (window.meeting_manager && window.meeting_manager.mm_manage_meetings) {
			wrapper.react_root = window.meeting_manager.mm_manage_meetings.mount(wrapper.meeting_root);
		} else {
			console.error('React component not loaded properly');
			frappe.msgprint('Failed to load the page. Please refresh and try again.');
		}
	}).catch((error) => {
		console.error('Error loading React bundle:', error);
		frappe.msgprint('Failed to load the page. Please refresh and try again.');
	});
};

frappe.pages['mm-manage-meetings'].on_page_hide = function(wrapper) {
	// Clean unmount when navigating away
	if (wrapper.react_root) {
		try {
			wrapper.react_root.unmount();
			wrapper.react_root = null;
		} catch (error) {
			console.error('Error unmounting React component:', error);
		}
	}
};