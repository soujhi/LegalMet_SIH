import React, { useState, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { ShieldCheck, Clock, User, ArrowRight, Eye, Layers } from 'lucide-react';

export const AdminAuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await ApiClient.getAuditLogs();
        setLogs(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadLogs();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-emerald-600" /> Immutable Audit Trails
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Complete traceable record of every administrative, officer, and trader state-changing action.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <span className="text-xs font-bold text-slate-700 uppercase">Recent System Events ({logs.length})</span>
        </div>

        {logs.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-500">
            No audit records captured yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold uppercase text-[11px]">
                <tr>
                  <th className="px-5 py-3">Timestamp</th>
                  <th className="px-5 py-3">Action</th>
                  <th className="px-5 py-3">Entity</th>
                  <th className="px-5 py-3">User / Actor</th>
                  <th className="px-5 py-3">State Change Payload</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-medium font-mono text-[11px]">
                {logs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60">
                    <td className="px-5 py-3 text-slate-500 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-800 font-bold border border-blue-200">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-700">
                      {log.entity_type} #{log.entity_id || 'N/A'}
                    </td>
                    <td className="px-5 py-3 font-sans font-semibold text-slate-900">
                      {log.user_name}
                    </td>
                    <td className="px-5 py-3 text-slate-600 max-w-md truncate">
                      {log.new_values ? JSON.stringify(log.new_values) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
