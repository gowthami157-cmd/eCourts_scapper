# Quick Start Guide - eCourts Scraper

Get the application running in 5 minutes.

## Step 1: Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Keep this terminal running. Backend will be at `http://localhost:8000`

## Step 2: Frontend Setup

Open a new terminal:

```bash
npm install
npm run dev
```

Frontend will be at `http://localhost:5173`

## Step 3: Use the Application

1. Open `http://localhost:5173` in your browser
2. Select State → District → Court Complex
3. Search for cases or fetch cause lists

## CLI Quick Test

```bash
# In backend directory with venv activated
python cli.py states
python cli.py causelist --state 1 --district 1 --complex 01 --today
```

## Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

**Frontend won't start?**
- Run: `npm install`
- Check Node version: `node --version` (need 18+)

**Can't connect to backend?**
- Verify backend is running on port 8000
- Check `src/services/api.ts` has correct API_BASE_URL

## Demo Data

Try these test queries:
- **State**: Delhi (code: 1)
- **District**: Central (code: 1)
- **CNR**: Any valid CNR from eCourts

## Next Steps

- Read full documentation in README.md
- Explore API docs at `http://localhost:8000/docs`
- Check CLI options: `python cli.py --help`
