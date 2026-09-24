# LionsPath: Dated Change Inventory

Prepared September 22, 2026. Based on the saved project history through August 28, 2026 (`becfc42`).

This is a timeline-ready list of medium-to-large changes. Each row has a short label for a graphic and a longer explanation for captions or presentation notes. Related small fixes are grouped into meaningful improvements.

For the expanded, individually dated bullet list, see the [comprehensive bulleted project history](COMPREHENSIVE-BULLETED-HISTORY.md).

## How to Read the Dates

- Dates are approximate development milestones taken from saved revisions, not verified public launch dates. A large revision may contain work completed over several earlier sessions.
- **By June 16** means the feature already existed in the earliest saved version. Those foundation items should be shown separately from later changes.
- Repeated topics on different dates represent actual rounds of improvement, such as adding a quiz, replacing it with Compass, and later rebuilding Compass inside the main site.
- **Superseded experiment** marks saved design work that was subsequently replaced. It is useful for depicting iteration, but is not an additional current feature.
- Analytics and hosting entries describe what was built or configured in the repository. This inventory does not establish production deployment dates.
- Two details are more precisely dated here than in the earlier overview: the prototype sign-in was removed June 25; the 52-question-per-grade Compass already existed in the June 24 revision.

## Original Foundation

Source: first saved revision, `6d89c2c`. These were already present by this date; their original creation dates are unknown.

| Approximate date | Area | Timeline label | What was in place |
| --- | --- | --- | --- |
| By 2026-06-16 | Structure | Three pathways, one planning site | Established a unified site around Enrollment, Employment, and Enlistment, with an embedded overview video and navigation connecting exploration, courses, coaching, readiness, and planning. |
| By 2026-06-16 | Pathways | Enrollment course organizer | Organized college-connected courses into Dual Enrollment, AP, Honors/Weighted, BRVGS, core preparation, and portfolio/leadership categories with expandable details. |
| By 2026-06-16 | Pathways | CTE program explorer | Built an Employment explorer around 18 CTE program areas, linking courses, sequences, credentials, and career information. |
| By 2026-06-16 | Pathways | Military pathway comparisons | Added military entry routes, branch information, career families, comparison tables, and questions to investigate before making a commitment. |
| By 2026-06-16 | Courses | Searchable school course catalog | Combined 219 academic, elective, and CTE course/program entries with search, pathway/grade/3E filters, and individual course-detail windows. |
| By 2026-06-16 | AI & voice | Embedded AI planning support | Embedded SchoolAI coaching, contextual prompt starters, copy/paste tools, and a plan-review workspace into the site. |
| By 2026-06-16 | Evidence & planning | First readiness simulator | Created the original evidence checklist and simple pathway-signal meters to help students recognize possible readiness evidence. |
| By 2026-06-16 | Evidence & planning | My Plan with saved courses | Created a student plan builder with selected-course records, experiences, questions, course removal, and an AI review prompt. |
| By 2026-06-16 | Privacy & reliability | Browser-based saving and recovery | Saved plan/evidence work in the current browser, restored it on return, and included clipboard and navigation fallbacks for embedding restrictions. |

## June: Branding, Guidance, and Career Compass

| Approximate date | Area | Timeline label | What changed |
| --- | --- | --- | --- |
| 2026-06-17 | Design & media | District and CTE identity | Added stronger Louisa County Public Schools branding, the CTE logo, and a direct connection to the district CTE website. |
| 2026-06-17 | Pathways | More useful military research | Made branch cards link to official destinations and added an Enlisted vs. Officer visual to support route comparison. |
| 2026-06-17 | Pathways | Full CTE guide connection | Promoted the full CTE Course Guide within the Employment explorer so students could move from a program summary to the source material. |
| 2026-06-18 | Design & media | Image-led home choices | Replaced the simpler home choices with custom Enrollment, Employment, Enlistment, and Help Me Choose imagery, alongside stronger Team LCPS presentation. |
| 2026-06-18 | Design & media | 3E overview video presentation | Reworked the existing embedded video's home-page presentation, including a widescreen layout. The video itself was already present by June 16. |
| 2026-06-18 | Help & counseling | Family conversation roadmap | Added grade-band checkpoints and separate questions for students and schools, giving families a practical way to support planning over time. |
| 2026-06-18 | Assessment | First guided interest quiz | Added the short 3E interest quiz and developed its one-question-at-a-time flow, progress display, back navigation, and result screen. |
| 2026-06-18 | Assessment | Quiz results become actions | Added blended pathway results, connected course suggestions, next steps, an AI discussion prompt, and a way to bring the result into My Plan. |
| 2026-06-18 | Pathways | Expanded Enrollment decisions | Added comparisons of community college/transfer, four-year college, technical training, and advanced coursework, with student/family questions and a next-action checklist. |
| 2026-06-18 | Pathways | Expanded career preparation | Added clearer Employment guidance around CTE completion, credentials, work-based learning, job readiness, and practical student/family planning questions. |
| 2026-06-18 | Pathways | Expanded service planning | Added structured research checkpoints, family questions, branch imagery, and a stronger visual comparison of enlisted and officer routes. |
| 2026-06-18 | Courses | Course-feature filtering | Added another way to narrow courses by features such as credentials, DE, AP, work-based learning, CTE, hands-on learning, college preparation, and leadership. |
| 2026-06-18 | Courses | Courses explain their value | Expanded course cards with why the course matters, what could come next, and a course-specific Ask AI Coach prompt. |
| 2026-06-18 | Evidence & planning | A fuller student plan | Expanded My Plan with skills/strengths, options under consideration, and a concrete next step, and included those details in the generated AI review prompt. |
| 2026-06-18 | Evidence & planning | Shareable and printable plans | Added a concise copyable plan summary and a dedicated print layout containing courses, reflections, and meeting reminders. |
| 2026-06-18 | Evidence & planning | Separate controls for plan cleanup | Added a way to clear written notes independently of saved courses, with confirmation behavior to reduce accidental loss. |
| 2026-06-18 | Design & media | First broad readability redesign | Made a site-wide pass across typography, pathway layouts, repeated panels, program explorers, and the home experience to improve consistency and readability. |
| 2026-06-24 | Assessment | Career Compass replaces short quiz | Introduced the full Career Compass in a dedicated section and replaced the home-page short quiz with a deeper assessment entry point. |
| 2026-06-24 | Assessment | Four grade-specific assessments | Added distinct Grade 9, 10, 11, and 12 experiences, each containing 52 questions with wording and planning emphasis appropriate to that stage. |
| 2026-06-24 | Assessment | Five ways to reflect | Organized Compass into five sections and supported ratings, scenarios, either/or choices, ranked top-three selections, and optional written reflections. |
| 2026-06-24 | Assessment | Personal strengths and pathway report | Added student profiles, strengths, growth areas, interest patterns, work-style tendencies, values, and a blend of the three pathways. |
| 2026-06-24 | Assessment | Local courses tied to career clusters | Connected nine career clusters with example careers and Louisa course/program suggestions; course links could open details in the main site. |
| 2026-06-24 | Help & counseling | Counselor assessment view | Added an advising-focused version of results with a snapshot, conversation starters, course ideas, work-based learning possibilities, and follow-up questions. |
| 2026-06-24 | Assessment | Preview, revisit, and share results | Added a sample report, retaking, report printing, and next-step/reflection content so the assessment could support demonstrations and real conversations. |
| 2026-06-24 | Design & media | Browser and device branding | Added the coordinated favicon, touch-icon, Android-icon, and web-manifest package so the site had a recognizable identity outside the page itself. |
| 2026-06-25 | Structure | Compact mobile navigation | Added a collapsible menu for smaller screens, page-selection closing, Escape handling, and responsive header behavior. |
| 2026-06-25 | Design & media | Tablet and phone layout overhaul | Reworked the site shell, stacked layouts, embedded-window sizing, and small-screen presentation across the main tools. |
| 2026-06-25 | Assessment | Less friction starting Compass | Started the assessment directly at grade selection, refreshed its header, and made Help Me Choose lead directly to Compass instead of competing entry points. |
| 2026-06-25 | Assessment | Assessment window follows content | Improved the embedded assessment's automatic height reporting and minimum sizes so questions and reports fit their host more reliably. |
| 2026-06-25 | Privacy & reliability | Removed prototype sign-in | Removed the local email-label/guest sign-in interface and related user-chip behavior, simplifying access and avoiding the appearance of a real student account system. |

## July: Native Tools, Voice, Window Controls, and Security

| Approximate date | Area | Timeline label | What changed |
| --- | --- | --- | --- |
| 2026-07-02 | Assessment | Career Compass rebuilt inside LionsPath | Replaced the primary embedded-assessment presentation with a native interface and a separate local scoring model, integrating question flow and reports more closely with the site. |
| 2026-07-02 | Evidence & planning | Compass findings flow into My Plan | Added a direct import of pathway lean, career clusters/options, strengths, next steps, and reflection questions into editable plan fields. |
| 2026-07-02 | Assessment | Downloadable Compass reports | Added direct PDF generation for assessment reports, extending the existing print/save workflow into a dedicated downloadable document. |
| 2026-07-02 | Evidence & planning | Downloadable My Plan | Added a direct plan PDF containing student-entered context, selected courses, next steps, questions, and planning reminders. |
| 2026-07-02 | Evidence & planning | Evidence becomes a readiness workspace | Replaced the basic checklist with grouped evidence, weighted scoring across the three Es, and live Exploring/Building/Strong readiness signals. |
| 2026-07-02 | Evidence & planning | Readiness matched to grade level | Added grade-sensitive evidence wording and expectations so younger students and upperclassmen received different planning prompts. |
| 2026-07-02 | Evidence & planning | Diploma-seal conversation indicators | Added visual seal-related signals, progress states, and explanatory guidance to help students prepare questions for official counselor review. |
| 2026-07-02 | Evidence & planning | Your next three moves | Generated recommended actions from missing evidence, with options to add a move to My Plan or copy an AI prompt to explore it. |
| 2026-07-02 | Evidence & planning | Shareable readiness snapshots | Added printable and downloadable Evidence reports that combined selected evidence, pathway signals, seal-related conversations, and suggested next moves. |
| 2026-07-02 | Design & media | Tool pages get dedicated identities | Added coordinated header artwork for Courses, AI Coach, Evidence, and My Plan, alongside a broader dark-theme and repeated-panel refinement. |
| 2026-07-08 | AI & voice | Talk to a 3E Coach introduced | Added Knowt voice coaching with its own launch artwork and entry point; the initially saved configuration launched externally while an inline panel was prepared. |
| 2026-07-08 | AI & voice | Voice-session lifecycle controls | Built the inline session bar, End Voice Session action, and page-exit cleanup to remove the embedded session when it was no longer in use. |
| 2026-07-08 | Design & media | Overview video stops when leaving | Added stopping/unloading when leaving Home, hiding the browser tab, scrolling the video out of view, or moving into another site action. |
| 2026-07-21 | AI & voice | One conversation across pages | Reworked multiple coach placements to share a persistent iframe so moving between pathway pages, AI Coach, and Plan Review would not itself restart the conversation. |
| 2026-07-21 | Structure | Expand and minimize embedded tools | Added Full Screen and Minimize controls for supported embedded experiences, using native fullscreen with an in-page expansion fallback. |
| 2026-07-21 | Structure | Coordinated embedded-window behavior | Added Escape handling, browser-fullscreen synchronization, one-expanded-window-at-a-time behavior, automatic controls for new iframes, and shared-coach positioning after window changes. |
| 2026-07-23 | AI & voice | Knowt iframe re-enabled | Revised the Knowt destination, enabled the inline experience in saved code, and retained an Open in New Tab fallback while investigating provider/domain restrictions. |
| 2026-07-23 | AI & voice | Voice microphone and media permissions | Normalized the Knowt hostname and added explicit microphone, camera, autoplay, speaker, clipboard, and fullscreen delegation, with eager iframe loading. This was compatibility work, not proof that all provider errors were resolved. |
| 2026-07-24 | Privacy & reliability | Application code reorganized | Moved main application behavior out of the large HTML file, removed obsolete assessment runtime files and a packaged site archive, and reduced unnecessary dependencies. |
| 2026-07-24 | Privacy & reliability | Saved-data validation and expiration | Validated restored plan/evidence records, bounded text and supported choices, and added a 180-day age limit for saved planning data. |
| 2026-07-24 | Privacy & reliability | Shared-device privacy controls | Added a prominent clear-all-data action and stronger first-name/initial, sensitive-information, and shared-device guidance around planning and external AI tools. |
| 2026-07-24 | Privacy & reliability | Restricted external content | Added a stricter Content Security Policy, explicit iframe sandbox/permission settings, and safer external-link and referrer handling. |
| 2026-07-24 | Privacy & reliability | Secure-hosting configuration | Prepared Apache HTTPS redirection, modern TLS settings, security headers, framing restrictions, and explicit browser-permission delegation for supported services. |
| 2026-07-24 | Privacy & reliability | Protected private project files | Added hosting rules to prevent public access to source-only folders, repository metadata, backups, configuration, certificates, keys, and other administrative files. |
| 2026-07-24 | Privacy & reliability | Deployment and operational guidance | Added security/deployment documentation, log-rotation configuration, and guidance separating public site assets from administrative files and external-service responsibilities. |

## August 3-13: Help, Counseling, and Cumulative Evidence

| Approximate date | Area | Timeline label | What changed |
| --- | --- | --- | --- |
| 2026-08-03 | Help & counseling | Goal-based Help center | Added a dedicated Help section with six routes covering choosing a direction, choosing courses, Enrollment, careers, military research, and preparing for a meeting. |
| 2026-08-03 | Help & counseling | Guided steps through the real site | Added a route bar, completion checkpoints, and contextual navigation that takes students into the actual tool or field needed for the next action. |
| 2026-08-03 | Help & counseling | Resume a guided route | Saved chosen goals and completed steps in the browser, with continuing, restarting, exiting, and integration with clear-all-data controls. |
| 2026-08-03 | Help & counseling | Visual walkthrough library | Added screenshot-based guides for nine major sections, explaining the actual workflows through captions and highlighted areas. |
| 2026-08-03 | Help & counseling | Accessible walkthrough player | Added play/pause, previous/next, replay, progress indicators, a guide dialog, focus handling, and reduced-motion behavior to the visual guides. |
| 2026-08-03 | Help & counseling | Student support and privacy FAQs | Added answers about local saving, Compass results, AI's role, privacy, verification, and leaving with a concrete action. |
| 2026-08-10 | Analytics | Site-visit reporting added | Connected GoatCounter and updated the site's security configuration and privacy explanations to support visit counting. |
| 2026-08-10 | Courses | Dual-enrollment claims corrected | Revised possible-DE language and related tags/evidence across eight CTE course entries, including turf, computer systems, automotive, nurse aide, culinary, and nutrition offerings. |
| 2026-08-11 | Help & counseling | Counseling connected throughout | Added counselor-finding, appointment-information, and contact links throughout relevant pages and reports to connect exploration with real school support. |
| 2026-08-11 | Pathways | Work-permit guidance added | Added a dedicated Employment section explaining the student, employer, and parent/guardian steps, with links to official resources. |
| 2026-08-11 | Structure | Expanded programs stop overlapping AI | Added coordinated accordion behavior and layout observation so opening program details repositions the shared AI workspace correctly and closes competing program cards. |
| 2026-08-13 | Evidence & planning | Evidence saved separately by grade | Reworked storage so students could switch among Grades 9-12 without overwriting the evidence selected for another grade. |
| 2026-08-13 | Evidence & planning | Current and cumulative readiness | Added side-by-side concepts for readiness in the selected grade and cumulative evidence across high school. |
| 2026-08-13 | Evidence & planning | Cumulative scoring corrected | Counted the same readiness signal once across grades, kept the grade-specific selections, and migrated older saved records into the new structure. |
| 2026-08-13 | Evidence & planning | Multi-grade readiness reports | Updated print and PDF snapshots to show evidence by grade together with cumulative pathway signals, seal conversations, and next actions. |

## August 20: Analytics and Theme Iterations

The analytics work below was saved together on August 20 after several development phases. Use this as an approximate milestone cluster, not a claim that it was all built in one day. Its production activation date is not established here.

| Approximate date | Area | Timeline label | What changed |
| --- | --- | --- | --- |
| 2026-08-20 | Analytics | Private analytics foundation | Built the Python/SQLite backend, request/event storage, and reporting architecture separate from student planning data. |
| 2026-08-20 | Analytics | Historical traffic importer | Added plain/compressed Apache-log parsing, resumable imports, duplicate prevention, rotated-file handling, and historical backfill. |
| 2026-08-20 | Analytics | Traffic classified into useful groups | Distinguished people-like page loads from assets, APIs, and known automation, while grouping devices, browsers, operating systems, referrers, and local time patterns. |
| 2026-08-20 | Analytics | Privacy-limited visitor estimates | Added rotating hashed visitor estimates and session calculations without retaining raw IP addresses or full user-agent strings in the analytics database. |
| 2026-08-20 | Analytics | Protected reporting and event APIs | Added authenticated reporting routes and a separate constrained event endpoint with checks on origins, payloads, allowed fields, and request volume. |
| 2026-08-20 | Analytics | Private administrator dashboard | Built a branded dashboard with date presets, custom periods, previous-period comparisons, audience metrics, trends, and content/feature tables. |
| 2026-08-20 | Analytics | Pathway and audience comparisons | Added reporting views for the three Es, traffic sources, devices, browsers, operating systems, hourly/weekday patterns, and a usage heatmap. |
| 2026-08-20 | Analytics | Aggregate exports and diagnostics | Added date-scoped CSV exports, import freshness, database coverage, technical health, and tools to compare imported records with original logs. |
| 2026-08-20 | Analytics | Scheduled analytics refresh | Prepared a five-minute import schedule, incremental recent-date updates, protected server routing, and service separation between reporting and log reading. |
| 2026-08-20 | Analytics | Analytics hardening and tests | Added layered access controls, spoofed-header defenses, safe export handling, restrictive runtime settings, a deployment preflight, and phase-based automated tests. |
| 2026-08-20 | Design & media | Alternative theme explored | **Superseded experiment:** saved a more restrained light/dark redesign spanning the site, Help, and the analytics dashboard before returning to a different design direction. |
| 2026-08-20 | Design & media | Alternative contrast and header pass | **Superseded experiment:** revised that design's contrast, section hierarchy, theme controls, and responsive header, documenting another substantial iteration. |
| 2026-08-20 | Design & media | Optional light mode introduced | Returned to the established dark site and added an optional light theme with a saved preference, forming the basis of the current theme approach. |

## August 21-28: Release Redesign, Course Enrichment, and Reporting Accuracy

| Approximate date | Area | Timeline label | What changed |
| --- | --- | --- | --- |
| 2026-08-21 | Design & media | LionsPath identity standardized | Brought the LionsPath name into site text, prompts, reports, Help, and browser metadata as part of the release redesign. |
| 2026-08-21 | Design & media | Local photography replaces key artwork | Added the graduation welcome photo, photographic pathway choices, and LCPS-related Employment and Enlistment imagery. |
| 2026-08-21 | Design & media | Light and dark experiences refined | Extended theme improvements through assessment answers/results, Evidence, Help, course dialogs, controls, and repeated content surfaces. |
| 2026-08-21 | Structure | Header and responsive navigation refined | Reworked the desktop navigation to stay on one line and moved the compact-menu breakpoint to better accommodate the expanded header. |
| 2026-08-21 | Structure | Direct links to site sections restored | Enabled URL fragments and hash-change handling so the visible section could be linked directly and restored from its URL. |
| 2026-08-21 | Courses | Search results ranked by relevance | Replaced broad matching with weighted search that favors course names and programs and reduces unrelated matches from incidental description words. |
| 2026-08-21 | Courses | Search understands student terminology | Added abbreviation/synonym handling, limited typo tolerance, plural/prefix matching, and better treatment of searches such as DE, IT, nursing, healthcare, and work-based learning. |
| 2026-08-21 | Courses | Course categories filter correctly | Refined credential and course-feature classification, added specific Honors/BRVGS/core/portfolio options, and connected Enrollment category buttons to the right filters. |
| 2026-08-21 | Courses | Course catalog cleaned up | Reduced the catalog from 219 to 214 entries by removing five entries and completed a remaining DE credential correction. |
| 2026-08-21 | Pathways | Enlistment page streamlined | Removed the separate Enlisted vs. Officer comparison block/table during the redesign while retaining entry-route, branch, career-family, and verification guidance. |
| 2026-08-24 | Design & media | Courses page visual refreshed | Replaced the Courses header with updated LionsPath artwork, continuing the page-by-page visual refresh. |
| 2026-08-26 | Design & media | Help Me Choose visual refreshed | Replaced the assessment-entry artwork with a new version, updating a prominent starting point in the student journey. |
| 2026-08-26 | Help & counseling | Counseling support consolidated | Replaced repeated page-ending counseling callouts with a consistent shared footer offering counselor lookup, appointment information, and contact links. |
| 2026-08-26 | Courses | Course-detail workspace rebuilt | Reorganized course details into clear facts, prerequisites, suggested sequence, credentials, planning actions, and career connections, with a responsive dialog/table layout. |
| 2026-08-26 | Courses | Prerequisites separated from sequence | Extracted prerequisite statements into a dedicated eligibility field, added targeted overrides, and provided a counselor-verification fallback when prerequisites were not listed. |
| 2026-08-26 | Courses | Six career examples for every course | Added occupation-based career mappings across the catalog, giving each current course six career examples drawn from 150 distinct occupation codes. |
| 2026-08-26 | Courses | Career outlook information added | Added labeled national median pay, typical entry education, projected growth, annual openings, occupation codes, and source/year explanations to career connections. |
| 2026-08-26 | AI & voice | SchoolAI account-access compatibility | Allowed the additional SchoolAI authentication origin, delegated identity-related permissions, and added direct new-tab links when embedded account sign-in could not complete. |
| 2026-08-27 | Design & media | Evidence page imagery refreshed | Updated the Evidence banner to represent more forms of student achievement, including academic, artistic, technical, service, athletic, and leadership experiences. |
| 2026-08-27 | AI & voice | Clearer SchoolAI sign-in route | Promoted the external sign-in action and explained the embedding limitation across coaching and plan-review workspaces. |
| 2026-08-28 | Analytics | Internal page and feature tracking | Wired fixed browser events for section views and major tools, assessment activity, coach launches, counseling links, and selected print/PDF actions. |
| 2026-08-28 | Analytics | Site loads separated from section views | Corrected headline counts so server page loads and internal navigation events were distinguished instead of combined into a misleading total. |
| 2026-08-28 | Analytics | Session-depth measurement corrected | Changed tracked views per session to count content views instead of treating every feature event as another page. |
| 2026-08-28 | Analytics | More accurate time comparisons | Added zero-activity dates to applicable trends and calculated weekday averages over all matching days in the selected range, including days without activity. |
| 2026-08-28 | Analytics | Charts become inspectable | Added tooltips and keyboard-focusable targets so users could inspect trend points and hourly activity values. |
| 2026-08-28 | Analytics | Missing tracking clearly identified | Distinguished unavailable pathway-event coverage from zero pathway interest and explained why older server logs cannot reconstruct internal tab choices. |
| 2026-08-28 | Analytics | High traffic gets useful context | Added notices for unusual repeat-load patterns and explained why site loads and shared-network visitor estimates are not counts of individual students. |
| 2026-08-28 | Analytics | Reconciliation and regression checks expanded | Updated historical-validation handling and added checks covering corrected calculations, event tracking, dashboard behavior, and end-to-end reporting. |

## Using This in a Timeline Graphic

Each row can become one event. Use the **Timeline label** as the short visible text and **What changed** for a caption, callout, or presentation note. The **Area** column can support color grouping.

Treat the original foundation as the opening state. Show subsequent changes chronologically, with clusters for days containing several improvements. Keep the two superseded theme experiments visually distinct if they are included. The number of rows measures documented change topics, not the number of commits, separate work sessions, or days worked.

A readable overview could use these chapter labels, with the individual rows filling out the detail:

| Approximate dates | Chapter label |
| --- | --- |
| By June 16, 2026 | Establishing the 3E planning foundation |
| June 17-18, 2026 | Building the student and family experience |
| June 24-25, 2026 | Introducing Career Compass and mobile access |
| July 2, 2026 | Connecting assessment, evidence, and plans |
| July 8-23, 2026 | Adding voice and improving embedded tools |
| July 24, 2026 | Strengthening privacy and hosting |
| August 3-13, 2026 | Guiding students and preserving progress |
| August 20-21, 2026 | Building analytics and revisiting the design |
| August 24-27, 2026 | Enriching course details and support |
| August 28, 2026 | Improving tracking and reporting accuracy |

## Revision References

These references support the approximate dates above and keep the timeline traceable without cluttering each graphic label.

| Date | Saved revisions |
| --- | --- |
| June 16, 2026 | `6d89c2c` |
| June 17, 2026 | `296d1b9` |
| June 18, 2026 | `ac4f537`, `2a63822`, `3ec3de3` |
| June 24, 2026 | `0521784` |
| June 25, 2026 | `d229931` |
| July 2, 2026 | `461b28a` |
| July 8, 2026 | `de521ad` |
| July 21, 2026 | `f6ed3bb` |
| July 23, 2026 | `853439c`, `a0b791b` |
| July 24, 2026 | `05cbb35` |
| August 3, 2026 | `c1d2bac` |
| August 10, 2026 | `5780e29` |
| August 11, 2026 | `35e1ada`, `8e6e047` |
| August 13, 2026 | `7323a1c` |
| August 20, 2026 | `02b47a3`, `199577e`; superseded experiments: `e21384d`, `5645297` |
| August 21, 2026 | `eba3650` |
| August 24, 2026 | `2b03ec5` |
| August 26, 2026 | `da507ca`, `9131f8e`, `58861ba` |
| August 27, 2026 | `4380c63` |
| August 28, 2026 | `becfc42` |

Companion document: [Thematic enhancement history](PROJECT-ENHANCEMENT-HISTORY.md).

No site code was changed to prepare this timeline. Current external-service behavior, production analytics activation, and live content accuracy were not re-tested for this historical inventory.
