import React, { useState, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { OCRDocument } from '../types';
import { 
  Sparkles, CheckCircle2, AlertTriangle, FileText, 
  Search, Check, Edit3, Eye, ShieldCheck, Database 
} from 'lucide-react';

export const AdminOCR: React.FC = () => {
  const [documents, setDocuments] = useState<OCRDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterVerified, setFilterVerified] = useState<string>('ALL');

  // Review Modal State
  const [selectedDoc, setSelectedDoc] = useState<OCRDocument | null>(null);
  const [certNo, setCertNo] = useState('');
  const [concernName, setConcernName] = useState('');
  const [verifDate, setVerifDate] = useState('');
  const [nextVerifDate, setNextVerifDate] = useState('');
  const [capacity, setCapacity] = useState('');
  const [accuracyClass, setAccuracyClass] = useState('');
  const [fee, setFee] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const loadDocs = async () => {
    setIsLoading(true);
    try {
      const data = await ApiClient.getOCRDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const openReviewModal = (doc: OCRDocument) => {
    setSelectedDoc(doc);
    setCertNo(doc.certificate_no || '');
    setConcernName(doc.concern_name || '');
    setVerifDate(doc.verification_date || '');
    setNextVerifDate(doc.next_verification_date || '');
    setCapacity(doc.capacity || '');
    setAccuracyClass(doc.accuracy_class || 'Class III');
    setFee(doc.verification_fee || 'Rs. 250/-');
  };

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoc) return;
    setIsSaving(true);
    try {
      await ApiClient.validateOCRDocument(selectedDoc.id, {
        certificate_no: certNo,
        concern_name: concernName,
        verification_date: verifDate,
        next_verification_date: nextVerifDate,
        capacity,
        accuracy_class: accuracyClass,
        verification_fee: fee,
        manual_verified: true
      });
      setSelectedDoc(null);
      loadDocs();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  const filtered = documents.filter(d => {
    if (filterVerified === 'VERIFIED') return d.manual_verified;
    if (filterVerified === 'PENDING') return !d.manual_verified;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-purple-600" /> Legacy Document Digitization & OCR Hub
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Jharkhand e-Legal Metrology Portal scanned records (Layer B) with confidence scoring & human validation.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 text-xs">
          <button
            onClick={() => setFilterVerified('ALL')}
            className={`px-3 py-1 rounded-lg font-semibold transition-all ${
              filterVerified === 'ALL' ? 'bg-[#0F2942] text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            All Records ({documents.length})
          </button>
          <button
            onClick={() => setFilterVerified('PENDING')}
            className={`px-3 py-1 rounded-lg font-semibold transition-all ${
              filterVerified === 'PENDING' ? 'bg-[#0F2942] text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Pending Review ({documents.filter(d => !d.manual_verified).length})
          </button>
          <button
            onClick={() => setFilterVerified('VERIFIED')}
            className={`px-3 py-1 rounded-lg font-semibold transition-all ${
              filterVerified === 'VERIFIED' ? 'bg-[#0F2942] text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Verified ({documents.filter(d => d.manual_verified).length})
          </button>
        </div>
      </div>

      {/* Warning Box on Provenance */}
      <div className="p-4 bg-purple-50 border border-purple-200 rounded-2xl flex items-start gap-3 text-xs text-purple-900">
        <Database className="h-5 w-5 text-purple-600 shrink-0 mt-0.5" />
        <div>
          <strong className="font-bold">Statutory Provenance Rule:</strong> Scanned legacy certificates may contain handwritten entries with low OCR recognition confidence. In accordance with PRD guidelines, raw OCR text is retained, and records remain unverified until an authorized officer performs human validation (`manual_verified=True`).
        </div>
      </div>

      {/* Documents Grid / Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-500">
            No OCR records found matching filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3">Certificate No</th>
                  <th className="px-5 py-3">Area / Concern Name</th>
                  <th className="px-5 py-3">Capacity & Class</th>
                  <th className="px-5 py-3">OCR Confidence</th>
                  <th className="px-5 py-3">Validation Status</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-medium">
                {filtered.map(doc => (
                  <tr key={doc.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-4 font-mono font-bold text-purple-900">
                      {doc.certificate_no || 'Pending OCR'}
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-bold text-slate-900">{doc.concern_name || 'Commercial Establishment'}</div>
                      <div className="text-[11px] text-slate-400">Area: {doc.area || 'BARHI'} • Source: {doc.source_type}</div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-bold text-slate-800">{doc.capacity || '30 kg'}</div>
                      <div className="text-[11px] text-slate-400">{doc.accuracy_class || 'Class III'}</div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full ${doc.ocr_confidence > 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                            style={{ width: `${doc.ocr_confidence}%` }}
                          ></div>
                        </div>
                        <span className="font-bold text-slate-700">{doc.ocr_confidence}%</span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      {doc.manual_verified ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                          <CheckCircle2 className="h-3 w-3" /> Manually Verified
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                          <AlertTriangle className="h-3 w-3" /> Needs Human Review
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={() => openReviewModal(doc)}
                        className="px-3 py-1 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-300 text-xs font-bold rounded-lg transition-colors flex items-center gap-1 inline-flex"
                      >
                        <Edit3 className="h-3.5 w-3.5" /> Review & Validate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review & Validate Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-600" />
                <h3 className="font-bold text-base text-slate-900">Validate OCR Extracted Certificate</h3>
              </div>
              <button onClick={() => setSelectedDoc(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Left Column: Raw OCR Stream */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold uppercase text-slate-500 block">Raw OCR Text Feed</span>
                <div className="bg-slate-900 text-slate-300 font-mono text-[11px] p-3 rounded-xl h-64 overflow-y-auto leading-relaxed border border-slate-800">
                  {selectedDoc.raw_ocr_text || 'No raw OCR stream available for this file.'}
                </div>
                <div className="text-[10px] text-slate-400">
                  Source Scan: <b>{selectedDoc.source_file}</b>
                </div>
              </div>

              {/* Right Column: Editable Structured Form */}
              <form onSubmit={handleValidate} className="space-y-3">
                <span className="text-[11px] font-bold uppercase text-slate-500 block">Human Verified Fields</span>

                <div>
                  <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Certificate Number</label>
                  <input
                    type="text"
                    required
                    value={certNo}
                    onChange={(e) => setCertNo(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-slate-300 font-mono font-bold text-blue-900"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Concern / Trader Name</label>
                  <input
                    type="text"
                    required
                    value={concernName}
                    onChange={(e) => setConcernName(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-slate-300"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Verification Date</label>
                    <input
                      type="text"
                      value={verifDate}
                      onChange={(e) => setVerifDate(e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-300"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Next Due Date</label>
                    <input
                      type="text"
                      value={nextVerifDate}
                      onChange={(e) => setNextVerifDate(e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-300"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Capacity</label>
                    <input
                      type="text"
                      value={capacity}
                      onChange={(e) => setCapacity(e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-300"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Accuracy Class</label>
                    <input
                      type="text"
                      value={accuracyClass}
                      onChange={(e) => setAccuracyClass(e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-300"
                    />
                  </div>
                </div>

                <div className="pt-2 flex justify-end gap-2 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setSelectedDoc(null)}
                    className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="px-4 py-1.5 text-xs font-bold bg-purple-600 hover:bg-purple-700 text-white rounded-lg shadow flex items-center gap-1"
                  >
                    <Check className="h-3.5 w-3.5" /> Save as Verified Record
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
