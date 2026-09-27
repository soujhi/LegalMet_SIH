import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  CheckCircle2, XCircle, AlertTriangle, ShieldCheck, Download, 
  Calendar, MapPin, Award, Scale, Cpu, Search, Lock, ArrowLeft 
} from 'lucide-react';
import { ApiClient } from '../api/client';
import { PublicVerification } from '../types';

export const PublicVerify: React.FC = () => {
  const { certNo } = useParams<{ certNo: string }>();
  const [data, setData] = useState<PublicVerification | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchInput, setSearchInput] = useState<string>(certNo || '');

  const loadVerification = async (numberToVerify: string) => {
    setIsLoading(true);
    try {
      const res = await ApiClient.verifyPublic(numberToVerify);
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
    if (certNo) {
      loadVerification(certNo);
    }
  }, [certNo]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      loadVerification(searchInput.trim());
    }
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
              placeholder="Search Certificate No..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="text-xs px-3 py-2 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
            <button
              type="submit"
              className="px-3 py-2 bg-[#0F2942] text-white text-xs font-semibold rounded-lg hover:bg-slate-800"
            >
              Verify
            </button>
          </form>
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
              No official Legal Metrology verification record was found for <span className="font-mono font-bold text-slate-900">"{certNo || searchInput}"</span>.
            </p>
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
                <div className="p-2 bg-emerald-100 text-emerald-800 rounded-lg text-xs font-bold flex items-center gap-1">
                  <ShieldCheck className="h-4 w-4" /> Digitally Authenticated
                </div>
              </div>

              {/* Test Observations Summary */}
              {data.tests_summary && data.tests_summary.length > 0 && (
                <div>
                  <h4 className="font-bold text-sm text-slate-900 mb-2">Statutory Field Observations</h4>
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

              {/* Cryptographic Hash */}
              <div className="p-3 bg-slate-900 text-slate-300 rounded-xl text-[11px] font-mono flex items-center justify-between overflow-hidden">
                <div className="flex items-center gap-2 truncate">
                  <Lock className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                  <span className="truncate">SHA-256: {data.certificate_hash}</span>
                </div>
                <span className="shrink-0 text-emerald-400 font-bold ml-2">VERIFIED RECORD</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
