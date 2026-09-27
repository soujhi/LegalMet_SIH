import React, { useState, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { Instrument, InstrumentCategory, InstrumentModel } from '../types';
import { Scale, Plus, ShieldCheck, CheckCircle2, Building, Layers, Search, FileText, Info } from 'lucide-react';

export const TraderInstruments: React.FC = () => {
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [categories, setCategories] = useState<InstrumentCategory[]>([]);
  const [models, setModels] = useState<InstrumentModel[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Model search state
  const [modelSearch, setModelSearch] = useState('');
  const [filteredModels, setFilteredModels] = useState<InstrumentModel[]>([]);

  // Form State
  const [selectedCat, setSelectedCat] = useState<number>(1);
  const [selectedModel, setSelectedModel] = useState<InstrumentModel | null>(null);
  const [serialNumber, setSerialNumber] = useState('');
  const [assetNumber, setAssetNumber] = useState('');
  const [capacity, setCapacity] = useState<number>(30);
  const [unit, setUnit] = useState('kg');
  const [accuracyClass, setAccuracyClass] = useState('Class III');
  const [scaleInterval, setScaleInterval] = useState<number>(5.0);
  const [location, setLocation] = useState('Barhi Market Shop 14');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [instList, catList, modelList] = await Promise.all([
        ApiClient.getInstruments(),
        ApiClient.getCategories(),
        ApiClient.getModels({ limit: 500 })
      ]);
      setInstruments(instList);
      setCategories(catList);
      setModels(modelList);
      setFilteredModels(modelList);
      if (modelList.length > 0) {
        selectModelObj(modelList[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (!modelSearch.trim()) {
      setFilteredModels(models);
    } else {
      const q = modelSearch.toLowerCase();
      setFilteredModels(
        models.filter(
          m =>
            m.model_series.toLowerCase().includes(q) ||
            m.brand.toLowerCase().includes(q) ||
            m.manufacturer.toLowerCase().includes(q) ||
            (m.approval_mark && m.approval_mark.toLowerCase().includes(q))
        )
      );
    }
  }, [modelSearch, models]);

  const selectModelObj = (m: InstrumentModel) => {
    setSelectedModel(m);
    setCapacity(m.max_capacity);
    setAccuracyClass(m.accuracy_class);
    setScaleInterval(m.verification_scale_interval);
    setUnit(m.capacity_unit || 'kg');
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFeedback(null);
    try {
      await ApiClient.createInstrument({
        category_id: selectedCat,
        model_id: selectedModel?.id,
        serial_number: serialNumber,
        asset_number: assetNumber,
        capacity,
        unit,
        accuracy_class: accuracyClass,
        verification_scale_interval: scaleInterval,
        location
      });
      setFeedback({ type: 'success', message: `Instrument ${serialNumber} registered successfully!` });
      setShowModal(false);
      setSerialNumber('');
      setAssetNumber('');
      loadData();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to register instrument.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <Scale className="h-6 w-6 text-amber-500" /> Weighing & Measuring Instruments Master
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Registered commercial instruments linked with DoCA Model Approvals and Legal Metrology statutory records.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 bg-[#0F2942] hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow transition-all flex items-center gap-2"
        >
          <Plus className="h-4 w-4" /> Register New Instrument
        </button>
      </div>

      {feedback && (
        <div className={`p-4 rounded-xl text-xs font-semibold ${feedback.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
          {feedback.message}
        </div>
      )}

      {/* Instruments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {instruments.map(inst => (
          <div key={inst.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  {inst.category?.name?.split('(')[0] || 'NAWI'}
                </span>
                <span className="text-[10px] font-mono font-bold text-slate-400">ID #{inst.id}</span>
              </div>

              <h3 className="text-base font-extrabold text-slate-900">
                {inst.model ? `${inst.model.brand} ${inst.model.model_series}` : 'Standard Commercial Scale'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Manufacturer: <b>{inst.model?.manufacturer || 'Standard Scale Co.'}</b>
              </p>

              <div className="mt-4 bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1.5 text-xs text-slate-700">
                <div className="flex justify-between">
                  <span className="text-slate-500">Serial No:</span>
                  <span className="font-mono font-bold text-slate-900">{inst.serial_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Max Capacity:</span>
                  <span className="font-bold">{inst.capacity} {inst.unit}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Accuracy Class:</span>
                  <span className="font-bold">{inst.accuracy_class}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Scale Interval (e):</span>
                  <span className="font-bold">{inst.verification_scale_interval} g</span>
                </div>
                {inst.model?.approval_mark && (
                  <div className="flex justify-between pt-1 border-t border-slate-200 text-[11px]">
                    <span className="text-slate-500">DoCA Approval:</span>
                    <span className="font-mono text-blue-700 font-semibold">{inst.model.approval_mark}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500 truncate max-w-[150px]">{inst.location || 'Barhi'}</span>
              <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                {inst.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Register Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-base text-slate-900">Register New Weighing Instrument</h3>
                <p className="text-xs text-slate-500">Links trader serial number to official DoCA Model Approval certificate.</p>
              </div>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  1. Instrument Category
                </label>
                <select
                  value={selectedCat}
                  onChange={(e) => setSelectedCat(parseInt(e.target.value))}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                >
                  {categories.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              {/* Layer A: Model Approval Reference */}
              <div className="p-4 bg-blue-50/60 border border-blue-200 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-900 flex items-center gap-1.5 uppercase tracking-wide">
                    <ShieldCheck className="w-4 h-4 text-blue-700" />
                    Layer A: Government Model Approval Reference ({models.length} Approved Models)
                  </span>
                </div>

                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search approved model by brand, manufacturer, series, or approval mark..."
                    value={modelSearch}
                    onChange={(e) => setModelSearch(e.target.value)}
                    className="w-full text-xs pl-9 pr-3 py-2 rounded-lg border border-blue-300 bg-white focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="max-h-40 overflow-y-auto border border-blue-200 rounded-lg bg-white divide-y divide-slate-100">
                  {filteredModels.slice(0, 50).map(m => (
                    <div
                      key={m.id}
                      onClick={() => selectModelObj(m)}
                      className={`p-2.5 text-xs cursor-pointer flex justify-between items-center hover:bg-blue-50 ${selectedModel?.id === m.id ? 'bg-blue-100/70 font-semibold' : ''}`}
                    >
                      <div>
                        <div className="font-bold text-slate-800">
                          {m.brand} {m.model_series} <span className="text-slate-500 font-normal">({m.manufacturer})</span>
                        </div>
                        <div className="text-[11px] text-slate-500">
                          {m.accuracy_class} | Max: {m.max_capacity}{m.capacity_unit} | e={m.verification_scale_interval}g
                          {m.approval_mark ? ` | Mark: ${m.approval_mark}` : ''}
                        </div>
                      </div>
                      {selectedModel?.id === m.id && (
                        <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                      )}
                    </div>
                  ))}
                  {filteredModels.length === 0 && (
                    <div className="p-3 text-center text-xs text-slate-400">No matching DoCA models found.</div>
                  )}
                </div>

                {selectedModel && (
                  <div className="bg-white p-3 rounded-lg border border-blue-100 text-xs text-slate-700 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Selected Model:</span>
                      <span className="font-bold">{selectedModel.brand} {selectedModel.model_series}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Approval Mark:</span>
                      <span className="font-mono text-blue-700 font-semibold">{selectedModel.approval_mark || 'IND/09/2022/145'}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Layer B: Physical In-Situ Instrument */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5 uppercase tracking-wide">
                  <Layers className="w-4 h-4 text-slate-600" />
                  Layer B: Trader Physical Instrument Deployment
                </span>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                      Serial Number (Unique Physical Device)
                    </label>
                    <input
                      type="text"
                      required
                      value={serialNumber}
                      onChange={(e) => setSerialNumber(e.target.value)}
                      placeholder="e.g. NK-2024-9912"
                      className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                      Asset / Store Tag
                    </label>
                    <input
                      type="text"
                      value={assetNumber}
                      onChange={(e) => setAssetNumber(e.target.value)}
                      placeholder="e.g. MANDI-COUNTER-1"
                      className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Max Cap ({unit})</label>
                    <input
                      type="number"
                      step="0.1"
                      value={capacity}
                      onChange={(e) => setCapacity(parseFloat(e.target.value))}
                      className="w-full text-xs p-2 rounded-xl border border-slate-300 bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Class</label>
                    <input
                      type="text"
                      value={accuracyClass}
                      onChange={(e) => setAccuracyClass(e.target.value)}
                      className="w-full text-xs p-2 rounded-xl border border-slate-300 bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Interval e (g)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={scaleInterval}
                      onChange={(e) => setScaleInterval(parseFloat(e.target.value))}
                      className="w-full text-xs p-2 rounded-xl border border-slate-300 bg-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                    Physical Installation Location
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Shop No. 14, Main Market, Barhi"
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 text-xs font-bold bg-[#0F2942] hover:bg-slate-800 text-white rounded-xl shadow"
                >
                  {isSubmitting ? 'Registering...' : 'Save & Register Instrument'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
