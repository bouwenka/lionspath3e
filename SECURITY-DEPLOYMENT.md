# LionPath Security Deployment

The application hardening is included in the site files. The HTTPS, TLS,
response-header, file-access, log-rotation, and private analytics controls
require server installation by an administrator.

## Apache files

- Virtual host: `deployment/apache/lionspath.conf`
- Log rotation: `deployment/logrotate/lionspath`
- Private analytics runtime: `deployment/analytics/`
- Analytics systemd units: `deployment/systemd/`

## Before activation

1. Confirm that the production document root is `/var/www/lionspath`.
2. Confirm the certificate, private-key, and chain paths in `lionspath.conf`.
3. Confirm that `lionspath.lcps.k12.va.us` is the only supported public hostname.
4. Make sure every site covered by the district certificate is already HTTPS-ready before adding `includeSubDomains` or `preload` to HSTS. Those options are intentionally not enabled in this configuration.
5. Keep the public document root limited to `index.html` and `assets/`. Prefer checking out Git in a separate administration directory and syncing only those public files into `/var/www/lionspath`; do not place `.git`, backups, deployment files, certificates, or reports in the web root.

## Activation status

The Apache template now includes the private analytics proxy and authentication
routes. Do not install it with the older static-only command sequence: Apache
would reference a password file and Unix socket that do not exist yet. Phase 8
will provide the exact ordered production procedure after the read-only
preflight confirms the server's actual packages, users, paths, modules, and log
permissions.

The eventual Apache module set includes:

```bash
sudo a2enmod ssl headers alias socache_shmcb proxy proxy_http auth_basic authn_file authz_user
```

This is documentation only, not the complete Phase 8 deployment procedure.
`apache2ctl configtest` must report `Syntax OK` before any Apache reload.

## Analytics access controls

The private dashboard uses multiple independent boundaries:

1. Apache Basic Authentication protects `/admin/analytics` and all report and
   export APIs using a password file outside the web root.
2. Apache removes browser-supplied trust, forwarding, and authorization headers
   before proxying through a `0660` Unix socket that has no public TCP listener.
3. The WSGI application requires Apache's proxy marker on every request and the
   administrator marker on every private route. A marker presented without the
   trusted proxy marker is rejected.
4. Dashboard responses are non-cacheable, non-indexable, same-origin resources
   and cannot be framed. The dashboard loads no third-party scripts or fonts.
5. The long-running service has no network access or Linux capabilities. Only
   the short-lived importer receives read-only Apache-log access.

Basic Authentication is safe here only because the route exists exclusively in
the HTTPS virtual host. Phase 8 will create individual administrator credentials
with strong password hashes and verify the entire boundary before activation.

## Verification

```bash
curl -I http://lionspath.lcps.k12.va.us/
curl -I https://lionspath.lcps.k12.va.us/
```

The HTTP request should return a permanent redirect to HTTPS. The HTTPS response should include HSTS, CSP, Referrer-Policy, Permissions-Policy, X-Content-Type-Options, and X-Frame-Options.

After deployment, verify the public endpoint with SSL Labs and SecurityHeaders.com. Test the Google Drive video, shared AI Coach, voice coach, GoatCounter visit reporting, clipboard actions, and fullscreen controls from a district-managed device before broad release.

## Data handling

LionPath has no student login or backend student-record database. Plan and
readiness information is stored in the current browser's local storage and is
only sent elsewhere when a user deliberately copies or enters it into an
external service. The Help page also stores the selected guide and completed
step numbers locally so students can return to their place; the existing
clear-all-data control removes that guide progress as well.

The private analytics backend stores classified web requests and fixed,
allowlisted interaction events. It does not retain raw IP addresses, full user
agents, assessment answers, plan contents, readiness entries, AI conversations,
voice conversations, names, emails, or arbitrary text. Dashboard access is
separate from the public site and requires server-managed credentials.
GoatCounter remains enabled during production reconciliation and will be removed
only after the private counts are verified.

Analytics configuration, secret, password, and database files use the ownership
and modes documented in `deployment/analytics/README.md`. The read-only
preflight reports any installed file that is broader than the expected mode and
verifies that the service account was not permanently added to the Apache log
group.

## District privacy review

Technical hardening does not by itself establish FERPA, COPPA, or state-law compliance. Before student release, the district privacy or legal owner should document:

1. Approval of SchoolAI, Knowt, Google Drive, and GoatCounter for the intended student use.
2. What each provider collects, including prompts, account identifiers, device information, and voice recordings.
3. Whether information is used for advertising, profiling, model training, or any purpose outside the district-authorized educational service.
4. Provider retention periods and the district's ability to access, correct, export, and delete student information.
5. Contract terms covering district control, permitted use, redisclosure, subprocessors, security controls, incident notification, return or destruction, and termination.
6. The authorization or parental-consent process for students under 13, if they can use a service that collects personal information.
7. A parent and student notice identifying the external services, the purpose of each service, what should not be entered, and the contact for privacy requests.
8. A response procedure for suspected disclosure, lost devices, shared-browser data, or vendor incidents.

The analytics event endpoint intentionally accepts only a small fixed event
allowlist and does not accept student-provided text. Apache access and error logs
continue to provide operational audit records and are rotated by
`deployment/logrotate/lionspath`.

## Intentional differences from the audit sample

- Marked and DOMPurify were removed because LionPath does not render user-authored Markdown. This eliminates the CDN and Markdown attack surface instead of adding SRI hashes.
- `X-XSS-Protection` is set to `0`; modern browsers rely on CSP, and the legacy filtering mode can introduce security problems.
- `Expect-CT` is omitted because it is obsolete.
- HSTS `includeSubDomains` and `preload` are not enabled until the district confirms every covered host is HTTPS-ready.
- `.htaccess` is disabled with `AllowOverride None`; adding backup `.htaccess` rules would have no effect and would conflict with the hardened configuration.
- `mod_status` is not required and should not be enabled for this static site unless IT separately restricts access to it.

## Embedding check

The supplied policy prevents other websites from framing LionPath by using `X-Frame-Options: SAMEORIGIN` and CSP `frame-ancestors 'self'`. This does not block LionPath's child Google Drive, SchoolAI, or Knowt frames. SchoolAI authentication may navigate its embedded frame from `student.schoolai.com` to `rosterstream.schoolai.com`, so both exact origins are included in `frame-src` and the SchoolAI frame delegates Google's `identity-credentials-get` permission. SchoolAI's provider links then continue to Google, Microsoft, Clever, or Classlink in the same child frame; those account authorization pages may not be embedded. Students who need an account sign-in must use the direct SchoolAI new-tab link instead. If the entire LionPath site must be embedded in a district or Wix page, IT must replace `frame-ancestors 'self'` with an allowlist containing the exact trusted parent origin and remove `X-Frame-Options`, then retest clickjacking protection and all embedded services.
