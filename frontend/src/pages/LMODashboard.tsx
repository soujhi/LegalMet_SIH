import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ApiClient } from '../api/client';
import { Application } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Smartphone, MapPin, Calendar, Scale, Clock, 
  CheckCircle2, ArrowRight, ShieldCheck, Play 
} from 'lucide-react';

export const LMODashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [inspections, setInspections] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadInspections = async () => {
      try {
        const apps = await ApiClient.getApplications();
        setInspections(apps);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadInspections();
  }, []);

  const pending = inspections.filter(i => 
    i.status === 'ASSIGNED' || i.status === 'SCHEDULED' || i.status === 'FIELD_VERIFICATION'
  );
  const completed = inspections.filter(i => 
    i.status === 'CERTIFICATE_ISSUED' || i.status === 'PASSED' || i.status === 'FAILED'
  );

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-xs text-slate-500 font-semibold">Loading LMO Field Verification Queue...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Officer Mobile-friendly Banner */}
      <div className="bg-gradient-to-r from-[#0F2942] to-[#1E3A5F] rounded-2xl p-6 text-white shadow-md">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
              LMO Field Officer Active
            </span>
            <h1 className="text-xl sm:text-2xl font-black">{user?.full_name || 'Inspector Amit Sharma'}</h1>
            <p className="text-xs text-slate-300">
              Jurisdiction: <b>{user?.jurisdiction || 'Barhi / Hazaribagh'}</b> • Officer Code: <b>{user?.officer_code || 'LMO-JH-001'}</b>
            </p>
          </div>
          <div className="p-3 bg-white/10 rounded-2xl">
            <Smartphone className="h-8 w-8 text-amber-400" />
          </div>
        </div>
      </div>

      {/* Action Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-bold text-slate-500 uppercase">Assigned Inspections</span>
          <div className="text-2xl font-black text-indigo-600 mt-1">{pending.length}</div>
          <span className="text-[10px] text-slate-400 block mt-0.5">Ready for field testing</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-bold text-slate-500 uppercase">Completed Verifications</span>
          <div className="text-2xl font-black text-emerald-600 mt-1">{completed.length}</div>
          <span className="text-[10px] text-slate-400 block mt-0.5">Certificates & reports filed</span>
        </div>
      </div>

      {/* Pending Inspections List */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <Clock className="h-4 w-4 text-indigo-600" /> Field Inspections Queue
        </h2>

        {pending.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
            No pending inspections assigned for today.
          </div>
        ) : (
          <div className="space-y-3">
            {pending.map(app => (
              <div
                key={app.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:border-indigo-300 transition-all space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-mono font-bold text-xs text-blue-900 block">
                      {app.application_number}
                    </span>
                    <h3 className="font-extrabold text-sm text-slate-900 mt-0.5">
                      {app.applicant?.organization_name || app.applicant?.full_name}
                    </h3>
                    <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                      <MapPin className="h-3.5 w-3.5 text-slate-400" /> {app.instrument?.location || 'Barhi Mandi Platform'}
                    </p>
                  </div>
                  <StatusBadge status={app.status} />
                </div>

                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Instrument:</span>
                    <span className="font-bold text-slate-800">
                      {app.instrument?.model?.brand} {app.instrument?.model?.model_series}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Capacity & Class:</span>
                    <span className="font-bold text-slate-800">
                      {app.instrument?.capacity} {app.instrument?.unit} ({app.instrument?.accuracy_class})
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Serial No:</span>
                    <span className="font-mono font-bold text-slate-800">
                      {app.instrument?.serial_number}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Scale Interval (e):</span>
                    <span className="font-bold text-slate-800">
                      {app.instrument?.verification_scale_interval} g
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                  <div className="text-[11px] text-slate-500 flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    Appointment: <b>{app.scheduled_at ? new Date(app.scheduled_at).toLocaleDateString() : 'Immediate'}</b>
                  </div>
                  <Link
                    to={`/lmo/inspections/${app.id}/verification`}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs flex items-center gap-1.5 transition-colors"
                  >
                    <Play className="h-3.5 w-3.5" /> Start Field Verification
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Completed Inspections Section */}
      {completed.length > 0 && (
        <div className="space-y-3 pt-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" /> Completed Inspections
          </h2>
          <div className="divide-y divide-slate-100 bg-white rounded-2xl border border-slate-200 p-4">
            {completed.map(app => (
              <div key={app.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="font-bold text-xs text-slate-900 flex items-center gap-2">
                    {app.application_number}
                    <StatusBadge status={app.status} />
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    {app.applicant?.organization_name} • Serial: {app.instrument?.serial_number}
                  </div>
                </div>
                <Link
                  to={`/lmo/inspections/${app.id}/verification`}
                  className="text-xs font-bold text-blue-600 hover:text-blue-800"
                >
                  View Details →
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
