import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  ShieldCheck, QrCode, Search, Award, CheckCircle2, ArrowRight, 
  FileCheck2, Smartphone, Cpu, Lock, Database, ArrowUpRight, Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const PublicHome: React.FC = () => {
  const [certInput, setCertInput] = useState('');
  const navigate = useNavigate();
  const { quickLogin } = useAuth();
  const [launchingRole, setLaunchingRole] = useState<string | null>(null);

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    if (certInput.trim()) {
      navigate(`/verify/${encodeURIComponent(certInput.trim())}`);
    }
  };

  const handleLaunch = async (role: 'TRADER' | 'ADMIN' | 'LMO', path: string) => {
    setLaunchingRole(role);
    try {
      await quickLogin(role);
      navigate(path);
    } catch (err) {
      console.error('Portal launch failed:', err);
    } finally {
      setLaunchingRole(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-[#0F2942] to-[#163554] text-white py-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]"></div>
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-400/30 text-amber-400 text-xs font-semibold tracking-wide uppercase">
              <ShieldCheck className="h-4 w-4" /> Official SIH26036 Prototype
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
              Digital Lifecycle Management for <br className="hidden sm:inline" />
              <span className="text-amber-400">Legal Metrology Verification</span>
            </h1>
            <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
              End-to-end statutory verification workflow: from trader instrument registration and administrative scrutiny to mobile-first field inspection, deterministic MPE evaluation, and cryptographically verifiable QR certificates.
            </p>
          </div>

          {/* Public Verification Box */}
          <div className="mt-10 max-w-2xl mx-auto bg-white/95 backdrop-blur-md rounded-2xl p-4 sm:p-6 shadow-2xl border border-white/20 text-slate-900">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-100 rounded-lg text-blue-800">
                <QrCode className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-900">Public Certificate Verification</h3>
                <p className="text-xs text-slate-500">Authenticate any issued legal metrology certificate instantly via certificate number or QR token</p>
              </div>
            </div>

            <form onSubmit={handleVerify} className="flex flex-col sm:flex-row gap-2 mt-4">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder="Enter Certificate No. (e.g. 141701 or LM/JH/2026/520900)"
                  value={certInput}
                  onChange={(e) => setCertInput(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                />
                <Search className="h-4 w-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
              <button
                type="submit"
                className="px-6 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-sm rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
              >
                Verify Now <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            <div className="mt-3 flex flex-wrap items-center justify-between text-xs text-slate-500 px-1 gap-2">
              <span className="flex flex-wrap items-center gap-1.5">
                <span className="text-slate-400 font-medium">Sample Numbers:</span>
                <button type="button" onClick={() => setCertInput("141701")} className="px-1.5 py-0.5 bg-slate-100 hover:bg-blue-50 text-blue-600 rounded font-semibold border border-slate-200">141701 (State Record)</button>
                <button type="button" onClick={() => setCertInput("141710")} className="px-1.5 py-0.5 bg-slate-100 hover:bg-blue-50 text-blue-600 rounded font-semibold border border-slate-200">141710</button>
                <button type="button" onClick={() => setCertInput("LM/JH/2026/520900")} className="px-1.5 py-0.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded font-semibold border border-emerald-200">LM/JH/2026/520900 (Digital QR)</button>
                <button type="button" onClick={() => setCertInput("520900")} className="px-1.5 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-semibold border border-slate-200">520900</button>
              </span>
              <span className="flex items-center gap-1"><Lock className="h-3 w-3 text-emerald-600" /> SHA-256 Tamper-Proof</span>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Access Roles Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-slate-900">Role-Based Portals & Golden Demo Workflow</h2>
          <p className="text-sm text-slate-500 mt-1">Explore all four touchpoints designed for the complete Legal Metrology ecosystem</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Trader Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-orange-100 text-orange-700 flex items-center justify-center font-bold mb-4">
                <Award className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Trader / Business User</h3>
              <p className="text-sm text-slate-600 mt-2">
                Register weighing instruments against DoCA Approved Model Master, submit verification applications, track scrutiny timeline, and download digital certificates.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => handleLaunch('TRADER', '/trader/dashboard')}
                disabled={launchingRole === 'TRADER'}
                className="text-sm font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1"
              >
                {launchingRole === 'TRADER' ? 'Opening...' : 'Launch Trader Portal'} <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Admin Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold mb-4">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Legal Metrology Admin</h3>
              <p className="text-sm text-slate-600 mt-2">
                Scrutinize trader applications (Approve / Query / Reject), schedule and assign LMO officers, inspect deterministic rules, and manage legacy OCR records.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => handleLaunch('ADMIN', '/admin/dashboard')}
                disabled={launchingRole === 'ADMIN'}
                className="text-sm font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                {launchingRole === 'ADMIN' ? 'Opening...' : 'Launch Admin Portal'} <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* LMO Officer Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold mb-4">
                <Smartphone className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">LMO / GATC Field Officer</h3>
              <p className="text-sm text-slate-600 mt-2">
                Mobile-first field verification interface. Captures GPS coordinates, timestamps, test observations (Zero, Half, Max load), executes deterministic MPE evaluation, and issues QR certificates.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => handleLaunch('LMO', '/lmo/dashboard')}
                disabled={launchingRole === 'LMO'}
                className="text-sm font-bold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
              >
                {launchingRole === 'LMO' ? 'Opening...' : 'Launch LMO Field App'} <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Core Architectural Highlights */}
      <section className="py-12 bg-slate-100/70 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <h2 className="text-2xl font-bold text-slate-900">Statutory Architecture & Provenance</h2>
            <p className="text-sm text-slate-600 mt-1">Built strictly adhering to the Master Dossier guidelines and Legal Metrology Act, 2009</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="p-2 bg-amber-50 text-amber-700 w-fit rounded-lg mb-3">
                <Cpu className="h-5 w-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Deterministic Rule Engine</h4>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                Legal Metrology Rules 2011 (Seventh Schedule) step-function MPE evaluation without arbitrary AI hallucination.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="p-2 bg-blue-50 text-blue-700 w-fit rounded-lg mb-3">
                <Database className="h-5 w-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Layered Provenance Data</h4>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                DoCA Model Approvals (Layer A), Jharkhand Government Portal certificates (Layer B), and Live Verified records (Layer C).
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="p-2 bg-emerald-50 text-emerald-700 w-fit rounded-lg mb-3">
                <FileCheck2 className="h-5 w-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">QR & SHA-256 Certificates</h4>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                Automatically generated official PDF certificates with dynamic verification QR codes and tamper-evident SHA-256 hashes.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="p-2 bg-purple-50 text-purple-700 w-fit rounded-lg mb-3">
                <Sparkles className="h-5 w-5" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">OCR Digitization Hub</h4>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                Ingestion of legacy handwritten/printed scans with confidence metrics and mandatory human officer validation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto bg-[#0F2942] text-slate-400 text-xs py-8 px-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-slate-200">LegalMet Verify</span> — SIH26036 Online Verification System for Weighing and Measuring Instruments.
          </div>
          <div>
            Department of Legal Metrology • Government of India & State Directorates
          </div>
        </div>
      </footer>
    </div>
  );
};
