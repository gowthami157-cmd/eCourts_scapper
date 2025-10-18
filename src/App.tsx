import { useState } from 'react';
import { Scale } from 'lucide-react';
import { CourtSelector } from './components/CourtSelector';
import { CaseSearch } from './components/CaseSearch';
import { CauseList } from './components/CauseList';
import { State, District, CourtComplex, Court } from './services/api';

function App() {
  const [selectedState, setSelectedState] = useState<State | undefined>();
  const [selectedDistrict, setSelectedDistrict] = useState<District | undefined>();
  const [selectedComplex, setSelectedComplex] = useState<CourtComplex | undefined>();
  const [selectedCourt, setSelectedCourt] = useState<Court | undefined>();

  const handleSelectionChange = (selection: {
    state?: State;
    district?: District;
    complex?: CourtComplex;
    court?: Court;
  }) => {
    setSelectedState(selection.state);
    setSelectedDistrict(selection.district);
    setSelectedComplex(selection.complex);
    setSelectedCourt(selection.court);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Scale className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">eCourts Scraper</h1>
              <p className="text-sm text-slate-600">
                Real-time access to Indian eCourts case listings and cause lists
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Court Selection</h2>
              <CourtSelector onSelectionChange={handleSelectionChange} />

              {selectedState && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Current Selection</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">State:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedState.name}</span>
                    </div>
                    {selectedDistrict && (
                      <div>
                        <span className="text-gray-600">District:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedDistrict.name}</span>
                      </div>
                    )}
                    {selectedComplex && (
                      <div>
                        <span className="text-gray-600">Complex:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedComplex.name}</span>
                      </div>
                    )}
                    {selectedCourt && (
                      <div>
                        <span className="text-gray-600">Court:</span>
                        <span className="ml-2 font-medium text-gray-900">{selectedCourt.name}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-2 space-y-8">
            <CaseSearch
              selectedState={selectedState}
              selectedDistrict={selectedDistrict}
              selectedCourt={selectedCourt}
            />

            <CauseList
              selectedState={selectedState}
              selectedDistrict={selectedDistrict}
              selectedComplex={selectedComplex}
              selectedCourt={selectedCourt}
            />
          </div>
        </div>
      </main>

      <footer className="mt-16 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center text-sm text-slate-600">
            <p>eCourts Scraper - Fetch case details and cause lists from Indian eCourts</p>
            <p className="mt-1">
              Data source:{' '}
              <a
                href="https://services.ecourts.gov.in/ecourtindia_v6/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                eCourts India
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
