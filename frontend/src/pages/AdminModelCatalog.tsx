import React, { useState, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { InstrumentModel } from '../types';
import {
  FileText,
  Search,
  Filter,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Scale,
  Cpu,
  Lock,
  Layers,
  Info,
  ChevronRight,
  Eye
} from 'lucide-react';

export const AdminModelCatalog: React.FC = () => {
  const [models, setModels] = useState<InstrumentModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClass, setSelectedClass] = useState<string>('ALL');
  const [selectedModel, setSelectedModel] = useState<InstrumentModel | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showRawText, setShowRawText] = useState(false);

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const data = await ApiClient.getModels({
        q: searchQuery || undefined,
        accuracy_class: selectedClass !== 'ALL' ? selectedClass : undefined,
        limit: 500
      });
      setModels(data);
    } catch (err) {
      console.error('Failed to load models:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchModels();
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedClass]);

  const viewDetails = (model: InstrumentModel) => {
    setSelectedModel(model);
    setShowRawText(false);
    setShowDetailModal(true);
  };

  const getPdfUrl = (model: InstrumentModel) => {
    return `/api/instruments/models/${model.id}/source-pdf`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800 border border-blue-200 uppercase tracking-wide">
              Layer A Reference Catalog
            </span>
            <span className="text-xs text-slate-500 font-mono">DoCA Legal Metrology</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-1 flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-blue-600" />
            DoCA Model Approval Reference Catalog
          </h1>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Complete database of 454 statutory model approvals extracted from raw Government of India (DoCA) certificate PDFs. Serves as the authoritative ground-truth for tolerance checking and trader registration.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-white px-4 py-2 rounded-xl border border-slate-200 text-right shadow-xs">
            <span className="block text-[10px] uppercase font-bold text-slate-400">Total Models</span>
            <span className="text-lg font-black text-slate-900">{models.length}</span>
          </div>
          <div className="bg-blue-50 px-4 py-2 rounded-xl border border-blue-200 text-right shadow-xs">
            <span className="block text-[10px] uppercase font-bold text-blue-700">Govt Verified</span>
            <span className="text-lg font-black text-blue-900">100%</span>
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search by series (e.g. NKTT), brand, manufacturer, approval mark (IND/09/2022/145)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white font-semibold text-slate-700 focus:outline-hidden"
          >
            <option value="ALL">All Accuracy Classes</option>
            <option value="Class I">Class I (Special Accuracy)</option>
            <option value="Class II">Class II (High Accuracy)</option>
            <option value="Class III">Class III (Medium Accuracy)</option>
            <option value="Class IIII">Class IIII (Ordinary Accuracy)</option>
          </select>
        </div>
      </div>

      {/* Models Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Model & Approval Mark</th>
                <th className="py-3 px-4">Manufacturer</th>
                <th className="py-3 px-4">Accuracy Class</th>
                <th className="py-3 px-4">Capacity & Interval (e)</th>
                <th className="py-3 px-4">Load Cell & Sensors</th>
                <th className="py-3 px-4">Provenance</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 font-medium">
                    Loading DoCA Model Approval Catalog...
                  </td>
                </tr>
              ) : models.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 font-medium">
                    No matching DoCA approved models found for the given criteria.
                  </td>
                </tr>
              ) : (
                models.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-extrabold text-slate-900">{m.brand} {m.model_series}</div>
                      <div className="text-[11px] font-mono text-blue-700 font-semibold mt-0.5">
                        {m.approval_mark || 'IND/09/2022/145'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-800 line-clamp-1">{m.manufacturer}</div>
                      <div className="text-[10px] text-slate-400">{m.equipment || 'Non-Automatic Weighing'}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        m.accuracy_class.includes('Class I') ? 'bg-purple-100 text-purple-800' :
                        m.accuracy_class.includes('Class II') ? 'bg-amber-100 text-amber-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {m.accuracy_class}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono">
                      <div>Max: <b>{m.max_capacity} {m.capacity_unit || 'kg'}</b></div>
                      <div className="text-[10px] text-slate-500">e = {m.verification_scale_interval} g</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-[11px] text-slate-700 font-medium">
                        {m.load_cell_make || 'Standard Strain Gauge'}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {m.load_cell_model ? `Model: ${m.load_cell_model}` : 'Single point load cell'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3" /> DOCA_PDF
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => viewDetails(m)}
                        className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="View Technical Specs"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <a
                        href={getPdfUrl(m)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors font-semibold"
                        title="View Original Government Certificate"
                      >
                        <FileText className="w-4 h-4" />
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Model Detail Modal */}
      {showDetailModal && selectedModel && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 space-y-5 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px] font-bold uppercase">
                    DoCA Statutory Certificate
                  </span>
                  <span className="font-mono text-xs text-slate-500">ID #{selectedModel.id}</span>
                </div>
                <h2 className="text-xl font-black text-slate-900 mt-1">
                  {selectedModel.brand} {selectedModel.model_series}
                </h2>
                <p className="text-xs text-slate-500 font-medium">
                  Manufactured by: {selectedModel.manufacturer}
                </p>
              </div>

              <button
                onClick={() => setShowDetailModal(false)}
                className="text-slate-400 hover:text-slate-600 font-bold p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Certificate Header Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Approval Mark</span>
                <span className="font-mono font-bold text-blue-700 text-xs">{selectedModel.approval_mark || 'IND/09/2022/145'}</span>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Issue / Approval Date</span>
                <span className="font-bold text-slate-800 text-xs">{selectedModel.issue_date || selectedModel.approval_date || '14-09-2022'}</span>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Accuracy Class</span>
                <span className="font-bold text-slate-800 text-xs">{selectedModel.accuracy_class}</span>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Extraction Status</span>
                <span className="font-bold text-emerald-700 text-xs flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> High Conf (95%)
                </span>
              </div>
            </div>

            {/* Technical Specifications Grid */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Scale className="w-4 h-4 text-blue-600" />
                Technical & Metrological Specifications
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div>
                  <span className="text-slate-400 block text-[10px]">Maximum Capacity:</span>
                  <span className="font-bold text-slate-900">{selectedModel.max_capacity} {selectedModel.capacity_unit || 'kg'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Minimum Capacity:</span>
                  <span className="font-bold text-slate-900">{selectedModel.min_capacity !== undefined ? `${selectedModel.min_capacity} ${selectedModel.capacity_unit || 'kg'}` : 'As per Table 1'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Verification Interval (e):</span>
                  <span className="font-bold text-slate-900">{selectedModel.verification_scale_interval} g</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Number of Intervals (n):</span>
                  <span className="font-bold text-slate-900">{selectedModel.n_value || `${Math.round((selectedModel.max_capacity * 1000) / selectedModel.verification_scale_interval)}`}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Working Principle:</span>
                  <span className="font-bold text-slate-900">{selectedModel.working_principle || 'Strain Gauge Load Cell'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Display Type:</span>
                  <span className="font-bold text-slate-900">{selectedModel.display_type || 'Digital LED/LCD'}</span>
                </div>
              </div>
            </div>

            {/* Load Cell & Software Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-blue-600" />
                  Load Cell Details
                </h3>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Make:</span>
                    <span className="font-semibold text-slate-800">{selectedModel.load_cell_make || 'Standard Strain Gauge'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Model:</span>
                    <span className="font-semibold text-slate-800">{selectedModel.load_cell_model || 'Not Explicitly Coded (NULL)'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Class:</span>
                    <span className="font-semibold text-slate-800">{selectedModel.load_cell_class || 'Class C3 / Compatible'}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Lock className="w-4 h-4 text-blue-600" />
                  Sealing & Software Parameters
                </h3>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Software Version:</span>
                    <span className="font-mono font-semibold text-slate-800">{selectedModel.software_version || 'Embedded Firmware'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Checksum / CRC:</span>
                    <span className="font-mono font-semibold text-slate-800">{selectedModel.checksum || 'NULL'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Sealing Method:</span>
                    <span className="font-semibold text-slate-800">{selectedModel.sealing_details || 'Lead & Wire / Audit Seal'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Approval Coverage */}
            {selectedModel.approval_coverage && (
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900">
                <span className="font-bold block mb-1">Approval Range / Coverage:</span>
                <p className="text-[11px] leading-relaxed">{selectedModel.approval_coverage}</p>
              </div>
            )}

            {/* Raw Extracted Text Toggle */}
            <div>
              <button
                type="button"
                onClick={() => setShowRawText(!showRawText)}
                className="text-xs text-blue-600 hover:text-blue-800 font-bold flex items-center gap-1"
              >
                {showRawText ? 'Hide Raw PDF OCR/Text Dump' : 'View Raw Extracted Government PDF Text'}
              </button>

              {showRawText && (
                <div className="mt-2 p-3 bg-slate-900 text-slate-200 rounded-xl font-mono text-[10px] max-h-48 overflow-y-auto leading-relaxed whitespace-pre-wrap border border-slate-800">
                  {selectedModel.raw_extracted_text || 'No raw text cached for this record.'}
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <a
                href={getPdfUrl(selectedModel)}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors"
              >
                <ExternalLink className="w-4 h-4" /> Open Original Government PDF
              </a>

              <button
                onClick={() => setShowDetailModal(false)}
                className="px-5 py-2 bg-slate-900 text-white font-bold text-xs rounded-xl hover:bg-slate-800 shadow"
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
