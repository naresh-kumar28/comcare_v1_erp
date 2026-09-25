# ComCare — Dependency Audit

Date: 2026-09-19

## Baseline

`requirements.txt` now (ASCII/UTF-8; previously UTF-16 which broke `pip`):

```
asgiref==3.12.1
certifi==2026.7.22
charset-normalizer==3.4.9
cloudinary==1.45.0
dj-database-url==3.1.2
Django==6.0.7
django-cloudinary-storage==0.3.0
django-htmx==1.28.0
gunicorn==26.0.0
idna==3.18
packaging==26.3
pillow==12.3.0
psycopg2-binary==2.9.12
python-decouple==3.8
razorpay==2.0.1
requests==2.34.2
six==1.17.0
sqlparse==0.5.5
tzdata==2026.3
urllib3==2.7.0
whitenoise==6.12.0
```

## Changes made

### Removed (safe, unused)

| Package | Reason | Risk |
|---------|--------|------|
| `mysqlclient==2.2.8` | Abandoned MySQL build; no code imports it; requires MySQL client headers and blocks `pip install` on fresh machines and CI. | None — nothing references it. |
| `PyMySQL==1.2.0` | Same MySQL leftover; unused. | None. |

Verification: `rg "mysqlclient|pymysql"` across the repo → no matches.

## Kept as-is (deliberately not upgraded)

The repository pins an exact, mutually consistent set (asgiref 3.12.x +
Django 6.0.x + certifi/urllib3/requests contemporary). Production is stable on
these. No blind upgrades.

| Package | Current | Consider later | Reason we kept |
|---------|---------|----------------|----------------|
| Django | 6.0.7 | Follow 6.0.x patch releases | Newest 6.0.x line; keep patched via routine `pip install -U django` on next maintenance window. |
| cloudinary | 1.45.0 | Latest | Don't change media pipeline without VPS testing. |
| django-cloudinary-storage | 0.3.0 | Latest | Stable, old but production-proven. |
| razorpay | 2.0.1 | Latest | Don't touch payment SDK outside a testing window. |
| psycopg2-binary | 2.9.12 | Latest 2.9.x | Works on Python 3.14 locally (wheel verified). |
| python-decouple | 3.8 | — | No newer stable release line. |

## Compatibility checks performed

- **Python 3.14, macOS arm64**: full `pip install -r requirements.txt`
  succeeded after removing the MySQL packages (psycopg2-binary 2.9.12 ships a
  cp314 macOS wheel).
- **Django 6.0.x** requires Python ≥ 3.12 → satisfied.
- **CI (GitHub Actions)**: jobs run Python 3.13; all packages are pure-Python or
  ship manylinux wheels, so installs are expected to succeed. If any wheel is
  missing for 3.13, switch `python-version` in `.github/workflows/ci.yml`.

## Residual notes

- `six` is a transitive pin (kept — something may still import it).
- Run `pip list --outdated` and `pip-audit` in a maintenance window for
  vulnerability scanning; nothing should be pinned behind known CVEs without a
  conscious decision.