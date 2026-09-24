# Light Theme Review

Reviewed and updated September 24, 2026.

## Findings And Changes

- **Nearly invisible enrollment buttons:** Some category actions inherited white text from the dark theme while receiving white backgrounds. Explicit light-theme button rules now give secondary actions dark text and primary actions white text on solid green.
- **Low-contrast text:** Evidence group headings were pale mint on white (about 1.76:1). They now use dark green (about 11.88:1 on white). Yellow counseling links were about 1.25:1 on white; the new green links are about 8.29:1. The course-dialog career label no longer uses yellow on a pale background.
- **Muddy page containers:** Several more-specific dark rules overrode low-specificity light rules. Translucent black backgrounds remained on course filters, page sections, and featured AI panels. Light surfaces now have explicit precedence, with neutral page backgrounds and opaque white content surfaces.
- **Competing visual layers:** Removed the light-mode background grid and decorative color glows. Reduced large shadows, eliminated decorative frames around page-section groups, and simplified section headings to dark text and a divider.
- **Weak action hierarchy:** Primary buttons now use consistent green fills, secondary buttons remain white, and keyboard focus has an explicit green outline. Full-screen iframe controls use the same restrained treatment.
- **Dense Evidence controls:** Choices now use readable 14px text, modest corners, and a clear square selection indicator. Selected choices have a green border, pale green background, and filled indicator. Readiness rows no longer sit inside extra shadowed cards.
- **Nested Plan panels:** Plan sections now use separators inside the existing builder rather than several framed boxes. Input borders, placeholder text, and focus states are clearer.
- **Inconsistent component states:** Expanded enrollment groups, Work Permit steps, Branch Snapshot cards, Help routes, Compass answers, and course dialogs share the light palette. Large dark hover shadows no longer appear on Compass answer buttons.
- **Oversized supporting headings:** Section, military-entry card, and Compass question headings use more restrained fixed sizes in light mode.
- **Hard-to-maintain colors:** Common light-theme text, surface, border, and accent colors now use named CSS variables. The browser theme-color metadata matches the new page background.

## Preserved

- Existing page structure, navigation, photos, illustrated headers, and green/gold branding.
- Course data, planning behavior, assessment logic, iframe permissions, and external service URLs.
- The earlier course-dialog change: Add to My Plan stays in the dialog and reports whether the course was added or was already saved.
- Dark mode. A before/after comparison of 2,000 sampled elements found no differences in text color, backgrounds, borders, shadows, corners, or font sizes. Shared course-dialog rules were also reviewed separately.

## Verification

- Reviewed all ten page views: Home, Enrollment, Employment, Enlistment, Courses, AI Coach, Evidence, My Plan, Help, and Career Compass.
- Ran computed text-contrast checks on displayed text with solid backgrounds. No remaining failures were found in the checked main-page views, expanded enrollment categories, course dialog, selected Evidence state, or sampled Compass question state. Thresholds were 4.5:1 for normal text and 3:1 for large text.
- Reviewed desktop and mobile screenshots. Checked all ten page views at 390px and 320px viewport widths without finding content extending beyond the viewport, excluding intentionally scrollable tables and screen-reader-only content.
- Exercised course saving and duplicate feedback, Evidence selection, the Help course-planning route, and a Compass answer transition.
- Verified JavaScript syntax with Node and checked the patch for whitespace errors with Git.

## Limits

- These checks are not a complete accessibility certification. Image-based lettering, gradients, pseudo-element backgrounds, every possible assessment result, and every hover state need separate coverage beyond the sampled visual checks.
- SchoolAI and Knowt control the contents of their cross-origin iframes. This update styles LionsPath's surrounding panels and full-screen controls; it does not change or verify third-party sign-in, microphone access, or their internal themes.
- Tests used temporary local preview origins so the user's existing saved plan and evidence were not modified.
