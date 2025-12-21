# Timeline Calendar - Meeting Manager

A professional resource-based timeline calendar view for managing meeting bookings.

## Overview

This page displays meetings in a timeline format with team members as columns and time slots as rows. It supports day, week, and month views with filtering by department and status.

## Features

- **Resource Timeline View**: Team members displayed as columns
- **Multiple Views**: Day (default), Week, and Month views
- **30-Minute Time Slots**: From 07:00 to 22:00
- **Current Time Indicator**: Red line showing current time
- **Status-Based Color Coding**:
  - Green: Confirmed
  - Yellow/Orange: Pending
  - Red: Cancelled
  - Blue: Completed
  - Gray: No-Show
  - Purple: Rescheduled
- **Filters**:
  - Department dropdown
  - Status dropdown
- **Dark/Light Theme Toggle**: User preference saved in localStorage
- **Event Interaction**: Click meetings to open the booking form
- **Permission-Based Access**: Different visibility for System Managers, Department Leaders, and Team Members

## Architecture

### Files

```
mm_timeline_calendar/
├── __init__.py                    # Python package marker
├── mm_timeline_calendar.json      # Page DocType definition
├── mm_timeline_calendar.js        # Frontend page loader and FullCalendar setup
├── api.py                         # Backend API endpoints
└── README.md                      # This file
```

### Technology Stack

- **Frontend**: FullCalendar v6.1.10 Scheduler (loaded from CDN)
- **Backend**: Frappe Python API
- **Data Source**: MM Meeting Booking DocType

## API Endpoints

### `get_resources(department=None)`

Returns team members to display as calendar resources.

**Parameters:**
- `department` (str, optional): Filter by department

**Returns:**
```python
[
    {"id": "user@example.com", "title": "John Doe"},
    ...
]
```

**Permission Logic:**
- System Managers: See all users
- Department Leaders: See members of departments they lead
- Team Members: See only themselves

### `get_events(start, end, department=None, status=None)`

Returns meetings for the calendar display.

**Parameters:**
- `start` (str): Start datetime in ISO format
- `end` (str): End datetime in ISO format
- `department` (str, optional): Filter by department
- `status` (str, optional): Filter by booking status

**Returns:**
```python
[
    {
        "id": "MM-MB-0001",
        "resourceId": "user@example.com",
        "title": "John Doe - 30-min Call",
        "start": "2025-12-17T14:00:00",
        "end": "2025-12-17T14:30:00",
        "backgroundColor": "#10b981",
        "borderColor": "#10b981",
        "textColor": "#ffffff",
        "extendedProps": {
            "booking_reference": "BK-0001",
            "customer_name": "John Doe",
            "status": "Confirmed",
            ...
        }
    },
    ...
]
```

## Usage

### Accessing the Page

1. **Direct URL**: `http://your-site:port/app/mm-timeline-calendar`
2. **Awesome Bar**: Search for "Timeline Calendar"
3. **Workspace**: Add link to Meeting Manager workspace

### View Controls

- **Navigation**:
  - `prev` / `next` buttons: Move forward/backward by current view (day/week/month)
  - `today` button: Jump to current date
- **View Switching**:
  - Day: Click "resourceTimelineDay"
  - Week: Click "resourceTimelineWeek"
  - Month: Click "dayGridMonth"
- **Filters**:
  - Select department to filter resources and events
  - Select status to filter events by booking status
- **Theme Toggle**:
  - Click moon icon to switch between dark and light themes
  - Preference saved in browser localStorage

### Interacting with Events

- **Click Event**: Opens the MM Meeting Booking form
- **Hover Event**: Shows tooltip with event details

## Permissions

### System Manager
- Sees all team members as resources
- Sees all meetings

### Department Leader
- Sees members from departments they lead
- Sees only meetings assigned to those members

### Team Member
- Sees only themselves as a resource
- Sees only their own meetings

## Color Coding

Colors are based on `booking_status` field:

| Status | Color | Hex Code |
|--------|-------|----------|
| Confirmed | Green | #10b981 |
| Pending | Yellow/Orange | #f59e0b |
| Cancelled | Red | #ef4444 |
| Completed | Blue | #3b82f6 |
| No-Show | Gray | #6b7280 |
| Rescheduled | Purple | #8b5cf6 |

## Performance Considerations

- **Date Range Limit**: Events are limited to the visible date range
- **Result Limit**: Maximum 500 meetings per query
- **Caching**: Department list cached client-side

## Customization

### Changing Time Range

Edit `mm_timeline_calendar.js`:

```javascript
slotMinTime: '08:00:00',  // Start time
slotMaxTime: '20:00:00',  // End time
```

### Changing Slot Duration

```javascript
slotDuration: '00:15:00',      // 15-minute slots
slotLabelInterval: '01:00:00', // Hourly labels
```

### Changing Resource Column Width

```javascript
resourceAreaWidth: '250px',  // Wider column
```

### Adding Custom Event Fields

Update `api.py` in the `get_events` function to include additional fields in `extendedProps`.

## Troubleshooting

### Calendar Not Loading

1. Check browser console for errors
2. Ensure FullCalendar Scheduler CDN is accessible
3. Clear cache: `bench --site your-site clear-cache`

### No Resources Showing

1. Verify user has correct permissions
2. Check that MM Department has active members
3. Verify department filter is not set to empty department

### Events Not Appearing

1. Check date range (events must be within visible dates)
2. Verify status filter is not excluding events
3. Check API logs for errors: `bench --site your-site logs`

### Permission Issues

1. Verify user roles in User DocType
2. Check department leader assignment in MM Department
3. Verify MM Meeting Booking has assigned users

## Future Enhancements

- [ ] Drag-and-drop to reschedule meetings
- [ ] Create new bookings by clicking time slots
- [ ] Multi-resource booking support
- [ ] Availability overlay
- [ ] Export calendar (PDF/Excel)
- [ ] Real-time updates via Socket.IO
- [ ] Add color field to MM Meeting Type
- [ ] Google Calendar / Outlook integration
- [ ] Print view
- [ ] Meeting conflict detection

## References

- [FullCalendar Documentation](https://fullcalendar.io/docs)
- [FullCalendar Scheduler](https://fullcalendar.io/docs/premium)
- [Resource Timeline View](https://fullcalendar.io/docs/timeline-view)
- Frappe Page: [mm_manage_meetings](../mm_manage_meetings/)

## License

Uses FullCalendar Scheduler with GPL-My-Project-Is-Open-Source license key.
Ensure compliance with FullCalendar's licensing terms for your use case.
