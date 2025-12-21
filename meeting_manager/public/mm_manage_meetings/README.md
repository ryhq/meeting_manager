# Manage Meetings - React Page

This is a React-based page for managing meeting bookings in the Meeting Manager app.

## Architecture

```
mm_manage_meetings/
├── index.jsx      # Main React component
├── bundle.js      # Entry point that exposes mount function
└── README.md      # This file
```

## How It Works

1. **Page Load**: Frappe loads `mm_manage_meetings.js` which creates the page structure
2. **React Mount**: When page is shown, it loads `bundle.js` which mounts the React component
3. **Data Fetching**: React component calls backend API at `mm_manage_meetings/api.py`
4. **Clean Unmount**: When navigating away, React unmounts cleanly

## Building

### Development Mode (Watch)
```bash
cd /home/ricksy/Documents/FRAPPER_PROJECTS/bestsecurity-bench
bench watch
```

### Production Build
```bash
cd /home/ricksy/Documents/FRAPPER_PROJECTS/bestsecurity-bench
bench build --app meeting_manager
```

## Features

- **Dashboard View**: Shows statistics (Total, Confirmed, Pending, Completed)
- **Meeting List**: Cards with meeting details
- **Search**: Filter meetings by reference, customer name, or meeting type
- **Status Filter**: Filter by meeting status
- **Quick Actions**: View details, mark complete, cancel
- **Responsive Design**: Works on desktop and mobile

## Components

### ManageMeetings (Main)
Main container component that manages state and data fetching

### StatCard
Displays statistics with icon and count

### MeetingCard
Individual meeting card with details and actions

### InfoItem
Displays label-value pairs

### LoadingSpinner
Loading state indicator

### EmptyState
Shows when no meetings are found

## API Endpoints

### `get_meetings(status=None)`
- **Method**: POST
- **Path**: `meeting_manager.meeting_manager.page.mm_manage_meetings.api.get_meetings`
- **Args**:
  - `status` (optional): Filter by status
- **Returns**:
  ```json
  {
    "meetings": [...],
    "stats": {
      "total": 0,
      "confirmed": 0,
      "pending": 0,
      "completed": 0
    }
  }
  ```

## Permissions

- **System Manager**: Can see all meetings
- **Department Leader**: Can see meetings in their departments
- **Team Members**: Can see only their assigned meetings

## Styling

Uses inline styles with Tailwind-like utility classes injected via `<style>` tag in the page loader.

## Future Enhancements

- [ ] Add date range filter
- [ ] Add department filter
- [ ] Add export functionality
- [ ] Add bulk actions
- [ ] Add meeting creation from this page
- [ ] Add pagination for large datasets
- [ ] Add real-time updates via Socket.IO
