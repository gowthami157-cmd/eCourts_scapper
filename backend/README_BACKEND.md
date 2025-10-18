# eCourts Scraper Backend

Python FastAPI backend for scraping Indian eCourts data.

## Quick Start

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

API will run at `http://localhost:8000`

## CLI Usage Examples

```bash
# Search by CNR
python cli.py search-cnr DLNC01-123456-2024

# Search by case details
python cli.py search-case --state 1 --district 1 --court 001 --type CS --number 1234 --year 2024

# Get today's cause list
python cli.py causelist --state 1 --district 1 --complex 01 --today

# Get tomorrow's cause list with PDF
python cli.py causelist --state 1 --district 1 --complex 01 --tomorrow --pdf

# List states
python cli.py states

# List districts
python cli.py districts 1
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Environment Variables

Create `.env` file with:
```
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

## Output Files

- Case searches: `case_search_*.json`
- Cause lists: `cause_list_*.json`
- PDFs: `downloads/cause_list_*.pdf`
