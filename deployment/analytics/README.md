# LionsPath Analytics Runtime

This directory contains the non-secret deployment template and a read-only
preflight check for Phase 6. The production service is not activated merely by
copying these files to the server.

## Production layout

The analytics Python package must be installed outside the public document root:

```text
/opt/lionspath-analytics/current/analytics/
/opt/lionspath-analytics/venv/
```

Only `index.html` and `assets/` belong in `/var/www/lionspath`. The Apache rules
also return 404 for repository-only `/analytics`, `/deployment`, and `/docs`
paths in case a complete checkout is accidentally placed under the document
root.

Runtime data and secrets use separate locations:

```text
/var/lib/lionspath/analytics.db
/etc/lionspath/analytics.env
/etc/lionspath/analytics.secret
/etc/lionspath/analytics.htpasswd
/run/lionspath-analytics.sock
```

The database and HMAC secret are owned by the unprivileged
`lionspath-analytics` account. The password file is read by Apache. None of
these files belongs in Git or the web root.

## Required ownership and modes

Phase 8 will create these paths in the correct order. These are the security
targets that the preflight verifies when a path already exists:

```text
/etc/lionspath                       0751 root:lionspath-analytics
/etc/lionspath/analytics.env         0640 root:lionspath-analytics
/etc/lionspath/analytics.secret      0600 lionspath-analytics:lionspath-analytics
/etc/lionspath/analytics.htpasswd    0640 root:www-data
/var/lib/lionspath                   0700 lionspath-analytics:lionspath-analytics
/var/lib/lionspath/analytics.db      0600 lionspath-analytics:lionspath-analytics
```

The analytics account must not be added permanently to `adm`. Only the
oneshot importer receives `adm` through its systemd unit, so the long-running
dashboard process cannot read Apache logs. Passwords and the HMAC secret are
never placed in `analytics.env`.

## Runtime flow

1. Apache accepts HTTPS traffic and strips any client-supplied analytics trust
   headers, forwarding headers, and Basic credentials before proxying.
2. `/admin/analytics` requires an Apache Basic Auth user from the external
   password file.
3. Apache proxies the dashboard and event endpoint through the root-managed
   Unix socket.
4. Gunicorn runs the standard-library WSGI application as the unprivileged
   analytics account with no network namespace access and no Linux capabilities.
5. A systemd timer imports the active and immediately rotated Apache logs every
   five minutes and rebuilds only the latest three local dates.

The public LionsPath pages remain static and continue working if the analytics
socket or importer is unavailable.

## Files

- `analytics.env.example`: non-secret environment template.
- `preflight.sh`: read-only prerequisite check for the Ubuntu server.
- `../systemd/lionspath-analytics.socket`: Apache-accessible Unix socket.
- `../systemd/lionspath-analytics.service`: hardened Gunicorn service.
- `../systemd/lionspath-analytics-import.service`: hardened incremental import.
- `../systemd/lionspath-analytics-import.timer`: five-minute refresh schedule.
- `../apache/lionspath.conf`: existing site configuration plus analytics routes.

Run the preflight only when preparing for Phase 8 deployment:

```bash
sudo bash deployment/analytics/preflight.sh
```

It reports prerequisites and makes no server changes.

The application also requires the trusted proxy marker before it accepts either
dashboard or event requests. The administrator marker is accepted only together
with that proxy marker. This is defense in depth behind Apache authentication
and the `0660` Unix socket; neither marker is a substitute for authentication.
