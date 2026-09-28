import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ApiClient } from '../api/client';
import { Instrument, Application, Certificate } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Scale, FileText, Award, AlertCircle, PlusCircle, 
  ArrowRight, ShieldCheck, Clock, CheckCircle2, QrCode
} from 'lucide-react';

export const TraderDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [insts, apps, certs] = await Promise.all([
          ApiClient.getInstruments(),
          ApiClient.getApplications(),
          ApiClient.getCertificates()
        ]);
        setInstruments(insts);
        setApplications(apps);
        setCertificates(certs);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-xs text-slate-500 font-semibold">Loading Trader Portal & Assets...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Enterprise Header */}
      <div className="bg-gradient-to-r from-[#0F2942] to-[#1E3A5F] rounded-2xl p-6 sm:p-8 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold uppercase">
            <Scale className="h-3.5 w-3.5" /> Registered Commercial Stakeholder
          </div>
          <h1 className="text-2xl sm:text-3xl font-black">{user?.organization_name || user?.full_name || 'Commercial Stakeholder Portal'}</h1>
          <p className="text-slate-300 text-xs sm:text-sm">
            Trader Portal • Location: Barhi Sub-Division, Jharkhand • Legal Metrology Act 2009 Compliance
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            to="/trader/instruments"
            className="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-xl shadow transition-colors flex items-center gap-2"
          >
            <PlusCircle className="h-4 w-4" /> Register Instrument
          </Link>
          <Link
            to="/trader/applications"
            className="px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-semibold rounded-xl transition-colors flex items-center gap-2"
          >
            <FileText className="h-4 w-4" /> New Verification Request
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Registered Instruments</span>
            <div className="text-2xl font-black text-slate-900 mt-1">{instruments.length}</div>
            <span className="text-[11px] text-emerald-600 font-semibold mt-0.5 block">All tagged with DoCA standards</span>
          </div>
          <div className="p-3 bg-blue-50 text-blue-700 rounded-xl">
            <Scale className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Active Applications</span>
            <div className="text-2xl font-black text-slate-900 mt-1">
              {applications.filter(a => a.status !== 'CERTIFICATE_ISSUED' && a.status !== 'FAILED').length}
            </div>
            <span className="text-[11px] text-indigo-600 font-semibold mt-0.5 block">Under scrutiny or scheduled</span>
          </div>
          <div className="p-3 bg-indigo-50 text-indigo-700 rounded-xl">
            <Clock className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Active Certificates</span>
            <div className="text-2xl font-black text-slate-900 mt-1">
              {certificates.filter(c => c.status === 'VALID').length}
            </div>
            <span className="text-[11px] text-emerald-600 font-semibold mt-0.5 block">Legally verified & QR stamped</span>
          </div>
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl">
            <Award className="h-6 w-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase">Next Re-Verification</span>
            <div className="text-sm font-black text-slate-900 mt-1">Within 11 Months</div>
            <span className="text-[11px] text-amber-600 font-semibold mt-0.5 block">Annual statutory cycle</span>
          </div>
          <div className="p-3 bg-amber-50 text-amber-700 rounded-xl">
            <CheckCircle2 className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Registered Instruments & Actions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Your Weighing Instruments</h3>
                <p className="text-xs text-slate-500">Registered assets eligible for verification / re-verification</p>
              </div>
              <Link to="/trader/instruments" className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1">
                View All <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            {instruments.length === 0 ? (
              <div className="text-center py-8 border-2 border-dashed border-slate-200 rounded-xl">
                <Scale className="h-10 w-10 text-slate-300 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-600">No instruments registered yet</p>
                <Link to="/trader/instruments" className="mt-2 inline-block px-3 py-1.5 bg-[#0F2942] text-white text-xs font-bold rounded-lg">
                  Add Your First Instrument
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {instruments.map(inst => (
                  <div key={inst.id} className="py-3.5 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-sm text-slate-900 flex items-center gap-2">
                        {inst.model?.brand || 'Standard'} {inst.model?.model_series || 'Scale'}
                        <span className="font-mono text-xs font-normal text-slate-500">SN: {inst.serial_number}</span>
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        Capacity: <b>{inst.capacity} {inst.unit}</b> • {inst.accuracy_class} • e={inst.verification_scale_interval}g
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-1 rounded-md">
                        {inst.status}
                      </span>
                      <Link
                        to={`/trader/applications?apply_inst_id=${inst.id}`}
                        className="px-3 py-1 bg-amber-50 hover:bg-amber-100 border border-amber-300 text-amber-900 text-xs font-bold rounded-lg transition-colors"
                      >
                        Apply Re-Verif
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Verification Requests Timeline */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Recent Verification Applications</h3>
                <p className="text-xs text-slate-500">Track scrutiny, scheduling, and officer assignment</p>
              </div>
              <Link to="/trader/applications" className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1">
                View All <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            {applications.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                No active applications filed.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {applications.slice(0, 4).map(app => (
                  <div key={app.id} className="py-3 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-900 flex items-center gap-2">
                        {app.application_number}
                        <StatusBadge status={app.status} />
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        Type: {app.application_type} • Submitted on {new Date(app.submitted_at).toLocaleDateString()}
                      </div>
                    </div>
                    <Link
                      to="/trader/applications"
                      className="text-xs font-bold text-slate-700 hover:text-slate-900"
                    >
                      View Details →
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Certificate Vault & Golden Demo Steps */}
        <div className="space-y-6">
          {/* Quick Vault Preview */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Award className="h-5 w-5 text-emerald-700" />
              <h3 className="text-base font-bold text-slate-900">Certificate Vault</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Verified legal metrology certificates with QR tokens and statutory seal.
            </p>

            {certificates.length === 0 ? (
              <div className="p-4 bg-slate-50 rounded-xl text-center text-xs text-slate-500">
                Complete a field verification to generate official certificates.
              </div>
            ) : (
              <div className="space-y-3">
                {certificates.slice(0, 3).map(cert => (
                  <div key={cert.id} className="p-3 bg-emerald-50/50 border border-emerald-200 rounded-xl flex items-center justify-between">
                    <div>
                      <span className="font-mono font-bold text-xs text-emerald-950 block">{cert.certificate_number}</span>
                      <span className="text-[10px] text-emerald-700">Valid until {new Date(cert.valid_until).toLocaleDateString()}</span>
                    </div>
                    <Link
                      to={`/verify/${cert.certificate_number}`}
                      className="p-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs"
                      title="View QR Certificate"
                    >
                      <QrCode className="h-4 w-4" />
                    </Link>
                  </div>
                ))}
              </div>
            )}

            <Link
              to="/trader/certificates"
              className="mt-4 block text-center w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl transition-colors"
            >
              Open Complete Certificate Vault
            </Link>
          </div>

          {/* Golden Demo Guide Card */}
          <div className="bg-amber-50/80 border border-amber-300 rounded-2xl p-5 shadow-xs">
            <div className="flex items-center gap-2 text-amber-900 font-bold text-xs uppercase mb-2">
              <ShieldCheck className="h-4 w-4 text-amber-600" /> End-to-End Golden Demo
            </div>
            <ol className="text-xs text-amber-950 space-y-2 list-decimal list-inside font-medium leading-relaxed">
              <li>Trader registers scale and submits re-verification.</li>
              <li>Switch to <b>Admin</b> to Approve & Assign LMO.</li>
              <li>Switch to <b>LMO</b> to lock GPS, run test observations, and execute deterministic Rule Engine.</li>
              <li>Certificate & QR are generated on PASS.</li>
              <li>Public scans QR to authenticate.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};
