import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ApiClient, API_BASE } from '../api/client';
import { Application, TestObservation, RuleEvaluationResult } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Smartphone, MapPin, Camera, CheckCircle2, XCircle, 
  Award, QrCode, Download, ShieldCheck, ArrowLeft, RefreshCw, Send, AlertTriangle 
} from 'lucide-react';

export const LMOInspectionExecution: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [app, setApp] = useState<Application | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Field Evidence State
  const [gpsLocked, setGpsLocked] = useState(false);
  const [latitude, setLatitude] = useState(24.3015);
  const [longitude, setLongitude] = useState(85.4228);
  const [address, setAddress] = useState('Barhi Market Yard, Sector 2, Hazaribagh, Jharkhand');
  const [lockTime, setLockTime] = useState(new Date().toLocaleString());

  // Test Observations
  const [observations, setObservations] = useState<TestObservation[]>([
    { test_name: 'Zero Load Test', test_type: 'ZERO_LOAD', test_load: 0.0, expected_value: 0.0, observed_value: 0.0, unit: 'kg' },
    { test_name: 'Half Capacity Test', test_type: 'HALF_CAPACITY', test_load: 15.0, expected_value: 15.0, observed_value: 15.005, unit: 'kg' },
    { test_name: 'Maximum Capacity Test', test_type: 'MAX_CAPACITY', test_load: 30.0, expected_value: 30.0, observed_value: 30.010, unit: 'kg' },
    { test_name: 'Eccentricity (Corner Load)', test_type: 'ECCENTRICITY', test_load: 10.0, expected_value: 10.0, observed_value: 10.002, unit: 'kg' },
  ]);

  const [remarks, setRemarks] = useState('Standard statutory verification carried out with verified standard weights. Sealing wire intact.');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [completionResult, setCompletionResult] = useState<any | null>(null);

  useEffect(() => {
    const loadApp = async () => {
      if (!id) return;
      try {
        const data = await ApiClient.getApplication(parseInt(id));
        setApp(data);
        const cap = data.instrument?.capacity || 30.0;
        setObservations([
          { test_name: 'Zero Load Test', test_type: 'ZERO_LOAD', test_load: 0.0, expected_value: 0.0, observed_value: 0.0, unit: 'kg' },
          { test_name: 'Half Capacity Test', test_type: 'HALF_CAPACITY', test_load: cap / 2, expected_value: cap / 2, observed_value: (cap / 2) + 0.005, unit: 'kg' },
          { test_name: 'Maximum Capacity Test', test_type: 'MAX_CAPACITY', test_load: cap, expected_value: cap, observed_value: cap + 0.010, unit: 'kg' },
          { test_name: 'Eccentricity (Corner Load)', test_type: 'ECCENTRICITY', test_load: cap / 3, expected_value: cap / 3, observed_value: (cap / 3) + 0.002, unit: 'kg' },
        ]);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadApp();
  }, [id]);

  const handleCaptureGps = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(pos.coords.latitude);
          setLongitude(pos.coords.longitude);
          setGpsLocked(true);
          setLockTime(new Date().toLocaleString());
        },
        () => {
          // Fallback to default Barhi coordinates
          setLatitude(24.3015);
          setLongitude(85.4228);
          setGpsLocked(true);
          setLockTime(new Date().toLocaleString());
        }
      );
    } else {
      setGpsLocked(true);
      setLockTime(new Date().toLocaleString());
    }
  };

  const handleObsChange = (index: number, field: string, value: any) => {
    const updated = [...observations];
    (updated[index] as any)[field] = value;
    setObservations(updated);
  };

  // Demo Scenarios Preset
  const setPassScenario = () => {
    const cap = app?.instrument?.capacity || 30.0;
    setObservations([
      { test_name: 'Zero Load Test', test_type: 'ZERO_LOAD', test_load: 0.0, expected_value: 0.0, observed_value: 0.0, unit: 'kg' },
      { test_name: 'Half Capacity Test', test_type: 'HALF_CAPACITY', test_load: cap / 2, expected_value: cap / 2, observed_value: (cap / 2) + 0.005, unit: 'kg' },
      { test_name: 'Maximum Capacity Test', test_type: 'MAX_CAPACITY', test_load: cap, expected_value: cap, observed_value: cap + 0.010, unit: 'kg' },
      { test_name: 'Eccentricity (Corner Load)', test_type: 'ECCENTRICITY', test_load: cap / 3, expected_value: cap / 3, observed_value: (cap / 3) + 0.002, unit: 'kg' },
    ]);
    setRemarks('All load tests verified within statutory MPE limits. Sealing stamp applied.');
  };

  const setFailScenario = () => {
    const cap = app?.instrument?.capacity || 30.0;
    setObservations([
      { test_name: 'Zero Load Test', test_type: 'ZERO_LOAD', test_load: 0.0, expected_value: 0.0, observed_value: 0.0, unit: 'kg' },
      { test_name: 'Half Capacity Test', test_type: 'HALF_CAPACITY', test_load: cap / 2, expected_value: cap / 2, observed_value: (cap / 2) + 0.045, unit: 'kg' }, // Large error!
      { test_name: 'Maximum Capacity Test', test_type: 'MAX_CAPACITY', test_load: cap, expected_value: cap, observed_value: cap + 0.080, unit: 'kg' },
      { test_name: 'Eccentricity (Corner Load)', test_type: 'ECCENTRICITY', test_load: cap / 3, expected_value: cap / 3, observed_value: (cap / 3) + 0.050, unit: 'kg' },
    ]);
    setRemarks('Instrument exceeds statutory Maximum Permissible Error (MPE). Commercial stamping rejected.');
  };

  const handleSubmitVerification = async () => {
    if (!app) return;
    setIsSubmitting(true);
    try {
      const res = await ApiClient.completeVerification(app.id, {
        observations,
        latitude,
        longitude,
        location_address: address,
        device_timestamp: new Date().toISOString(),
        remarks,
        photos: [
          'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=400&q=80'
        ]
      });
      setCompletionResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading || !app) {
    return <div className="p-8 text-center text-xs text-slate-500">Loading inspection details...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      <Link to="/lmo/dashboard" className="inline-flex items-center gap-1 text-xs font-bold text-slate-600 hover:text-slate-900">
        <ArrowLeft className="h-4 w-4" /> Back to Inspections Queue
      </Link>

      {/* Completion Modal / Result Overlay */}
      {completionResult && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xl space-y-5">
          <div className="text-center">
            {completionResult.overall_result === 'PASS' ? (
              <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle2 className="h-8 w-8" />
              </div>
            ) : (
              <div className="w-14 h-14 bg-rose-100 text-rose-700 rounded-full flex items-center justify-center mx-auto mb-3">
                <XCircle className="h-8 w-8" />
              </div>
            )}

            <h2 className="text-xl font-black text-slate-900">
              {completionResult.overall_result === 'PASS' ? 'Field Verification Passed!' : 'Field Verification Failed'}
            </h2>
            <p className="text-xs text-slate-600 mt-1">
              {completionResult.overall_result === 'PASS'
                ? 'Deterministic Rule Engine confirmed all observations within statutory MPE limits. Digital Certificate issued.'
                : 'Observed error exceeded legal limits. Certificate generation prevented and compliance risk logged.'}
            </p>
          </div>

          {completionResult.certificate_number && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-center space-y-2">
              <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wide block">
                Official Certificate Number
              </span>
              <div className="font-mono font-black text-xl text-emerald-950">
                {completionResult.certificate_number}
              </div>

              <div className="pt-2 flex flex-wrap justify-center gap-3">
                <Link
                  to={`/verify/${encodeURIComponent(completionResult.certificate_number)}`}
                  className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl shadow flex items-center gap-1.5"
                >
                  <QrCode className="h-4 w-4" /> Test Public QR Verification
                </Link>
                {completionResult.pdf_url && (
                  <a
                    href={`${API_BASE}/certificates/${app.id}/pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-bold text-xs rounded-xl shadow-xs flex items-center gap-1.5"
                  >
                    <Download className="h-4 w-4" /> Download PDF
                  </a>
                )}
              </div>
            </div>
          )}

          <div className="flex justify-center pt-2">
            <button
              onClick={() => navigate('/lmo/dashboard')}
              className="px-6 py-2.5 bg-[#0F2942] text-white font-bold text-xs rounded-xl"
            >
              Return to LMO Dashboard
            </button>
          </div>
        </div>
      )}

      {/* Main Inspection Header */}
      {!completionResult && (
        <>
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                  Application #{app.application_number}
                </span>
                <h1 className="text-xl font-extrabold text-slate-900 mt-2">
                  {app.applicant?.organization_name || app.applicant?.full_name}
                </h1>
                <p className="text-xs text-slate-500 mt-0.5">
                  Instrument: <b>{app.instrument?.model?.brand} {app.instrument?.model?.model_series}</b> (Serial: {app.instrument?.serial_number})
                </p>
              </div>
              <StatusBadge status={app.status} />
            </div>

            {/* Instrument Parameters Strip */}
            <div className="grid grid-cols-3 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px]">Capacity:</span>
                <span className="font-bold text-slate-800">{app.instrument?.capacity} {app.instrument?.unit}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Class:</span>
                <span className="font-bold text-slate-800">{app.instrument?.accuracy_class}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Scale Interval (e):</span>
                <span className="font-bold text-slate-800">{app.instrument?.verification_scale_interval} g</span>
              </div>
            </div>
          </div>

          {/* GPS and Geo-Evidence Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-indigo-600" />
                <h3 className="font-bold text-sm text-slate-900">GPS & Timestamp Lock Evidence</h3>
              </div>
              <button
                type="button"
                onClick={handleCaptureGps}
                className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-bold text-xs rounded-xl flex items-center gap-1"
              >
                <RefreshCw className="h-3.5 w-3.5" /> Lock Current GPS
              </button>
            </div>

            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs space-y-1 font-mono">
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Coordinates:</span>
                <span className="font-bold text-slate-900">{latitude.toFixed(4)}° N, {longitude.toFixed(4)}° E</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Timestamp:</span>
                <span className="text-slate-700">{lockTime}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Location:</span>
                <span className="text-slate-700 truncate max-w-[280px] font-sans">{address}</span>
              </div>
            </div>
          </div>

          {/* Quick Demo Scenario Switcher */}
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span className="text-xs font-bold text-amber-900 block">Golden Demo / Failure Preset</span>
              <span className="text-[11px] text-amber-700">Auto-fill test readings to demonstrate deterministic Pass or Fail</span>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={setPassScenario}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs"
              >
                Preset PASS
              </button>
              <button
                type="button"
                onClick={setFailScenario}
                className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-xs"
              >
                Preset FAIL
              </button>
            </div>
          </div>

          {/* Dynamic Test Observations Table */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-900">Statutory Field Test Observations</h3>
              <span className="text-[11px] text-slate-500">Legal Metrology Rules 2011</span>
            </div>

            <div className="space-y-3">
              {observations.map((obs, idx) => (
                <div key={idx} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-slate-900">{obs.test_name}</span>
                    <span className="text-[11px] text-slate-500 font-mono">Load: {obs.test_load} {obs.unit}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Standard Load ({obs.unit})</label>
                      <input
                        type="number"
                        step="0.001"
                        value={obs.test_load}
                        onChange={(e) => handleObsChange(idx, 'test_load', parseFloat(e.target.value))}
                        className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Observed Reading ({obs.unit})</label>
                      <input
                        type="number"
                        step="0.001"
                        value={obs.observed_value}
                        onChange={(e) => handleObsChange(idx, 'observed_value', parseFloat(e.target.value))}
                        className="w-full text-xs p-2 rounded-lg border border-slate-300 bg-white font-bold"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Officer Remarks */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Field Inspection Remarks & Sealing Status
              </label>
              <textarea
                rows={2}
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
              />
            </div>

            <button
              type="button"
              disabled={isSubmitting}
              onClick={handleSubmitVerification}
              className="w-full py-3 bg-[#0F2942] hover:bg-slate-800 text-white font-black text-sm rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
            >
              {isSubmitting ? 'Evaluating & Processing...' : 'Evaluate & Submit Verification Result'} <Send className="h-4 w-4" />
            </button>
          </div>
        </>
      )}
    </div>
  );
};
