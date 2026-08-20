# LionsPath Private Analytics

## Status

Phases 1 through 7 are implemented locally. The project architecture, SQLite schema,
privacy helpers, Apache log parser, classifier, idempotent importer, historical
backfill, aggregate rollups, reconciliation tooling, protected reporting API,
privacy-limited event endpoint, branded private dashboard, aggregate CSV
exports, scheduled refresh command, hardened systemd units, Apache proxy and
authentication template, deployment preflight, and automated test suite are in
place. No analytics service is active on the production server yet, and
GoatCounter remains enabled until the new system is reconciled against the real
production logs.

## Phase 2 implementation

The backend foundation is located in `analytics/`:

- `schema.sql` defines request, event, importer-diagnostic, and rollup tables.
- `privacy.py` creates daily/monthly HMAC visitor estimates and stable rotated-log
  fingerprints without retaining raw IP addresses.
- `parser.py` parses Apache Combined Log Format and converts timestamps to
  `America/New_York` using DST-aware time-zone data.
- `classify.py` removes query strings and classifies assets, APIs, bots,
  referrers, browsers, operating systems, and device types.
- `import_logs.py` imports plain or gzip logs, resumes active files by inode and
  byte offset, defers partial live lines, skips malformed lines, and uses SQLite
  uniqueness to make repeated and post-rotation imports safe.
- `tests/test_phase2.py` tests parsing, privacy, classification, duplicate
  prevention, gzip support, and simulated log rotation.

The local verification command is:

```bash
python3 -m unittest discover -s analytics/tests -v
```

The importer command is present for testing, but production backfill should wait
for the Phase 6 service account, permissions, secret, and deployment steps:

```bash
python3 -m analytics.import_logs --help
```

## Phase 3 implementation

Historical processing adds:

- `backfill.py`, which discovers every available plain and gzip access log,
  imports them idempotently, and refreshes persistent daily, hourly, and page
  aggregates.
- `rollups.py`, which rebuilds a complete or selected date range without
  duplicating aggregate rows.
- `validate.py`, which scans one raw log and reconciles every valid request with
  its SQLite fingerprint. Output contains counts only and never prints raw log
  lines, IP addresses, or user agents.
- `tests/test_phase3.py`, which covers multi-day aggregation, repeated rollup
  rebuilding, full backfill discovery, gzip reconciliation, missing-row
  detection, expected-count mismatches, and dry-run behavior.

The production backfill command will be:

```bash
python3 -m analytics.backfill \
  --db /var/lib/lionspath/analytics.db \
  --log-pattern '/var/log/apache2/lionspath_ssl_access.log*' \
  --secret-file /etc/lionspath/analytics.secret
```

The August 14 reconciliation command will be:

```bash
python3 -m analytics.validate \
  --db /var/lib/lionspath/analytics.db \
  --file /var/log/apache2/lionspath_ssl_access.log.3.gz \
  --expected-total 27519 \
  --expected-home 1342
```

Do not run these commands until the service account, secret, database directory,
and read-only log permissions are installed in Phase 6. The production
reconciliation itself remains pending because server logs are not copied into
the repository or local development workspace.

## Phase 4 implementation

The reporting and event layer adds:

- `app.py`, a dependency-free WSGI application with a public, same-origin event
  endpoint and separate protected reporting routes.
- `queries.py`, which produces date-range summaries, previous-period
  comparisons, 30-minute sessions, trends, page and feature usage, 3E pathway
  comparisons, technology/referrer breakdowns, time patterns, errors, and
  importer diagnostics.
- Privacy-safe CSV exports for daily totals, pages, features, devices, and
  hourly activity. Exports never contain visitor hashes, IP addresses, user
  agents, or student-provided content.
- `tests/test_phase4.py`, which verifies the authorization boundary, event
  allowlist, origin/content-type/size validation, rate limiting, proxy handling,
  report calculations, exports, and failure behavior.

The implemented routes are:

```text
POST /api/analytics/event
GET  /admin/analytics/api/health
GET  /admin/analytics/api/report
GET  /admin/analytics/api/pages
GET  /admin/analytics/api/features
GET  /admin/analytics/api/export
```

The WSGI application does not implement passwords itself. Reporting routes
require an internal `X-LionsPath-Admin: 1` marker. The Phase 6 Apache template
strips any client-supplied copy of that header, requires Basic Authentication,
injects the trusted marker, and proxies the request through a private Unix
socket. The API must not be exposed directly to a public interface.

The student-facing application has not been instrumented yet. Adding browser
event calls before the backend is deployed would create failed requests on the
current static site, so that wiring is intentionally deferred until the backend
and Apache route are active.

## Phase 5 implementation

The private dashboard is available from the WSGI application at:

```text
/admin/analytics/
```

It adds:

- `templates/dashboard.html`, a compact administrative workspace with date
  presets, custom dates, summary metrics, content and feature tables, 3E
  pathway comparisons, technology/source tabs, time patterns, technical health,
  importer diagnostics, and CSV controls.
- `static/dashboard.css`, a responsive LionPath dark-green-and-gold interface
  with high-contrast type, keyboard focus states, reduced-motion support,
  tablet/mobile layouts, and horizontally scrollable data surfaces where needed.
- `static/dashboard.js`, which renders local SVG charts and semantic HTML from
  the reporting API. It uses text-safe DOM methods rather than inserting API
  values as HTML.
- Protected WSGI routes for the dashboard HTML, CSS, JavaScript, and brand mark.
  The interface, its data APIs, and all of its assets require the administrator
  marker that Apache will supply after authentication in Phase 6.
- A strict dashboard Content Security Policy, `noindex` metadata, no iframes,
  and no third-party scripts, fonts, chart packages, or CDNs.
- `tests/test_phase5.py`, which checks dashboard authorization, redirects,
  method restrictions, required workspaces, security headers, local-only assets,
  API wiring, and responsive/reduced-motion rules.

CSV downloads use the Phase 4 aggregate export endpoints and inherit the
dashboard's selected dates. They contain no raw visitor identifiers.

## Phase 6 implementation

The local production-runtime package adds:

- `refresh.py`, which imports only the active and immediately rotated Apache
  logs, resumes from importer checkpoints, and rebuilds the latest three local
  dates so late log entries are included without reprocessing all history.
- `deployment/systemd/lionspath-analytics.socket`, which creates an
  Apache-accessible Unix socket without opening a network port.
- Separate hardened systemd units for the WSGI dashboard and the five-minute
  incremental importer. Only the importer receives read-only access to the
  Apache log group.
- Apache proxy rules that remove client-supplied trust headers, protect the
  dashboard and exports with Basic Authentication, permit only the event
  endpoint's intended methods, and proxy both routes through the Unix socket.
- `deployment/analytics/analytics.env.example`, which contains paths and
  settings but no passwords or HMAC secret.
- `deployment/analytics/preflight.sh`, a read-only prerequisite check reserved
  for the Phase 8 server deployment.
- `tests/test_phase6.py`, which covers recent-file selection, repeated-import
  idempotence, rollup refreshes, proxy trust handling, Apache protection,
  service hardening, timer cadence, and secret-free templates.

Phase 6 changes only repository files. Nothing has been copied, enabled, or
restarted on the production server.

## Phase 7 implementation

The private dashboard and public event route now use layered controls:

- The WSGI application rejects every request that lacks Apache's trusted proxy
  marker. Dashboard access additionally requires the separate administrator
  marker that Apache injects only after successful Basic Authentication.
- Apache removes client-supplied trust markers, `X-Forwarded-For`, `Forwarded`,
  and `Authorization` before proxying. It then adds a fresh proxy marker and a
  server-derived forwarding address; administrator routes receive the admin
  marker only after authentication.
- Forwarded client addresses must parse as IPv4 or IPv6 before they contribute
  to privacy-preserving visitor hashes or rate limits.
- Dashboard queries have route-specific field allowlists, duplicate-field and
  length limits, and bounded table sizes.
- CSV exports neutralize formula-leading text before it reaches spreadsheet
  software. Dashboard JavaScript continues to render API values with safe text
  methods rather than HTML insertion.
- Secrets can be loaded only from a regular, non-symlink file. The production
  environment template contains file paths but no secret or password.
- The database is forced to owner-only mode on POSIX systems, and both services
  use `UMask=0077`, no network namespace, no capabilities, a read-only operating
  system view, and narrowly scoped writable paths.
- The service account is not a permanent member of `adm`; only the scheduled
  importer receives that supplemental group. The read-only preflight verifies
  this separation and checks installed file ownership and modes.
- `tests/test_phase7.py` adds adversarial checks for marker spoofing, forwarded
  address forgery, query ambiguity, CSV formulas, unsafe origins, secret
  handling, response headers, Apache rules, and systemd isolation.

Phase 7 does not create credentials or activate services. Those server actions
remain in the ordered Phase 8 deployment procedure.

## Existing application

LionsPath is currently a static single-page application:

- `index.html` contains the page structure and most styling.
- `assets/lionpath-app.js` contains navigation and application behavior.
- `assets/lionpath-training.js` and `assets/lionpath-training.css` provide Help.
- Student plan, assessment, Evidence, and Help progress stays in browser local
  storage.
- The public application has no student login or student database. The private
  analytics backend now exists in the repository but is not deployed yet.
- Apache serves `/var/www/lionspath` directly and writes Combined Log Format
  requests to `/var/log/apache2/lionspath_ssl_access.log`.
- Apache logs rotate daily as `root:adm`, mode `0640`.
- The current deployment already applies HTTPS and restrictive security headers.

The analytics system must remain optional. Importer or dashboard failure must
never affect the student-facing application.

## Important SPA limitation

The visible pages use URL fragments such as `#enrollment`, `#employment`, and
`#enlistment`. URL fragments are handled by the browser and are never included
in an Apache request. Apache logs can accurately report site loads, server
requests, status codes, referrers, devices, and time patterns, but cannot tell
which LionPath tab a student opened after the initial load.

The implementation will therefore use two first-party sources:

1. Apache logs for authoritative site visits, requests, referrers, devices,
   errors, and bot traffic.
2. A small same-origin event endpoint for allowlisted aggregate events such as
   `section_view`, `career_assessment_start`, `plan_open`, and `ai_coach_open`.

Events will never include assessment answers, plan contents, Evidence choices,
AI conversations, names, emails, account identifiers, or arbitrary text.

## Selected architecture

```text
Apache access logs                  LionPath allowlisted events
        |                                      |
        +---------- Python importer/API -------+
                           |
             /var/lib/lionspath/analytics.db
                           |
                authenticated JSON queries
                           |
        https://lionspath.lcps.k12.va.us/admin/analytics/
```

### Backend

A small standard-library Python WSGI application served by Gunicorn accepts
traffic only through a root-managed Unix socket. Apache reverse proxies the
analytics routes. This keeps the existing static application unchanged,
minimizes dependencies, and avoids exposing a new service port.

Planned repository structure:

```text
analytics/
  app.py
  classify.py
  config.py
  database.py
  import_logs.py
  privacy.py
  queries.py
  refresh.py
  schema.sql
  requirements.txt
  static/
  templates/
  tests/
deployment/
  apache/lionspath.conf
  analytics/analytics.env.example
  analytics/preflight.sh
  systemd/lionspath-analytics.socket
  systemd/lionspath-analytics.service
  systemd/lionspath-analytics-import.service
  systemd/lionspath-analytics-import.timer
docs/ANALYTICS.md
```

### Private URL and authentication

The dashboard will not appear in LionPath navigation. Its planned URL is:

```text
https://lionspath.lcps.k12.va.us/admin/analytics/
```

The URL alone is not an access control. Apache Basic Authentication will protect
the dashboard and every reporting/export API route. Password hashes will live
outside the repository and web root in an administrator-owned file such as:

```text
/etc/lionspath/analytics.htpasswd
```

Administrators should receive individual credentials rather than sharing one
password. The event-ingest route must remain available to the public site, but
will accept only POST requests, same-origin browser requests, a fixed event
allowlist, small payloads, and no free-form student data.

### Runtime identity and permissions

A dedicated unprivileged account, `lionspath-analytics`, will run the importer
and local dashboard service. It will receive read-only access to Apache logs
through the existing `adm` group (or a narrowly scoped ACL if district policy
prefers it). Logs will not be made world-readable.

The service account will own:

```text
/var/lib/lionspath/analytics.db
/var/lib/lionspath/import-state/
```

Application code remains read-only to the service account in production.

## Privacy model

- Raw IP addresses are used only in memory while parsing a request and are never
  written to SQLite.
- Visitor identifiers use HMAC-SHA256 with a secret stored outside the repository.
- A daily visitor hash supports daily estimates and sessions without long-term
  student tracking.
- A monthly rotating visitor hash may support less inflated month-level estimates;
  ranges crossing rotation boundaries will be clearly labeled as estimates.
- User agents are classified into aggregate browser, operating-system, and device
  categories. The full value is not required for dashboard display.
- Referrers are reduced to a source category/domain. Full referrer query strings
  are not retained.
- Sessions use a 30-minute inactivity window and do not attempt to identify a
  person.
- Dashboard language will say `Estimated Visitors`, never `Students`.

## Database design

The initial SQLite database will contain:

- `requests`: classified Apache requests with rotating visitor hashes and no raw IP.
- `events`: fixed, privacy-limited LionPath interaction events.
- `import_files`: inode/path/offset checkpoints and importer diagnostics.
- `import_runs`: start, finish, source, row, warning, and failure information.
- Daily/hourly/page/feature rollups for long-range queries and future retention.

Indexes will cover local timestamp, local date, normalized path, request class,
visitor hash, event name, and status code.

### Duplicate prevention and rotation

Automatic imports will track device/inode and byte offset for the active log.
Historical and rotated files will also use an entry fingerprint. The fingerprint
will combine the canonical log line with its occurrence number among identical
lines in that file. This preserves legitimate duplicate-looking requests while
remaining stable when `.1` is renamed or gzip-compressed.

SQLite will enforce fingerprint uniqueness, making repeated backfills safe.

## Classification and normalization

Each request will be classified as one of:

- human page load
- static asset
- analytics event/API
- bot or automated traffic
- other server request

Paths will be normalized without storing sensitive query values. Static file
extensions and `/assets/` requests will not count as page views. Obvious crawlers,
scanners, command-line tools, and uptime probes will be reported separately.

Times will be parsed from their recorded UTC offset and converted with Python's
`zoneinfo` support for `America/New_York`, including EST/EDT transitions.

## Dashboard scope

The private dashboard will provide:

- Today, Yesterday, 7 Days, 30 Days, month, year, all-time, and custom ranges.
- Estimated Visitors, page views, sessions, pages/session, session duration, and
  total requests.
- Previous-period comparisons.
- Hourly/daily/weekly/monthly trends.
- Most visited pages and LionPath feature usage.
- Enrollment, Employment, and Enlistment comparison from first-party events.
- Referrer, device, browser, OS, day-of-week, hourly, and heatmap views.
- Human versus bot traffic and a secondary status/error section.
- CSV exports containing no raw identifiers.
- Import freshness, processed rows, log source, database range, and size.

Charts will use local HTML/CSS/JavaScript assets so the private page does not
need a public analytics or charting CDN.

## Phased delivery

1. Project inspection and architecture (complete).
2. SQLite schema, privacy helpers, parser/importer, and automated tests (complete).
3. Historical backfill and reconciliation tooling (implemented; production
   August 14 run pending deployment access).
4. Protected reporting API and narrowly scoped event endpoint (complete; Apache
   authentication integration follows in Phase 6).
5. Branded responsive dashboard and CSV exports (complete).
6. systemd socket/service/timer, scheduled refresh, Apache authentication and
   Unix-socket reverse proxy, and read-only deployment preflight (complete
   locally; production activation deferred to Phase 8).
7. Access-control, request-validation, permissions, and privacy hardening
   (complete locally; production verification follows in Phase 8).
8. End-to-end tests and exact deployment/troubleshooting instructions.
9. Remove GoatCounter only after production results are verified.

## Server facts still requiring production verification

The following cannot be safely inferred from the repository and will be checked
during deployment rather than guessed:

- Ubuntu and Python versions.
- Whether `proxy`, `proxy_http`, `auth_basic`, and `headers` Apache modules are enabled.
- The current `/etc/logrotate.d/apache2` rules in addition to the repository rule.
- The deployment checkout/sync location used before `/var/www/lionspath`.
- Whether district policy prefers `adm` membership or a read-only ACL.
- The actual August 14 log file needed for reconciliation.
