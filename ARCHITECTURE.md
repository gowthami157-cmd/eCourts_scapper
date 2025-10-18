# System Architecture - eCourts Scraper

## Overview

The eCourts Scraper is a full-stack application with clear separation between backend (Python) and frontend (React).

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CourtSelector│  │  CaseSearch  │  │  CauseList   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                │                  │               │
│           └────────────────┴──────────────────┘               │
│                           │                                   │
│                      API Service                              │
└───────────────────────────┼───────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────┼───────────────────────────────────┐
│                   Backend (FastAPI)                           │
│                           │                                   │
│           ┌───────────────┴───────────────┐                  │
│           │                               │                  │
│    ┌──────▼─────┐              ┌─────────▼────────┐         │
│    │   API      │              │   CLI Interface  │         │
│    │ Endpoints  │              └──────────────────┘         │
│    └──────┬─────┘                                            │
│           │                                                  │
│    ┌──────▼──────────────────────────────┐                  │
│    │     eCourts Scraper Service         │                  │
│    │  - fetch_states()                   │                  │
│    │  - fetch_districts()                │                  │
│    │  - fetch_court_complexes()          │                  │
│    │  - fetch_courts()                   │                  │
│    │  - search_case_by_cnr()             │                  │
│    │  - search_case_by_details()         │                  │
│    │  - fetch_cause_list()               │                  │
│    │  - download_cause_list_pdf()        │                  │
│    └──────┬──────────────────────────────┘                  │
│           │                                                  │
│    ┌──────▼─────────┐       ┌────────────┐                 │
│    │   Database     │       │  eCourts   │                 │
│    │   Service      │       │  Website   │                 │
│    │  (Supabase)    │       └────────────┘                 │
│    └────────────────┘                                       │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

**Technology**: React 18 + TypeScript + Vite + TailwindCSS

**Components**:
1. **App.tsx**: Main application container, manages global state
2. **CourtSelector.tsx**: Hierarchical court selection with cascading dropdowns
3. **CaseSearch.tsx**: Case search interface (CNR or details)
4. **CauseList.tsx**: Displays cause list with download options

**Services**:
- **api.ts**: API client with typed interfaces for backend communication

### Backend Layer

**Technology**: Python 3.9+ + FastAPI + BeautifulSoup4 + httpx

**Core Services**:

1. **ecourts_scraper.py**
   - Web scraping logic
   - HTTP session management
   - HTML parsing
   - Data extraction and normalization

2. **database.py**
   - Supabase integration
   - Caching layer
   - Data persistence
   - Query optimization

**API Endpoints** (main.py):
- Court hierarchy endpoints
- Case search endpoints
- Cause list endpoints
- PDF download endpoint

**CLI Interface** (cli.py):
- Command-line wrapper around scraper
- File output management
- Automation support

### Data Layer

**Supabase PostgreSQL Database**

**Tables**:
1. `states` - State codes and names
2. `districts` - Districts per state
3. `court_complexes` - Court complexes per district
4. `courts` - Individual courts
5. `search_results` - Cached case search results
6. `cause_lists` - Cached cause lists

**Security**: Row Level Security (RLS) enabled with public read access

### External Integration

**eCourts Website**:
- Primary: `https://services.ecourts.gov.in/ecourtindia_v6/`
- Alternative: `https://newdelhi.dcourts.gov.in/`

## Data Flow

### Court Selection Flow
```
User selects state
    ↓
Frontend → GET /api/states
    ↓
Backend checks cache (Supabase)
    ↓
If not cached: Scrape eCourts website
    ↓
Cache result in Supabase
    ↓
Return to frontend
    ↓
User selects district (repeat pattern)
```

### Case Search Flow
```
User enters CNR/case details
    ↓
Frontend → POST /api/search/cnr or /api/search/case
    ↓
Backend scrapes eCourts
    ↓
Parse HTML response
    ↓
Check if listed today/tomorrow
    ↓
Save result to database
    ↓
Return structured data
    ↓
Frontend displays result
```

### Cause List Flow
```
User selects date
    ↓
Frontend → POST /api/cause-list
    ↓
Backend scrapes cause list
    ↓
Parse case entries
    ↓
Save to database
    ↓
Return case list
    ↓
Frontend displays table
    ↓
User clicks download
    ↓
Download JSON (client-side) or PDF (backend)
```

## Technology Choices

### Why FastAPI?
- High performance with async support
- Automatic API documentation (Swagger)
- Type checking with Pydantic
- Easy deployment

### Why React + TypeScript?
- Type safety reduces bugs
- Component reusability
- Modern, maintainable code
- Excellent developer experience

### Why Supabase?
- Managed PostgreSQL
- Built-in authentication (future)
- Real-time capabilities (future)
- Easy to deploy and scale

### Why BeautifulSoup?
- Robust HTML parsing
- Easy to maintain
- Well-documented
- Handles malformed HTML

## Scalability Considerations

### Current Architecture
- Suitable for 100s of concurrent users
- Database caching reduces scraping load
- Async operations for efficiency

### Scaling Options

**Horizontal Scaling**:
- Multiple backend instances behind load balancer
- Shared Supabase database
- Redis for session management

**Performance Optimization**:
- CDN for frontend assets
- Database query optimization
- Request rate limiting
- Background job queue for bulk operations

**Monitoring**:
- API response time tracking
- Error rate monitoring
- Database performance metrics
- eCourts website availability checks

## Security Considerations

### Current Implementation
- No authentication (public data)
- Input validation on all endpoints
- SQL injection prevention (Supabase ORM)
- XSS prevention (React auto-escaping)

### Production Hardening
- Rate limiting per IP
- CAPTCHA for bulk requests
- API key authentication
- Request logging and audit trail

## Deployment

### Development
- Backend: `python main.py` (uvicorn)
- Frontend: `npm run dev` (Vite dev server)

### Production

**Backend**:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend**:
```bash
npm run build
# Serve dist/ with nginx or similar
```

**Database**: Supabase cloud (already configured)

## Testing Strategy

### Backend Tests
- Unit tests for scraper functions
- Integration tests for API endpoints
- Mock eCourts responses

### Frontend Tests
- Component unit tests
- Integration tests with mock API
- E2E tests with Playwright

### Manual Testing
- CLI test script (`test_api.py`)
- Browser testing across devices
- API testing via Swagger UI

## Future Enhancements

### Phase 2
- User authentication and profiles
- Saved searches and favorites
- Email notifications for case updates
- Automated daily scraping

### Phase 3
- Mobile app (React Native)
- Advanced analytics and insights
- Case status tracking over time
- Integration with legal practice management

### Phase 4
- AI-powered case prediction
- Document management
- Multi-language support
- WhatsApp notifications

## Development Workflow

1. **Feature Development**:
   - Create feature branch
   - Implement backend first
   - Add API tests
   - Build frontend components
   - Test end-to-end
   - Code review
   - Merge to main

2. **Bug Fixes**:
   - Reproduce issue
   - Write failing test
   - Fix bug
   - Verify test passes
   - Deploy

3. **Deployment**:
   - Run tests
   - Build frontend
   - Deploy backend
   - Deploy frontend
   - Verify production

## Contributing

See main README.md for contribution guidelines.

## License

MIT License - See LICENSE file for details
