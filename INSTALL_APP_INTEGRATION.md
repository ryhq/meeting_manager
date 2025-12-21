# Meeting Manager - App Integration Setup

This guide shows you how to add Meeting Manager to the Frappe Apps screen so users can access it like Helpdesk and ERPNext.

## What You'll Get

After following these steps, users will:
1. See **Meeting Manager** in the Apps screen (alongside Helpdesk, ERPNext, etc.)
2. Click the Meeting Manager icon to access the workspace
3. See shortcuts to:
   - Meeting Bookings
   - Departments
   - Meeting Types
   - User Settings
   - Availability Rules

---

## Automatic Installation (Recommended)

The workspace is **automatically created** when you install the app. No manual steps needed!

### Fresh Installation

```bash
cd ~/Documents/FRAPPER_PROJECTS/bestsecurity-bench
bench --site bestsecurity.local install-app meeting_manager
```

**Expected Output:**
```
Installing meeting_manager...
============================================================
✅ Meeting Manager workspace created automatically!
============================================================

📌 Next Steps:
1. Refresh your browser (Ctrl+R or Cmd+R)
2. Click on 'Apps' in the top menu
3. You should see 'Meeting Manager' app
4. Click it to access the workspace
```

### Reinstallation (Testing)

If you want to test the automatic installation:

```bash
cd ~/Documents/FRAPPER_PROJECTS/bestsecurity-bench

# Uninstall the app
bench --site bestsecurity.local uninstall-app meeting_manager

# Reinstall it
bench --site bestsecurity.local install-app meeting_manager
```

The workspace will be created automatically during installation.

---

## Manual Setup (If Needed)

If for some reason the automatic installation didn't create the workspace, you can run it manually:

```bash
cd ~/Documents/FRAPPER_PROJECTS/bestsecurity-bench
bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.setup_workspace
```

**Expected Output:**
```
============================================================
🚀 SETTING UP MEETING MANAGER WORKSPACE
============================================================

Creating new workspace: Meeting Manager
✅ Workspace 'Meeting Manager' created/updated successfully

📄 Workspace saved to: meeting_manager/workspace/meeting_manager/meeting_manager.json

📊 Workspace contains:
   - 3 shortcuts
   - 5 links
   - 6 content blocks

📁 Workspace exported to: [path]

============================================================
✅ SETUP COMPLETE!
============================================================
```

After running the command:
1. Refresh your browser (Ctrl+R or Cmd+R)
2. Click on 'Apps' in the top menu
3. You should see 'Meeting Manager' app
4. Click it to access the workspace

---

## Accessing Meeting Manager

### From Apps Screen

1. Login to Frappe at `http://bestsecurity.local:8001`
2. Click **"Apps"** in the top navigation bar
3. Click the **"Meeting Manager"** icon
4. You'll see the Meeting Manager workspace with shortcuts

### Direct URLs

- **Workspace**: `http://bestsecurity.local:8001/app/meeting-manager`
- **Calendar View**: `http://bestsecurity.local:8001/calendar-view`
- **Create Meeting**: `http://bestsecurity.local:8001/create-meeting`

---

## Workspace Features

The Meeting Manager workspace includes:

### Quick Shortcuts
- 📋 **Meeting Bookings** - List of all bookings
- ➕ **New Department** - Create a department
- 📅 **Meeting Types** - List of meeting types

### Organized Links

**Bookings**
- Meeting Bookings (list view)

**Setup**
- Departments
- Meeting Types

**Configuration**
- User Settings
- Availability Rules

---

## Permissions

The app automatically checks permissions:

- **System Manager**: Full access to everything
- **Department Leader**: Access to their departments only
- **Department Members**: Access to their own bookings
- **Others**: No access (app won't appear)

This is controlled by [meeting_manager/utils/permissions.py:has_app_permission()](meeting_manager/meeting_manager/utils/permissions.py)

---

## How It Works

### Installation Hook

When you install the app, Frappe automatically calls:

```python
# From hooks.py line 99
after_install = "meeting_manager.meeting_manager.setup.after_install"
```

This function ([setup.py:after_install()](meeting_manager/meeting_manager/setup.py)):
1. Creates the Meeting Manager workspace
2. Adds shortcuts and links
3. Exports the workspace to JSON
4. Displays success message

### App Registration

The app appears in the Apps screen because of this configuration in [hooks.py](meeting_manager/hooks.py):

```python
add_to_apps_screen = [
	{
		"name": "meeting_manager",
		"logo": "/assets/meeting_manager/images/meeting-manager-logo.png",
		"title": "Meeting Manager",
		"route": "/app/meeting-manager",
		"has_permission": "meeting_manager.meeting_manager.utils.permissions.has_app_permission"
	}
]
```

### Workspace Export

The workspace is also exported as a fixture (lines 270-275 in hooks.py):

```python
fixtures = [
	{
		"doctype": "Workspace",
		"filters": [["name", "in", ["Meeting Manager"]]]
	}
]
```

This means the workspace will be included when you export fixtures with:
```bash
bench --site bestsecurity.local export-fixtures
```

---

## Customization

### Change the Icon

Edit [apps/meeting_manager/meeting_manager/hooks.py](meeting_manager/hooks.py):

```python
add_to_apps_screen = [
	{
		"name": "meeting_manager",
		"logo": "/assets/meeting_manager/images/meeting-manager-logo.png",  # Change this
		"title": "Meeting Manager",
		"route": "/app/meeting-manager",
		"has_permission": "meeting_manager.meeting_manager.utils.permissions.has_app_permission"
	}
]
```

Then run:
```bash
bench build --app meeting_manager
bench restart
```

### Add More Shortcuts

Edit [meeting_manager/meeting_manager/setup.py](meeting_manager/meeting_manager/setup.py) and add to the `shortcuts` list:

```python
shortcuts = [
	{
		"label": "Your New Shortcut",
		"link_to": "Your DocType",
		"type": "DocType",
		"doc_view": "List",  # or "New"
		"color": "Blue",     # Grey, Blue, Green, Red, etc.
		"icon": "calendar",
		"format": "{} Open"
	},
	# ... existing shortcuts
]
```

Then run:
```bash
bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.setup_workspace
```

### Modify Workspace Layout

The workspace layout is defined in [setup.py:setup_workspace()](meeting_manager/meeting_manager/setup.py) in the `content` array.

You can modify:
- Headers
- Card organization
- Link grouping

After changes, run:
```bash
bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.setup_workspace
```

---

## Troubleshooting

### App Not Appearing

**Problem**: Meeting Manager doesn't show in Apps screen

**Solutions**:
1. Check if you're logged in as a user with permission
2. Check browser console for errors (F12)
3. Clear browser cache (Ctrl+Shift+R)
4. Restart bench: `bench restart`
5. Run setup manually:
   ```bash
   bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.setup_workspace
   ```

### Permission Denied

**Problem**: "You don't have permission to access this app"

**Solutions**:
1. Ensure your user has one of these roles:
   - System Manager
   - Department Leader
   - Is a member of at least one MM Department

2. Add user to a department:
   ```python
   # In Frappe console (bench --site bestsecurity.local console)
   dept = frappe.get_doc("MM Department", "YOUR_DEPT")
   dept.append("department_members", {
       "member": "user@example.com",
       "is_active": 1
   })
   dept.save()
   ```

### Workspace is Empty

**Problem**: Workspace has no links or shortcuts

**Solutions**:
1. Run the setup script:
   ```bash
   bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.setup_workspace
   ```

2. Check if workspace was created:
   ```bash
   bench --site bestsecurity.local execute "frappe.db.exists('Workspace', 'Meeting Manager')"
   ```

3. Manually edit via UI:
   - Go to `http://bestsecurity.local:8001/app/workspace/Meeting Manager`
   - Click "Edit"
   - Add shortcuts and links manually
   - Save

### Icon Not Showing

**Problem**: App icon is blank or broken

**Solutions**:
1. Check if logo file exists:
   ```bash
   ls -la apps/meeting_manager/meeting_manager/public/images/
   ```

2. Rebuild assets:
   ```bash
   bench build --app meeting_manager
   bench restart
   ```

3. Use a different image format (PNG vs SVG)

### Installation Hook Didn't Run

**Problem**: App installed but workspace wasn't created automatically

**Solutions**:
1. Check if hook is configured in [hooks.py:99](meeting_manager/hooks.py):
   ```python
   after_install = "meeting_manager.meeting_manager.setup.after_install"
   ```

2. Run the setup manually:
   ```bash
   bench --site bestsecurity.local execute meeting_manager.meeting_manager.setup.after_install
   ```

3. Check error logs:
   ```bash
   tail -f logs/frappe.log
   ```

---

## Files Reference

This integration involves:

```
apps/meeting_manager/
├── meeting_manager/
│   ├── hooks.py                                    # App registration & hooks
│   ├── meeting_manager/
│   │   ├── setup.py                                # Workspace setup functions
│   │   ├── utils/
│   │   │   └── permissions.py                      # Permission checker
│   │   └── workspace/
│   │       └── meeting_manager/
│   │           └── meeting_manager.json            # Workspace definition
│   └── public/
│       └── images/
│           ├── meeting-manager-logo.svg            # App icon (SVG)
│           └── meeting-manager-logo.png            # App icon (PNG)
└── INSTALL_APP_INTEGRATION.md                      # This guide
```

---

## Testing Checklist

After installation, verify:

- [ ] Meeting Manager appears in Apps screen
- [ ] Clicking the icon opens the workspace
- [ ] Workspace shows shortcuts
- [ ] Workspace shows organized links
- [ ] Permission check works (try as different user roles)
- [ ] Calendar View accessible via direct URL
- [ ] Create Meeting accessible via direct URL
- [ ] All DocType links work from workspace

---

## Next Steps

After integration is complete:

1. **Create Test Data**:
   - Add departments
   - Add department members
   - Create meeting types
   - Set user availability

2. **Test Features**:
   - Create internal meeting
   - Create customer meeting
   - Use calendar view
   - Test drag-and-drop

3. **Configure**:
   - Set up email notifications
   - Configure meeting types
   - Set department settings

---

## Support

For issues or questions:
- Check the main project documentation: `Meeting_Manager_PD.md`
- Review implementation phases
- Check API documentation in `api/booking.py`
