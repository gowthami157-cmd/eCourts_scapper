# eCourts Scraper - Indian eCourts Case Listing System

A complete end-to-end web application for scraping cause lists and case details from Indian eCourts websites in real-time.

## Features

- **Real-time Court Hierarchy**: Dynamic fetching of State → District → Court Complex → Court Name
- **Case Search**: Search by CNR number or Case Type/Number/Year
- **Case Status**: Check if a case is listed today or tomorrow with serial number and court details
- **Cause Lists**: Fetch and download complete cause lists for any date
- **PDF Downloads**: Download official cause list PDFs
- **JSON Export**: Export cause list data as JSON
- **Data Persistence**: Supabase database integration for caching and history
- **CLI Interface**: Command-line tool with flags for automation
- **Modern UI**: Clean, responsive React interface

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI** - High-performance REST API
- **BeautifulSoup4** - HTML parsing
- **httpx** - Async HTTP client
- **Supabase** - Database for caching and persistence

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Lucide React** - Icons

## Project Structure

```
.
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── cli.py                     # CLI interface
│   ├── requirements.txt           # Python dependencies
│   ├── services/
│   │   ├── ecourts_scraper.py    # Core scraping logic
│   │   └── database.py           # Supabase integration
│   └── .env                       # Backend environment variables
├── src/
│   ├── App.tsx                    # Main React component
│   ├── components/
│   │   ├── CourtSelector.tsx     # Court hierarchy selector
│   │   ├── CaseSearch.tsx        # Case search interface
│   │   └── CauseList.tsx         # Cause list viewer
│   └── services/
│       └── api.ts                 # API client
└── README.md
```

## Setup Instructions

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **npm or yarn**

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
The `.env` file is already created with Supabase credentials. If you need to update them:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

5. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

### Web Interface

1. **Select Court Hierarchy**:
   - Choose State → District → Court Complex → Court
   - Selections update dynamically in real-time

2. **Search for a Case**:
   - **By CNR**: Enter the CNR number
   - **By Details**: Enter Case Type, Number, and Year
   - View if the case is listed today or tomorrow
   - See serial number, court name, and hearing date

3. **Fetch Cause List**:
   - Select a date (Today, Tomorrow, or custom)
   - Click "Fetch Cause List"
   - View all cases listed for that date
   - Download as JSON or PDF

### CLI Interface

The CLI tool provides command-line access to all features.

#### Search by CNR
```bash
python backend/cli.py search-cnr DLNC01-123456-2024 --state 1 --district 1
```

#### Search by Case Details
```bash
python backend/cli.py search-case \
  --state 1 \
  --district 1 \
  --court 001 \
  --type CS \
  --number 1234 \
  --year 2024
```

#### Fetch Today's Cause List
```bash
python backend/cli.py causelist \
  --state 1 \
  --district 1 \
  --complex 01 \
  --today
```

#### Fetch Tomorrow's Cause List
```bash
python backend/cli.py causelist \
  --state 1 \
  --district 1 \
  --complex 01 \
  --tomorrow
```

#### Fetch Cause List with PDF Download
```bash
python backend/cli.py causelist \
  --state 1 \
  --district 1 \
  --complex 01 \
  --date 20-10-2024 \
  --pdf
```

#### List All States
```bash
python backend/cli.py states
```

#### List Districts for a State
```bash
python backend/cli.py districts 1
```

### API Endpoints

The backend provides a REST API:

- `GET /api/states` - Get all states
- `GET /api/districts/{state_code}` - Get districts for a state
- `GET /api/court-complexes/{state_code}/{district_code}` - Get court complexes
- `GET /api/courts/{state_code}/{district_code}/{complex_code}` - Get courts
- `POST /api/search/cnr` - Search case by CNR
- `POST /api/search/case` - Search case by details
- `POST /api/cause-list` - Fetch cause list
- `GET /api/download/pdf` - Download cause list PDF

API documentation available at `http://localhost:8000/docs` (Swagger UI)

## Data Sources

- **Primary**: https://services.ecourts.gov.in/ecourtindia_v6/
- **Alternative**: https://newdelhi.dcourts.gov.in/

## Database Schema

The application uses Supabase with the following tables:

- `states` - Indian states
- `districts` - Districts by state
- `court_complexes` - Court complexes by district
- `courts` - Individual courts
- `search_results` - Cached case search results
- `cause_lists` - Cached cause lists

All data is cached to improve performance and reduce load on eCourts servers.

## Features in Detail

### Real-time Court Hierarchy
- Dynamically fetches court structure from live eCourts portal
- Cascading dropdowns for intuitive navigation
- Caches results in database for faster subsequent loads

### Case Search
- **CNR Search**: Universal case identification across all courts
- **Details Search**: Search by case type, number, and year
- Shows listing status (today/tomorrow)
- Displays serial number and court name when listed
- Full case details available in expandable section

### Cause List Management
- Fetch for any date (past, present, or future)
- Quick access buttons for today and tomorrow
- View complete case list in tabular format
- Download as JSON for data processing
- Download official PDF from eCourts

### CLI Automation
- Full feature parity with web interface
- Supports flags: `--today`, `--tomorrow`, `--causelist`, `--pdf`
- JSON output saved automatically
- Perfect for automation and scripting

## Error Handling

The application includes comprehensive error handling:
- Network failures with retry logic
- Invalid inputs with clear error messages
- Missing data handling
- CORS and API access issues
- Database connection errors

## Performance

- Async operations for concurrent requests
- Database caching reduces API calls
- Lazy loading of court hierarchy
- Optimized React rendering

## Security

- Row Level Security (RLS) enabled on all database tables
- Public read access (court data is public information)
- No authentication required for viewing public records
- Environment variables for sensitive credentials
- CORS protection on backend API

## Development

### Running Tests
```bash
npm test  # Frontend tests
pytest    # Backend tests (when implemented)
```

### Building for Production

Frontend:
```bash
npm run build
```

Backend:
```bash
# Use gunicorn or uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Backend Not Starting
- Ensure Python 3.9+ is installed
- Activate virtual environment
- Check all dependencies are installed
- Verify Supabase credentials in `.env`

### Frontend Not Loading
- Run `npm install` to ensure all dependencies are present
- Check backend is running on port 8000
- Verify API_BASE_URL in `src/services/api.ts`

### Scraping Errors
- eCourts website structure may change
- Check internet connectivity
- Verify court codes are correct
- Some courts may not have data for selected dates

## Limitations

- Depends on eCourts website availability
- Some courts may not have complete data
- PDF downloads depend on eCourts PDF generation
- Historical data availability varies by court

## Future Enhancements

- [ ] Automated daily cause list downloads
- [ ] Email notifications for case listings
- [ ] Advanced search filters
- [ ] Historical data analysis
- [ ] Multi-case batch search
- [ ] Export to Excel/CSV
- [ ] Mobile app

## License

MIT License

## Acknowledgments

- Data source: eCourts India (https://ecourts.gov.in/)
- Built for educational and research purposes
- Respects eCourts terms of service

## Submission Details

**Deadline**: 20th October 2024
**Evaluation Criteria**:
- Accuracy & completeness
- Code quality & clarity
- Proper error handling

## Contact

For questions or issues, please create an issue in the repository.

---

Made with care for the Indian legal community
