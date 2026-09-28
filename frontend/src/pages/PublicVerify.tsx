import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, XCircle, AlertTriangle, ShieldCheck, Download, 
  Calendar, MapPin, Award, Scale, Cpu, Search, Lock, ArrowLeft, RefreshCw 
} from 'lucide-react';
import { ApiClient } from '../api/client';
import { PublicVerification } from '../types';

export const PublicVerify: React.FC = () => {
  const params = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  // Extract certificate number from params (:certNo, wildcard *), path, or query string
  const queryParam = new URLSearchParams(location.search).get('cert') || new URLSearchParams(location.search).get('q');
  const pathParam = params.certNo || params['*'] || location.pathname.replace(/^\/verify\/?/, '');
  const activeCertNo = queryParam || (pathParam ? decodeURIComponent(pathParam).trim() : '');

  const [data, setData] = useState<PublicVerification | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(!!activeCertNo);
  const [searchInput, setSearchInput] = useState<string>(activeCertNo);

  const loadVerification = async (numberToVerify: string) => {
    if (!numberToVerify.trim()) return;
    setIsLoading(true);
    try {
      const res = await ApiClient.verifyPublic(numberToVerify.trim());
      setData(res);
    } catch (err) {
      setData({
        is_valid: false,
        status: 'NOT_FOUND',
        certificate_number: numberToVerify,
        message: 'Could not connect to the verification registry or record not found.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeCertNo) {
      setSearchInput(activeCertNo);
      loadVerification(activeCertNo);
    }
  }, [activeCertNo]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      navigate(`/verify/${encodeURIComponent(searchInput.trim())}`);
    }
  };

  const handleQuickVerify = (sample: string) => {
    setSearchInput(sample);
    navigate(`/verify/${encodeURIComponent(sample)}`);
  };

  return (
    <div className="min-h-screen bg-slate-100 py-10 px-4 sm:px-6 lg:px-8 flex flex-col items-center">
      <div className="w-full max-w-3xl space-y-6">
        {/* Top Back Link & Search */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <Link to="/" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" /> Back to Home Portal
          </Link>
          <form onSubmit={handleSearchSubmit} className="flex gap-2 w-full sm:w-auto">
            <input
              type="text"
              placeholder="Search Certificate No. (e.g. 141701 or 520900)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="text-xs px-3 py-2 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 w-full sm:w-64"
            />
            <button
              type="submit"
              className="px-3 py-2 bg-[#0F2942] text-white text-xs font-semibold rounded-lg hover:bg-slate-800 shrink-0"
            >
              Verify
            </button>
          </form>
        </div>

        {/* Quick Sample Selector Bar */}
        <div className="bg-white px-4 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-600 flex flex-wrap items-center justify-between gap-2 shadow-xs">
          <span className="font-semibold text-slate-700">Verified Test Samples:</span>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleQuickVerify("141701")}
              className="px-2 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold border border-blue-200"
            >
              141701 (State Record)
            </button>
            <button
              onClick={() => handleQuickVerify("141710")}
              className="px-2 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold border border-blue-200"
            >
              141710 (State Record)
            </button>
            <button
              onClick={() => handleQuickVerify("LM/JH/2026/520900")}
              className="px-2 py-1 rounded bg-emerald-50 text-emerald-800 hover:bg-emerald-100 font-semibold border border-emerald-200"
            >
              LM/JH/2026/520900 (QR Digital)
            </button>
            <button
              onClick={() => handleQuickVerify("520900")}
              className="px-2 py-1 rounded bg-slate-100 text-slate-700 hover:bg-slate-200 font-semibold border border-slate-200"
            >
              520900
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center shadow-sm">
            <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <h3 className="font-bold text-slate-800 text-base">Verifying Certificate Authenticity...</h3>
            <p className="text-xs text-slate-500 mt-1">Checking central Legal Metrology repository & cryptographic hash...</p>
          </div>
        ) : !data || data.status === 'NOT_FOUND' ? (
          <div className="bg-white rounded-2xl p-8 border border-red-200 shadow-sm text-center">
            <div className="w-14 h-14 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="h-8 w-8" />
            </div>
            <h2 className="text-xl font-extrabold text-slate-900">Certificate Not Found or Unverified</h2>
            <p className="text-sm text-slate-600 mt-2 max-w-md mx-auto">
              No official Legal Metrology verification record was found for <span className="font-mono font-bold text-slate-900">"{activeCertNo || searchInput || 'Query'}"</span>.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2 text-xs">
              <span className="text-slate-500">Try verifying one of these valid sample records:</span>
              <button
                onClick={() => handleQuickVerify("141701")}
                className="text-blue-600 font-bold underline"
              >
                141701
              </button>
              <span>•</span>
              <button
                onClick={() => handleQuickVerify("LM/JH/2026/520900")}
                className="text-emerald-700 font-bold underline"
              >
                LM/JH/2026/520900
              </button>
            </div>
            <div className="mt-6 p-4 bg-rose-50 border border-rose-100 rounded-xl text-xs text-rose-800 text-left max-w-md mx-auto">
              <strong>Caution:</strong> Weighing and measuring instruments without verified statutory certification may be non-compliant under the Legal Metrology Act, 2009.
            </div>
          </div>
        ) : (
          /* Valid / Verified Certificate Card */
          <div className="bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden">
            {/* Header Status Banner */}
            <div className={`p-6 text-white ${data.is_valid ? 'bg-gradient-to-r from-emerald-700 to-teal-800' : 'bg-gradient-to-r from-amber-700 to-orange-800'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {data.is_valid ? (
                    <div className="p-2 bg-white/20 rounded-xl">
                      <CheckCircle2 className="h-8 w-8 text-white" />
                    </div>
                  ) : (
                    <div className="p-2 bg-white/20 rounded-xl">
                      <AlertTriangle className="h-8 w-8 text-white" />
                    </div>
                  )}
                  <div>
                    <span className="text-xs uppercase font-bold tracking-widest text-emerald-200">
                      {data.is_valid ? 'Official Verification Status' : 'Verification Warning'}
                    </span>
                    <h2 className="text-2xl font-black tracking-tight">
                      {data.status === 'VALID' ? 'CERTIFICATE VALID & VERIFIED' : data.status}
                    </h2>
                  </div>
                </div>
                <div className="text-right hidden sm:block">
                  <span className="text-xs text-slate-200 block">Certificate Number</span>
                  <span className="font-mono font-bold text-base text-amber-300">{data.certificate_number}</span>
                </div>
              </div>
            </div>

            {/* Content Details */}
            <div className="p-6 sm:p-8 space-y-6">
              {/* Key Specs Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50 p-5 rounded-xl border border-slate-200">
                <div>
                  <span className="text-[11px] font-semibold uppercase text-slate-500 block">Instrument Category</span>
                  <span className="text-sm font-bold text-slate-900 flex items-center gap-1.5 mt-0.5">
                    <Scale className="h-4 w-4 text-blue-700" /> {data.instrument_category}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] font-semibold uppercase text-slate-500 block">Manufacturer & Model</span>
                  <span className="text-sm font-bold text-slate-900 mt-0.5 block">
                    {data.manufacturer} ({data.instrument_model})
                  </span>
                </div>
                <div>
                  <span className="text-[11px] font-semibold uppercase text-slate-500 block">Serial Number</span>
                  <span className="text-sm font-mono font-bold text-slate-900 mt-0.5 block">
                    {data.serial_number}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] font-semibold uppercase text-slate-500 block">Capacity & Accuracy Class</span>
                  <span className="text-sm font-bold text-slate-900 mt-0.5 block">
                    Max: {data.capacity} | {data.accuracy_class}
                  </span>
                </div>
              </div>

              {/* Verification & Validity Metadata */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl border border-slate-200 bg-white">
                  <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold mb-1">
                    <Calendar className="h-4 w-4 text-slate-600" /> Date of Verification
                  </div>
                  <div className="font-bold text-sm text-slate-900">{data.verification_date}</div>
                </div>

                <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50">
                  <div className="flex items-center gap-2 text-emerald-800 text-xs font-semibold mb-1">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" /> Valid Until
                  </div>
                  <div className="font-bold text-sm text-emerald-950">{data.valid_until}</div>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 bg-white">
                  <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold mb-1">
                    <MapPin className="h-4 w-4 text-slate-600" /> Verification Location
                  </div>
                  <div className="font-bold text-sm text-slate-900 truncate">{data.verification_location}</div>
                </div>
              </div>

              {/* Inspection Officer & Authority */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div>
                  <span className="text-xs font-semibold text-slate-500 uppercase block">Issuing Authority & Officer</span>
                  <span className="text-sm font-bold text-slate-900">{data.issuing_officer}</span>
                  <span className="text-xs text-slate-500 block">{data.issuing_authority}</span>
                </div>
                <div className={`p-2 rounded-lg text-xs font-bold flex items-center gap-1 ${
                  data.record_integrity_verified ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                }`}>
                  <ShieldCheck className="h-4 w-4" />
                  {data.record_integrity_verified ? 'Record Integrity Verified' : 'Integrity Mismatch'}
                </div>
              </div>

              {/* Statutory DoCA Model Approval Reference Layer */}
              {data.model_approval_reference && (
                <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-blue-900 flex items-center gap-1.5">
                      <Cpu className="h-4 w-4 text-blue-700" />
                      Statutory DoCA Model Approval Reference
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                      Layer A Reference
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-slate-500 block">Approval Mark / Certificate:</span>
                      <span className="font-mono font-bold text-slate-900">
                        {data.model_approval_reference.approval_mark || data.model_approval_reference.certificate_no || 'Central DoCA Approved'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Approved Specifications:</span>
                      <span className="font-semibold text-slate-900">
                        {data.model_approval_reference.accuracy_class} | Max: {data.model_approval_reference.max_capacity} (e = {data.model_approval_reference.verification_scale_interval})
                      </span>
                    </div>
                  </div>
                  {data.model_approval_reference.source_pdf && (
                    <div className="pt-1">
                      <a
                        href={`http://127.0.0.1:8000/api/instruments/models/${data.model_approval_reference.model_id}/source-pdf`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-bold text-blue-700 hover:text-blue-900 underline"
                      >
                        <Award className="h-3.5 w-3.5" /> View Official Gazette PDF Certificate
                      </a>
                    </div>
                  )}
                </div>
              )}

              {/* Test Observations Summary */}
              {data.tests_summary && data.tests_summary.length > 0 && (
                <div>
                  <h4 className="font-bold text-sm text-slate-900 mb-2">Statutory Field Observations & MPE Tolerances</h4>
                  <div className="border border-slate-200 rounded-xl overflow-hidden">
                    <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                      <thead className="bg-slate-100 text-slate-700 font-semibold">
                        <tr>
                          <th className="px-4 py-2.5">Test Procedure</th>
                          <th className="px-4 py-2.5">Test Load</th>
                          <th className="px-4 py-2.5">Observed</th>
                          <th className="px-4 py-2.5">Error</th>
                          <th className="px-4 py-2.5">MPE Limit</th>
                          <th className="px-4 py-2.5">Result</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 bg-white font-medium">
                        {data.tests_summary.map((t, idx) => (
                          <tr key={idx}>
                            <td className="px-4 py-2 font-semibold text-slate-900">{t.test_name}</td>
                            <td className="px-4 py-2 text-slate-600">{t.test_load}</td>
                            <td className="px-4 py-2 text-slate-600">{t.observed_value}</td>
                            <td className="px-4 py-2 text-slate-900">{t.error}</td>
                            <td className="px-4 py-2 text-slate-600">{t.tolerance_mpe}</td>
                            <td className="px-4 py-2 text-emerald-700 font-bold">{t.result}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Cryptographic Hash Verification Box */}
              <div className="space-y-1.5">
                <div className={`p-3 rounded-xl text-[11px] font-mono flex items-center justify-between overflow-hidden ${
                  data.record_integrity_verified ? 'bg-slate-900 text-slate-300' : 'bg-rose-950 text-rose-200'
                }`}>
                  <div className="flex items-center gap-2 truncate">
                    <Lock className={`h-3.5 w-3.5 shrink-0 ${data.record_integrity_verified ? 'text-amber-400' : 'text-rose-400'}`} />
                    <span className="truncate">SHA-256: {data.certificate_hash}</span>
                  </div>
                  <span className={`shrink-0 font-bold ml-2 ${
                    data.record_integrity_verified ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {data.record_integrity_verified ? 'RECORD INTEGRITY VERIFIED' : 'TAMPER DETECTED'}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 italic text-center">
                  {data.disclaimer || 'Application-level cryptographic SHA-256 fingerprint verification (Tamper Detection). Not a government PKI digital signature.'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
