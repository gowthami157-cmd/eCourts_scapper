#!/usr/bin/env python3

import asyncio
import sys
from services.ecourts_scraper import ECourtsScraper

async def test_scraper():
    """Test the eCourts scraper functionality"""
    print("=" * 60)
    print("eCourts Scraper API Test")
    print("=" * 60)

    scraper = ECourtsScraper()

    print("\n1. Testing States Fetch...")
    try:
        states = await scraper.fetch_states()
        print(f"   ✓ Success: Found {len(states)} states")
        if states:
            print(f"   Sample: {states[0]['name']} (code: {states[0]['code']})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

    print("\n2. Testing Districts Fetch...")
    try:
        if states:
            districts = await scraper.fetch_districts(states[0]['code'])
            print(f"   ✓ Success: Found {len(districts)} districts")
            if districts:
                print(f"   Sample: {districts[0]['name']} (code: {districts[0]['code']})")
        else:
            print("   ⊘ Skipped: No states available")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n3. Testing Court Complexes Fetch...")
    try:
        if states and districts:
            complexes = await scraper.fetch_court_complexes(
                states[0]['code'],
                districts[0]['code']
            )
            print(f"   ✓ Success: Found {len(complexes)} court complexes")
            if complexes:
                print(f"   Sample: {complexes[0]['name']} (code: {complexes[0]['code']})")
        else:
            print("   ⊘ Skipped: No districts available")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n4. Testing Courts Fetch...")
    try:
        if states and districts and complexes:
            courts = await scraper.fetch_courts(
                states[0]['code'],
                districts[0]['code'],
                complexes[0]['code']
            )
            print(f"   ✓ Success: Found {len(courts)} courts")
            if courts:
                print(f"   Sample: {courts[0]['name']} (code: {courts[0]['code']})")
        else:
            print("   ⊘ Skipped: No court complexes available")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNote: Actual data availability depends on eCourts website.")
    print("If tests fail, the website might be down or changed.")
    print("\nNext steps:")
    print("1. Start the API: python main.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Try the CLI: python cli.py states")

    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_scraper())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
