import { useState } from 'react';
import { Search, AlertCircle, CheckCircle, Calendar } from 'lucide-react';
import { apiService, CaseSearchResult, State, District, Court } from '../services/api';

interface CaseSearchProps {
  selectedState?: State;
  selectedDistrict?: District;
  selectedCourt?: Court;
}

export function CaseSearch({ selectedState, selectedDistrict, selectedCourt }: CaseSearchProps) {
  const [searchType, setSearchType] = useState<'cnr' | 'details'>('cnr');
  const [cnr, setCnr] = useState('');
  const [caseType, setCaseType] = useState('');
  const [caseNumber, setCaseNumber] = useState('');
  const [caseYear, setCaseYear] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CaseSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      let searchResult: CaseSearchResult;

      if (searchType === 'cnr') {
        if (!cnr.trim()) {
          setError('Please enter CNR number');
          return;
        }
        searchResult = await apiService.searchByCNR(
          cnr,
          selectedState?.code,
          selectedDistrict?.code
        );
      } else {
        if (!selectedState || !selectedDistrict || !selectedCourt) {
          setError('Please select State, District, and Court');
          return;
        }
        if (!caseType || !caseNumber || !caseYear) {
          setError('Please fill all case details');
          return;
        }
        searchResult = await apiService.searchByDetails(
          selectedState.code,
          selectedDistrict.code,
          selectedCourt.code,
          caseType,
          caseNumber,
          caseYear
        );
      }

      setResult(searchResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Case Search</h2>

      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setSearchType('cnr')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
            searchType === 'cnr'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Search by CNR
        </button>
        <button
          onClick={() => setSearchType('details')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
            searchType === 'details'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Search by Details
        </button>
      </div>

      {searchType === 'cnr' ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CNR Number
            </label>
            <input
              type="text"
              value={cnr}
              onChange={(e) => setCnr(e.target.value)}
              placeholder="Enter CNR number"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Case Type
              </label>
              <input
                type="text"
                value={caseType}
                onChange={(e) => setCaseType(e.target.value)}
                placeholder="e.g., CS"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Case Number
              </label>
              <input
                type="text"
                value={caseNumber}
                onChange={(e) => setCaseNumber(e.target.value)}
                placeholder="e.g., 1234"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Case Year
              </label>
              <input
                type="text"
                value={caseYear}
                onChange={(e) => setCaseYear(e.target.value)}
                placeholder="e.g., 2024"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      )}

      <button
        onClick={handleSearch}
        disabled={loading}
        className="mt-6 w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
      >
        <Search className="w-5 h-5" />
        {loading ? 'Searching...' : 'Search Case'}
      </button>

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="mt-6 border border-gray-200 rounded-lg p-4">
          {result.found ? (
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-green-700 mb-2">Case Found</h3>

                  {(result.listed_today || result.listed_tomorrow) && (
                    <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center gap-2 text-yellow-800 font-medium">
                        <Calendar className="w-5 h-5" />
                        {result.listed_today ? 'Listed TODAY' : 'Listed TOMORROW'}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    {result.serial_number && (
                      <div className="flex">
                        <span className="font-medium text-gray-700 w-40">Serial Number:</span>
                        <span className="text-gray-900">{result.serial_number}</span>
                      </div>
                    )}
                    {result.court_name && (
                      <div className="flex">
                        <span className="font-medium text-gray-700 w-40">Court:</span>
                        <span className="text-gray-900">{result.court_name}</span>
                      </div>
                    )}
                    {result.next_hearing_date && (
                      <div className="flex">
                        <span className="font-medium text-gray-700 w-40">Next Hearing:</span>
                        <span className="text-gray-900">{result.next_hearing_date}</span>
                      </div>
                    )}
                    {result.case_status && (
                      <div className="flex">
                        <span className="font-medium text-gray-700 w-40">Status:</span>
                        <span className="text-gray-900">{result.case_status}</span>
                      </div>
                    )}
                  </div>

                  {Object.keys(result.details).length > 0 && (
                    <details className="mt-4">
                      <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                        View Full Details
                      </summary>
                      <div className="mt-2 p-3 bg-gray-50 rounded text-sm">
                        <pre className="whitespace-pre-wrap">
                          {JSON.stringify(result.details, null, 2)}
                        </pre>
                      </div>
                    </details>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-gray-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-gray-700 mb-1">Case Not Found</h3>
                <p className="text-gray-600">
                  The case is not listed for today or tomorrow, or could not be found in the system.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
