import React, { useState, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { Application, Officer } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { 
  FileCheck2, CheckCircle2, XCircle, HelpCircle, 
  UserCheck, Calendar, Clock, AlertCircle, Eye, ArrowRight 
} from 'lucide-react';

export const AdminApplications: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [officers, setOfficers] = useState<any[]>([]);
  const [filter, setFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);

  // Scrutiny Modal
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [actionType, setActionType] = useState<'APPROVE' | 'QUERY' | 'REJECT' | 'ASSIGN' | null>(null);
  const [remarks, setRemarks] = useState('');
  const [selectedOfficerId, setSelectedOfficerId] = useState<number>(0);
  const [scheduledDate, setScheduledDate] = useState<string>(
    new Date(Date.now() + 86400000).toISOString().slice(0, 16)
  );
  const [isProcessing, setIsProcessing] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [apps, offList] = await Promise.all([
        ApiClient.getApplications(),
        ApiClient.getOfficers()
      ]);
      setApplications(apps);
      setOfficers(offList);
      if (offList.length > 0) {
        setSelectedOfficerId(offList[0].id);
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

  const handleAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedApp || !actionType) return;
    setIsProcessing(true);
    try {
      if (actionType === 'APPROVE') {
        await ApiClient.updateApplicationStatus(selectedApp.id, 'APPROVED', remarks || 'Documents scrutinized and approved for scheduling.');
      } else if (actionType === 'QUERY') {
        await ApiClient.updateApplicationStatus(selectedApp.id, 'QUERIED', remarks || 'Query: Please provide verification invoice and site location.');
      } else if (actionType === 'REJECT') {
        await ApiClient.updateApplicationStatus(selectedApp.id, 'REJECTED', remarks || 'Application rejected due to invalid model approval reference.');
      } else if (actionType === 'ASSIGN') {
        await ApiClient.assignOfficer(selectedApp.id, {
          officer_id: selectedOfficerId,
          scheduled_at: new Date(scheduledDate).toISOString(),
          remarks: remarks || 'Assigned for on-site field verification.'
        });
      }
      setSelectedApp(null);
      setActionType(null);
      setRemarks('');
      loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const filtered = applications.filter(a => {
    if (filter === 'ALL') return true;
    return a.status === filter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <FileCheck2 className="h-6 w-6 text-blue-600" /> Application Scrutiny & Officer Assignment
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Review trader submissions, raise queries, approve, and schedule LMO field verifications.
          </p>
        </div>

        {/* Filter Badges */}
        <div className="flex flex-wrap items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 text-xs">
          {['ALL', 'SUBMITTED', 'APPROVED', 'ASSIGNED', 'CERTIFICATE_ISSUED', 'QUERIED', 'FAILED'].map(st => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                filter === st ? 'bg-[#0F2942] text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {st.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Applications Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-500">
            No applications found matching the selected status.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3">Application No</th>
                  <th className="px-5 py-3">Trader / Enterprise</th>
                  <th className="px-5 py-3">Instrument Details</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Submitted</th>
                  <th className="px-5 py-3">Assigned Officer</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-medium">
                {filtered.map(app => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-4 font-mono font-bold text-blue-900">
                      {app.application_number}
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-bold text-slate-900">{app.applicant?.full_name}</div>
                      <div className="text-[11px] text-slate-500">{app.applicant?.organization_name || 'Barhi Mandi Store'}</div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-bold text-slate-800">
                        {app.instrument?.model?.brand || 'Scale'} ({app.instrument?.capacity} {app.instrument?.unit})
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        SN: {app.instrument?.serial_number} • {app.instrument?.accuracy_class}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {new Date(app.submitted_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {app.assigned_officer_id ? (
                        <div className="text-indigo-900 font-bold">
                          LMO Assigned
                          <span className="text-[10px] block text-slate-400 font-normal">
                            {app.scheduled_at ? new Date(app.scheduled_at).toLocaleDateString() : 'Pending'}
                          </span>
                        </div>
                      ) : (
                        <span className="text-slate-400">Unassigned</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-right space-x-1.5">
                      {app.status === 'SUBMITTED' && (
                        <>
                          <button
                            onClick={() => { setSelectedApp(app); setActionType('APPROVE'); }}
                            className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-xs"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => { setSelectedApp(app); setActionType('QUERY'); }}
                            className="px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-lg shadow-xs"
                          >
                            Query
                          </button>
                          <button
                            onClick={() => { setSelectedApp(app); setActionType('REJECT'); }}
                            className="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs rounded-lg border border-rose-200"
                          >
                            Reject
                          </button>
                        </>
                      )}

                      {app.status === 'APPROVED' && (
                        <button
                          onClick={() => { setSelectedApp(app); setActionType('ASSIGN'); }}
                          className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-lg shadow-xs flex items-center gap-1 inline-flex"
                        >
                          <UserCheck className="h-3.5 w-3.5" /> Assign LMO
                        </button>
                      )}

                      {app.status === 'ASSIGNED' && (
                        <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-1 rounded">
                          Scheduled for Field Verif
                        </span>
                      )}

                      {app.status === 'CERTIFICATE_ISSUED' && (
                        <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded">
                          Certificate Issued
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Action Scrutiny / Assignment Modal */}
      {selectedApp && actionType && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-base text-slate-900">
                {actionType === 'APPROVE' && 'Approve Application for Scheduling'}
                {actionType === 'QUERY' && 'Raise Official Scrutiny Query'}
                {actionType === 'REJECT' && 'Reject Verification Application'}
                {actionType === 'ASSIGN' && 'Assign LMO Officer & Set Schedule'}
              </h3>
              <button onClick={() => { setSelectedApp(null); setActionType(null); }} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs space-y-1">
              <div><strong>Application:</strong> {selectedApp.application_number}</div>
              <div><strong>Trader:</strong> {selectedApp.applicant?.full_name} ({selectedApp.applicant?.organization_name})</div>
              <div><strong>Instrument:</strong> {selectedApp.instrument?.model?.brand} (SN: {selectedApp.instrument?.serial_number})</div>
            </div>

            <form onSubmit={handleAction} className="space-y-4">
              {actionType === 'ASSIGN' ? (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                      Select Legal Metrology Officer (LMO)
                    </label>
                    <select
                      value={selectedOfficerId}
                      onChange={(e) => setSelectedOfficerId(parseInt(e.target.value))}
                      className="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white"
                    >
                      {officers.map(o => (
                        <option key={o.id} value={o.id}>
                          {o.name} ({o.officer_code}) — {o.jurisdiction}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                      Inspection Appointment Date & Time
                    </label>
                    <input
                      type="datetime-local"
                      required
                      value={scheduledDate}
                      onChange={(e) => setScheduledDate(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
                    />
                  </div>
                </>
              ) : null}

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Officer Remarks / Legal Notes
                </label>
                <textarea
                  rows={3}
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder={
                    actionType === 'QUERY' ? 'Specify missing documents or clarifications needed...' :
                    actionType === 'REJECT' ? 'State regulatory reason for rejection...' :
                    'Enter remarks...'
                  }
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-300"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => { setSelectedApp(null); setActionType(null); }}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isProcessing}
                  className={`px-5 py-2 text-xs font-bold text-white rounded-xl shadow transition-all ${
                    actionType === 'APPROVE' ? 'bg-emerald-600 hover:bg-emerald-700' :
                    actionType === 'QUERY' ? 'bg-amber-500 hover:bg-amber-600 text-slate-950' :
                    actionType === 'REJECT' ? 'bg-rose-600 hover:bg-rose-700' :
                    'bg-indigo-600 hover:bg-indigo-700'
                  }`}
                >
                  {isProcessing ? 'Processing...' : 'Confirm Action'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
