# LionsPath Project Enhancement History

Prepared September 18, 2026.

For the most detailed chronological list, see the [comprehensive bulleted project history](COMPREHENSIVE-BULLETED-HISTORY.md), prepared September 22.

For individual dated milestones, see the [dated change inventory](DATED-CHANGE-TIMELINE.md), prepared September 22. Its revision-by-revision review places prototype sign-in removal on June 25 and confirms the 52-question-per-grade assessment was already present June 24.

This inventory groups the major capabilities, improvements, and revisions found in the saved project history and current source. It covers the original foundation as well as later enhancements, including work that was subsequently replaced or consolidated.

## Scope and Evidence

- The earliest available Git snapshot is June 16, 2026. It already contains a substantial working site, so that date is the beginning of the available saved history, not necessarily the beginning of the project.
- The current revision is `becfc42`, dated August 28, 2026. Its history contains 27 commits. Two additional saved theme commits exist outside the current revision's ancestry; those experiments are not counted as separate features in the finished site.
- This review uses the first snapshot, subsequent changes, current application files, assessment model, Help content, analytics implementation, and deployment documentation. It is an inventory of development work, not a new live-site acceptance test.
- Some deployment documentation predates later code. For example, analytics documentation says browser event wiring is deferred, but the August 28 code implements it. Current source takes precedence when describing what was built; production activation is not inferred from local files.

## Verified Current Scale

| Area | What the current source contains |
| --- | --- |
| Main sections | 10: Home, Career Compass, Enrollment, Employment, Enlistment, Courses, AI Coach, Evidence, My Plan, and Help |
| Course catalog | 214 course/program entries |
| Employment explorer | 18 CTE program areas |
| Enrollment explorer | 6 course categories |
| Career Compass | 52 questions for each of Grades 9, 10, 11, and 12 |
| Assessment structure | 5 sections and 5 question formats |
| Assessment career connections | 9 career clusters |
| Course career connections | 6 career examples per course, drawing from 150 distinct occupation codes |
| Guided Help | 6 goal-based routes |
| Visual walkthroughs | 9 page guides containing 63 configured steps |
| External resource collections | 29 resource cards across the three pathway pages, plus other contextual links |
| Analytics test coverage | 58 test methods across the phase-based test files; not rerun for this documentation review |

These are counts of the current implementation. They are not all additions since the first snapshot. In particular, the original catalog contained 219 entries; later cleanup reduced it to 214.

## 1. Overall Planning Experience

- Established the three-part Enrollment, Employment, and Enlistment framework as the organizing structure of the site.
- Built a unified experience connecting pathway research, courses, AI assistance, readiness evidence, and a personal plan. The basic sections were already present in the first saved version.
- Expanded that foundation with Career Compass and a dedicated Help section.
- Added more routes from exploration into an action: save a course, import assessment findings, add a readiness move, prepare a question, and export a plan.
- Supported students who are still exploring or considering multiple pathways, rather than requiring an immediate single-pathway choice.
- Broadened the framing from a high-school course resource to a Louisa County Public Schools planning resource with family and counselor connections.
- Repeatedly clarified that the site supports decisions and conversations; it does not make official placement, eligibility, graduation, admission, or registration decisions.

## 2. Branding, Photography, and Visual Identity

- Evolved the LionPath branding into the current LionsPath naming across the site, reports, Help content, and browser metadata.
- Added the Louisa County CTE logo and its link to the district CTE website.
- Added Team LCPS branding to the home experience.
- Created distinctive illustrated pathway buttons, the Help Me Choose button, and the Talk to a 3E Coach button.
- Added dedicated page-header artwork for Career Compass, Courses, AI Coach, Evidence, and My Plan.
- Added branch-specific military imagery and an Enlisted vs. Officer visual.
- Introduced LCPS-related photography for the home welcome area, the three main pathway choices, and Employment and Enlistment page imagery.
- Refreshed the Courses, My Plan, Help Me Choose, and Evidence images in later August revisions.
- Added a coordinated favicon and device-icon package, including browser icons, an Apple touch icon, Android-sized icons, and a web manifest. The manifest alone is not an offline-app feature.

## 3. Themes and Readability

- Refined the green-and-gold identity across repeated panels, buttons, headings, tables, forms, and result displays.
- Made repeated typography and contrast passes to improve readability and reduce oversized or cramped text.
- Added an optional light mode while retaining dark mode as the default.
- Added a persistent theme preference that is restored on a later visit to the same browser.
- Applied the theme early in page loading and synchronized browser theme color and form-control color scheme.
- Extended light-mode styling into Career Compass, Evidence, Help, course dialogs, selected states, and other components that have their own colors.
- Preserved legible branding in image-led headers and embedded workspaces across both themes.
- Refined selected, hover, and focus states so active answers and controls remain distinguishable.

## 4. Navigation and Page Switching

- Expanded the main navigation as Career Compass and Help were introduced.
- Improved the desktop header so navigation remains on one line when sufficient space is available.
- Added a compact menu for narrower desktop, tablet, and phone widths.
- Added automatic menu closing after a page choice, Escape-key closing, and resetting when returning to a wide layout.
- Added accessible expanded-state information for the menu and current-page information for navigation.
- Reintroduced working page URLs such as `#compass` and `#plan`, including loading a directly linked section and responding to hash changes.
- Standardized scrolling to the top when changing sections, with reduced-motion-aware behavior.
- Coordinated page changes with embedded content: close a voice session, stop the home video, leave an expanded window, and reposition the shared AI workspace as appropriate.
- Retained navigation recovery behavior developed for Wix embedding and initialization failures.

## 5. Window Sizes, Responsive Layout, and Overlap Fixes

- Reworked column proportions and stacking for pathway pages, the course explorer, the coach-and-prompts workspace, Evidence, and My Plan.
- Refined mobile and tablet spacing, header dimensions, image sizing, content widths, and navigation behavior.
- Improved wrapping and sizing for long course names, labels, descriptions, and action groups.
- Reworked course details to fit the available viewport, including bounded dialog height and an independently scrollable body.
- Adapted the career-information table into a more readable layout on smaller screens.
- Refined how expanded Enrollment and Employment program cards occupy their grid.
- Added one-open-at-a-time behavior within a program-card group.
- Fixed the shared AI workspace positioning after accordion expansion or collapse, including resize observation and delayed layout resynchronization.
- Updated embedded-workspace positioning on screen resize and orientation changes.

## 6. Full-Screen Embedded Windows and Media Behavior

- Added Full Screen and Minimize controls to supported embedded videos and coaching windows.
- Used browser-native fullscreen when available, with an in-page expanded layout as a fallback.
- Added Escape-key handling and synchronization when fullscreen is exited through the browser.
- Ensured only one supported embedded window is expanded at a time.
- Automatically attached expansion controls to iframes created after the initial page load, including a newly opened voice session.
- Adjusted surrounding page scrolling and window placement while an embedded experience is expanded.
- Added automatic stopping/unloading of the home overview video when leaving Home, hiding the browser tab, or scrolling it out of view.
- Restored the home video when returning to the appropriate visible area.
- Added handling to stop the home video when a user moves into another action, while preserving the fullscreen control's behavior.

## 7. Home Page and Family Orientation

- Rebuilt the welcome area around a clearer LionsPath identity and explanation of the three Es.
- Included a playable 3E overview video in the original saved foundation, then reworked its home-page presentation in June and its playback behavior in July.
- Added prominent image-based starting points for Enrollment, Employment, Enlistment, and Help Me Choose.
- Developed the Help Me Choose journey from a short interest quiz into the Career Compass entry point.
- Added a family conversation roadmap covering Grades 6-8, Grade 9, Grades 10-11, and Grade 12.
- Added separate question sets for conversations with a student and with the school.
- Emphasized low-pressure exploration, comparing options, and leaving with a manageable next step.

## 8. Enrollment Guidance

- Built and refined college, community-college, transfer, certificate, and technical-training guidance.
- Organized relevant courses into six groups: Dual Enrollment, AP, Honors/Weighted, BRVGS, core college preparation, and portfolio/leadership/communication.
- Connected category entries to full course details and filtered course searches.
- Explained how different kinds of coursework support readiness, applications, transferable credit questions, and future programs.
- Added comparisons of education routes, student questions, family questions, and practical planning checkpoints.
- Added contextual AI prompt starters for Enrollment research.
- Connected students with resources for college comparison, FAFSA, applications, AP, PVCC, transfer, and other regional college opportunities.
- Improved category and filter distinctions so advanced coursework and general core preparation are represented more accurately.

## 9. Employment and CTE Guidance

- Organized the Employment explorer around 18 CTE program areas rather than only a small selection of individual courses.
- Linked program areas to their course lists, suggested sequences, credentials, and career information.
- Connected course choices to CTE completer planning, credentials, licenses, work-based learning, and job preparation.
- Added guidance on resumes, interviews, portfolios, internships, clinical experiences, cooperative education, job shadowing, and apprenticeships.
- Added a prominent link to the full CTE Course Guide.
- Added student and family questions about practical issues such as transportation, schedules, equipment, training, and advancement.
- Added a dedicated work-permit information section with steps for the student, employer, and parent/guardian, plus official-source links. This records the content added to the site, not a fresh legal review of its wording.
- Added contextual AI prompts and workforce research resources, including occupation, job-search, and apprenticeship tools.

## 10. Enlistment and Military Research

- Built and expanded comparisons of enlisted service, Reserve/Guard service, ROTC, service academies, officer routes, and related entry options.
- Added a more prominent Enlisted vs. Officer comparison, supporting artwork, and a route-comparison table.
- Added branch-specific images and links for the Army, Navy, Marine Corps, Air Force, Coast Guard, Space Force, and Reserve/Guard research.
- Expanded military career-family exploration beyond a single generic description of service.
- Connected military-related interests with JROTC, ASVAB exploration, leadership, public safety, technical courses, and civilian career possibilities.
- Added structured questions about contracts, job guarantees, training, benefits, obligations, and what should be verified before a commitment.
- Added questions and research checkpoints for both students and families.
- Integrated official military career and entry-route resources with pathway-specific AI prompts.

## 11. Course Catalog and Search

- Brought academic courses, electives, and CTE programs into a searchable catalog using the LCHS Program of Studies and CTE guide as its stated source material.
- Maintained catalog accuracy through corrections and cleanup; the current catalog has 214 entries, compared with 219 in the first snapshot.
- Added and refined filters for program/subject, 3E connection, grade, and course feature.
- Added feature filtering for credentials/licenses, DE, AP, Honors, BRVGS, core college preparation, portfolio/communication, work-based learning, CTE, hands-on learning, and leadership/service.
- Improved grade-range matching rather than relying only on simple text searches.
- Replaced broad search matching with ranked results that favor course names and program areas over incidental words in descriptions.
- Added recognition of common terms and abbreviations such as AP, DE, CTE, IT, WBL, nursing, healthcare, automotive, and biology.
- Added limited typo tolerance, plural/prefix matching, and handling of low-value search words such as "course" and "the."
- Reduced irrelevant matches by requiring search terms to match and filtering results below a relevance threshold.
- Added clearer result counts, best-match wording, and useful empty-result messages.
- Linked pathway-category buttons and Career Compass course suggestions into the same course-detail experience.

## 12. Course Cards, Prerequisites, and Career Connections

- Expanded course cards with grade, credits, program, pathway, evidence tags, a "why it matters" explanation, and a suggested next step.
- Added a consistent Details, Add to My Plan, and Ask AI Coach action set.
- Rebuilt the course-detail window into clearly separated course facts, prerequisites, sequence, evidence/credentials, planning actions, and career connections.
- Extracted prerequisite statements from sequence data so eligibility and course order are easier to distinguish.
- Added targeted prerequisite overrides and a counselor-verification fallback where the source does not list a prerequisite.
- Removed duplicate evidence/credential labels in course details and added meaningful empty states.
- Added six career examples to every current course entry, using 150 distinct occupation codes across the catalog.
- Added national median pay, typical entry education, projected growth, annual openings, and occupation codes, with BLS source attribution and data-year labels.
- Distinguished national median pay from local starting wages and career examples from guaranteed outcomes.
- Added course-specific AI prompts that carry relevant course details into a coaching conversation.
- Added direct links to verify course and prerequisite information with LCHS Counseling.

## 13. Career Assessment Evolution

- Added an initial short 3E interest quiz, then improved it into a one-question-at-a-time flow with blended results and suggested actions.
- Introduced the more substantial Career Compass assessment in June.
- Moved Career Compass from a separately embedded experience into the native LionsPath page in July.
- Created distinct assessment experiences for Grades 9, 10, 11, and 12, with age/stage-appropriate wording and planning emphasis.
- Expanded the current full assessment to 52 questions for each grade.
- Organized questions into Interests, Work Style, What Matters, Your Path, and Reflect.
- Supported five formats: self-ratings, either/or choices, scenarios, top-three rankings, and written reflections.
- Added question and section progress, back navigation, automatic advancement for applicable single-choice questions, and a return-to-grade-selection option.
- Required exactly three choices in ranking questions before continuing, while allowing optional written reflection.
- Added a sample report preview and a retake workflow.
- Retired the short quiz from the main user journey while retaining legacy code; it should not be presented as a second equally prominent current assessment.

## 14. Career Compass Results and Counselor Reports

- Added a student snapshot with a profile name, explanation, and pathway-blend visualization.
- Added top strengths, growth areas, six interest dimensions, work-style patterns, and values summaries.
- Represented Enrollment, Employment, and Enlistment as a blend rather than a forced single result.
- Matched results to nine career clusters connected to Louisa course/program suggestions and example careers.
- Made suggested courses actionable through course-detail links.
- Added grade-specific next steps, longer-term considerations, reflection questions, and the student's entered reflections.
- Added a separate counselor view with a concise snapshot, pathway matches, conversation starters, course ideas, work-based learning ideas, and follow-up questions.
- Added explicit guidance against treating the result as a placement, eligibility, or tracking decision.
- Added report printing, direct PDF download, a counseling link, and a retake action.
- Added an import into My Plan that carries the pathway lean, clusters/options, strengths, next steps, and questions into editable plan fields.

## 15. AI Coach and Prompt Tools

- Embedded a live SchoolAI coaching workspace in the planning experience; a basic version was already in the first snapshot.
- Added contextual access from Enrollment, Employment, Enlistment, the main AI Coach page, and AI Plan Review.
- Reworked those placements to share one persistent coaching iframe so changing LionsPath sections does not itself recreate the conversation.
- Added prompt starters for choosing a pathway, comparing options, finding courses, researching a career, creating a 30-day plan, and preparing for a counselor meeting.
- Added pathway-specific prompts and course-specific prompts alongside the general starters.
- Generated a detailed AI plan-review prompt from the student's chosen courses and written plan fields.
- Kept prompt actions as copy-and-paste steps controlled by the student.
- Added copied-state feedback and several clipboard fallbacks, including a selected-text panel for manual copying when browser embedding restrictions interfere.
- Added clearer privacy and verification language around AI usage.
- Added direct SchoolAI sign-in links for account authentication that cannot complete inside the embedded window.
- Updated allowed SchoolAI authentication origins and delegated identity-related browser permissions in the iframe/server configuration.

## 16. Knowt Voice Coach

- Added the Talk to a 3E Coach entry point and custom launch image.
- Built an inline voice-session panel with a live-session bar and explicit End Voice Session control.
- Tested and revised the integration as Knowt embedding restrictions and approved hosting domains were investigated.
- Replaced the original join link with the later join/quiz destination and normalized the launch URL to `knowt.com`.
- Enabled the iframe version in the saved code and retained Open in New Tab as a fallback.
- Added iframe delegation for microphone, camera, autoplay, speaker selection, clipboard, and fullscreen capabilities, including both Knowt host variants.
- Changed iframe loading behavior to eager and integrated it with the shared fullscreen controls.
- Removed the iframe when ending a session or leaving the AI Coach page, so the embedded session is not left running in the background.
- Added quiet-space and privacy reminders.
- The history demonstrates implementation and permission work. It does not establish that Knowt's microphone interaction or first-start error is resolved on every device today.

## 17. Evidence and Readiness Snapshot

- Replaced the original simple evidence checklist and fixed-increment signals with a more detailed readiness system.
- Added grade-specific checklists for Grades 9-12, using early- and upper-high-school wording and expectations.
- Grouped evidence into classes/grades, careers/credentials, tests/scores, activities/service/language, and applications/conversations.
- Used weighted signals that can contribute to more than one pathway.
- Added live Enrollment, Employment, and Enlistment readiness meters with Exploring, Building, and Strong labels.
- Added separate current-grade and cumulative Grades 9-12 readiness views.
- Preserved a separate set of selections for each grade when the user changes the grade selector.
- Counted repeated signals only once in cumulative scoring while retaining the grade-by-grade selections.
- Added migration of older saved evidence formats into the newer per-grade structure.
- Added diploma-seal conversation indicators, explanatory tooltips, progress states, and reminders that official requirements require counselor verification.
- Added "Your next 3 moves" based on missing evidence, including counselor-conversation actions.
- Connected those moves to My Plan and to ready-to-copy AI prompts.
- Added a cumulative printable/PDF snapshot that includes the grades represented, checked evidence, readiness signals, seal conversations, and next moves.
- Added snapshot clearing and local saving.

## 18. My Plan and Saved Courses

- Expanded the original plan builder with fields for experiences, strengths/skills, possible options, a concrete next step, and questions.
- Supported Enrollment, Employment, Enlistment, Still Exploring, and Multiple Pathways as planning directions.
- Represented saved courses as structured cards carrying their program, grades, credits, pathway, evidence, and description.
- Added duplicate-course prevention, individual removal, and a separate clear-all-courses action.
- Added confirmation behavior for bulk course clearing and written-note clearing.
- Kept clearing written notes separate from clearing the selected-course list.
- Migrated recognizable older text-based course selections into structured course records.
- Added automatic saving and restoration of plan fields and selected courses in the current browser.
- Connected Career Compass imports and Evidence actions to editable plan fields.
- Added both a concise shareable plan summary and a fuller AI review prompt.
- Added printing and direct PDF download, with saved courses and meeting reminders included.
- Clarified that saving a course in My Plan does not register the student for it.

## 19. Sharing, Printing, and PDF Exports

- Added a dedicated print layout for the plan instead of relying on printing the entire interactive page.
- Added print/save support for Career Compass reports and Evidence snapshots.
- Added direct PDF downloads for all three planning outputs: My Plan, Career Compass, and Evidence.
- Built text wrapping, page creation, character cleanup, and document headings into the local PDF-generation utility.
- Included planning context and relevant verification reminders in exported documents.
- Updated Evidence exports to include cumulative, grade-by-grade selections after the readiness redesign.
- Added Copy Plan Summary for a concise text handoff to an adult, alongside the more detailed AI prompt.
- Kept export generation local to the browser; these controls are not automatic submission to a counselor or a student-record system.

## 20. Guided Help and Visual Walkthroughs

- Added a dedicated Help page focused on choosing a goal and following a short route through the site.
- Created six routes: find a direction, choose courses, build an Enrollment plan, connect school to a career, explore military service, and prepare for a meeting.
- Added grade selection and pathway choices to tailor the starting context.
- Added step-by-step route actions, completion criteria, progress indicators, and links to the relevant page/control.
- Added a route bar that accompanies the student through the actual site rather than requiring repeated returns to Help.
- Saved the selected route and completed steps in the browser so the user can resume.
- Added restart/exit behavior and integrated Help progress with the clear-all-data control.
- Added nine screenshot-based page guides covering Home, Compass, Enrollment, Employment, Enlistment, Courses, Coach, Evidence, and My Plan.
- Built 63 configured walkthrough steps with captions, highlighted screenshot regions, and visual focus cues.
- Added play/pause, previous/next, replay, progress, and frame-count controls.
- Added a page-guide dialog and contextual access to the appropriate guide.
- Added reduced-motion behavior, focus management, accessible labels, image descriptions, and pause behavior when leaving the relevant view.
- Added frequently asked questions about saved work, assessment results, AI, and the role of adult verification.
- Updated walkthrough language as the branding, counseling footer, and other parts of the site changed. Some screenshots/captions may still reflect an earlier layout or behavior; they were not all recaptured in this review.

## 21. Counseling and Adult Support

- Added direct links to LCHS Counseling, counselor identification, appointment information, and contact information.
- Connected course eligibility, assessment reports, readiness evidence, and plan review with counselor follow-up.
- Added student and family question sets so an online exploration can lead to a more productive conversation.
- Initially introduced counseling callouts throughout the pages, then consolidated repeated closing sections into a shared counseling footer.
- Preserved targeted counseling links in course details and Career Compass reports.
- Clarified the handoff: LionsPath helps organize a plan, while counselors and other appropriate adults confirm official requirements.
- The appointment controls link to counseling resources; the site does not implement its own appointment-booking system.

## 22. Privacy and Local Data Handling

- Removed the prototype local sign-in/email-label experience and its implication of a real student account system.
- Kept the public planning application available without a LionsPath student login.
- Limited saved plan and Evidence information to the current browser/device rather than adding a central student-record database.
- Added a 180-day age limit for saved plan/Evidence data, measured from its last update.
- Added validation of restored grades, pathway choices, course records, text lengths, evidence identifiers, and saved timestamps.
- Added recovery from malformed or unusable saved data.
- Added clear-all-data and more focused clearing actions for shared-device use.
- Added warnings against entering student IDs, passwords, home addresses, medical details, and other sensitive information into planning or AI tools.
- Documented the difference between local plan storage and information a user chooses to enter into an external AI/voice service.
- Limited analytics events to fixed usage categories; no assessment answers, plan contents, student names, or AI conversations are included in those event payloads.
- Career Compass answers/results are held in page memory in the current implementation; importing results into My Plan or exporting a report is different from automatic assessment-answer saving across browser reloads.

## 23. Application Security, Reliability, and Maintenance

- Moved the main application JavaScript out of the large HTML file into a local application asset.
- Kept the Career Compass model, Help behavior/styles, theme, and later course enrichment in dedicated files.
- Removed unused remote Markdown-rendering dependencies.
- Removed the legacy embedded assessment files and a downloadable site archive from the public project contents.
- Replaced inline event-handler usage where needed for the stricter script policy.
- Added a Content Security Policy with specific allowed frame/script/connect destinations and restrictions on plugins, form actions, and base URLs.
- Added explicit iframe sandbox/permission settings and safer referrer/new-tab link handling.
- Added an Apache deployment template for HTTPS redirection, modern TLS, HSTS, content-type protection, restricted framing, and browser-permission delegation.
- Added server rules to prevent public access to repository metadata, backups, configuration, source-only directories, certificates, keys, logs, and other private files.
- Added log-rotation configuration and separation between publicly served assets and administrative/runtime files.
- Preserved isolated initialization steps so a failure in one renderer does not automatically disable every navigation or action control.
- Added versioned asset references for later changes so browsers can request refreshed scripts and styles.
- Added security/deployment documentation and a read-only analytics deployment preflight.
- Server templates document/build these controls; their presence alone does not confirm what is currently installed on the production server.

## 24. Analytics Infrastructure and Private Dashboard

- Added GoatCounter visit reporting and the required script/security-policy configuration.
- Built a separate private analytics system using Python, SQLite, Apache request logs, and fixed browser events.
- Added parsing for plain and compressed Apache logs, including local-time conversion with daylight-saving handling.
- Added classification for human page loads, assets, API requests, bots/automation, referrers, browsers, operating systems, and device types.
- Added historical backfill, resumable incremental imports, duplicate prevention, rotated-log handling, and incomplete/malformed-line handling.
- Added daily/hourly/page aggregation and tools to reconcile imported counts against source logs.
- Added rotating hashed visitor estimates without writing raw IP addresses or full user-agent strings into the analytics database.
- Added an authenticated reporting API and a separately constrained public event endpoint.
- Built a branded private dashboard with date presets, custom ranges, previous-period comparisons, visitor estimates, site loads, sessions, tracked views per session, session duration, and request totals.
- Added usage trends, content/feature tables, 3E comparisons, technology/source views, hourly/weekday views, and an activity heatmap.
- Added technical-health information, status/error reporting, import freshness, database coverage, and import diagnostics.
- Added aggregate CSV downloads tied to the selected date range.
- Kept dashboard assets local and protected rather than loading a public chart service into the private dashboard.
- Built a five-minute refresh schedule and hardened service/socket templates that separate the dashboard process from log-reading duties.
- Added automated tests for parsing, privacy, imports, reports, authorization, dashboard delivery, exports, runtime configuration, and end-to-end flows.

## 25. Analytics Accuracy and Protection Improvements

- Added browser event tracking for section views, Course Explorer, AI Coach, Evidence, My Plan, assessment starts/completions, voice launches, SchoolAI launches, counseling links, and selected print/PDF actions.
- Distinguished site loads from internal single-page-app section views so opening another tab within LionsPath does not inflate the same headline metric.
- Corrected views-per-session calculations so arbitrary feature events do not all count as content views.
- Added zero-activity dates to applicable time-series displays.
- Corrected weekday averages to include all matching calendar days in the selected range, including days with no activity.
- Added chart tooltips and keyboard-focusable chart targets for trend and hourly data.
- Displayed missing 3E event coverage as unavailable/not measured rather than implying zero student interest.
- Added explanatory notices for repeated-load patterns, large traffic totals, and the limits of estimated visitors on shared networks.
- Added same-origin, content-type, size, field, and rate-limit checks for event ingestion.
- Added protected-report query validation, trusted-proxy checks, spoofed-header handling, and restrictions on database/secret files.
- Neutralized spreadsheet-formula prefixes in CSV exports and used safe text rendering for dashboard data.
- Kept analytics failure from blocking student navigation and planning actions.
- Retained GoatCounter during the transition. The repository still contains its script; this review does not claim that the private system has replaced it in production.

## Major Milestones

Dates below are saved-commit dates, not guaranteed first-design or public-launch dates.

| Date | Saved milestone | Reference |
| --- | --- | --- |
| June 16 | Initial saved site with the three pathway pages, catalog, SchoolAI, basic Evidence, and My Plan | `6d89c2c` |
| June 17-18 | CTE/LCPS branding, military visuals/links, home/video presentation and image choices, short interest quiz, expanded guidance, course actions, and plan sharing/printing | `296d1b9`, `ac4f537`, `2a63822`, `3ec3de3` |
| June 24 | Career Compass added, with browser/device branding assets | `0521784` |
| June 25 | Career Compass presentation, mobile/tablet navigation refinements, and removal of prototype sign-in | `d229931` |
| July 2 | Native Career Compass, richer readiness snapshot, seal conversation indicators, PDF/report tools, and page-header/theme work | `461b28a` |
| July 8 | Knowt voice-coach integration and home-video lifecycle controls | `de521ad` |
| July 21 | Persistent shared AI workspace and full-screen/minimize controls | `f6ed3bb` |
| July 23 | Knowt link, iframe enablement, and microphone/media permission revisions | `853439c`, `a0b791b` |
| July 24 | Application/server hardening, local-data validation, and removal of legacy dependencies/files | `05cbb35` |
| August 3 | Goal-based Help routes and visual page walkthroughs | `c1d2bac` |
| August 10 | Visit-reporting configuration updates | `5780e29` |
| August 11 | Counseling connections, work-permit content, and program-card/AI overlap correction | `35e1ada`, `8e6e047` |
| August 13 | Separate per-grade Evidence selections and current/cumulative readiness reporting | `7323a1c` |
| August 20 | Private analytics foundation/dashboard/runtime/security work saved; optional light mode introduced | `02b47a3`, `199577e` |
| August 21 | Site redesign/release sweep, local photography, search relevance improvements, catalog cleanup, and navigation refinements | `eba3650` |
| August 24 | Courses header image refresh | `2b03ec5` |
| August 26 | Help Me Choose image, consolidated counseling footer, enriched course/prerequisite/career details, and SchoolAI sign-in handling | `da507ca`, `9131f8e`, `58861ba` |
| August 27 | Evidence imagery and related content updates | `4380c63` |
| August 28 | Browser analytics events, corrected metric definitions/calculations, interactive chart details, and data-quality explanations | `becfc42` |

## Status Boundaries Worth Preserving

- The early short quiz, prototype sign-in, and legacy embedded Career Compass are part of the development history, not all current primary features.
- Native assessment scoring and printed reports are custom planning tools, not evidence of a validated psychological assessment or official readiness determination.
- Local saving is not cloud synchronization, counselor access to student records, or persistence across devices.
- Counseling and sign-in buttons often link to external services; LionsPath does not control those services' authentication or appointment workflows.
- Knowt embedding/microphone behavior depends on the host, browser permissions, and Knowt itself. The recorded iframe work is not a guarantee of universal present-day compatibility.
- Analytics implementation and server templates are verified in the repository. Production activation, actual traffic accuracy, and removal of GoatCounter need separate confirmation.
- Course availability, labor-market values, work-permit wording, external links, and diploma rules were not freshly revalidated against outside sources during this historical inventory.

## Source Map

| Source | Main evidence |
| --- | --- |
| [Site HTML](../index.html) | Page structure, navigation, current imagery, plan fields, Help entry points, privacy text, script/security configuration |
| [Main application](../assets/lionpath-app.js) | Catalog, pathways, shared AI/voice windows, fullscreen, search, assessment presentation, readiness, plans, exports, browser events |
| [Career Compass model](../assets/pathfinder/native-compass-model.js) | Grade-specific question banks, scoring, profiles, career clusters, student/counselor result data |
| [Course enhancements](../assets/lionpath-course-enhancements.js) | Prerequisite extraction, career groupings, BLS-labeled occupation data, text cleanup |
| [Theme styles](../assets/lionpath-theme.css) and [theme behavior](../assets/lionpath-theme.js) | Light/dark appearance, stored preference, responsive course-detail and theme refinements |
| [Help behavior](../assets/lionpath-training.js) and [Help styles](../assets/lionpath-training.css) | Six routes, nine tours, 63 steps, saved progress, contextual guidance |
| [Analytics implementation](../analytics/) | Private application, reporting, imports, privacy, dashboard, exports, and tests |
| [Analytics documentation](ANALYTICS.md) | Architecture and phased work; some activation/instrumentation descriptions predate later code |
| [Security deployment notes](../SECURITY-DEPLOYMENT.md) | Hosting controls, local data handling, external-service boundaries, deployment requirements |
| [Apache template](../deployment/apache/lionspath.conf) and [analytics runtime notes](../deployment/analytics/README.md) | HTTPS/security headers, private routes, service separation, deployment/runtime controls |

No application code was changed for this inventory.
