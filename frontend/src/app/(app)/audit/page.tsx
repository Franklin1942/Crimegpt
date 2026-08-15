'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string;
  resource_id: string;
  details: string;
  ip_address: string;
  created_at: string;
}

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get<AuditLog[]>('/audit')
      .then(setLogs)
      .catch((err) =>
        setError(
          err instanceof Error && err.message
            ? err.message
            : 'Audit logs are restricted to administrators',
        ),
      );
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Audit log</h1>
        <p className="text-sm text-slate-500">Administrator-only compliance trail</p>
      </header>

      {error && <p className="rounded-lg bg-amber-50 px-3 py-2 text-amber-800">{error}</p>}

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Resource</th>
              <th className="px-4 py-3">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="px-4 py-3">{new Date(log.created_at).toLocaleString()}</td>
                <td className="px-4 py-3">{log.user_id ?? '—'}</td>
                <td className="px-4 py-3">{log.action}</td>
                <td className="px-4 py-3">
                  {log.resource_type} {log.resource_id}
                </td>
                <td className="px-4 py-3 text-slate-600">{log.details}</td>
              </tr>
            ))}
            {logs.length === 0 && !error && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No audit entries.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
