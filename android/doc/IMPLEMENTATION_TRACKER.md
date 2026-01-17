# DistCapsule Android App - Implementation Tracker

This document tracks incremental implementation against `doc/ANDROID_APP_SPEC.md`.

## Scope Map (from spec)
- Connection settings (base URL, persistence)
- User list (view ID, permission, channel, active status)
- Logs (who/when/how, recent history)
- Enrollment flow
  - User profile input (name, auth level, assigned channel)
  - Trigger face enrollment
  - Trigger fingerprint enrollment
- Network/Wi-Fi behavior (bind to Wi-Fi if no internet)
- Async feedback (loading/progress for hardware capture)

## Milestones
- Step 1: Data models + users/logs API wiring + basic UI hooks
  - Status: Completed
  - Notes:
    - Added `User` and `LogEntry` models for JSON parsing.
    - `/users` now returns `List<User>`, displayed in spinner and result text.
    - `/logs?limit=50` wired to "Load Log Files" button.
    - Assumes backend JSON fields: `id`, `name`, `auth_level`, `assigned_channel`, `is_active`,
      `timestamp`, `user_id`, `event_type`, `status`.

- Step 2: Enrollment API + request models
  - Status: Completed
  - Notes:
    - Added request/response models for enroll and hardware triggers.
    - Added Retrofit endpoints for `/users/enroll`, `/hardware/enroll_face`,
      `/hardware/enroll_finger`.
    - Assumes response fields include `status` and optional `message`.

- Step 3: Enrollment UI flow
  - Status: Completed
  - Notes:
    - Added form fields for name/auth/channel and enroll button.
    - Added face/fingerprint trigger buttons tied to selected user.
    - Uses spinner selection or last enrolled user ID.

- Step 4: Logs UI improvements
  - Status: Completed
  - Notes:
    - Added log list UI using RecyclerView.
    - Logs render as two-line items (timestamp/user + event/status).

- Step 5: Network binding + async feedback
  - Status: Completed
  - Notes:
    - Added Wi-Fi binding when base URL resolves to local/private host.
    - Added loading indicator and disabled actions during network requests.

- Step 6: Enrollment UX follow-up
  - Status: Completed
  - Notes:
    - After successful enroll, refreshes user list and selects new user in spinner.

- Step 7: Accessibility + UI polish
  - Status: Completed
  - Notes:
    - Switched inputs to Material TextInputLayout for clearer labels.
    - Added headings, live region for status, and touch target minimums.
    - Added labels/content descriptions for spinner, logs, and loading state.

- Step 8: Visual refresh
  - Status: Completed
  - Notes:
    - Introduced cohesive color palette and gradient background.
    - Rebuilt layout with card-based sections and typographic hierarchy.

- Step 9: Coffee palette + spinner UX
  - Status: Completed
  - Notes:
    - Switched UI colors to a coffee-inspired palette.
    - Added spinner dropdown mode and a prompt when user list is empty.

- Step 10: Header icon
  - Status: Completed
  - Notes:
    - Added coffee capsule icon in the header card for visual branding.

- Step 11: Connection UX simplify
  - Status: Completed
  - Notes:
    - Removed Save/Load buttons, replaced with a single editable field.
    - Added pen icon to toggle edit mode and auto-save on done/blur.

- Step 12: Biometric capture layout + French UI
  - Status: Completed
  - Notes:
    - Replaced user dropdown with two side-by-side capture cards.
    - Updated UI strings and runtime messages to French.

- Step 13: Capture cards icons + handwritten title
  - Status: Completed
  - Notes:
    - Added face/fingerprint icons inside capture cards.
    - Applied handwritten font to the main title.

- Step 14: Header free layout
  - Status: Completed
  - Notes:
    - Removed the header card and subtitle line so title + capsule float freely.

- Step 15: Header spacing + capture icon sizing
  - Status: Completed
  - Notes:
    - Added top spacing and horizontal padding for the header row.
    - Expanded face/fingerprint icons to fill the card area.

- Step 16: Enrollment card layout + cafe palette
  - Status: Completed
  - Notes:
    - Moved enrollment card to the left with a cafe image panel on the right.
    - Updated the color palette to match the cafe illustration.

- Step 17: Button palette sync
  - Status: Completed
  - Notes:
    - Tuned "Charger" and "Inscrire" button colors to match cafe palette.

- Step 18: Cafe image fit + Handlee typography
  - Status: Completed
  - Notes:
    - Adjusted cafe image to fit fully within its panel.
    - Applied Handlee font to non-title text (inputs, buttons, section labels).

- Step 19: Cafe2 refresh
  - Status: Completed
  - Notes:
    - Swapped cafe image to cafe2 and updated palette to match.

- Step 20: Cafe2 background removal + contrast
  - Status: Completed
  - Notes:
    - Rendered cafe2 with transparent background and matched card heights.
    - Darkened non-title text for better contrast.

- Step 21: Image fit + bold text
  - Status: Completed
  - Notes:
    - Ensured cafe image stays within the card bounds.
    - Increased non-title text weight for readability.

- Step 22: Cafe2 clean v2 + darker text
  - Status: Completed
  - Notes:
    - Replaced the image with a stronger background-removed version.
    - Darkened non-title text colors for better contrast.

- Step 23: Connection-first flow
  - Status: Completed
  - Notes:
    - Reintroduced a dedicated connection card with base URL input and connect action.
    - Split the UI into steps: connection → enrollment → biometric capture.
    - Hid enrollment/capture/logs/status until the previous step succeeds.

- Step 24: Splash intro + per-step cafe art
  - Status: Completed
  - Notes:
    - Added a splash overlay animation (title pop, capsule drop) before showing the main UI.
    - Added separate connection/enrollment/capture panels with their own cafe cutout images.

- Step 25: V2 auth + role dashboard
  - Status: Completed
  - Notes:
    - Switched to token bind/auth flow and updated API endpoints to V2.
    - Rebuilt UI into Connection → Bind → Dashboard screens.
    - Added biometric status display and actions (unlock, update face/finger, delete user).
    - Added admin-only management panel (select user, enroll, delete) and create-user form.

- Step 26: Channel map + admin channel control
  - Status: Completed
  - Notes:
    - Added channel map for all users and per-user channel status display.
    - Added admin controls to assign channels and manually unlock channels 1-5.

## Open Questions / Assumptions
- Confirm JSON field names and response schemas for `/users` and `/logs`.
- Confirm whether logs should be paged or filtered by user/event type.
