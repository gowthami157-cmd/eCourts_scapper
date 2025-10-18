import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import asyncio
import httpx
import os

class ECourtsScraper:
    def __init__(self):
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6"
        self.alternative_url = "https://newdelhi.dcourts.gov.in"
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest"
        }

    async def _get_session(self):
        if not self.session:
            self.session = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        return self.session

    async def fetch_states(self) -> List[Dict[str, str]]:
        """Fetch list of all states from eCourts"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/?p=cause_list/"
            response = await session.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            states = []
            state_select = soup.find('select', {'id': 'state_code'}) or soup.find('select', {'name': 'state_code'})

            if state_select:
                for option in state_select.find_all('option'):
                    value = option.get('value', '').strip()
                    text = option.text.strip()
                    if value and value != '0':
                        states.append({
                            "code": value,
                            "name": text
                        })

            if not states:
                states = self._get_default_states()

            return states
        except Exception as e:
            print(f"Error fetching states: {e}")
            return self._get_default_states()

    def _get_default_states(self) -> List[Dict[str, str]]:
        """Fallback list of Indian states"""
        return [
            {"code": "1", "name": "Delhi"},
            {"code": "2", "name": "Maharashtra"},
            {"code": "3", "name": "Karnataka"},
            {"code": "4", "name": "Tamil Nadu"},
            {"code": "5", "name": "Gujarat"},
            {"code": "6", "name": "Rajasthan"},
            {"code": "7", "name": "West Bengal"},
            {"code": "8", "name": "Uttar Pradesh"},
            {"code": "9", "name": "Madhya Pradesh"},
            {"code": "10", "name": "Punjab"}
        ]

    async def fetch_districts(self, state_code: str) -> List[Dict[str, str]]:
        """Fetch districts for a given state"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/get_district.php"
            data = {"state_code": state_code}
            response = await session.post(url, data=data)

            districts = []
            soup = BeautifulSoup(response.text, 'html.parser')

            for option in soup.find_all('option'):
                value = option.get('value', '').strip()
                text = option.text.strip()
                if value and value != '0':
                    districts.append({
                        "code": value,
                        "name": text
                    })

            return districts
        except Exception as e:
            print(f"Error fetching districts: {e}")
            return []

    async def fetch_court_complexes(self, state_code: str, district_code: str) -> List[Dict[str, str]]:
        """Fetch court complexes for a given state and district"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/get_court_complex.php"
            data = {
                "state_code": state_code,
                "dist_code": district_code
            }
            response = await session.post(url, data=data)

            complexes = []
            soup = BeautifulSoup(response.text, 'html.parser')

            for option in soup.find_all('option'):
                value = option.get('value', '').strip()
                text = option.text.strip()
                if value and value != '0':
                    complexes.append({
                        "code": value,
                        "name": text
                    })

            return complexes
        except Exception as e:
            print(f"Error fetching court complexes: {e}")
            return []

    async def fetch_courts(self, state_code: str, district_code: str, complex_code: str) -> List[Dict[str, str]]:
        """Fetch individual courts for a given court complex"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/get_court.php"
            data = {
                "state_code": state_code,
                "dist_code": district_code,
                "court_complex_code": complex_code
            }
            response = await session.post(url, data=data)

            courts = []
            soup = BeautifulSoup(response.text, 'html.parser')

            for option in soup.find_all('option'):
                value = option.get('value', '').strip()
                text = option.text.strip()
                if value and value != '0':
                    courts.append({
                        "code": value,
                        "name": text
                    })

            return courts
        except Exception as e:
            print(f"Error fetching courts: {e}")
            return []

    async def search_case_by_cnr(self, cnr: str, state_code: Optional[str] = None, district_code: Optional[str] = None) -> Optional[Dict]:
        """Search for a case using CNR number"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/search_case_cnr.php"
            data = {"cnr": cnr}

            if state_code:
                data["state_code"] = state_code
            if district_code:
                data["dist_code"] = district_code

            response = await session.post(url, data=data)

            result = self._parse_case_result(response.text, cnr)
            result["search_type"] = "CNR"
            result["cnr"] = cnr

            return result
        except Exception as e:
            print(f"Error searching case by CNR: {e}")
            return None

    async def search_case_by_details(
        self,
        state_code: str,
        district_code: str,
        court_code: str,
        case_type: str,
        case_number: str,
        case_year: str
    ) -> Optional[Dict]:
        """Search for a case using case details"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/search_case_details.php"
            data = {
                "state_code": state_code,
                "dist_code": district_code,
                "court_code": court_code,
                "case_type": case_type,
                "case_no": case_number,
                "case_year": case_year
            }

            response = await session.post(url, data=data)

            result = self._parse_case_result(response.text, f"{case_type}/{case_number}/{case_year}")
            result["search_type"] = "DETAILS"
            result["case_details"] = {
                "case_type": case_type,
                "case_number": case_number,
                "case_year": case_year
            }

            return result
        except Exception as e:
            print(f"Error searching case by details: {e}")
            return None

    def _parse_case_result(self, html_content: str, case_id: str) -> Dict:
        """Parse case search result HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')

        result = {
            "case_id": case_id,
            "found": False,
            "listed_today": False,
            "listed_tomorrow": False,
            "serial_number": None,
            "court_name": None,
            "next_hearing_date": None,
            "case_status": None,
            "details": {}
        }

        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()

                result["details"][label] = value

                if 'hearing date' in label or 'next date' in label:
                    result["next_hearing_date"] = value
                    try:
                        hearing_date = datetime.strptime(value, "%d-%m-%Y").date()
                        if hearing_date == today:
                            result["listed_today"] = True
                            result["found"] = True
                        elif hearing_date == tomorrow:
                            result["listed_tomorrow"] = True
                            result["found"] = True
                    except:
                        pass

                if 'court' in label:
                    result["court_name"] = value

                if 'serial' in label or 'sr.' in label:
                    result["serial_number"] = value

                if 'status' in label:
                    result["case_status"] = value

        return result

    async def fetch_cause_list(
        self,
        state_code: str,
        district_code: str,
        court_complex_code: str,
        court_code: Optional[str],
        date: str
    ) -> Dict:
        """Fetch cause list for a specific court and date"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/get_cause_list.php"
            data = {
                "state_code": state_code,
                "dist_code": district_code,
                "court_complex_code": court_complex_code,
                "date": date
            }

            if court_code:
                data["court_code"] = court_code

            response = await session.post(url, data=data)

            cause_list = self._parse_cause_list(response.text)
            cause_list["metadata"] = {
                "state_code": state_code,
                "district_code": district_code,
                "court_complex_code": court_complex_code,
                "court_code": court_code,
                "date": date,
                "fetched_at": datetime.now().isoformat()
            }

            return cause_list
        except Exception as e:
            print(f"Error fetching cause list: {e}")
            return {"error": str(e), "cases": []}

    def _parse_cause_list(self, html_content: str) -> Dict:
        """Parse cause list HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')

        cases = []
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    case = {
                        "serial_number": cells[0].text.strip(),
                        "case_number": cells[1].text.strip(),
                        "parties": cells[2].text.strip(),
                        "advocate": cells[3].text.strip() if len(cells) > 3 else "",
                        "purpose": cells[4].text.strip() if len(cells) > 4 else ""
                    }
                    cases.append(case)

        return {
            "total_cases": len(cases),
            "cases": cases
        }

    async def download_cause_list_pdf(
        self,
        state_code: str,
        district_code: str,
        court_complex_code: str,
        court_code: Optional[str],
        date: str
    ) -> Optional[str]:
        """Download cause list PDF"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/ajax/download_cause_list_pdf.php"
            data = {
                "state_code": state_code,
                "dist_code": district_code,
                "court_complex_code": court_complex_code,
                "date": date
            }

            if court_code:
                data["court_code"] = court_code

            response = await session.post(url, data=data)

            if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                os.makedirs('downloads', exist_ok=True)

                filename = f"cause_list_{state_code}_{district_code}_{court_complex_code}_{date.replace('-', '')}.pdf"
                filepath = os.path.join('downloads', filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                return filepath

            return None
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None
