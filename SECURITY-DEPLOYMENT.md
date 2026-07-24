# LionPath Security Deployment

The application hardening is included in the site files. The HTTPS, TLS, response-header, file-access, and log-rotation controls require server installation by an administrator.

## Apache files

- Virtual host: `deployment/apache/lionspath.conf`
- Log rotation: `deployment/logrotate/lionspath`

## Before activation

1. Confirm that the production document root is `/var/www/lionspath`.
2. Confirm the certificate, private-key, and chain paths in `lionspath.conf`.
3. Confirm that `lionspath.lcps.k12.va.us` is the only supported public hostname.
4. Make sure every site covered by the district certificate is already HTTPS-ready before adding `includeSubDomains` or `preload` to HSTS. Those options are intentionally not enabled in this configuration.
5. Keep the public document root limited to `index.html` and `assets/`. Prefer checking out Git in a separate administration directory and syncing only those public files into `/var/www/lionspath`; do not place `.git`, backups, deployment files, certificates, or reports in the web root.

## Installation

```bash
sudo a2enmod ssl headers alias socache_shmcb
sudo cp deployment/apache/lionspath.conf /etc/apache2/sites-available/lionspath.conf
sudo cp deployment/logrotate/lionspath /etc/logrotate.d/lionspath
sudo a2ensite lionspath.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

`apache2ctl configtest` must report `Syntax OK` before Apache is reloaded.

## Verification

```bash
curl -I http://lionspath.lcps.k12.va.us/
curl -I https://lionspath.lcps.k12.va.us/
```

The HTTP request should return a permanent redirect to HTTPS. The HTTPS response should include HSTS, CSP, Referrer-Policy, Permissions-Policy, X-Content-Type-Options, and X-Frame-Options.

After deployment, verify the public endpoint with SSL Labs and SecurityHeaders.com. Test the Google Drive video, shared AI Coach, voice coach, clipboard actions, and fullscreen controls from a district-managed device before broad release.

## Data handling

LionPath has no application login or backend student database. Plan and readiness information is stored in the current browser's local storage and is only sent elsewhere when a user deliberately copies or enters it into an external service. The application validates locally stored records, limits free-text lengths, expires saved data after 180 days without an update, removes unused third-party scripts, and provides a visible clear-all-data control.

## District privacy review

Technical hardening does not by itself establish FERPA, COPPA, or state-law compliance. Before student release, the district privacy or legal owner should document:

1. Approval of SchoolAI, Knowt, and Google Drive for the intended student use.
2. What each provider collects, including prompts, account identifiers, device information, and voice recordings.
3. Whether information is used for advertising, profiling, model training, or any purpose outside the district-authorized educational service.
4. Provider retention periods and the district's ability to access, correct, export, and delete student information.
5. Contract terms covering district control, permitted use, redisclosure, subprocessors, security controls, incident notification, return or destruction, and termination.
6. The authorization or parental-consent process for students under 13, if they can use a service that collects personal information.
7. A parent and student notice identifying the external services, the purpose of each service, what should not be entered, and the contact for privacy requests.
8. A response procedure for suspected disclosure, lost devices, shared-browser data, or vendor incidents.

The site intentionally does not record an application-level activity log because it has no backend and adding one would create a new store of student activity. Apache access and error logs provide operational audit records and are rotated by `deployment/logrotate/lionspath`.

## Intentional differences from the audit sample

- Marked and DOMPurify were removed because LionPath does not render user-authored Markdown. This eliminates the CDN and Markdown attack surface instead of adding SRI hashes.
- `X-XSS-Protection` is set to `0`; modern browsers rely on CSP, and the legacy filtering mode can introduce security problems.
- `Expect-CT` is omitted because it is obsolete.
- HSTS `includeSubDomains` and `preload` are not enabled until the district confirms every covered host is HTTPS-ready.
- `.htaccess` is disabled with `AllowOverride None`; adding backup `.htaccess` rules would have no effect and would conflict with the hardened configuration.
- `mod_status` is not required and should not be enabled for this static site unless IT separately restricts access to it.

## Embedding check

The supplied policy prevents other websites from framing LionPath by using `X-Frame-Options: SAMEORIGIN` and CSP `frame-ancestors 'self'`. This does not block LionPath's child Google Drive, SchoolAI, or Knowt frames. If the entire LionPath site must be embedded in a district or Wix page, IT must replace `frame-ancestors 'self'` with an allowlist containing the exact trusted parent origin and remove `X-Frame-Options`, then retest clickjacking protection and all embedded services.
