from supabase import create_client, Client
from typing import List, Dict, Optional
import os
from datetime import datetime
import json

class Database:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        if supabase_url and supabase_key:
            self.client: Client = create_client(supabase_url, supabase_key)
        else:
            self.client = None
            print("Warning: Supabase credentials not found. Database features disabled.")

    async def cache_states(self, states: List[Dict[str, str]]) -> bool:
        """Cache states in database"""
        if not self.client:
            return False

        try:
            for state in states:
                self.client.table("states").upsert({
                    "code": state["code"],
                    "name": state["name"],
                    "updated_at": datetime.now().isoformat()
                }, on_conflict="code").execute()
            return True
        except Exception as e:
            print(f"Error caching states: {e}")
            return False

    async def cache_districts(self, state_code: str, districts: List[Dict[str, str]]) -> bool:
        """Cache districts in database"""
        if not self.client:
            return False

        try:
            for district in districts:
                self.client.table("districts").upsert({
                    "state_code": state_code,
                    "code": district["code"],
                    "name": district["name"],
                    "updated_at": datetime.now().isoformat()
                }, on_conflict="state_code,code").execute()
            return True
        except Exception as e:
            print(f"Error caching districts: {e}")
            return False

    async def cache_court_complexes(self, state_code: str, district_code: str, complexes: List[Dict[str, str]]) -> bool:
        """Cache court complexes in database"""
        if not self.client:
            return False

        try:
            for complex in complexes:
                self.client.table("court_complexes").upsert({
                    "state_code": state_code,
                    "district_code": district_code,
                    "code": complex["code"],
                    "name": complex["name"],
                    "updated_at": datetime.now().isoformat()
                }, on_conflict="state_code,district_code,code").execute()
            return True
        except Exception as e:
            print(f"Error caching court complexes: {e}")
            return False

    async def cache_courts(self, state_code: str, district_code: str, complex_code: str, courts: List[Dict[str, str]]) -> bool:
        """Cache courts in database"""
        if not self.client:
            return False

        try:
            for court in courts:
                self.client.table("courts").upsert({
                    "state_code": state_code,
                    "district_code": district_code,
                    "complex_code": complex_code,
                    "code": court["code"],
                    "name": court["name"],
                    "updated_at": datetime.now().isoformat()
                }, on_conflict="state_code,district_code,complex_code,code").execute()
            return True
        except Exception as e:
            print(f"Error caching courts: {e}")
            return False

    async def save_search_result(self, result: Dict) -> bool:
        """Save case search result"""
        if not self.client:
            return False

        try:
            self.client.table("search_results").insert({
                "case_id": result.get("case_id"),
                "search_type": result.get("search_type"),
                "cnr": result.get("cnr"),
                "case_details": json.dumps(result.get("case_details", {})),
                "found": result.get("found", False),
                "listed_today": result.get("listed_today", False),
                "listed_tomorrow": result.get("listed_tomorrow", False),
                "serial_number": result.get("serial_number"),
                "court_name": result.get("court_name"),
                "next_hearing_date": result.get("next_hearing_date"),
                "case_status": result.get("case_status"),
                "full_result": json.dumps(result),
                "searched_at": datetime.now().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving search result: {e}")
            return False

    async def save_cause_list(self, cause_list: Dict) -> bool:
        """Save cause list"""
        if not self.client:
            return False

        try:
            metadata = cause_list.get("metadata", {})
            self.client.table("cause_lists").insert({
                "state_code": metadata.get("state_code"),
                "district_code": metadata.get("district_code"),
                "court_complex_code": metadata.get("court_complex_code"),
                "court_code": metadata.get("court_code"),
                "date": metadata.get("date"),
                "total_cases": cause_list.get("total_cases", 0),
                "cases": json.dumps(cause_list.get("cases", [])),
                "full_data": json.dumps(cause_list),
                "fetched_at": metadata.get("fetched_at", datetime.now().isoformat())
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving cause list: {e}")
            return False

    async def get_cached_states(self) -> Optional[List[Dict[str, str]]]:
        """Get cached states from database"""
        if not self.client:
            return None

        try:
            response = self.client.table("states").select("*").execute()
            return [{"code": row["code"], "name": row["name"]} for row in response.data]
        except Exception as e:
            print(f"Error getting cached states: {e}")
            return None
