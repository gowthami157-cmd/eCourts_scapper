import { useState, useEffect } from 'react';
import { Download, FileText, Calendar as CalendarIcon, AlertCircle, RefreshCw, Volume2 } from 'lucide-react';
import { apiService, CauseList as CauseListType, State, District, CourtComplex, Court } from '../services/api';

interface CauseListProps {
  selectedState?: State;
  selectedDistrict?: District;
  selectedComplex?: CourtComplex;
  selectedCourt?: Court;
}

export function CauseList({ selectedState, selectedDistrict, selectedComplex, selectedCourt }: CauseListProps) {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [causeList, setCauseList] = useState<CauseListType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [captchaImage, setCaptchaImage] = useState<string | null>(null);
  const [captchaAudio, setCaptchaAudio] = useState<string | null>(null);
  const [captchaCode, setCaptchaCode] = useState('');
  const [causeType, setCauseType] = useState<'civ' | 'cri'>('civ');

  const formatDateForApi = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-');
    return `${day}-${month}-${year}`;
  };

  const loadCaptcha = async (quiet = false) => {
    if (!selectedState || !selectedDistrict || !selectedComplex) {
      setCaptchaImage(null);
      setCaptchaAudio(null);
      setCaptchaCode('');
      return;
    }

    try {
      const payload = await apiService.getCauseListCaptcha();
      setCaptchaImage(payload.image);
      setCaptchaAudio(payload.audio ?? null);
      setCaptchaCode('');
      if (!quiet) {
        setWarning(null);
      }
    } catch (err) {
      console.error(err);
      if (!quiet) {
        setWarning('Unable to load captcha from eCourts. Please try again.');
      }
    }
  };

  useEffect(() => {
    if (selectedState && selectedDistrict && selectedComplex) {
      loadCaptcha();
    } else {
      setCaptchaImage(null);
      setCaptchaAudio(null);
      setCaptchaCode('');
    }
  }, [selectedState, selectedDistrict, selectedComplex]);

  const handleFetchCauseList = async () => {
    if (!selectedState || !selectedDistrict || !selectedComplex) {
      setError('Please select State, District, and Court Complex');
      return;
    }
    if (!selectedCourt) {
      setError('Please select a court before fetching the cause list');
      return;
    }
    if (!captchaCode.trim()) {
      setError('Please enter the captcha shown above');
      return;
    }

    setError(null);
    setWarning(null);
    setCauseList(null);
    setLoading(true);

    try {
      const formattedDate = formatDateForApi(date);
      const result = await apiService.getCauseList(
        selectedState.code,
        selectedDistrict.code,
        selectedComplex.code,
        selectedCourt.code,
        formattedDate,
        captchaCode.trim(),
        causeType,
        selectedCourt.name
      );
      const hasPortalError = Boolean(result.error || (result.errors && result.errors.length));
      if (hasPortalError) {
        const message = [result.error, ...(result.errors ?? [])].filter(Boolean).join(' ');
        setWarning(message || 'The eCourts portal rejected the request. Please re-enter the captcha and try again.');
        setCauseList(null);
      } else {
        setWarning(null);
        setCauseList(result);
      }
      if (result.next_captcha) {
        setCaptchaImage(result.next_captcha.image);
        setCaptchaAudio(result.next_captcha.audio ?? null);
        setCaptchaCode('');
      } else {
        await loadCaptcha(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cause list');
      await loadCaptcha(true);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    if (!selectedState || !selectedDistrict || !selectedComplex || !selectedCourt) {
      setError('Please select a court before downloading the PDF');
      return;
    }

    const formattedDate = formatDateForApi(date);
    const url = apiService.getDownloadPdfUrl(
      selectedState.code,
      selectedDistrict.code,
      selectedComplex.code,
      selectedCourt.code,
      formattedDate
    );

    window.open(url, '_blank');
  };
  const handleDownloadJson = () => {
    if (!causeList) return;

    const dataStr = JSON.stringify(causeList, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cause_list_${date}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Cause List</h2>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Date
          </label>
          <div className="relative">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setDate(new Date().toISOString().split('T')[0])}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Today
          </button>
          <button
            onClick={() => {
              const tomorrow = new Date();
              tomorrow.setDate(tomorrow.getDate() + 1);
              setDate(tomorrow.toISOString().split('T')[0]);
            }}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Tomorrow
          </button>
        </div>

        <div className="grid gap-3 lg:grid-cols-[auto,1fr] lg:items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Captcha
            </label>
            {captchaImage ? (
              <div className="flex items-center gap-3">
                <img
                  src={captchaImage}
                  alt="eCourts Captcha"
                  className="h-12 w-auto rounded border border-gray-300 bg-white p-1"
                />
                <button
                  type="button"
                  onClick={loadCaptcha}
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
                {captchaAudio && (
                  <a
                    href={captchaAudio}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded transition-colors"
                  >
                    <Volume2 className="w-4 h-4" />
                    Audio
                  </a>
                )}
              </div>
            ) : (
              <button
                type="button"
                onClick={loadCaptcha}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Load Captcha
              </button>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter Captcha <span className="text-gray-500 text-xs">(match case exactly)</span>
            </label>
            <input
              type="text"
              value={captchaCode}
              onChange={(e) => setCaptchaCode(e.target.value)}
              maxLength={6}
              placeholder="Enter captcha"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent tracking-widest"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setCauseType('civ')}
            className={`px-4 py-2 rounded-lg transition-colors font-medium ${
              causeType === 'civ'
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Civil
          </button>
          <button
            type="button"
            onClick={() => setCauseType('cri')}
            className={`px-4 py-2 rounded-lg transition-colors font-medium ${
              causeType === 'cri'
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Criminal
          </button>
        </div>
      </div>

      <button
        onClick={handleFetchCauseList}
        disabled={
          loading ||
          !selectedState ||
          !selectedDistrict ||
          !selectedComplex ||
          !selectedCourt ||
          !captchaImage
        }
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
      >
        <FileText className="w-5 h-5" />
        {loading ? 'Fetching...' : 'Fetch Cause List'}
      </button>

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {warning && (
        <div className="mt-4 flex items-start gap-3 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
          <AlertCircle className="w-5 h-5 mt-0.5 text-yellow-600 flex-shrink-0" />
          <div>
            <p className="font-medium">Portal response</p>
            <p className="text-sm mt-1 whitespace-pre-wrap">{warning}</p>
          </div>
        </div>
      )}

      {causeList && (
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-bold text-gray-800">Total Cases</h3>
              <p className="text-3xl font-bold text-blue-600">{causeList.total_cases}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleDownloadJson}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                JSON
              </button>
              <button
                onClick={handleDownloadPdf}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                PDF
              </button>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Sr. No.</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Case Number</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Parties</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Advocate</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Purpose</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {causeList.cases.map((caseItem, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">{caseItem.serial_number}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{caseItem.case_number}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{caseItem.parties}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{caseItem.advocate}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{caseItem.purpose}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
