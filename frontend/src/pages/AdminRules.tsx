import React, { useState, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { RuleEvaluationResult } from '../types';
import { Cpu, ShieldCheck, Scale, Play, CheckCircle2, XCircle, Info, BookOpen } from 'lucide-react';

export const AdminRules: React.FC = () => {
  const [rules, setRules] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Live Simulator Form
  const [simClass, setSimClass] = useState('Class III');
  const [simCap, setSimCap] = useState(30.0);
  const [simInterval, setSimInterval] = useState(5.0); // e = 5g
  const [simLoad, setSimLoad] = useState(10.0); // 10 kg
  const [simObserved, setSimObserved] = useState(10.005); // 10.005 kg
  const [simUnit, setSimUnit] = useState('kg');
  const [simResult, setSimResult] = useState<RuleEvaluationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    const loadRules = async () => {
      try {
        const data = await ApiClient.getRules();
        setRules(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadRules();
    // Run initial simulation
    runSimulation(simClass, simCap, simInterval, simLoad, simObserved);
  }, []);

  const runSimulation = async (accClass: string, cap: number, interval: number, load: number, obs: number) => {
    setIsSimulating(true);
    try {
      const res = await ApiClient.evaluateRule({
        accuracy_class: accClass,
        capacity: cap,
        verification_scale_interval: interval,
        test_load: load,
        observed_value: obs,
        test_type: 'LOAD_TEST',
        unit: 'kg'
      });
      setSimResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleSimSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runSimulation(simClass, simCap, simInterval, simLoad, simObserved);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          <Cpu className="h-6 w-6 text-amber-500" /> Deterministic Regulatory Rule Engine
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Statutory Maximum Permissible Error (MPE) rules codified under Legal Metrology (General) Rules, 2011 (Seventh Schedule).
        </p>
      </div>

      {/* Simulator Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Play className="h-5 w-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">Interactive MPE Statutory Simulator</h3>
          </div>
          <span className="text-[11px] font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
            Real-time Evaluation
          </span>
        </div>

        <form onSubmit={handleSimSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">Accuracy Class</label>
            <select
              value={simClass}
              onChange={(e) => setSimClass(e.target.value)}
              className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
            >
              <option value="Class III">Class III (Medium Accuracy)</option>
              <option value="Class IIII">Class IIII (Ordinary Accuracy)</option>
              <option value="Class II">Class II (High Accuracy)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">Max Capacity (kg)</label>
            <input
              type="number"
              step="0.1"
              value={simCap}
              onChange={(e) => setSimCap(parseFloat(e.target.value))}
              className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">Scale Interval e (g)</label>
            <input
              type="number"
              step="0.1"
              value={simInterval}
              onChange={(e) => setSimInterval(parseFloat(e.target.value))}
              className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">Test Load (kg)</label>
            <input
              type="number"
              step="0.001"
              value={simLoad}
              onChange={(e) => setSimLoad(parseFloat(e.target.value))}
              className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">Observed Reading (kg)</label>
            <div className="flex gap-1.5">
              <input
                type="number"
                step="0.0001"
                value={simObserved}
                onChange={(e) => setSimObserved(parseFloat(e.target.value))}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
              />
              <button
                type="submit"
                className="px-3 py-2 bg-[#0F2942] hover:bg-slate-800 text-white rounded-xl text-xs font-bold shrink-0"
              >
                Test
              </button>
            </div>
          </div>
        </form>

        {/* Quick Presets for Demo */}
        <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
          <span className="font-semibold">Quick Demo Scenarios:</span>
          <button
            type="button"
            onClick={() => { setSimLoad(10.0); setSimObserved(10.005); runSimulation('Class III', 30, 5, 10.0, 10.005); }}
            className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded font-bold hover:bg-emerald-100"
          >
            ✓ PASS Scenario (+0.005kg error ≤ ±0.010kg MPE)
          </button>
          <button
            type="button"
            onClick={() => { setSimLoad(10.0); setSimObserved(10.025); runSimulation('Class III', 30, 5, 10.0, 10.025); }}
            className="px-2 py-0.5 bg-rose-50 text-rose-700 border border-rose-200 rounded font-bold hover:bg-rose-100"
          >
            ✗ FAIL Scenario (+0.025kg error &gt; ±0.010kg MPE)
          </button>
        </div>

        {/* Simulation Output Card */}
        {simResult && (
          <div className={`mt-5 p-5 rounded-2xl border ${simResult.is_compliant ? 'bg-emerald-50/70 border-emerald-300 text-emerald-950' : 'bg-rose-50/70 border-rose-300 text-rose-950'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {simResult.is_compliant ? (
                  <div className="p-2 bg-emerald-600 text-white rounded-xl">
                    <CheckCircle2 className="h-6 w-6" />
                  </div>
                ) : (
                  <div className="p-2 bg-rose-600 text-white rounded-xl">
                    <XCircle className="h-6 w-6" />
                  </div>
                )}
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider">
                    Deterministic Compliance Outcome
                  </span>
                  <h4 className="text-lg font-black">
                    {simResult.result === 'PASS' ? 'PASS — Within Legal Error Limit' : 'FAIL — Error Exceeds Statutory MPE'}
                  </h4>
                </div>
              </div>

              <div className="text-right">
                <span className="text-xs font-mono font-bold block">Rule Code: {simResult.rule_code}</span>
                <span className="text-[10px] text-slate-600">
                  {simResult.is_verified_government_rule ? '✓ Verified Statutory Rule' : 'Demo Rule'}
                </span>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 bg-white/80 p-3.5 rounded-xl border border-slate-200/60 text-xs">
              <div>
                <span className="text-slate-500 block">Calculated Error:</span>
                <span className="font-mono font-bold text-slate-900">{simResult.error_calculated > 0 ? '+' : ''}{simResult.error_calculated.toFixed(4)} kg</span>
              </div>
              <div>
                <span className="text-slate-500 block">Permissible MPE Limit:</span>
                <span className="font-mono font-bold text-slate-900">±{simResult.tolerance_mpe} kg ({simResult.mpe_formula})</span>
              </div>
              <div>
                <span className="text-slate-500 block">Statutory Reference:</span>
                <span className="font-medium text-slate-800 truncate block">{simResult.rule_source_reference}</span>
              </div>
            </div>

            <p className="mt-2 text-xs font-medium text-slate-700 leading-relaxed">
              {simResult.explanation}
            </p>
          </div>
        )}
      </div>

      {/* Configured Rule Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-slate-600" />
            <span className="text-xs font-bold text-slate-700 uppercase">Codified Statutory MPE Limits ({rules.length})</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px]">
              <tr>
                <th className="px-5 py-3">Rule Code</th>
                <th className="px-5 py-3">Accuracy Class</th>
                <th className="px-5 py-3">Load Range (Intervals e)</th>
                <th className="px-5 py-3">MPE Formula</th>
                <th className="px-5 py-3">Government Source Reference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white font-medium">
              {rules.map((r, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="px-5 py-3 font-mono font-bold text-blue-900">{r.rule_code}</td>
                  <td className="px-5 py-3 font-bold text-slate-800">{r.accuracy_class}</td>
                  <td className="px-5 py-3 text-slate-600">{r.min_range_e} e to {r.max_range_e} e</td>
                  <td className="px-5 py-3 font-bold text-emerald-800">{r.mpe_formula}</td>
                  <td className="px-5 py-3 text-slate-500 text-[11px] max-w-xs">{r.rule_source_reference}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
