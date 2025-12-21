/**
 * Bundle entry point for Manage Meetings React page
 * Exposes the mount function to Frappe's global scope
 */
import { mount } from "./index.js";

// Create namespace if it doesn't exist
window.meeting_manager = window.meeting_manager || {};

// Expose mount function
window.meeting_manager.mm_manage_meetings = {
	mount
};
