# CityMender SA — Community Service Delivery Platform

A Django web application for South African communities to report, track, and verify
local service delivery issues (water, electricity, roads, waste, etc.).

## Screens
| # | URL | View | Description |
|---|-----|------|-------------|
| 1 | `/` | `HomeView` | Landing page with category picker CTA |
| 2 | `/report/location/` | `LocationView` | GPS + address fallback location picker |
| 3 | `/report/submit/` | `ReportSubmitView` | Issue form with photo + voice-to-text |
| 4 | `/report/done/<ref_id>/` | `ReportDoneView` | Confirmation with reference ID |
| 5 | `/map/` | `IssueMapView` | Leaflet map with clustered pins + "+1 Issue" |
| 6 | `/hub/` | `CommunityHubView` | Prioritised issues + status tracker |

## API Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/issues/` | GeoJSON FeatureCollection of all issues |
| POST | `/api/issues/` | Create a new issue report |
| GET | `/api/issues/<id>/` | Retrieve a single issue |
| POST | `/api/issues/<id>/verify/` | Toggle "+1 Issue" confirmation |
| GET | `/api/issues/<id>/status/` | Get full status history |

## Setup

```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create superuser (for /admin/)
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/

## Key Features
- **GPS location picker** with Leaflet mini-map preview + Nominatim reverse geocode
- **Voice-to-text** via Web Speech API (English, isiZulu, Sesotho, Afrikaans)
- **Offline mode** — Service Worker caches app shell; IndexedDB queues reports
- **"+1 Issue" verification** — community members confirm problems (replaces "Me Too")
- **DRF REST API** — GeoJSON endpoint for Leaflet, toggle verify, status log
- **4-step progress indicator** throughout the report flow
- **Reference ID** auto-generated (e.g. `CSR-A1B2C3D4`) for tracking
- **Status tracker** — Logged → Dispatched → Resolved
- **Django Admin** — full CRUD with status-change audit log

## Project Structure
```
community_service/
├── manage.py
├── requirements.txt
├── community_service/      # Django project config
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── reports/            # Core: models, views, forms, admin
│   ├── hub/                # Community Hub view
│   └── api/                # DRF ViewSet + serializers
├── templates/
│   ├── base/base.html      # App shell (header, nav, offline banner)
│   ├── report/             # home, location, submit, done
│   ├── map/issue_map.html  # Leaflet map with MarkerCluster
│   └── hub/community.html  # Prioritised issue list
└── static/
    ├── css/main.css        # Full design system (~710 lines)
    └── js/
        ├── voice.js        # Web Speech API, multilingual
        ├── offline.js      # IndexedDB queue + SW registration
        ├── sw.js           # Service Worker (app shell cache)
        └── app.js          # General UI interactions
```

## Production Checklist
- [ ] Change `SECRET_KEY` in settings.py (use environment variable)
- [ ] Set `DEBUG = False`
- [ ] Configure PostgreSQL + PostGIS (for full GeoJSON support)
- [ ] Add Twilio credentials for WhatsApp notifications
- [ ] Set up Celery + Redis for async notifications
- [ ] Run `python manage.py collectstatic`
- [ ] Configure `ALLOWED_HOSTS`
