# Django Appointment Breformed

A reusable Django library for appointment booking and scheduling. This is a private fork/customization of an appointment system, distributed via Azure DevOps Artifacts.

## Overview

This library provides a complete appointment booking system with:
- Service and staff management
- Working hours and days off scheduling
- Membership/subscription system with credits
- Client booking flow with email verification
- Appointment rescheduling
- Session-based group appointments
- Waiting list functionality
- Email notifications (via Django-Q)

## Installation

The package is published to Azure DevOps Artifacts as `django-appointment-breformed`.

```bash
pip install django-appointment-breformed --extra-index-url <azure-artifacts-url>
```

## Project Structure

```
appointment/
├── models.py           # Core models (Service, StaffMember, Appointment, etc.)
├── views.py            # Public booking views
├── views_admin.py      # Admin/staff management views
├── services.py         # Business logic layer
├── forms.py            # Django forms
├── urls.py             # URL patterns
├── settings.py         # Library settings with defaults
├── decorators.py       # View decorators
├── admin.py            # Django admin registration
├── tasks.py            # Django-Q async tasks
├── utils/              # Utility functions
│   ├── date_time.py    # Date/time helpers
│   ├── session.py      # Session utilities
│   └── view_helpers.py # View helper functions
├── email_sender/       # Email templates and sending logic
├── templates/          # Default templates
│   ├── administration/ # Admin templates
│   ├── appointment/    # Booking flow templates
│   ├── email_sender/   # Email templates
│   ├── error_pages/    # Error page templates
│   └── modal/          # Modal dialogs
└── tests/              # Test suite
```

## Core Models

### Service
Represents a bookable service with duration, price, and rescheduling settings.

### StaffMember
Links to Django User model. Contains scheduling preferences:
- `slot_duration` - Appointment slot length in minutes
- `lead_time` / `finish_time` - Working hours boundaries
- `appointment_buffer_time` - Buffer for same-day bookings
- `work_on_saturday` / `work_on_sunday` - Weekend availability

### WorkingHours
Per-day working hours for staff members (day_of_week 0=Sunday to 6=Saturday).

### DayOff
Date ranges when staff members are unavailable.

### AppointmentRequest
Initial booking request before client confirmation. Contains date, time, service, and staff member.

### Appointment
Confirmed booking linked to AppointmentRequest. Contains client info, payment status.

### Session
Groups multiple appointments into a single time slot (for group classes). Used in the Pilates studio for group sessions.

### Membership / MembershipType
Subscription system with credits:
- `MembershipType` - Defines subscription plans (credits, duration, valid services)
- `Membership` - Client's active subscription with remaining credits

### Client
Extended user profile for booking clients with membership access.

### Config
Singleton model for global appointment settings.

## URL Structure

### Public URLs (`/appointment/`)
- `request/<service_id>/` - Start booking flow
- `request-submit/` - Submit appointment request
- `client-info/<id>/<request_id>/` - Enter client information
- `thank-you/<appointment_id>/` - Confirmation page
- `appointment/<id_request>/reschedule/` - Reschedule flow

### AJAX URLs (`/appointment/ajax/`)
- `available_slots/` - Get available time slots
- `all_available_slots/` - Get slots for all staff
- `staff_of_slots_ajax/` - Get staff for specific slot
- `request_next_available_slot/<service_id>/` - Next available date
- `request_staff_info/` - Non-working days info

### Admin URLs (`/appointment/app-admin/`)
- `appointments/` - List appointments (JSON or HTML)
- `user-profile/` - Staff profile management
- `add-service/`, `update-service/<id>/`, `delete-service/<id>/` - Service CRUD
- `add-working-hours/`, `update-working-hours/<id>/`, `delete-working-hours/<id>/` - Working hours CRUD
- `add-day-off/`, `update-day-off/<id>/`, `delete-day-off/<id>/` - Days off CRUD
- `display-appointment/<id>/` - Single appointment details
- `delete-appointment/<id>/` - Delete appointment

## Settings

Configure in your Django settings:

```python
# Base templates for extending
APPOINTMENT_BASE_TEMPLATE = 'your_app/base.html'
APPOINTMENT_ADMIN_BASE_TEMPLATE = 'your_app/admin_base.html'

# Optional settings
APPOINTMENT_WEBSITE_NAME = 'Your Site'
APPOINTMENT_PAYMENT_URL = '/payment/'
APPOINTMENT_THANK_YOU_URL = '/thank-you/'
APPOINTMENT_SLOT_DURATION = 30  # minutes
APPOINTMENT_BUFFER_TIME = 0  # minutes
APPOINTMENT_LEAD_TIME = (9, 0)  # 9:00 AM
APPOINTMENT_FINISH_TIME = (18, 30)  # 6:30 PM

# Timezone
APP_TIME_ZONE = 'Europe/Athens'

# Email async sending
USE_DJANGO_Q_FOR_EMAILS = True
```

## Integration with PanagiotisPilates

This library is used in the PanagiotisPilates project:

```
C:\Users\giann\PycharmProjects\PanagiotisPilates
```

Key integration points:
- Templates overridden in `templates/appointment/`
- Base templates: `pilates_studio/profile_base_page.html` and `pilates_studio/admin_base_page.html`
- Custom views in `pilates_studio/views.py` extend booking functionality
- Session-based group appointments for Pilates classes

## Development

### Running the test project

```bash
cd django-appointment
venv\Scripts\activate
python manage.py runserver
```

The `appointments/` folder contains a test Django project for development.

### Building the package

```bash
python setup.py sdist bdist_wheel
```

### Dependencies

- Django >= 4.2, < 5.0
- Pillow >= 10.1.0
- phonenumbers >= 8.13.22
- django-phonenumber-field >= 7.2.0
- babel >= 2.13.0
- pytz >= 2023.3
- pendulum (for date handling)

## Key Concepts

### Booking Flow
1. User selects service → `appointment_request`
2. User selects date/time → AJAX calls for available slots
3. User enters client info → `appointment_client_information`
4. Email verification (if existing user) → `enter_verification_code`
5. Confirmation → `default_thank_you`

### Membership Credits
When a client books:
1. Check `Client.can_book_appointment(date)` for valid membership
2. `Client.apply_appointment_request(date)` consumes a credit
3. Credits are refunded on cancellation via `Appointment.refund_credits()`

### Sessions (Group Classes)
Sessions group multiple appointments at the same time slot:
- `Session.get_specific_session(date, start_time, staff_member)`
- Max capacity controlled by `MAX_SESSION_CAPACITY` setting in consuming project
- Waiting list via `WaitingList` model
