#!/usr/bin/env python3

import asyncio
import argparse
import json
from datetime import datetime, timedelta
from services.ecourts_scraper import ECourtsScraper
from services.database import Database

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def save_to_file(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to: {filename}")

async def search_cnr(cnr: str, state_code: str = None, district_code: str = None):
    """Search case by CNR number"""
    scraper = ECourtsScraper()
    db = Database()

    print(f"\nSearching for CNR: {cnr}")
    print("=" * 50)

    result = await scraper.search_case_by_cnr(cnr, state_code, district_code)

    if result:
        print_json(result)

        if result.get("found"):
            print("\n" + "=" * 50)
            print("CASE FOUND!")
            if result.get("listed_today"):
                print("Listed: TODAY")
            elif result.get("listed_tomorrow"):
                print("Listed: TOMORROW")

            if result.get("serial_number"):
                print(f"Serial Number: {result['serial_number']}")
            if result.get("court_name"):
                print(f"Court: {result['court_name']}")
            print("=" * 50)
        else:
            print("\nCase not found or not listed today/tomorrow")

        await db.save_search_result(result)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_to_file(result, f"case_search_{cnr}_{timestamp}.json")
    else:
        print("Error: Unable to fetch case details")

async def search_case(state_code: str, district_code: str, court_code: str,
                     case_type: str, case_number: str, case_year: str):
    """Search case by case details"""
    scraper = ECourtsScraper()
    db = Database()

    print(f"\nSearching for Case: {case_type}/{case_number}/{case_year}")
    print("=" * 50)

    result = await scraper.search_case_by_details(
        state_code, district_code, court_code,
        case_type, case_number, case_year
    )

    if result:
        print_json(result)

        if result.get("found"):
            print("\n" + "=" * 50)
            print("CASE FOUND!")
            if result.get("listed_today"):
                print("Listed: TODAY")
            elif result.get("listed_tomorrow"):
                print("Listed: TOMORROW")

            if result.get("serial_number"):
                print(f"Serial Number: {result['serial_number']}")
            if result.get("court_name"):
                print(f"Court: {result['court_name']}")
            print("=" * 50)
        else:
            print("\nCase not found or not listed today/tomorrow")

        await db.save_search_result(result)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_id = f"{case_type}_{case_number}_{case_year}"
        save_to_file(result, f"case_search_{case_id}_{timestamp}.json")
    else:
        print("Error: Unable to fetch case details")

async def fetch_cause_list(state_code: str, district_code: str,
                          court_complex_code: str, court_code: str = None,
                          date: str = None, download_pdf: bool = False):
    """Fetch cause list for a court"""
    scraper = ECourtsScraper()
    db = Database()

    if not date:
        date = datetime.now().strftime("%d-%m-%Y")

    print(f"\nFetching cause list for date: {date}")
    print("=" * 50)

    cause_list = await scraper.fetch_cause_list(
        state_code, district_code, court_complex_code, court_code, date
    )

    if cause_list:
        print_json(cause_list)

        print(f"\nTotal cases: {cause_list.get('total_cases', 0)}")

        await db.save_cause_list(cause_list)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cause_list_{state_code}_{district_code}_{date.replace('-', '')}_{timestamp}.json"
        save_to_file(cause_list, filename)

        if download_pdf:
            print("\nDownloading PDF...")
            pdf_path = await scraper.download_cause_list_pdf(
                state_code, district_code, court_complex_code, court_code, date
            )
            if pdf_path:
                print(f"PDF downloaded: {pdf_path}")
            else:
                print("Error: Unable to download PDF")
    else:
        print("Error: Unable to fetch cause list")

async def list_states():
    """List all available states"""
    scraper = ECourtsScraper()
    print("\nFetching states...")
    print("=" * 50)

    states = await scraper.fetch_states()
    if states:
        print(f"\nTotal states: {len(states)}\n")
        for state in states:
            print(f"{state['code']}: {state['name']}")
    else:
        print("Error: Unable to fetch states")

async def list_districts(state_code: str):
    """List all districts for a state"""
    scraper = ECourtsScraper()
    print(f"\nFetching districts for state code: {state_code}")
    print("=" * 50)

    districts = await scraper.fetch_districts(state_code)
    if districts:
        print(f"\nTotal districts: {len(districts)}\n")
        for district in districts:
            print(f"{district['code']}: {district['name']}")
    else:
        print("Error: Unable to fetch districts")

async def main():
    parser = argparse.ArgumentParser(
        description="eCourts Scraper CLI - Fetch case details and cause lists from Indian eCourts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_cnr_parser = subparsers.add_parser("search-cnr", help="Search case by CNR number")
    search_cnr_parser.add_argument("cnr", help="CNR number")
    search_cnr_parser.add_argument("--state", help="State code (optional)")
    search_cnr_parser.add_argument("--district", help="District code (optional)")

    search_case_parser = subparsers.add_parser("search-case", help="Search case by details")
    search_case_parser.add_argument("--state", required=True, help="State code")
    search_case_parser.add_argument("--district", required=True, help="District code")
    search_case_parser.add_argument("--court", required=True, help="Court code")
    search_case_parser.add_argument("--type", required=True, help="Case type")
    search_case_parser.add_argument("--number", required=True, help="Case number")
    search_case_parser.add_argument("--year", required=True, help="Case year")

    causelist_parser = subparsers.add_parser("causelist", help="Fetch cause list")
    causelist_parser.add_argument("--state", required=True, help="State code")
    causelist_parser.add_argument("--district", required=True, help="District code")
    causelist_parser.add_argument("--complex", required=True, help="Court complex code")
    causelist_parser.add_argument("--court", help="Court code (optional)")
    causelist_parser.add_argument("--date", help="Date (DD-MM-YYYY), defaults to today")
    causelist_parser.add_argument("--today", action="store_true", help="Fetch today's cause list")
    causelist_parser.add_argument("--tomorrow", action="store_true", help="Fetch tomorrow's cause list")
    causelist_parser.add_argument("--pdf", action="store_true", help="Download PDF")

    states_parser = subparsers.add_parser("states", help="List all states")

    districts_parser = subparsers.add_parser("districts", help="List districts for a state")
    districts_parser.add_argument("state_code", help="State code")

    args = parser.parse_args()

    if args.command == "search-cnr":
        await search_cnr(args.cnr, args.state, args.district)

    elif args.command == "search-case":
        await search_case(
            args.state, args.district, args.court,
            args.type, args.number, args.year
        )

    elif args.command == "causelist":
        date = args.date
        if args.today:
            date = datetime.now().strftime("%d-%m-%Y")
        elif args.tomorrow:
            date = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")

        await fetch_cause_list(
            args.state, args.district, args.complex, args.court,
            date, args.pdf
        )

    elif args.command == "states":
        await list_states()

    elif args.command == "districts":
        await list_districts(args.state_code)

    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
