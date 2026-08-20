#!/usr/bin/env bash

set -u

failures=0

pass() {
    printf 'PASS  %s\n' "$1"
}

fail() {
    printf 'FAIL  %s\n' "$1"
    failures=$((failures + 1))
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        pass "command available: $1"
    else
        fail "missing command: $1"
    fi
}

check_metadata_if_present() {
    path="$1"
    expected_mode="$2"
    expected_owner="$3"
    expected_group="$4"
    label="$5"

    if [ ! -e "$path" ]; then
        printf 'INFO  not installed yet: %s\n' "$label"
        return
    fi

    actual_mode="$(stat -c '%a' "$path" 2>/dev/null || printf '?')"
    actual_owner="$(stat -c '%U' "$path" 2>/dev/null || printf '?')"
    actual_group="$(stat -c '%G' "$path" 2>/dev/null || printf '?')"
    if [ "$actual_mode" = "$expected_mode" ] && \
       [ "$actual_owner" = "$expected_owner" ] && \
       [ "$actual_group" = "$expected_group" ]; then
        pass "$label permissions are $expected_mode $expected_owner:$expected_group"
    else
        fail "$label is $actual_mode $actual_owner:$actual_group; expected $expected_mode $expected_owner:$expected_group"
    fi
}

printf '%s\n' 'LionsPath analytics read-only preflight'

for command_name in python3 apache2ctl htpasswd openssl systemctl getent id stat; do
    check_command "$command_name"
done

if getent passwd lionspath-analytics >/dev/null 2>&1; then
    account_groups=" $(id -nG lionspath-analytics 2>/dev/null || true) "
    case "$account_groups" in
        *" adm "*)
            fail "lionspath-analytics must not be a permanent member of adm"
            ;;
        *)
            pass "lionspath-analytics receives adm only from the importer unit"
            ;;
    esac
else
    printf '%s\n' 'INFO  service account not installed yet: lionspath-analytics'
fi

check_metadata_if_present /etc/lionspath 751 root lionspath-analytics "analytics configuration directory"
check_metadata_if_present /etc/lionspath/analytics.env 640 root lionspath-analytics "analytics environment file"
check_metadata_if_present /etc/lionspath/analytics.secret 600 lionspath-analytics lionspath-analytics "analytics HMAC secret"
check_metadata_if_present /etc/lionspath/analytics.htpasswd 640 root www-data "analytics password file"
check_metadata_if_present /var/lib/lionspath 700 lionspath-analytics lionspath-analytics "analytics state directory"
check_metadata_if_present /var/lib/lionspath/analytics.db 600 lionspath-analytics lionspath-analytics "analytics database"

if command -v python3 >/dev/null 2>&1; then
    if python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
        pass "Python is 3.10 or newer"
    else
        fail "Python 3.10 or newer is required by the pinned Gunicorn release"
    fi
fi

if command -v apache2ctl >/dev/null 2>&1; then
    module_output="$(apache2ctl -M 2>/dev/null || true)"
    for module_name in ssl_module headers_module proxy_module proxy_http_module auth_basic_module authn_file_module authz_user_module socache_shmcb_module; do
        if printf '%s\n' "$module_output" | grep -q "$module_name"; then
            pass "Apache module enabled: $module_name"
        else
            fail "Apache module not enabled: $module_name"
        fi
    done
fi

for group_name in www-data adm; do
    if getent group "$group_name" >/dev/null 2>&1; then
        pass "group exists: $group_name"
    else
        fail "missing group: $group_name"
    fi
done

if [ -f /var/www/lionspath/index.html ]; then
    pass "current LionsPath document root found"
else
    fail "expected /var/www/lionspath/index.html"
fi

if compgen -G '/var/log/apache2/lionspath_ssl_access.log*' >/dev/null; then
    pass "LionsPath Apache access logs found"
else
    fail "no LionsPath HTTPS access logs found"
fi

printf '\nPreflight complete: %d failure(s). No server changes were made.\n' "$failures"
exit "$failures"
