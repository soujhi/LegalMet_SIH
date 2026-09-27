import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ApiClient } from '../api/client';
import { DashboardMetrics } from '../types';
import { 
  ShieldCheck, FileText, CheckCircle2, AlertTriangle, 
  Layers, MapPin, TrendingUp, Users, Smartphone, Sparkles, ArrowRight, Activity 
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await ApiClient.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadMetrics();
  }, []);

  if (isLoading || !metrics) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-xs text-slate-500">
        Loading Legal Metrology Directorate analytics...
      </div>
    );
  }

  const s = metrics.summary;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0F2942] to-[#1E3A5F] rounded-2xl p-6 sm:p-8 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold uppercase">
            <ShieldCheck className="h-3.5 w-3.5" /> Department of Legal Metrology • Administrative Control Center
          </div>
          <h1 className="text-2xl sm:text-3xl font-black">Jharkhand State Verification Dashboard</h1>
          <p className="text-slate-300 text-xs sm:text-sm">
            Jurisdiction: Hazaribagh / Barhi Sub-Division • Live Application Scrutiny & Field Inspection Oversight
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            to="/admin/applications"
            className="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-xl shadow transition-colors flex items-center gap-2"
          >
            <FileText className="h-4 w-4" /> Scrutinize Applications ({s.pending_scrutiny})
          </Link>
          <Link
            to="/admin/ocr"
            className="px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-semibold rounded-xl transition-colors flex items-center gap-2"
          >
            <Sparkles className="h-4 w-4" /> OCR Digitization Hub
          </Link>
        </div>
      </div>

      {/* Core KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Pending Scrutiny</span>
            <div className="text-2xl font-black text-amber-600 mt-1">{s.pending_scrutiny}</div>
            <span className="text-[11px] text-slate-500 font-medium mt-0.5 block">Requires review / approval</span>
          </div>
          <div className="p-3 bg-amber-50 text-amber-700 rounded-xl">
            <FileText className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Assigned Inspections</span>
            <div className="text-2xl font-black text-indigo-600 mt-1">{s.assigned_inspections}</div>
            <span className="text-[11px] text-slate-500 font-medium mt-0.5 block">Active with LMO officers</span>
          </div>
          <div className="p-3 bg-indigo-50 text-indigo-700 rounded-xl">
            <Smartphone className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Verifications Passed</span>
            <div className="text-2xl font-black text-emerald-600 mt-1">{s.passed_verifications}</div>
            <span className="text-[11px] text-emerald-700 font-medium mt-0.5 block">Within MPE statutory error</span>
          </div>
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl">
            <CheckCircle2 className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Compliance Risk Flags</span>
            <div className="text-2xl font-black text-rose-600 mt-1">{s.total_risk_flags}</div>
            <span className="text-[11px] text-rose-700 font-medium mt-0.5 block">MPE tolerance failures</span>
          </div>
          <div className="p-3 bg-rose-50 text-rose-700 rounded-xl">
            <AlertTriangle className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Analytics Breakdown & Region Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* District Compliance Breakdown */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">District Verification & Compliance Breakdown</h3>
              <p className="text-xs text-slate-500">Legal Metrology field records across Jharkhand jurisdiction</p>
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
              Avg 95.8% Compliance
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {metrics.district_breakdown.map((d, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-slate-100 rounded-lg text-slate-700">
                    <MapPin className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="font-bold text-xs text-slate-900">{d.district}</div>
                    <div className="text-[11px] text-slate-500">{d.instruments} Registered Units</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-xs text-emerald-700">{d.compliance_rate}</div>
                  <span className="text-[10px] text-slate-400">Pass Rate</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* OCR & Provenance Status */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              <h3 className="text-base font-bold text-slate-900">Legacy OCR Digitization</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Jharkhand Barhi public certificates dataset (Layer B) ingested for human verification.
            </p>

            <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-100 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-600">Total OCR Ingested:</span>
                <span className="font-bold text-slate-900">{s.ocr_digitized_total} records</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Manually Verified:</span>
                <span className="font-bold text-emerald-700">{s.ocr_verified_count} validated</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Pending Officer Review:</span>
                <span className="font-bold text-amber-700">{s.ocr_digitized_total - s.ocr_verified_count} pending</span>
              </div>
            </div>
          </div>

          <Link
            to="/admin/ocr"
            className="w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow text-center flex items-center justify-center gap-2 transition-colors"
          >
            Open OCR Digitization Hub <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};
