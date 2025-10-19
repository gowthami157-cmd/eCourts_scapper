import { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import { apiService, State, District, CourtComplex, Court } from '../services/api';

interface CourtSelectorProps {
  onSelectionChange: (selection: {
    state?: State;
    district?: District;
    complex?: CourtComplex;
    court?: Court;
  }) => void;
}

export function CourtSelector({ onSelectionChange }: CourtSelectorProps) {
  const [states, setStates] = useState<State[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [complexes, setComplexes] = useState<CourtComplex[]>([]);
  const [courts, setCourts] = useState<Court[]>([]);

  const [selectedState, setSelectedState] = useState<State | undefined>();
  const [selectedDistrict, setSelectedDistrict] = useState<District | undefined>();
  const [selectedComplex, setSelectedComplex] = useState<CourtComplex | undefined>();
  const [selectedCourt, setSelectedCourt] = useState<Court | undefined>();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStates();
  }, []);

  useEffect(() => {
    onSelectionChange({
      state: selectedState,
      district: selectedDistrict,
      complex: selectedComplex,
      court: selectedCourt,
    });
  }, [selectedState, selectedDistrict, selectedComplex, selectedCourt]);

  const loadStates = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getStates();
      setStates(data);
    } catch (err) {
      setError('Failed to load states');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = async (stateCode: string) => {
    const state = states.find(s => s.code === stateCode);
    setSelectedState(state);
    setSelectedDistrict(undefined);
    setSelectedComplex(undefined);
    setSelectedCourt(undefined);
    setDistricts([]);
    setComplexes([]);
    setCourts([]);

    if (!state) return;

    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getDistricts(stateCode);
      setDistricts(data);
    } catch (err) {
      setError('Failed to load districts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDistrictChange = async (districtCode: string) => {
    const district = districts.find(d => d.code === districtCode);
    setSelectedDistrict(district);
    setSelectedComplex(undefined);
    setSelectedCourt(undefined);
    setComplexes([]);
    setCourts([]);

    if (!district || !selectedState) return;

    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getCourtComplexes(selectedState.code, districtCode);
      setComplexes(data);
    } catch (err) {
      setError('Failed to load court complexes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleComplexChange = async (complexCode: string) => {
    const complex = complexes.find(c => c.code === complexCode);
    setSelectedComplex(complex);
    setSelectedCourt(undefined);
    setCourts([]);

    if (!complex || !selectedState || !selectedDistrict) return;

    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getCourts(selectedState.code, selectedDistrict.code, complexCode);
      setCourts(data);
      if (data.length) {
        setSelectedCourt(data[0]);
      }
    } catch (err) {
      setError('Failed to load courts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCourtChange = (courtCode: string) => {
    const court = courts.find(c => c.code === courtCode);
    setSelectedCourt(court);
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          State
        </label>
        <div className="relative">
          <select
            value={selectedState?.code || ''}
            onChange={(e) => handleStateChange(e.target.value)}
            disabled={loading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          >
            <option value="">Select State</option>
            {states.map((state) => (
              <option key={state.code} value={state.code}>
                {state.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
        </div>
      </div>

      {selectedState && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            District
          </label>
          <div className="relative">
            <select
              value={selectedDistrict?.code || ''}
              onChange={(e) => handleDistrictChange(e.target.value)}
              disabled={loading || !districts.length}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            >
              <option value="">Select District</option>
              {districts.map((district) => (
                <option key={district.code} value={district.code}>
                  {district.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>
      )}

      {selectedDistrict && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Court Complex
          </label>
          <div className="relative">
            <select
              value={selectedComplex?.code || ''}
              onChange={(e) => handleComplexChange(e.target.value)}
              disabled={loading || !complexes.length}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            >
              <option value="">Select Court Complex</option>
              {complexes.map((complex) => (
                <option key={complex.code} value={complex.code}>
                  {complex.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>
      )}

      {selectedComplex && courts.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Court (Required for cause list)
          </label>
          <div className="relative">
            <select
              value={selectedCourt?.code || ''}
              onChange={(e) => handleCourtChange(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            >
              <option value="">Select Court</option>
              {courts.map((court) => (
                <option key={court.code} value={court.code}>
                  {court.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>
      )}
    </div>
  );
}
