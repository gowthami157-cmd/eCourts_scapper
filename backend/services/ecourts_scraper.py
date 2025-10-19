import base64
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import json
from datetime import datetime, timedelta
import asyncio
import httpx
import os
from urllib.parse import urljoin

class ECourtsScraper:
    def __init__(self):
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6"
        self.alternative_url = "https://newdelhi.dcourts.gov.in"
        self.session = None
        self.session_initialized = False
        self._init_path = "/?p=cause_list/"
        self.app_token: Optional[str] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://services.ecourts.gov.in",
            "Referer": "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

    async def _get_session(self):
        if not self.session:
            self.session = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        if not self.session_initialized:
            await self._initialize_session(self.session)
        return self.session

    async def _initialize_session(self, session: httpx.AsyncClient) -> None:
        if self.session_initialized:
            return
        init_url = f"{self.base_url}{self._init_path}"
        try:
            response = await session.get(init_url)
            response.raise_for_status()
            self._capture_app_token_from_html(response.text)
            self.session_initialized = True
        except Exception as exc:
            print(f"[WARN] Unable to warm up eCourts session via {init_url}: {exc}")

    def _capture_app_token_from_html(self, html_content: str) -> None:
        if self.app_token:
            return
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            token_input = soup.find('input', {'id': 'app_token'})
            if token_input:
                token = token_input.get('value', '').strip()
                if token:
                    self.app_token = token
        except Exception as exc:
            print(f"[WARN] Failed to capture app_token from HTML: {exc}")

    def _prepare_form_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = {"ajax_req": "true"}
        if self.app_token:
            data["app_token"] = self.app_token
        data.update(payload)
        return {key: str(value) for key, value in data.items() if value is not None}

    def _extract_complex_parts(self, complex_code: str) -> Dict[str, Any]:
        parts = complex_code.split('@') if complex_code else []
        complex_id = parts[0] if parts else complex_code
        est_codes = []
        flag = None

        if len(parts) > 1:
            est_codes = [code.strip() for code in parts[1].split(',') if code.strip()]
        if len(parts) > 2:
            flag = parts[2].strip()

        return {
            "id": complex_id,
            "est_codes": est_codes,
            "flag": flag
        }

    def _parse_json_payload(self, response_text: str) -> Dict[str, Any]:
        text = response_text.strip()
        if not text:
            return {}
        candidate = text
        if not text.startswith("{"):
            start_index = text.find('{"')
            if start_index == -1:
                return {}
            candidate = text[start_index:]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            print(f"[WARN] Failed to decode JSON payload: {exc}")
            return {}

    def _update_app_token(self, payload: Dict[str, Any]) -> None:
        token = payload.get("app_token")
        if token:
            self.app_token = token

    async def fetch_states(self) -> List[Dict[str, str]]:
        """Fetch list of all states from eCourts"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/?p=cause_list/"
            response = await session.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')
            self._capture_app_token_from_html(response.text)

            states = []
            state_select = (
                soup.find('select', {'id': 'sess_state_code'})
                or soup.find('select', {'id': 'state_code'})
                or soup.find('select', {'name': 'state_code'})
            )

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
            {"code": "28", "name": "Andaman and Nicobar"},
            {"code": "2", "name": "Andhra Pradesh"},
            {"code": "36", "name": "Arunachal Pradesh"},
            {"code": "6", "name": "Assam"},
            {"code": "8", "name": "Bihar"},
            {"code": "27", "name": "Chandigarh"},
            {"code": "18", "name": "Chhattisgarh"},
            {"code": "26", "name": "Delhi"},
            {"code": "30", "name": "Goa"},
            {"code": "17", "name": "Gujarat"},
            {"code": "14", "name": "Haryana"},
            {"code": "5", "name": "Himachal Pradesh"},
            {"code": "12", "name": "Jammu and Kashmir"},
            {"code": "7", "name": "Jharkhand"},
            {"code": "3", "name": "Karnataka"},
            {"code": "4", "name": "Kerala"},
            {"code": "33", "name": "Ladakh"},
            {"code": "37", "name": "Lakshadweep"},
            {"code": "23", "name": "Madhya Pradesh"},
            {"code": "1", "name": "Maharashtra"},
            {"code": "25", "name": "Manipur"},
            {"code": "21", "name": "Meghalaya"},
            {"code": "19", "name": "Mizoram"},
            {"code": "34", "name": "Nagaland"},
            {"code": "11", "name": "Odisha"},
            {"code": "35", "name": "Puducherry"},
            {"code": "22", "name": "Punjab"},
            {"code": "9", "name": "Rajasthan"},
            {"code": "24", "name": "Sikkim"},
            {"code": "10", "name": "Tamil Nadu"},
            {"code": "29", "name": "Telangana"},
            {"code": "38", "name": "The Dadra And Nagar Haveli And Daman And Diu"},
            {"code": "20", "name": "Tripura"},
            {"code": "15", "name": "Uttarakhand"},
            {"code": "13", "name": "Uttar Pradesh"},
            {"code": "16", "name": "West Bengal"}
        ]

    async def fetch_districts(self, state_code: str) -> List[Dict[str, str]]:
        """Fetch districts for a given state"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/?p=casestatus/fillDistrict"
            data = self._prepare_form_data({"state_code": state_code})
            response = await session.post(url, data=data)

            payload = self._parse_json_payload(response.text)
            self._update_app_token(payload)

            districts = []
            options_html = payload.get("dist_list", "")
            soup = BeautifulSoup(options_html, 'html.parser')

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
            print(f"[ERROR] Error fetching districts for state {state_code}: {e}")
            return []

    async def fetch_court_complexes(self, state_code: str, district_code: str) -> List[Dict[str, str]]:
        """Fetch court complexes for a given state and district"""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/?p=casestatus/fillcomplex"
            data = self._prepare_form_data({
                "state_code": state_code,
                "dist_code": district_code
            })
            response = await session.post(url, data=data)

            payload = self._parse_json_payload(response.text)
            self._update_app_token(payload)

            complexes = []
            options_html = payload.get("complex_list", "")
            soup = BeautifulSoup(options_html, 'html.parser')

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

    async def _fetch_court_numbers(self, session: httpx.AsyncClient, state_code: str, district_code: str, complex_code: str, est_code: Optional[str] = None) -> List[Dict[str, str]]:
        complex_parts = self._extract_complex_parts(complex_code)
        complex_id = complex_parts["id"]

        data = self._prepare_form_data({
            "state_code": state_code,
            "dist_code": district_code,
            "court_complex_code": complex_id,
            "est_code": est_code or ""
        })

        url = f"{self.base_url}/?p=courtorder/fillCourtNumber"
        response = await session.post(url, data=data)

        payload = self._parse_json_payload(response.text)
        self._update_app_token(payload)

        courts: List[Dict[str, str]] = []
        options_html = payload.get("courtnumber_list", "")
        soup = BeautifulSoup(options_html, 'html.parser')

        for option in soup.find_all('option'):
            value = option.get('value', '').strip()
            text = option.text.strip()
            if not value or value.upper() == 'D' or 'Select Court' in text:
                continue
            courts.append({
                "code": value,
                "name": text
            })

        return courts

    async def fetch_courts(self, state_code: str, district_code: str, complex_code: str) -> List[Dict[str, str]]:
        """Fetch individual courts for a given court complex"""
        try:
            session = await self._get_session()

            complex_parts = self._extract_complex_parts(complex_code)
            est_codes = complex_parts["est_codes"] or [None]

            courts: List[Dict[str, str]] = []
            for est_code in est_codes:
                try:
                    courts.extend(
                        await self._fetch_court_numbers(
                            session,
                            state_code,
                            district_code,
                            complex_code,
                            est_code
                        )
                    )
                except Exception as inner_exc:
                    print(f"[WARN] Failed to fetch court numbers for establishment {est_code}: {inner_exc}")

            # Deduplicate while preserving order
            unique_courts: Dict[str, Dict[str, str]] = {}
            for court in courts:
                unique_courts.setdefault(court["code"], court)

            return list(unique_courts.values())
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

    async def fetch_cause_list_captcha(self) -> Optional[Dict[str, str]]:
        """Retrieve a new captcha image and optional audio link for cause list submission."""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/?p=casestatus/getCaptcha"
            response = await session.post(url, data=self._prepare_form_data({}), timeout=None)

            payload = self._parse_json_payload(response.text)
            if not payload:
                return None

            self._update_app_token(payload)

            div_html = payload.get("div_captcha", "")
            if not div_html:
                return None

            soup = BeautifulSoup(div_html, 'html.parser')
            img_tag = soup.find('img', {'id': 'captcha_image'}) or soup.find('img')
            if not img_tag:
                return None

            img_src = img_tag.get('src', '')
            if not img_src:
                return None

            root_base = self.base_url.split('/ecourtindia_v6')[0] or self.base_url
            img_url = urljoin(f"{root_base}/", img_src.lstrip('/'))
            img_response = await session.get(img_url)
            img_response.raise_for_status()

            image_data = base64.b64encode(img_response.content).decode('utf-8')

            audio_link = None
            audio_anchor = soup.find('a', {'class': 'captcha_play_button'})
            if audio_anchor:
                href = audio_anchor.get('href')
                if href:
                    audio_link = urljoin(f"{root_base}/", href.lstrip('/'))

            return {
                "image": f"data:image/png;base64,{image_data}",
                "audio": audio_link
            }
        except Exception as exc:
            print(f"[ERROR] Unable to fetch cause list captcha: {exc}")
            return None

    async def fetch_cause_list(
        self,
        state_code: str,
        district_code: str,
        court_complex_code: str,
        court_code: Optional[str],
        date: str,
        captcha_code: str,
        cause_type: str = "civ",
        court_name: Optional[str] = None
    ) -> Dict:
        """Fetch cause list for a specific court and date"""
        try:
            session = await self._get_session()

            if not court_code:
                return {
                    "error": "Court selection is required for cause list download.",
                    "cases": [],
                    "metadata": {
                        "state_code": state_code,
                        "district_code": district_code,
                        "court_complex_code": court_complex_code,
                        "court_code": court_code,
                        "date": date,
                        "cause_type": cause_type,
                        "fetched_at": datetime.now().isoformat()
                    }
                }

            complex_parts = self._extract_complex_parts(court_complex_code)
            complex_id = complex_parts["id"]
            flag = complex_parts.get("flag")

            # Ensure date is dd-mm-yyyy
            formatted_date = date
            if '-' in date:
                pieces = date.split('-')
                if len(pieces[0]) == 4:
                    formatted_date = f"{pieces[2]}-{pieces[1]}-{pieces[0]}"

            try:
                selected_date = datetime.strptime(formatted_date, "%d-%m-%Y")
            except ValueError:
                selected_date = datetime.now()

            today = datetime.now()
            days_difference = (today.date() - selected_date.date()).days
            selprevdays = "1" if days_difference >= 1 else "0"

            est_code = ""
            if flag == "Y" and court_code:
                est_code = court_code.split("$")[0]

            payload_data = {
                "state_code": state_code,
                "dist_code": district_code,
                "court_complex_code": complex_id,
                "est_code": est_code,
                "CL_court_no": court_code,
                "causelist_date": formatted_date,
                "cause_list_captcha_code": captcha_code,
                "fcaptcha_code": captcha_code,
                "cicri": cause_type,
                "selprevdays": selprevdays,
                "court_name_txt": court_name or ""
            }

            url = f"{self.base_url}/?p=cause_list/submitCauseList"
            response = await session.post(url, data=self._prepare_form_data(payload_data))

            payload = self._parse_json_payload(response.text)
            self._update_app_token(payload)

            metadata = {
                "state_code": state_code,
                "district_code": district_code,
                "court_complex_code": complex_id,
                "court_code": court_code,
                "date": formatted_date,
                "cause_type": cause_type,
                "court_name": court_name,
                "fetched_at": datetime.now().isoformat()
            }

            if not payload:
                raw_content = response.content[:200]
                snippet = response.text[:200]
                print(f"[WARN] Cause list response not in JSON format. Status={response.status_code} TextLen={len(response.text)} ContentLen={len(response.content)} Snippet repr={repr(snippet)} Raw repr={repr(raw_content)} Headers={dict(response.headers)}")
                self._capture_app_token_from_html(response.text)
                return {
                    "error": "Unable to process cause list response.",
                    "cases": [],
                    "metadata": metadata
                }

            status = payload.get("status")
            error_messages: List[str] = []

            if status != 1:
                err_html = payload.get("errormsg") or payload.get("message")
                if err_html:
                    err_text = BeautifulSoup(err_html, 'html.parser').get_text().strip()
                    if err_text:
                        error_messages.append(err_text)
                # when status not 1, still return any partial metadata
                result = {
                    "error": error_messages[0] if error_messages else "Cause list request was rejected.",
                    "cases": [],
                    "metadata": metadata
                }
                if error_messages:
                    result["errors"] = error_messages
                next_captcha = await self.fetch_cause_list_captcha()
                if next_captcha:
                    result["next_captcha"] = next_captcha
                return result

            case_html = payload.get("case_data", "")
            parsed = self._parse_cause_list(case_html)
            parsed["metadata"] = metadata

            if payload.get("div_captcha"):
                next_captcha = await self.fetch_cause_list_captcha()
                if next_captcha:
                    parsed["next_captcha"] = next_captcha

            return parsed
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

            complex_parts = self._extract_complex_parts(court_complex_code)
            complex_id = complex_parts["id"]

            formatted_date = date
            if '-' in date:
                pieces = date.split('-')
                if len(pieces[0]) == 4:
                    formatted_date = f"{pieces[2]}-{pieces[1]}-{pieces[0]}"

            url = f"{self.base_url}/ajax/download_cause_list_pdf.php"
            data = self._prepare_form_data({
                "state_code": state_code,
                "dist_code": district_code,
                "court_complex_code": complex_id,
                "date": formatted_date
            })

            if court_code:
                data["court_code"] = court_code

            response = await session.post(url, data=data)

            if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                os.makedirs('downloads', exist_ok=True)

                filename = f"cause_list_{state_code}_{district_code}_{complex_id}_{formatted_date.replace('-', '')}.pdf"
                filepath = os.path.join('downloads', filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                return filepath

            return None
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None
