const API_BASE_URL = 'http://localhost:8000/api';

export interface State {
  code: string;
  name: string;
}

export interface District {
  code: string;
  name: string;
}

export interface CourtComplex {
  code: string;
  name: string;
}

export interface Court {
  code: string;
  name: string;
}

export interface CaseSearchResult {
  case_id: string;
  search_type: string;
  cnr?: string;
  case_details?: any;
  found: boolean;
  listed_today: boolean;
  listed_tomorrow: boolean;
  serial_number?: string;
  court_name?: string;
  next_hearing_date?: string;
  case_status?: string;
  details: any;
}

export interface CauseList {
  total_cases: number;
  cases: Array<{
    serial_number: string;
    case_number: string;
    parties: string;
    advocate: string;
    purpose: string;
  }>;
  metadata: {
    state_code: string;
    district_code: string;
    court_complex_code: string;
    court_code?: string;
    court_name?: string | null;
    cause_type?: string;
    date: string;
    fetched_at: string;
  };
  error?: string;
  errors?: string[];
  next_captcha?: Captcha;
}

export interface Captcha {
  image: string;
  audio?: string | null;
}

class ApiService {
  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    const data = await response.json();
    return data.data || data;
  }

  async getStates(): Promise<State[]> {
    return this.fetchApi<State[]>('/states');
  }

  async getDistricts(stateCode: string): Promise<District[]> {
    return this.fetchApi<District[]>(`/districts/${stateCode}`);
  }

  async getCourtComplexes(stateCode: string, districtCode: string): Promise<CourtComplex[]> {
    return this.fetchApi<CourtComplex[]>(`/court-complexes/${stateCode}/${districtCode}`);
  }

  async getCourts(stateCode: string, districtCode: string, complexCode: string): Promise<Court[]> {
    return this.fetchApi<Court[]>(`/courts/${stateCode}/${districtCode}/${complexCode}`);
  }

  async searchByCNR(cnr: string, stateCode?: string, districtCode?: string): Promise<CaseSearchResult> {
    return this.fetchApi<CaseSearchResult>('/search/cnr', {
      method: 'POST',
      body: JSON.stringify({ cnr, state_code: stateCode, district_code: districtCode }),
    });
  }

  async searchByDetails(
    stateCode: string,
    districtCode: string,
    courtCode: string,
    caseType: string,
    caseNumber: string,
    caseYear: string
  ): Promise<CaseSearchResult> {
    return this.fetchApi<CaseSearchResult>('/search/case', {
      method: 'POST',
      body: JSON.stringify({
        state_code: stateCode,
        district_code: districtCode,
        court_code: courtCode,
        case_type: caseType,
        case_number: caseNumber,
        case_year: caseYear,
      }),
    });
  }

  async getCauseList(
    stateCode: string,
    districtCode: string,
    courtComplexCode: string,
    courtCode: string | null,
    date: string,
    captchaCode: string,
    causeType: 'civ' | 'cri',
    courtName?: string | null
  ): Promise<CauseList> {
    return this.fetchApi<CauseList>('/cause-list', {
      method: 'POST',
      body: JSON.stringify({
        state_code: stateCode,
        district_code: districtCode,
        court_complex_code: courtComplexCode,
        court_code: courtCode,
        court_name: courtName,
        cause_type: causeType,
        captcha_code: captchaCode,
        date,
      }),
    });
  }

  async getCauseListCaptcha(): Promise<Captcha> {
    return this.fetchApi<Captcha>('/cause-list/captcha');
  }

  getDownloadPdfUrl(
    stateCode: string,
    districtCode: string,
    courtComplexCode: string,
    courtCode: string | null,
    date: string
  ): string {
    const params = new URLSearchParams({
      state_code: stateCode,
      district_code: districtCode,
      court_complex_code: courtComplexCode,
      date,
    });

    if (courtCode) {
      params.append('court_code', courtCode);
    }

    return `${API_BASE_URL}/download/pdf?${params.toString()}`;
  }
}

export const apiService = new ApiService();
