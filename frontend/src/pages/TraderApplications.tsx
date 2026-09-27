import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ApiClient } from '../api/client';
import { Application, Instrument, ApplicationTimelineEvent } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { 
  FileText, Plus, Clock, CheckCircle2, AlertCircle, 
  Send, RefreshCw, Eye, Calendar, ArrowRight 
} from 'lucide-react';

export const TraderApplications: React.FC = () => {
  const [searchParams] = useSearchParams();
  const applyInstId = searchParams.get('apply_inst_id');

  const [applications, setApplications] = useState<Application[]>([]);
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [showNewModal, setShowNewModal] = useState(false);
  const [selectedInstId, setSelectedInstId] = useState<number>(0);
  const [appType, setAppType] = useState<'RE_VERIFICATION' | 'INITIAL_VERIFICATION'>('RE_VERIFICATION');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Timeline Modal State
  const [timelineApp, setTimelineApp] = useState<Application | null>(null);
  const [timelineEvents, setTimelineEvents] = useState<ApplicationTimelineEvent[]>([]);
  const [isTimelineLoading, setIsTimelineLoading] = useState(false);

  // Query Resubmit State
  const [resubmitApp, setResubmitApp] = useState<Application | null>(null);
  const [resubmitNotes, setResubmitNotes] = useState('');

  const loadData = async () => {
    try {
      const [apps, insts] = await Promise.all([
        ApiClient.getApplications(),
        ApiClient.getInstruments()
      ]);
      setApplications(apps);
      setInstruments(insts);
      if (insts.length > 0 && !selectedInstId) {
        setSelectedInstId(applyInstId ? parseInt(applyInstId) : insts[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
    if (applyInstId) {
      setShowNewModal(true);
    }
  }, [applyInstId]);

  const handleCreateApp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInstId) return;
    setIsSubmitting(true);
    try {
      await ApiClient.createApplication({
        instrument_id: selectedInstId,
        application_type: appType,
        documents: [
          { type: 'TAX_INVOICE', name: 'Purchase_Invoice_2024.pdf', url: '/storage/uploads/invoice.pdf' },
          { type: 'PREVIOUS_CERTIFICATE', name: 'Prev_Certificate_Jharkhand.pdf', url: '/storage/uploads/prev_cert.pdf' }
        ]
      });
      setShowNewModal(false);
      loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const openTimeline = async (app: Application) => {
    setTimelineApp(app);
    setIsTimelineLoading(true);
    try {
      const events = await ApiClient.getApplicationTimeline(app.id);
      setTimelineEvents(events);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTimelineLoading(false);
    }
  };

  const handleResubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resubmitApp) return;
    try {
      await ApiClient.updateApplicationStatus(
        resubmitApp.id,
        'RESUBMITTED',
        resubmitNotes || 'Clarification and revised documents uploaded by trader.'
      );
      setResubmitApp(null);
      setResubmitNotes('');
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <FileText className="h-6 w-6 text-amber-500" /> Verification Applications
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Submit, track scrutiny progress, view inspection appointments, and resolve queries.
          </p>
        </div>
        <button
          onClick={() => setShowNewModal(true)}
          className="px-4 py-2.5 bg-[#0F2942] hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow transition-all flex items-center gap-2"
        >
          <Plus className="h-4 w-4" /> Apply for Verification
        </button>
      </div>

      {/* Applications Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <span className="text-xs font-bold text-slate-700 uppercase">All Submitted Requests ({applications.length})</span>
        </div>

        {applications.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-10 w-10 text-slate-300 mx-auto mb-2" />
            <p className="text-xs font-semibold text-slate-600">No applications found</p>
            <button
              onClick={() => setShowNewModal(true)}
              className="mt-2 px-3 py-1.5 bg-amber-500 text-slate-950 font-bold text-xs rounded-lg"
            >
              Submit Your First Request
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3">Application No</th>
                  <th className="px-5 py-3">Instrument</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Submitted On</th>
                  <th className="px-5 py-3">Scheduled / Officer</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-medium">
                {applications.map(app => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-4 font-mono font-bold text-blue-900">
                      {app.application_number}
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-bold text-slate-900">{app.instrument?.model?.brand || 'Scale'} ({app.instrument?.capacity} {app.instrument?.unit})</div>
                      <div className="text-[11px] text-slate-400 font-mono">SN: {app.instrument?.serial_number}</div>
                    </td>
                    <td className="px-5 py-4 text-slate-700">
                      {app.application_type.replace(/_/g, ' ')}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {new Date(app.submitted_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {app.scheduled_at ? (
                        <div>
                          <span className="font-bold text-slate-800">{new Date(app.scheduled_at).toLocaleDateString()}</span>
                          <span className="text-[11px] block text-indigo-700 font-medium">Assigned to LMO</span>
                        </div>
                      ) : (
                        <span className="text-slate-400">Pending Scrutiny</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-right space-x-2">
                      <button
                        onClick={() => openTimeline(app)}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg"
                      >
                        Timeline
                      </button>
                      {app.status === 'QUERIED' && (
                        <button
                          onClick={() => setResubmitApp(app)}
                          className="px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-bold rounded-lg shadow-xs"
                        >
                          Respond Query
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Application Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-base text-slate-900">Apply for Verification / Re-verification</h3>
              <button onClick={() => setShowNewModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <form onSubmit={handleCreateApp} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Select Registered Instrument
                </label>
                <select
                  value={selectedInstId}
                  onChange={(e) => setSelectedInstId(parseInt(e.target.value))}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                >
                  {instruments.map(inst => (
                    <option key={inst.id} value={inst.id}>
                      {inst.model?.brand || 'Scale'} ({inst.serial_number}) — {inst.capacity} {inst.unit} ({inst.accuracy_class})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Verification Category
                </label>
                <select
                  value={appType}
                  onChange={(e) => setAppType(e.target.value as any)}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                >
                  <option value="RE_VERIFICATION">Periodic Re-Verification (Annual Statutory)</option>
                  <option value="INITIAL_VERIFICATION">Initial Stamping / Verification (New Scale)</option>
                </select>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 space-y-1">
                <div className="font-bold text-slate-800">Statutory Verification Fee: ₹ 250.00</div>
                <div className="text-[11px] text-slate-500">Includes on-site LMO inspection, test standard weights, and digital QR certificate issuance.</div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 text-xs font-bold bg-[#0F2942] hover:bg-slate-800 text-white rounded-xl shadow flex items-center gap-1.5"
                >
                  <Send className="h-3.5 w-3.5" /> Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Timeline Modal */}
      {timelineApp && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-base text-slate-900">Application State Timeline</h3>
                <span className="font-mono text-xs font-semibold text-blue-800">{timelineApp.application_number}</span>
              </div>
              <button onClick={() => setTimelineApp(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            {isTimelineLoading ? (
              <div className="text-center py-6 text-xs text-slate-500">Loading audit history...</div>
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {timelineEvents.map((evt, idx) => (
                  <div key={idx} className="relative">
                    <div className="absolute -left-6 top-1 w-3.5 h-3.5 rounded-full bg-blue-600 ring-4 ring-blue-100"></div>
                    <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                      <span>{evt.to_status}</span>
                      <span className="text-[10px] text-slate-400 font-normal">by {evt.changed_by}</span>
                    </div>
                    {evt.remarks && (
                      <p className="text-xs text-slate-600 mt-0.5 bg-slate-50 p-2 rounded-lg border border-slate-100">
                        {evt.remarks}
                      </p>
                    )}
                    <span className="text-[10px] text-slate-400 block mt-1">
                      {new Date(evt.created_at).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Query Response Modal */}
      {resubmitApp && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-base text-slate-900">Respond to Scrutiny Query</h3>
              <button onClick={() => setResubmitApp(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900">
              <strong>Admin Note:</strong> {resubmitApp.reviewer_notes || 'Please provide updated installation certificate and clarify establishment location.'}
            </div>

            <form onSubmit={handleResubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Clarification Response
                </label>
                <textarea
                  rows={3}
                  required
                  value={resubmitNotes}
                  onChange={(e) => setResubmitNotes(e.target.value)}
                  placeholder="Enter clarification details and confirmed address..."
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setResubmitApp(null)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 text-xs font-bold bg-amber-500 hover:bg-amber-600 text-slate-950 rounded-xl shadow"
                >
                  Resubmit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
