# Meeting Manager - Department-Based Booking System

# Table of Contents

- [Meeting Manager - Department-Based Booking System](#meeting-manager---department-based-booking-system)
  - [Project Overview](#project-overview)
  - [Business Requirements](#business-requirements)
    - [Core Objectives](#core-objectives)
  - [Functional Requirements](#functional-requirements)
    - [1. Department & Calendar Management](#1-department--calendar-management)
      - [Department Profile](#department-profile)
      - [Availability Rules](#availability-rules)
      - [Calendar Integration](#calendar-integration)
    - [2. Meeting Types](#2-meeting-types)
      - [Meeting Type Properties](#meeting-type-properties)
      - [Booking Link Generation](#booking-link-generation)
    - [3. Scheduling Engine](#3-scheduling-engine)
      - [Availability Calculation](#availability-calculation)
      - [Conflict Prevention](#conflict-prevention)
      - [Time Zone Handling](#time-zone-handling)
    - [4. Public Booking Interface](#4-public-booking-interface)
      - [Step 1: Select Department](#step-1-select-department)
      - [Step 2: Select Meeting Type](#step-2-select-meeting-type)
      - [Step 3: Choose Date](#step-3-choose-date)
      - [Step 4: Choose Time](#step-4-choose-time)
      - [Step 5: Enter Customer Details](#step-5-enter-customer-details)
      - [Step 6: Confirmation (Public Page)](#step-6-confirmation-public-page)
      - [Email Confirmations Sent](#email-confirmations-sent)
      - [Under the Hood (Auto-Assignment)](#under-the-hood-auto-assignment)
    - [5. Internal Management Interface](#5-internal-management-interface)
      - [Calendar View (Drag-and-Drop UI/UX)](#calendar-view-drag-and-drop-uiux)
      - [Meeting Creation Interface](#meeting-creation-interface)
      - [Booking List View](#booking-list-view)
      - [Department Dashboard/Analytics](#department-dashboardanalytics)
    - [6. Notifications & Reminders](#6-notifications--reminders)
      - [Confirmation Emails](#confirmation-emails)
      - [Reminder Emails](#reminder-emails)
      - [Cancellation Notifications](#cancellation-notifications)
      - [Rescheduling Notifications](#rescheduling-notifications)
      - [Reassignment Notifications](#reassignment-notifications)
      - [Post-Meeting Follow-up](#post-meeting-follow-up)
  - [Technical Architecture](#technical-architecture)
    - [Technology Stack](#technology-stack)
  - [Data Model Design](#data-model-design)
    - [DocTypes to Create](#doctypes-to-create)
      - [1. MM Department](#1-mm-department)
      - [2. MM User Settings](#2-mm-user-settings)
      - [3. MM Availability Rule](#3-mm-user-availability-rule)
      - [4. MM Calendar Integration](#4-mm-calendar-integration)
      - [5. MM Department Meeting Type](#5-mm-department-meeting-type)
      - [6. MM Meeting Booking](#6-mm-meeting-booking)
      - [7. MM Calendar Event Sync](#7-mm-calendar-event-sync)
  - [High-Level Implementation Strategy](#high-level-implementation-strategy)
    - [Phase 1: Foundation Setup (Week 1)](#phase-1-foundation-setup-week-1)
    - [Phase 2: Availability Engine & Calendar Sync (Week 2)](#phase-2-availability-engine--calendar-sync-week-2)
    - [Phase 3: Public Booking Interface - 6-Step Department Flow (Week 3)](#phase-3-public-booking-interface---6-step-department-flow-week-3)
    - [Phase 4: Calendar Integrations (Week 4)](#phase-4-calendar-integrations-week-4)
    - [Phase 5: Internal Management Interface with Drag-and-Drop (Week 5)](#phase-5-internal-management-interface-with-drag-and-drop-week-5)
    - [Phase 6: Notifications & Automations (Week 6)](#phase-6-notifications--automations-week-6)
    - [Phase 7: Advanced Features (Week 7-8)](#phase-7-advanced-features-week-7-8)
    - [Phase 8: Testing & Optimization (Week 9)](#phase-8-testing--optimization-week-9)
    - [Phase 9: Documentation & Deployment (Week 10)](#phase-9-documentation--deployment-week-10)
  - [Technical Implementation Details](#technical-implementation-details)
    - [File Structure](#file-structure)
  - [API Specifications](#api-specifications)
    - [Public Booking APIs](#public-booking-apis)
      - [1. Get Departments](#1-get-departments)
      - [2. Get Department Meeting Types](#2-get-department-meeting-types)
      - [3. Get Available Dates](#3-get-available-dates)
      - [4. Get Available Time Slots](#4-get-available-time-slots)
      - [5. Create Customer Booking](#5-create-customer-booking)
    - [Internal APIs](#internal-apis)
      - [6. Reassign Booking](#6-reassign-booking)
      - [7. Create Internal Meeting](#7-create-internal-meeting)
      - [8. Create Customer Booking for Member](#8-create-customer-booking-for-member)
      - [9. Sync External Calendar](#9-sync-external-calendar)
  - [Database Indexes](#database-indexes)
  - [Security Considerations](#security-considerations)
  - [Monitoring & Analytics](#monitoring--analytics)
    - [Key Metrics to Track](#key-metrics-to-track)
    - [Logging Strategy](#logging-strategy)
  - [Maintenance & Support](#maintenance--support)
    - [Daily Tasks](#daily-tasks)
    - [Weekly Tasks](#weekly-tasks)
    - [Monthly Tasks](#monthly-tasks)
  - [Future Enhancements (Post-MVP)](#future-enhancements-post-mvp)
  - [Success Criteria](#success-criteria)
  - [Estimated Timeline](#estimated-timeline)
  - [Budget Estimate (If outsourcing)](#budget-estimate-if-outsourcing)

---

## Project Overview

A comprehensive department-based meeting booking system that enables:
1. **Customer Booking Flow**: Customers book meetings with departments (e.g., Support, Sales) through a public booking interface. The system automatically assigns bookings to available department members using round-robin or least-busy algorithms, respecting individual availability schedules.
2. **Internal Meeting Creation**: System Managers and Department Leaders can create internal meetings directly with specific employees/workers through the admin interface, respecting their availability schedules.
3. **Meeting Management**: Features include drag-and-drop meeting reassignment for admins and department leaders, automated email confirmations to all parties, and cancellation capabilities for customers, admins, and department leaders.

The system will be integrated into the bs-infra.dk Frappe site.

---

## Business Requirements

### Core Objectives
1. **Eliminate scheduling friction** - Remove email ping-pong for booking meetings
2. **Department-based public booking** - Customers book with departments, not individuals; system auto-assigns to available members using round-robin or least-busy algorithms
3. **Multi-user support** - Each employee belongs to one or more departments, can view their own calendar meetings and availability
4. **Multiple booking creation methods**:
   - **Customer self-service**: Customers book through public department booking pages (auto-assignment to available member)
   - **Admin/Department Leader for member**: Create bookings on behalf of department members with customers
   - **Department Member direct**: Department members create customer meetings directly for themselves
   - **Internal meetings**: Admins/Department Leaders create internal meetings between employees
5. **Public booking interface** - Clean, fast multi-step flow: Department → Meeting Type → Date → Time → Customer Details
6. **Calendar integration** - Sync with Google Calendar, Outlook, and iCal to respect existing commitments
7. **Automated notifications** - Email confirmations to all parties (customers, assigned hosts, admins, department leaders)
8. **Visual meeting management** - Drag-and-drop interface for admins and department leaders to reassign meetings between department members
9. **Flexible cancellation** - Customers, admins, and department leaders can cancel bookings with automatic notifications to all parties

---

## Functional Requirements

### 1. Department & Calendar Management

#### Department Profile
Each department should have comprehensive profile settings:
- **Department Information**: Name, description, Department Leader
- **Department Members**: List of employees belonging to this department (many-to-many relationship)
- **Time Zone**: Department time zone (all members work under department's time zone)
- **Public Booking Link**: Unique URL like `bs-infra.dk/book/support` or `bs-infra.dk/book/sales`
- **Assignment Algorithm**: Choose between Round-robin or Least-busy for auto-assigning customer bookings
- **Department Meeting Types**: Meeting types offered by this department (e.g., "30 min Call", "Technical Consultation")

#### Availability Rules
Users define when they're available for meetings:
- **Working hours** per day of the week
- **Buffer time** between meetings (e.g., 15 min before/after)
- **Maximum bookings** per day/week
- **Advance booking window** (e.g., allow bookings 1-60 days ahead)
- **Minimum notice** (e.g., require 2 hours notice before booking)
- **Break times** (lunch, recurring breaks)
- **Date-specific overrides** (vacations, special availability)

#### Calendar Integration
Bidirectional sync with external calendars:
- **Google Calendar** (OAuth 2.0)
- **Microsoft Outlook** (OAuth 2.0)
- **iCal** (URL-based subscription)
- **Conflict detection** - Check external calendars for existing events
- **Automatic blocking** - Block times when busy in external calendar
- **Event creation** - Add confirmed bookings to external calendar

---

### 2. Meeting Types

Each user can create multiple meeting types with different configurations:

#### Meeting Type Properties
- **Name**: e.g., "30-min Intro Call", "Technical Consultation"
- **Description**: What the meeting is about
- **Duration**: 15, 30, 45, 60, 90, 120 minutes (customizable)
- **Location Type**:
  - Video call (Zoom, Google Meet, Microsoft Teams)
  - Phone call
  - Physical address
  - Custom location
- **Color Code**: Visual identification
  - 🟢 Green - Confirmed/Sales meetings
  - 🟡 Yellow - Pending/Waiting
  - 🔴 Red - Cancelled
  - 🔵 Blue - Consultation
  - 🟣 Purple - Internal meetings
- **Price**: Optional - for paid consultations
- **Custom Questions**: Additional form fields for invitees
- **Confirmation**: Automatic or manual approval required

#### Booking Link Generation
Each meeting type generates a unique URL:
- Format: `bs-infra.dk/book/john-doe/intro-call`
- Shareable via email, website, social media
- Embeddable widget option

---

### 3. Scheduling Engine

The core logic that manages availability and prevents conflicts:

#### Availability Calculation
The system must:
1. **Read user's availability rules** (working hours, buffer times)
2. **Fetch existing bookings** from internal database
3. **Check external calendars** for conflicts (via API)
4. **Apply meeting type duration** to find available slots
5. **Handle time zone conversion** automatically
6. **Generate available time slots** for display

#### Conflict Prevention
- **Double-booking protection** - Verify availability before confirmation
- **Buffer time enforcement** - Maintain gaps between meetings
- **Maximum capacity** - Respect daily/weekly booking limits
- **Real-time updates** - Refresh availability as bookings are made

#### Time Zone Handling
- **Detect visitor's time zone** automatically
- **Display slots in visitor's local time**
- **Store events in UTC** for consistency
- **Show both time zones** in confirmations

---

### 4. Public Booking Interface

A clean, responsive multi-step booking flow for external visitors (customers):

#### Step 1: Select Department
URL: `bs-infra.dk/book`
- Display all available departments as cards (e.g., Support Department, Sales Department)
- Show department description and available meeting types count
- Clear call-to-action: "Book with [Department Name]"

#### Step 2: Select Meeting Type
URL: `bs-infra.dk/book/[department-slug]`
- Display available meeting types offered by selected department
- Show duration and description for each type (no pricing)
- Clear indication of what to expect (e.g., "30-min Call", "Technical Consultation")

#### Step 3: Choose Date
URL: `bs-infra.dk/book/[department-slug]/[meeting-type-slug]`
- **Calendar view** showing available dates (computed by aggregating all department members' availability)
- **Unavailable dates** grayed out
- **Next available slot** highlighted
- **Month navigation** with clear indicators
- Dates shown respect department members' availability schedules

#### Step 4: Choose Time
URL: `bs-infra.dk/book/[department-slug]/[meeting-type-slug]/[date]`
- **Time slots** displayed in visitor's time zone
- **Unavailable slots** disabled
- Time slots computed by checking availability of department members
- Show duration for each slot

#### Step 5: Enter Customer Details
Form fields:
- Name (required)
- Email (required)
- Phone (required)
- Additional questions (custom per meeting type, if any)
- Notes/comments (optional)

#### Step 6: Confirmation (Public Page)
- **Summary review** - Department, meeting type, date, time
- **Timezone confirmation** - Display visitor's timezone
- **Add to calendar** button (.ics download)
- **Cancellation & Reschedule links** included for customer self-service
- **Host identity hidden** - Customer does NOT see which department member is assigned on public page

#### Email Confirmations Sent
**To Customer**:
- Meeting details (department, meeting type, date, time)
- **Assigned host revealed**: "Your meeting will be with [Member Name] from [Department Name]"
- Timezone confirmation
- Calendar invite (.ics attachment)
- Cancellation link
- Reschedule link

**To Assigned Host (Department Member)**:
- New booking notification
- Customer details (name, email, phone)
- Meeting details
- Cancellation link
- Reschedule link

**To Department Leader** (if configured in department settings):
- Notification of new booking assigned to team member
- Summary of booking details

**To System Manager/Admin** (if notification enabled in settings):
- Notification of new customer booking
- Summary of booking details

#### Under the Hood (Auto-Assignment)
When customer completes booking:
1. System uses department's assignment algorithm (Round-robin or Least-busy)
2. Assigns booking to an available department member
3. Sends confirmation emails to all relevant parties (as configured)
4. Creates calendar event in assigned host's integrated calendar (if enabled)

---

### 5. Internal Management Interface

For System Managers and Department Leaders managing department bookings and calendars:

#### Calendar View (Drag-and-Drop UI/UX)
**Access**: System Managers and Department Leaders only

**Features**:
- **Month/Week/Day views** - Switch between different perspectives
- **Department filter** - View bookings for specific departments
- **Member filter** - View bookings for specific department members
- **Color-coded meetings** - Visual status identification (Confirmed, Pending, Cancelled, Completed)
- **Drag-and-drop reassignment**:
  - **Drag meeting between members**: Reassign to another department member within same department
  - **Validation**: System checks if new assignee is available at that time
  - **Automatic notifications**: Sends emails to:
    - Customer (informing of new host)
    - Old host (meeting reassigned away)
    - New host (meeting assigned to them)
    - Department Leader (if configured)
    - System Manager/Admin (if configured)
  - **Drag to reschedule**: Move meetings to different time slots for same host
  - **Visual feedback**: Real-time validation (green = valid, red = conflict)
- **Click to view details** - Popup with full meeting information
- **Quick actions** - Cancel, reschedule, reassign, mark as completed

#### Meeting Creation Interface
**For Admins and Department Leaders**:

1. **Create Internal Meeting**:
   - Select employee(s) to meet with
   - Choose meeting type (internal)
   - Select date and time (respecting availability)
   - Add agenda/notes
   - System validates availability before creation

2. **Create Customer Meeting for Member**:
   - Select department and member to assign meeting to
   - Enter customer details (name, email, phone)
   - Choose meeting type from department's offerings
   - Select date and time (respecting member's availability)
   - System sends confirmation to customer and assigned member

**For Department Members**:
- **Create direct customer meeting**: Members can create meetings with customers directly for themselves
- System validates against their own availability schedule

#### Booking List View
Tabular view with advanced filters:
- **Status filter** - Confirmed, Pending, Cancelled, Completed, No-show
- **Date range filter** - Today, This week, Next week, Custom range
- **Meeting type filter** - By meeting type
- **Department filter** - By department
- **Assignee filter** - By team member
- **Customer filter** - By customer name/email
- **Search** - By invitee name, email, or notes
- **Bulk actions** - Cancel multiple, export to CSV, etc.
- **Quick reassign** - Reassign button in each row

#### Department Dashboard/Analytics
- **Booking statistics** - Total bookings by department, by member, by status
- **Assignment distribution** - Verify round-robin/least-busy is working correctly
- **Peak booking times** - Heatmap view by department
- **No-show rate** - Track attendance by department/member
- **Popular meeting types** - Most booked meeting types per department
- **Member workload** - Compare booking distribution across department members

---

### 6. Notifications & Reminders

Automated communication throughout the booking lifecycle:

#### Confirmation Emails
Sent immediately after booking creation:

**Customer Booking (via public interface)**:
- **To Customer**: Meeting details, assigned host name (revealed in email), calendar invite (.ics), cancellation link, reschedule link
- **To Assigned Host**: New booking notification, customer details, meeting details, cancellation link, reschedule link
- **To Department Leader** (if enabled): Notification of new booking assigned to team member
- **To System Manager/Admin** (if enabled): Notification of new customer booking

**Internal Meeting Creation**:
- **To All Participants**: Meeting details, agenda/notes, calendar invite (.ics)
- **To Creator**: Confirmation of meeting creation

**Admin/Leader Creates Meeting for Member with Customer**:
- **To Customer**: Meeting details, assigned host name, calendar invite, cancellation link, reschedule link
- **To Assigned Member**: New booking assigned by admin/leader, customer details
- **To Admin/Leader**: Confirmation of meeting creation

#### Reminder Emails
Configurable reminder schedule (per meeting type):
- **24 hours before** - Standard reminder with meeting details
- **1 hour before** - Final reminder with join link (if video meeting)
- **Custom timing** - Configurable per meeting type (e.g., 2 days, 3 hours)
- **Recipients**: Both customer and assigned host receive reminders
- **SMS reminders** - Optional, configurable per meeting type

#### Cancellation Notifications
Sent when booking is cancelled:

**Cancelled by Customer**:
- **To Customer**: Cancellation confirmation
- **To Assigned Host**: Meeting cancelled by customer
- **To Department Leader** (if enabled): Notification of cancellation
- **To System Manager/Admin** (if enabled): Notification of cancellation

**Cancelled by Admin/Department Leader/Member**:
- **To Customer**: Meeting cancelled with reason (if provided)
- **To Assigned Host**: Confirmation of cancellation
- **To Other Participants** (for internal meetings): Cancellation notification

#### Rescheduling Notifications
Sent when booking is rescheduled:
- **To Customer**: Old time cancelled, new time confirmed, updated calendar invite
- **To Assigned Host**: Meeting rescheduled notification, updated calendar invite
- **To Department Leader** (if enabled): Notification of reschedule
- **To System Manager/Admin** (if enabled): Notification of reschedule

#### Reassignment Notifications
Sent when booking is reassigned via drag-and-drop:
- **To Customer**: "Your meeting host has been changed to [New Member Name]", updated meeting details
- **To Old Host**: "Meeting has been reassigned to [New Member Name]"
- **To New Host**: "Meeting has been assigned to you", customer details, meeting details
- **To Department Leader** (if enabled): Notification of reassignment
- **To System Manager/Admin** (if enabled): Notification of reassignment

#### Post-Meeting Follow-up
Sent after meeting end time:
- **Thank you email to customer** - Optional, configurable per meeting type
- **Feedback request** - Optional survey/rating link
- **Next steps** - Custom message per meeting type
- **Internal summary to admin** - Meeting completion statistics

---

## Technical Architecture

### Technology Stack
- **Backend**: Frappe Framework (Python)
- **Frontend**: Frappe UI (Vue.js 3)
- **Database**: MariaDB (Frappe default)
- **Calendar Integration**: Google Calendar API, Microsoft Graph API
- **Video Conferencing**: Zoom API, Google Meet API
- **Email**: Frappe's Email Queue + SMTP
- **SMS**: Twilio API (optional)

---

## Data Model Design

### DocTypes to Create

**Note**: All parent DocTypes use "MM" prefix (Meeting Manager) to prevent collision with existing Frappe/ERPNext DocTypes.

#### 1. MM Department
Central DocType for managing departments and their booking settings.

**Fields**:
- `department_name` (Data, Required) - e.g., "Support Department", "Sales Department"
- `department_slug` (Data, Unique) - URL-friendly identifier (e.g., "support", "sales")
- `description` (Text Editor) - Rich text description of department
- `department_leader` (Link to User) - Leader/Manager of this department (must be a member of the department)
- `is_active` (Check, Default: 1) - Enable/disable public booking for this department
- `timezone` (Select) - Department timezone (all operations in this timezone)
- `assignment_algorithm` (Select) - "Round Robin" or "Least Busy"
- `public_booking_url` (Read Only) - Auto-generated: `bs-infra.dk/book/{slug}`
- `notify_leader_on_booking` (Check) - Send email to leader on new bookings
- `notify_admin_on_booking` (Check) - Send email to admin on new bookings

**Child Table - Department Members**:
- `member` (Link to User) - Employee/User belonging to this department
- `is_active` (Check) - Active member (only active members receive assignments)
- `assignment_priority` (Int) - For future weighted assignment (optional)
- `last_assigned_datetime` (Datetime) - Track for round-robin (auto-updated)
- `total_assignments` (Int) - Count of assignments (auto-updated)

**Validation Rules**:
- Department leader must be an active member in the department members child table
- At least one active member required
- Department slug must be unique and URL-safe

#### 2. MM User Settings
Extends User doctype with calendar-specific settings.

**Fields**:
- `user` (Link to User, Required, Unique) - Foreign key
- `timezone` (Select) - User's timezone (can be overridden by department timezone)
- `profile_picture` (Attach Image)
- `bio` (Small Text)
- `working_hours_json` (JSON) - Serialized working hours config

**Example JSON**:
```json
{
  "monday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "tuesday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "wednesday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "thursday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "friday": {"enabled": true, "start": "09:00", "end": "17:00"},
  "saturday": {"enabled": false},
  "sunday": {"enabled": false}
}
```

---

#### 3. MM User Availability Rule
Define availability constraints and preferences for users.

**Fields**:
- `user` (Link to User, Required)
- `rule_name` (Data) - e.g., "Standard Availability"
- `is_default` (Check) - Default rule for this user
- `buffer_time_before` (Int) - Minutes before meeting
- `buffer_time_after` (Int) - Minutes after meeting
- `max_bookings_per_day` (Int)
- `max_bookings_per_week` (Int)
- `min_notice_hours` (Int) - Minimum hours before booking allowed
- `max_days_advance` (Int) - Maximum days in future for bookings

**Child Table - MM User Date Overrides**:
- `date` (Date)
- `available` (Check)
- `custom_hours_start` (Time)
- `custom_hours_end` (Time)
- `reason` (Small Text) - e.g., "Vacation", "Conference", "Out of Office"

---

#### 4. MM Calendar Integration
Store OAuth credentials and sync settings for external calendars.

**Fields**:
- `user` (Link to User, Required)
- `integration_type` (Select) - Google Calendar, Outlook Calendar, iCal
- `integration_name` (Data) - User-friendly name
- `is_active` (Check)
- `access_token` (Password) - OAuth access token (encrypted)
- `refresh_token` (Password) - OAuth refresh token (encrypted)
- `token_expiry` (Datetime)
- `calendar_id` (Data) - External calendar ID
- `ical_url` (Data) - For iCal subscriptions
- `sync_direction` (Select) - One-way (read), Two-way (read/write)
- `last_sync` (Datetime)
- `sync_status` (Select) - Success, Failed, Pending
- `sync_error_log` (Text) - Last error message if sync failed

---

#### 5. MM Department Meeting Type
Meeting types offered by a specific department.

**Fields**:
- `department` (Link to MM Department, Required) - Parent department
- `meeting_name` (Data, Required) - e.g., "30-min Call", "Technical Consultation", "Team Standup"
- `meeting_slug` (Data, Required) - URL-friendly identifier (e.g., "30-min-call", "tech-consultation")
- `description` (Text Editor) - Rich text description
- `duration` (Int, Required) - Minutes (15, 30, 45, 60, 90, 120)
- `location_type` (Select) - Video Call, Phone Call, Physical Location, Custom
- `video_platform` (Select) - Zoom, Google Meet, Microsoft Teams, Custom
- `custom_location` (Small Text) - Address or custom instructions
- `requires_approval` (Check) - Manual approval needed (for customer bookings)
- `is_public` (Check) - Available for public/customer booking
- `is_internal` (Check) - Available for internal meetings
- `is_active` (Check, Default: 1) - Enable/disable this meeting type
- `created_by` (Link to User) - Creator of this meeting type
- `booking_url` (Read Only) - Full URL: `bs-infra.dk/book/{department_slug}/{meeting_slug}`

**Child Table - Reminder Schedule**:
- `hours_before` (Int) - Hours before meeting to send reminder
- `notification_type` (Select) - Email, SMS, Both
- `is_active` (Check)

**Validation Rules**:
- Meeting slug must be unique within the department
- At least one of is_public or is_internal must be checked
- If is_public is checked, requires_approval can be enabled

---

#### 6. MM Meeting Booking
The core booking record for all meetings (customer and internal).

**Fields**:
- `booking_id` (Data, Primary, Read Only) - Auto-generated unique ID (e.g., "BOOK-2025-001")
- `booking_type` (Select, Read Only) - Customer Booking or Internal Meeting (derived from meeting_type.is_public/is_internal)
- `department` (Link to MM Department) - Department handling this booking (from meeting_type.department)
- `meeting_type` (Link to MM Department Meeting Type, Required) - Type of meeting
- `assigned_to` (Link to User, Required) - Current assigned host/member

**Customer Information** (for customer bookings):
- `customer_name` (Data, Required if booking_type=Customer Booking)
- `customer_email` (Data, Required if booking_type=Customer Booking)
- `customer_phone` (Data, Required if booking_type=Customer Booking)
- `customer_timezone` (Select) - Customer's timezone
- `customer_notes` (Text) - Customer's notes/comments

**Scheduling Information**:
- `scheduled_date` (Date, Required)
- `scheduled_start_time` (Time, Required)
- `scheduled_end_time` (Time, Required, Read Only) - Calculated from start_time + duration
- `duration` (Int, Read Only) - Minutes (copied from meeting type)
- `timezone` (Select, Read Only) - Department timezone

**Meeting Details**:
- `location_type` (Select, Read Only) - Copied from meeting type
- `video_platform` (Select) - Zoom, Google Meet, Teams, Custom
- `meeting_link` (Data) - Video call URL (auto-generated or manual)
- `physical_location` (Small Text) - Address if physical meeting
- `meeting_notes` (Text) - Internal notes about the meeting

**Status Tracking**:
- `status` (Select, Required, Default: Confirmed) - Pending (if requires approval), Confirmed, Cancelled, Completed, No-show
- `requires_approval` (Check, Read Only) - Copied from meeting type
- `approved_by` (Link to User) - Who approved (if requires_approval)
- `approved_datetime` (Datetime)

**Cancellation Details**:
- `cancellation_reason` (Select) - Customer Cancelled, Host Cancelled, No-show, Rescheduled, Other
- `cancellation_notes` (Small Text)
- `cancelled_by_role` (Select) - Customer, Host, Department Leader, System Manager
- `cancelled_datetime` (Datetime)

**Assignment Tracking** (for department bookings):
- `assignment_method` (Select, Read Only) - Round Robin, Least Busy, Manual Assignment
- `reassignment_count` (Int, Default: 0) - Number of times reassigned

**Security & Access**:
- `reschedule_token` (Data) - Unique token for customer reschedule link (e.g., random hash)
- `cancel_token` (Data) - Unique token for customer cancel link (e.g., random hash)
- `created_from_ip` (Data) - IP address for spam prevention

**Notification Tracking**:
- `confirmation_sent` (Check) - Confirmation email sent
- `confirmation_sent_datetime` (Datetime)
- `reminder_sent` (Check) - Reminder email sent
- `reminder_sent_datetime` (Datetime)
- `thank_you_sent` (Check) - Thank you email sent
- `thank_you_sent_datetime` (Datetime)

**Internal Meeting Fields** (for internal meetings):
- `meeting_agenda` (Text) - Agenda for internal meetings
- `meeting_minutes` (Text) - Minutes/notes after meeting
- `action_items` (Text) - Action items from meeting

**Child Table - Assignment History** (tracks all assignment changes):
- `assigned_to` (Link to User) - Member who was assigned
- `assigned_datetime` (Datetime) - When assignment was made
- `assigned_by` (Link to User) - Who made the assignment (null for auto-assignment)
- `assignment_type` (Select) - Auto (Round Robin), Auto (Least Busy), Manual (Drag-Drop), Manual (Direct)
- `is_current` (Check) - Is this the current assignment

**Child Table - Meeting Participants** (for internal meetings with multiple attendees):
- `participant` (Link to User) - User attending the meeting
- `attendance_status` (Select) - Invited, Confirmed, Declined, Attended, No-show
- `response_datetime` (Datetime)

**Child Table - Booking History**:
- `action` (Select) - Created, Confirmed, Rescheduled, Cancelled, Reassigned, Completed, Approved, Declined
- `action_by` (Link to User) - Who performed the action (null for customer/system actions)
- `action_by_role` (Select) - Customer, Host, Department Leader, System Manager, System
- `action_datetime` (Datetime)
- `old_value` (Data) - Previous value (for changes)
- `new_value` (Data) - New value (for changes)
- `notes` (Small Text) - Additional notes about the action

**Validation Rules**:
- scheduled_end_time must be after scheduled_start_time
- If booking_type = Customer Booking, customer fields are required
- assigned_to must be an active member of the department (for customer bookings)
- Cannot create booking in the past
- Cannot create booking outside assigned_to user's availability

---

#### 7. MM Calendar Event Sync
Track synced events from external calendars for availability computation.

**Fields**:
- `user` (Link to User, Required)
- `integration` (Link to MM Calendar Integration, Required)
- `external_event_id` (Data, Unique) - ID in external calendar
- `event_summary` (Data)
- `event_start` (Datetime, Required)
- `event_end` (Datetime, Required)
- `event_status` (Select) - Busy, Free, Tentative
- `is_all_day` (Check) - All-day event flag
- `last_synced` (Datetime)
- `sync_hash` (Data) - For change detection (MD5 hash of event data)

---

## High-Level Implementation Strategy

### Phase 1: Foundation Setup (Week 1)
**Goal**: Set up core data structure and basic CRUD operations for department-based booking system

#### Tasks:
1. **Confirm app name**: `meeting_manager` (already created and installed)
   ```bash
   # Already done:
   # bench new-app meeting_manager
   # bench --site bestsecurity.local install-app meeting_manager
   ```

2. **Create DocTypes with MM prefix**:
   - **MM Department** - Central department management with members and assignment algorithm
   - **MM User Settings** - User calendar settings and working hours
   - **MM User Availability Rule** - User availability constraints and date overrides
   - **MM Department Meeting Type** - Meeting types per department with reminder schedules
   - **MM Meeting Booking** - Core booking record with assignment history
   - **MM Calendar Integration** - OAuth credentials for external calendars
   - **MM Calendar Event Sync** - Synced events from external calendars

3. **Set up permissions**:
   - **System Manager**: Full access to all DocTypes
   - **Department Leader**:
     - Read/Write access to their department(s)
     - Read/Write access to bookings for their department members
     - Can reassign bookings within their department
   - **Department Member**:
     - Read access to their own user settings and availability
     - Read/Write access to bookings assigned to them
     - Can create customer bookings for themselves
   - **Guest**:
     - Create access only for MM Meeting Booking (public booking creation)
     - Read access to MM Department (public booking page)
     - Read access to MM Department Meeting Type (public meeting types)

4. **Create basic forms** for each DocType with validation rules:
   - MM Department: Validate leader is active member, slug is unique
   - MM Department Meeting Type: Validate slug unique within department
   - MM Meeting Booking: Validate availability, prevent double-booking
   - Implement auto-calculation fields (end_time, booking_type, etc.)

5. **Create initial test data**:
   - Create 2-3 test departments (Support, Sales)
   - Add test users as department members
   - Create sample meeting types for each department

---

### Phase 2: Availability Engine & Calendar Sync (Week 2)
**Goal**: Build calendar sync system and department-based availability calculation

#### Tasks:
1. **External Calendar Sync Service** (`services/calendar_sync.py`):
   - **Scheduled Job** (runs every 5-10 minutes via Frappe scheduler):
     - `sync_all_users_calendars()`
       - Get all users with active MM Calendar Integration
       - For each user, call `sync_user_calendar(user)`
       - Log sync status and errors

   - Function: `sync_user_calendar(user)`
     - Get all active integrations for user (Google, Outlook, iCal)
     - For each integration:
       - Fetch events from external calendar (next 60 days)
       - For each event:
         - Check if event exists in MM Calendar Event Sync (by external_event_id)
         - Calculate sync_hash (MD5 of event data)
         - If new or sync_hash changed: Create/Update MM Calendar Event Sync record
         - Mark event as last_synced
       - Delete MM Calendar Event Sync records for events no longer in external calendar
     - Update integration.last_sync and integration.sync_status

2. **Department Availability Calculator Service** (`api/availability.py`):
   - Function: `get_department_available_dates(department_slug, meeting_type_slug, month, year)`
     - Load all active members of department
     - For each member:
       - Load working hours from MM User Settings
       - Load availability rules from MM User Availability Rule
       - Fetch existing MM Meeting Booking records
       - Fetch busy times from MM Calendar Event Sync (local data, NO external API calls)
       - Calculate available dates considering all constraints
     - Aggregate availability across all members (date available if ANY member free)
     - Return available dates for the month

   - Function: `get_department_available_slots(department_slug, meeting_type_slug, date, visitor_timezone)`
     - Load all active members of department
     - For each member:
       - Calculate available time slots for the date
       - Check against: working hours, existing bookings, synced calendar events, buffer times
     - Aggregate slots (show slot if ANY member is available)
     - Return slots in visitor's timezone with availability count per slot

3. **Assignment Algorithm Service** (`api/assignment.py`):
   - Function: `assign_to_member(department, meeting_type, datetime)`
     - **Round Robin**:
       - Get active members ordered by `last_assigned_datetime` (oldest first)
       - Find first member with availability at requested time
       - Validate against: working hours, existing bookings, synced calendar events
       - Assign to that member
       - Update `last_assigned_datetime` and `total_assignments` in Department Members child table

     - **Least Busy**:
       - Get all active members
       - Count existing bookings for each member (next 7 days)
       - Find member with fewest bookings who is available at requested time
       - Assign to that member
       - Update `total_assignments`

     - Return assigned member

4. **Conflict Detection** (`utils/validation.py`):
   - Function: `check_member_availability(member, datetime, duration)`
     - Check MM Meeting Booking for overlaps
     - Check MM Calendar Event Sync for busy times (local data)
     - Check availability rules and working hours
     - Apply buffer times
     - Return True/False with conflict details

5. **Time Zone Utilities** (`utils/timezone.py`):
   - Convert between department timezone and visitor timezone
   - Handle DST transitions
   - Validate timezone inputs
   - Store all times in UTC, display in appropriate timezone

6. **Public API Endpoints** (`api/public.py`):
   ```python
   @frappe.whitelist(allow_guest=True)
   def get_departments()
   # Returns all active departments for public booking

   @frappe.whitelist(allow_guest=True)
   def get_department_meeting_types(department_slug)
   # Returns all active public meeting types for department

   @frappe.whitelist(allow_guest=True)
   def get_available_dates(department_slug, meeting_type_slug, month, year)
   # Returns available dates (uses local MM Calendar Event Sync data)

   @frappe.whitelist(allow_guest=True)
   def get_available_slots(department_slug, meeting_type_slug, date, visitor_timezone)
   # Returns available time slots (uses local data, NO external API calls)

   @frappe.whitelist(allow_guest=True, methods=["POST"])
   def create_customer_booking(booking_data)
   # Creates booking with auto-assignment
   # Rate limiting: 10 requests per hour per IP
   ```

7. **Internal API Endpoints** (`api/booking.py`):
   ```python
   @frappe.whitelist()
   def reassign_booking(booking_id, new_assigned_to)
   # Reassign booking (drag-drop), validates availability

   @frappe.whitelist()
   def create_internal_meeting(meeting_data)
   # Create internal meeting

   @frappe.whitelist()
   def create_customer_booking_for_member(booking_data, assigned_to)
   # Admin/Leader creates customer booking for specific member
   ```

8. **Scheduler Configuration** (`hooks.py`):
   ```python
   scheduler_events = {
       "cron": {
           "*/10 * * * *": [  # Every 10 minutes
               "meeting_manager.services.calendar_sync.sync_all_users_calendars"
           ]
       }
   }
   ```

---

### Phase 3: Public Booking Interface - 6-Step Department Flow (Week 3)
**Goal**: Build the Vue.js public booking page with department-based 6-step flow

#### Tasks:
1. **Create Vue.js app** in `meeting_manager/public/js/booking/`
   - Use Frappe's frontend build system or Vite
   - Component structure:
     ```
     booking/
     ├── App.vue (Main container with step management)
     ├── components/
     │   ├── Step1_DepartmentSelector.vue
     │   ├── Step2_MeetingTypeSelector.vue
     │   ├── Step3_DatePicker.vue
     │   ├── Step4_TimeSlotPicker.vue
     │   ├── Step5_CustomerDetailsForm.vue
     │   └── Step6_ConfirmationPage.vue
     ├── services/
     │   └── api.js (API calls to public endpoints)
     └── utils/
         ├── timezone.js (timezone detection & conversion)
         └── validation.js (client-side form validation)
     ```

2. **Routing setup**:
   - URL patterns:
     - `/book` → Step 1: Department selection
     - `/book/{department_slug}` → Step 2: Meeting type selection
     - `/book/{department_slug}/{meeting_type_slug}` → Step 3: Date selection
     - `/book/{department_slug}/{meeting_type_slug}/{date}` → Step 4: Time selection
     - `/book/{department_slug}/{meeting_type_slug}/{date}/{time}` → Step 5: Customer details
     - `/book/confirm/{booking_id}` → Step 6: Confirmation
   - Handle 404 for invalid slugs
   - Mobile-responsive design (Tailwind CSS or Frappe UI components)

3. **Step 1: Department Selector Component**:
   - API call: `get_departments()`
   - Display departments as cards with:
     - Department name
     - Description
     - Available meeting types count
   - Click handler navigates to Step 2

4. **Step 2: Meeting Type Selector Component**:
   - API call: `get_department_meeting_types(department_slug)`
   - Display meeting types as cards with:
     - Meeting name
     - Duration
     - Description
   - Click handler navigates to Step 3

5. **Step 3: Date Picker Component**:
   - API call: `get_available_dates(department_slug, meeting_type_slug, month, year)`
   - Month view calendar with navigation
   - Highlight available dates
   - Gray out unavailable dates
   - Show "Next Available" indicator
   - Loading states during API calls
   - Click handler navigates to Step 4

6. **Step 4: Time Slot Picker Component**:
   - API call: `get_available_slots(department_slug, meeting_type_slug, date, visitor_timezone)`
   - Auto-detect visitor's timezone
   - Display time slots in visitor's local time
   - Show duration for each slot
   - Disable unavailable slots
   - Grid or list view of slots
   - Click handler navigates to Step 5

7. **Step 5: Customer Details Form Component**:
   - Form fields:
     - Name (required, text)
     - Email (required, email validation)
     - Phone (required, phone validation)
     - Notes (optional, textarea)
   - Client-side validation
   - Display summary of selections (department, meeting type, date, time, timezone)
   - Submit button with loading state
   - API call: `create_customer_booking(booking_data)`
   - On success, navigate to Step 6

8. **Step 6: Confirmation Page Component**:
   - Display booking details (department, meeting type, date, time)
   - Show visitor's timezone
   - **DO NOT show assigned host name** (only in email)
   - Success message
   - "Add to Calendar" button (.ics file download)
   - Cancellation link with cancel_token
   - Reschedule link with reschedule_token
   - Message: "Check your email for meeting details and assigned host"

9. **Progressive Enhancement**:
   - Back button support (navigate to previous step)
   - Browser back/forward handling
   - Save progress in session storage
   - Loading states for all API calls
   - Error handling with user-friendly messages

10. **Mobile Responsiveness**:
    - Touch-friendly UI elements
    - Responsive layout (mobile-first)
    - Swipe gestures for calendar navigation (optional)

---

### Phase 4: Calendar Integrations (Week 4)
**Goal**: Integrate with Google Calendar, Outlook, and iCal for two-way sync

#### Tasks:
1. **Google Calendar Integration** (`services/google_calendar.py`):
   - Set up OAuth 2.0 in Google Cloud Console (credentials, redirect URIs)
   - Create authorization flow (OAuth consent screen)
   - Implement token refresh mechanism (auto-refresh before expiry)
   - API methods:
     - `authorize_google_calendar(user)` - Start OAuth flow
     - `handle_google_oauth_callback(code, state)` - Complete OAuth, store tokens in MM Calendar Integration
     - `sync_google_calendar_events(integration)` - Fetch events from Google Calendar, update MM Calendar Event Sync
     - `create_google_calendar_event(booking)` - Push booking to user's Google Calendar
     - `update_google_calendar_event(booking)` - Update event in Google Calendar
     - `delete_google_calendar_event(booking)` - Delete event from Google Calendar
     - `refresh_google_token(integration)` - Refresh expired access token

2. **Microsoft Outlook Integration** (`services/outlook_calendar.py`):
   - Register app in Azure AD (App Registration)
   - Implement OAuth 2.0 flow (Microsoft Graph API)
   - Similar CRUD methods as Google:
     - `authorize_outlook_calendar(user)`
     - `handle_outlook_oauth_callback(code, state)`
     - `sync_outlook_calendar_events(integration)`
     - `create_outlook_calendar_event(booking)`
     - `update_outlook_calendar_event(booking)`
     - `delete_outlook_calendar_event(booking)`
     - `refresh_outlook_token(integration)`

3. **iCal Support** (`services/ical_sync.py`):
   - Parse iCal feed URLs (.ics format)
   - Periodic sync via scheduled job
   - Read-only support (fetch events, no write-back)
   - Methods:
     - `parse_ical_feed(ical_url)` - Download and parse iCal feed
     - `sync_ical_events(integration)` - Update MM Calendar Event Sync from iCal

4. **Sync Scheduler Integration**:
   - Already implemented in Phase 2 (`sync_all_users_calendars()`)
   - Runs every 10 minutes
   - Calls appropriate sync method based on integration_type (Google, Outlook, iCal)
   - Handles errors gracefully (log and continue to next user)
   - Updates `last_sync`, `sync_status`, `sync_error_log` in MM Calendar Integration

5. **Calendar Settings Page** (Frappe DocType form customization):
   - **MM Calendar Integration Form**:
     - "Connect Google Calendar" button → triggers OAuth flow
     - "Connect Outlook Calendar" button → triggers OAuth flow
     - "Add iCal URL" field → manual iCal URL entry
     - Display current sync status (Success, Failed, Pending)
     - Show last_sync datetime
     - Show sync_error_log if failed
     - "Disconnect" button → deactivate integration
     - "Force Sync Now" button → manual sync trigger

6. **Two-Way Sync Logic** (`services/calendar_sync.py`):
   - **Read from external** (already in Phase 2): Fetch external events → MM Calendar Event Sync
   - **Write to external** (new): When MM Meeting Booking is created/updated/cancelled:
     - If assigned_to has active calendar integration with sync_direction = "Two-way"
     - Call create/update/delete methods for Google/Outlook
     - Store external_event_id in MM Meeting Booking for future updates
     - Handle errors gracefully (notify user if calendar write fails)

---

### Phase 5: Internal Management Interface with Drag-and-Drop (Week 5)
**Goal**: Build calendar views for System Managers and Department Leaders with drag-and-drop reassignment

#### Tasks:
1. **Calendar View Component** (`meeting_manager/public/js/calendar_view/`):
   - Use FullCalendar library (https://fullcalendar.io/)
   - **Month/Week/Day view switcher**
   - **Department filter dropdown** - View bookings for specific department
   - **Member filter dropdown** - View bookings for specific member
   - **Color-coded events** by status:
     - Confirmed: Green
     - Pending: Yellow
     - Cancelled: Red
     - Completed: Blue
     - No-show: Gray

   - **Drag-and-drop reschedule functionality**:
     - `handleEventDrop(event, newDateTime)`
     - Validate new time slot (check availability)
     - API call: `reschedule_booking(booking_id, new_datetime)`
     - Send notifications to customer and host
     - Update calendar view

   - **Drag-and-drop reassignment functionality**:
     - **Resource view**: Display columns for each department member
     - Drag event from one member column to another
     - `handleEventReassign(event, oldMember, newMember)`
     - **Real-time validation**: Check if newMember is available
     - **Visual feedback**: Green checkmark if valid, red X if conflict
     - API call: `reassign_booking(booking_id, new_assigned_to)`
     - Update Assignment History child table
     - Send notifications to: Customer, Old Host, New Host, Department Leader (if enabled), Admin (if enabled)
     - Update calendar view

   - **Click to view details** - Modal popup with full booking information
   - **Quick actions menu**:
     - Reschedule
     - Reassign (shows member dropdown)
     - Cancel
     - Mark as Completed
     - Mark as No-show

2. **Booking List View** (Customize Frappe List view):
   - **Advanced filters**:
     - Department (multi-select)
     - Assigned to (multi-select)
     - Status (multi-select)
     - Date range (preset: Today, This Week, Next Week, Custom)
     - Meeting Type (multi-select)
     - Customer name/email (search)
   - **Quick actions in each row**:
     - View details
     - Reassign (quick reassign button)
     - Cancel
     - Reschedule
   - **Bulk actions**:
     - Bulk cancel
     - Bulk export to CSV
   - **Permission-based visibility**:
     - System Manager: See all bookings
     - Department Leader: See only their department's bookings
     - Department Member: See only their own bookings

3. **Booking Detail Page** (MM Meeting Booking DocType Form):
   - **Booking Information section**:
     - Booking ID, Type, Status
     - Department, Meeting Type
     - Scheduled date/time, duration, timezone
   - **Customer Information section** (if customer booking):
     - Name, Email, Phone, Timezone, Notes
   - **Assignment Information section**:
     - Current assigned to
     - Assignment method (Round Robin, Least Busy, Manual)
     - Reassignment count
     - **Assignment History child table** (expandable)
   - **Meeting Details section**:
     - Location type, Video platform, Meeting link
     - Physical location, Internal notes
   - **Status Timeline** (Booking History child table):
     - Show all actions chronologically
     - Who did what, when
   - **Quick action buttons**:
     - Reassign (opens reassign dialog)
     - Reschedule (opens date/time picker)
     - Cancel (with reason field)
     - Mark as Completed
     - Mark as No-show

4. **Meeting Creation Forms**:
   - **Create Customer Booking for Member** (Admin/Leader):
     - Department selection
     - Member selection (dropdown filtered by department)
     - Meeting type selection (filtered by department)
     - Customer details (name, email, phone)
     - Date/time picker (validate against member availability)
     - Submit → Creates booking, sends confirmation emails

   - **Create Internal Meeting** (Admin/Leader):
     - Select participants (multi-select users)
     - Meeting type (internal only)
     - Date/time picker (find common availability)
     - Agenda/notes
     - Submit → Creates booking, sends invites to all participants

5. **Department Dashboard** (`meeting_manager/public/js/dashboard/`):
   - **KPI Cards**:
     - Total bookings (this month)
     - Today's meetings
     - Upcoming meetings (next 7 days)
     - No-show rate (%)
   - **Charts**:
     - Bookings over time (line chart, last 30 days)
     - Bookings by meeting type (pie chart)
     - Bookings by status (bar chart)
     - Bookings by department member (bar chart)
   - **Heatmap**:
     - Popular booking times (day of week x hour of day)
   - **Assignment Distribution Table**:
     - Verify round-robin/least-busy is balanced
     - Show each member's total assignments, last assigned datetime
   - **Filter by department** (dropdown)

---

### Phase 6: Notifications & Automations (Week 6)
**Goal**: Implement all automated communications for department-based booking system

#### Tasks:
1. **Email Templates** (`meeting_manager/templates/emails/`):
   Create Jinja2 email templates:

   **Customer Booking Confirmation** (`customer_booking_confirmation.html`):
   - To: Customer
   - Subject: "Meeting Confirmed with [Department Name]"
   - Body: Department, Meeting Type, Date, Time, **Assigned Host Name**, Calendar invite, Cancel link, Reschedule link

   **Host Assignment Notification** (`host_assignment_notification.html`):
   - To: Assigned Host
   - Subject: "New Meeting Assigned to You"
   - Body: Customer details, Meeting details, Calendar invite, Cancel link, Reschedule link

   **Department Leader Notification** (`department_leader_notification.html`):
   - To: Department Leader (if enabled)
   - Subject: "New Booking for [Department Name]"
   - Body: Summary of booking, assigned member, customer name

   **Reassignment Notifications**:
   - `customer_reassignment.html` - To: Customer ("Your meeting host has changed")
   - `host_old_reassignment.html` - To: Old Host ("Meeting reassigned away")
   - `host_new_reassignment.html` - To: New Host ("Meeting assigned to you")

   **Reminder Email** (`booking_reminder.html`):
   - To: Customer + Assigned Host
   - Subject: "Reminder: Meeting in [X hours]"
   - Body: Meeting details, join link (if video)

   **Cancellation Email** (`booking_cancellation.html`):
   - Multiple variants for different cancellation sources
   - Subject: "Meeting Cancelled"
   - Body: Cancellation reason, rescheduling options

   **Reschedule Confirmation** (`booking_rescheduled.html`):
   - To: Customer + Assigned Host
   - Subject: "Meeting Rescheduled"
   - Body: Old time, new time, updated calendar invite

   **Thank You / Follow-up** (`booking_thankyou.html`):
   - To: Customer (optional)
   - Subject: "Thank you for your meeting"
   - Body: Feedback request, next steps

2. **Calendar Invite Generation** (`utils/ical_generator.py`):
   - Function: `generate_ics_file(booking)`
     - Create .ics file programmatically (use icalendar library)
     - Include: Summary, Description, Start/End datetime, Location, Organizer, Attendees
     - Add meeting link for video meetings
     - Add VALARM for reminders
     - Return .ics file path for attachment

3. **Notification Service** (`services/notifications.py`):
   - Function: `send_booking_confirmation(booking)`
     - Determine recipients based on booking_type and department settings
     - Generate .ics file
     - Send emails to: Customer, Assigned Host, Department Leader (if enabled), Admin (if enabled)
     - Log email sent status in notification tracking fields

   - Function: `send_reassignment_notifications(booking, old_assigned_to, new_assigned_to)`
     - Send emails to: Customer, Old Host, New Host, Department Leader, Admin
     - Update Assignment History child table

   - Function: `send_cancellation_notifications(booking, cancelled_by_role)`
     - Send emails to all relevant parties
     - Update booking status and cancellation fields

   - Function: `send_reschedule_notifications(booking, old_datetime, new_datetime)`
     - Send emails with updated calendar invites

4. **Reminder Scheduler** (`services/reminder_scheduler.py`):
   - **Scheduled Job** (runs every hour via Frappe scheduler):
     - `send_pending_reminders()`
       - Query MM Meeting Booking where:
         - status = "Confirmed"
         - scheduled_date/time is in the future
         - reminder_sent = False
         - Calculate hours until meeting
       - For each booking, check MM Department Meeting Type → Reminder Schedule child table
       - If hours_before matches, send reminder email
       - Mark reminder_sent = True, update reminder_sent_datetime

5. **Event Hooks** (`hooks.py`):
   ```python
   doc_events = {
       "MM Meeting Booking": {
           "after_insert": "meeting_manager.services.notifications.send_booking_confirmation",
           "on_update": "meeting_manager.services.notifications.handle_booking_update",
           "on_trash": "meeting_manager.services.notifications.send_cancellation_notifications",
       }
   }
   ```

   - Function: `handle_booking_update(doc, method)`
     - Detect what changed (status, assigned_to, scheduled_datetime)
     - If assigned_to changed: send reassignment notifications
     - If scheduled_datetime changed: send reschedule notifications
     - If status changed to "Cancelled": send cancellation notifications

6. **SMS Integration** (Optional - `services/sms_service.py`):
   - Integrate Twilio API
   - Function: `send_sms_reminder(booking, message)`
   - Configuration in MM Department Meeting Type → Reminder Schedule (notification_type: SMS)
   - Require: Twilio Account SID, Auth Token, Phone Number in site config

7. **Video Meeting Link Generation** (`services/video_meeting.py`):
   - **Zoom Integration**:
     - Function: `create_zoom_meeting(booking)`
     - Use Zoom API to create meeting
     - Return meeting join URL
     - Store in booking.meeting_link

   - **Google Meet Integration**:
     - Function: `create_google_meet_link(booking)`
     - Use Google Calendar API to create event with conferenceData
     - Return Google Meet link

   - **Microsoft Teams Integration**:
     - Function: `create_teams_meeting(booking)`
     - Use Microsoft Graph API to create online meeting
     - Return Teams join URL

   - **Auto-generation**: When booking is created, if video_platform is set, auto-generate link

---

### Phase 7: Advanced Features (Week 7-8)
**Goal**: Implement additional functionality

#### Tasks:
1. **Department-Based Booking Enhancements**:
   - ✅ Round-robin assignment (already in Phase 2)
   - ✅ Load balancing across team members (Least Busy algorithm in Phase 2)
   - ✅ Collective availability calculation (already in Phase 2)
   - **New**: Weighted assignment (use assignment_priority field in Department Members)
   - **New**: Department capacity limits (max bookings per day for entire department)

2. **Recurring Meetings**:
   - Weekly, bi-weekly, monthly patterns
   - Series management
   - Cancel single occurrence vs entire series

3. **Booking Approval Workflow**:
   - Manual approval mode for certain meeting types
   - Pending → Approved/Rejected flow
   - Email notifications for approval requests

4. **Payment Integration** (If needed):
   - Stripe integration for paid consultations
   - Payment before booking confirmation
   - Refund handling for cancellations

5. **Embeddable Widget**:
   - JavaScript widget for external websites
   - Iframe-based booking form
   - Customizable styling

6. **Buffer Time Logic**:
   - Automatic buffer before/after meetings
   - Different buffers per meeting type
   - Override for specific bookings

7. **No-show Tracking**:
   - Mark bookings as no-show
   - Analytics on no-show rates
   - Optional automatic cancellation

---

### Phase 8: Testing & Optimization (Week 9)
**Goal**: Ensure reliability and performance

#### Tasks:
1. **Unit Tests**:
   - Test availability calculation logic
   - Test conflict detection
   - Test timezone conversions
   - Test edge cases (midnight, DST, etc.)

2. **Integration Tests**:
   - Test full booking flow
   - Test calendar sync
   - Test notification sending
   - Test drag-and-drop operations

3. **Performance Optimization**:
   - Cache availability calculations
   - Optimize database queries
   - Implement pagination for large booking lists
   - CDN for static assets

4. **Security Audit**:
   - Rate limiting on public endpoints
   - CSRF protection
   - SQL injection prevention
   - XSS protection in custom fields

5. **User Acceptance Testing**:
   - Test with real users
   - Gather feedback
   - Iterate on UX issues

---

### Phase 9: Documentation & Deployment (Week 10)
**Goal**: Prepare for production launch

#### Tasks:
1. **User Documentation**:
   - Setup guide for new users
   - How to connect external calendars
   - How to create meeting types
   - How to share booking links
   - FAQ section

2. **Admin Documentation**:
   - Installation guide
   - Configuration reference
   - Troubleshooting guide
   - API documentation

3. **Deployment Checklist**:
   - Backup database before deployment
   - Run database migrations
   - Build and deploy frontend assets
   - Configure email settings
   - Set up scheduled jobs
   - Test all integrations in production
   - Monitor error logs

4. **Training Materials**:
   - Video tutorials
   - Screenshot guides
   - Best practices document

---

## Technical Implementation Details

### File Structure
```
apps/calendar_booking/
├── calendar_booking/
│   ├── calendar_booking/
│   │   ├── doctype/
│   │   │   ├── calendar_user_settings/
│   │   │   ├── availability_rule/
│   │   │   ├── meeting_type/
│   │   │   ├── meeting_booking/
│   │   │   ├── calendar_integration/
│   │   │   └── calendar_event_sync/
│   │   ├── api/
│   │   │   ├── booking.py (Public booking APIs)
│   │   │   ├── availability.py (Availability logic)
│   │   │   ├── integrations.py (Calendar sync)
│   │   │   └── notifications.py (Email/SMS)
│   │   ├── public/
│   │   │   ├── js/
│   │   │   │   └── booking/ (Vue.js app)
│   │   │   └── css/
│   │   │       └── booking.css
│   │   ├── services/
│   │   │   ├── google_calendar.py
│   │   │   ├── outlook_calendar.py
│   │   │   ├── zoom_api.py
│   │   │   └── ical_parser.py
│   │   ├── utils/
│   │   │   ├── timezone.py
│   │   │   ├── validation.py
│   │   │   └── calendar_helpers.py
│   │   ├── templates/
│   │   │   └── emails/ (Email templates)
│   │   └── www/
│   │       └── book/ (Public booking pages)
│   ├── hooks.py
│   └── patches.txt
```

---

## API Specifications

### Public Booking APIs

#### 1. Get Meeting Types
```python
@frappe.whitelist(allow_guest=True)
def get_meeting_types(user_slug):
    """
    Returns active meeting types for a user
    """
    return {
        "meeting_types": [
            {
                "slug": "intro-call",
                "name": "30-min Intro Call",
                "description": "Quick introduction meeting",
                "duration": 30,
                "color": "green",
                "price": 0
            }
        ]
    }
```

#### 2. Get Available Dates
```python
@frappe.whitelist(allow_guest=True)
def get_available_dates(user_slug, meeting_type_slug, year, month):
    """
    Returns dates with availability for a given month
    """
    return {
        "available_dates": ["2025-11-15", "2025-11-16", "2025-11-18"],
        "timezone": "Europe/Copenhagen"
    }
```

#### 3. Get Available Time Slots
```python
@frappe.whitelist(allow_guest=True)
def get_available_slots(user_slug, meeting_type_slug, date, timezone):
    """
    Returns available time slots for a specific date
    """
    return {
        "slots": [
            {
                "start_time": "09:00",
                "end_time": "09:30",
                "start_utc": "2025-11-15T08:00:00Z",
                "end_utc": "2025-11-15T08:30:00Z"
            }
        ],
        "date": "2025-11-15",
        "user_timezone": "Europe/Copenhagen",
        "visitor_timezone": "America/New_York"
    }
```

#### 4. Create Booking
```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_booking(booking_data):
    """
    Creates a new meeting booking
    Rate limit: 10 requests per hour per IP
    """
    # Validate data
    # Check availability again
    # Create booking record
    # Send confirmations
    return {
        "success": True,
        "booking_id": "BOOK-2025-001",
        "reschedule_url": "https://bs-infra.dk/reschedule/abc123",
        "cancel_url": "https://bs-infra.dk/cancel/xyz789"
    }
```

### Internal APIs

#### 5. Update Booking
```python
@frappe.whitelist()
def update_booking(booking_id, new_datetime=None, new_assignee=None):
    """
    Updates booking time or assignee (drag-drop)
    """
    # Validate new slot availability
    # Update booking
    # Send notifications
    return {"success": True}
```

#### 6. Sync External Calendar
```python
@frappe.whitelist()
def sync_external_calendar(integration_id):
    """
    Manually trigger calendar sync
    """
    # Fetch events from external calendar
    # Update Calendar Event Sync records
    # Refresh availability
    return {"success": True, "events_synced": 15}
```

---

## Database Indexes

For optimal performance, create indexes on:

```sql
-- Meeting Booking
CREATE INDEX idx_booking_datetime ON `tabMeeting Booking` (scheduled_date, scheduled_start_time);
CREATE INDEX idx_booking_user ON `tabMeeting Booking` (assigned_to, scheduled_date);
CREATE INDEX idx_booking_status ON `tabMeeting Booking` (status);

-- Calendar Event Sync
CREATE INDEX idx_sync_user_datetime ON `tabCalendar Event Sync` (user, event_start, event_end);
CREATE INDEX idx_sync_external_id ON `tabCalendar Event Sync` (external_event_id);

-- Calendar User Settings
CREATE UNIQUE INDEX idx_user_slug ON `tabCalendar User Settings` (public_slug);
```

---

## Security Considerations

1. **Rate Limiting**:
   - 10 booking attempts per hour per IP
   - Prevent brute force on reschedule/cancel tokens

2. **Token Security**:
   - Generate cryptographically secure tokens for reschedule/cancel links
   - Expire tokens after 30 days or when used

3. **Data Validation**:
   - Sanitize all user inputs
   - Validate email formats
   - Prevent XSS in custom questions/answers

4. **OAuth Security**:
   - Store tokens encrypted in database
   - Implement token refresh before expiry
   - Revoke tokens on integration disconnect

5. **CORS Configuration**:
   - Allow embedding from specific domains
   - Restrict public API access patterns

---

## Monitoring & Analytics

### Key Metrics to Track
1. **Booking Metrics**:
   - Total bookings created
   - Conversion rate (views → bookings)
   - Cancellation rate
   - No-show rate

2. **Performance Metrics**:
   - API response times
   - Calendar sync duration
   - Email delivery success rate
   - Error rates

3. **Usage Metrics**:
   - Most popular meeting types
   - Peak booking hours/days
   - Average booking lead time
   - User engagement

### Logging Strategy
- Log all booking creation/updates
- Log external API calls (success/failure)
- Log email/SMS delivery
- Log errors with context for debugging

---

## Maintenance & Support

### Daily Tasks
- Monitor scheduled jobs (reminders, sync)
- Check email queue for failed messages
- Review error logs

### Weekly Tasks
- Review analytics dashboard
- Check calendar sync health
- Monitor storage usage

### Monthly Tasks
- Analyze booking trends
- Review user feedback
- Plan feature improvements
- Database optimization

---

## Future Enhancements (Post-MVP)

1. **Multi-language Support** - Internationalization for booking pages
2. **Mobile Apps** - Native iOS/Android apps
3. **Webhook Integrations** - Zapier, IFTTT integration
4. **CRM Integration** - Sync with Salesforce, HubSpot
5. **Advanced Analytics** - Detailed reporting, forecasting
6. **AI-powered Scheduling** - Smart time suggestions
7. **Virtual Waiting Room** - For early joiners
8. **Screen Sharing** - Built-in video conferencing
9. **Resource Booking** - Book meeting rooms, equipment
10. **Multi-participant Scheduling** - Find time that works for multiple people

---

## Success Criteria

The project will be considered successful when:

✅ Users can create and manage their availability rules
✅ Public booking page is live and functional
✅ External calendar integration works bidirectionally
✅ Automated notifications are sent reliably
✅ Drag-and-drop calendar management works smoothly
✅ Zero double-bookings occur
✅ Mobile-responsive design works on all devices
✅ System handles timezone conversions accurately
✅ Performance: Page loads < 2 seconds, API responses < 500ms
✅ User satisfaction: Positive feedback from internal team

---

## Estimated Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Foundation | 1 week | DocTypes, Forms, Permissions |
| Phase 2: Availability Engine | 1 week | Scheduling logic, APIs |
| Phase 3: Public Booking UI | 1 week | Vue.js booking flow |
| Phase 4: Calendar Integrations | 1 week | Google, Outlook sync |
| Phase 5: Internal Management | 1 week | Calendar view, Drag-drop |
| Phase 6: Notifications | 1 week | Emails, Reminders, .ics |
| Phase 7: Advanced Features | 2 weeks | Team booking, Payments |
| Phase 8: Testing | 1 week | QA, Bug fixes |
| Phase 9: Deployment | 1 week | Docs, Training, Launch |

**Total Estimated Time**: 10 weeks (2.5 months)

---

## Budget Estimate (If outsourcing)

- **Development**: 300-400 hours @ $50-150/hr = $15,000 - $60,000
- **Design**: 40 hours @ $60-120/hr = $2,400 - $4,800
- **Testing/QA**: 40 hours @ $40-80/hr = $1,600 - $3,200
- **Project Management**: 60 hours @ $70-150/hr = $4,200 - $9,000

**Total**: $23,200 - $77,000 (depending on location and seniority)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| External API rate limits | Medium | High | Implement caching, batch requests |
| OAuth token expiry | High | Medium | Automated refresh, user notifications |
| Double-booking edge cases | Low | High | Thorough testing, pessimistic locking |
| Email deliverability issues | Medium | Medium | Use reputable SMTP, SPF/DKIM setup |
| Performance with scale | Medium | High | Database optimization, caching layer |
| User timezone confusion | High | Low | Clear UI indicators, confirmations |
| Data privacy compliance | Low | High | GDPR-compliant data handling |

---

## Conclusion

This calendar booking system will streamline appointment scheduling for bs-infra.dk, eliminating back-and-forth communication and providing a professional booking experience. The phased approach allows for incremental development and testing, ensuring a robust and user-friendly final product.

The system's flexibility with meeting types, colors, drag-and-drop management, and calendar integrations positions it as a comprehensive solution comparable to commercial alternatives like Calendly, while being fully integrated into the Frappe ecosystem.

**Next Steps**: Review this document, confirm requirements, and begin Phase 1 implementation with DocType creation.

---

**Document Version**: 1.0  
**Last Updated**: November 13, 2025  
**Author**: Implementation Guide for bs-infra.dk Calendar Booking System
