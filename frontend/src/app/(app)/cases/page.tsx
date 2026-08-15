'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, Search } from 'lucide-react';
import Badge from '@/components/Badge';
import { api } from '@/lib/api';
import type { Case } from '@/types';

const CRIME_TYPES = [
  'phishing',
  'upi_fraud',
  'identity_theft',
  'malware',
  'ransomware',
  'social_media_fraud',
  'sim_swap',
  'financial_fraud',
  'cyber_stalking',
  'data_breach',
  'other',
];

const PRIORITIES = ['low', 'medium', 'high', 'critical'];

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (statusFilter) params.set('status', statusFilter);
    const query = params.toString();
    try {
      setCases(await api.get<Case[]>(`/cases${query ? `?${query}` : ''}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load cases');
    }
  }, [search, statusFilter]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Cases</h1>
          <p className="text-sm text-slate-500">{cases.length} case(s)</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm((value) => !value)}>
          <Plus className="h-4 w-4" /> New case
        </button>
      </header>

      {showForm && <NewCaseForm onCreated={() => { setShowForm(false); load(); }} />}

      <div className="card flex flex-wrap items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            className="input pl-9"
            placeholder="Search by title, case number or complainant"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <select
          className="input w-48"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
        >
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In progress</option>
          <option value="pending">Pending</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      {error && <p className="text-red-600">{error}</p>}

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3">Case</th>
              <th className="px-4 py-3">Crime type</th>
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Loss</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {cases.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50">
                <td className="px-4 py-3">
                  <Link href={`/cases/${item.id}`} className="font-medium text-brand-600 hover:underline">
                    {item.case_number}
                  </Link>
                  <p className="text-slate-600">{item.title}</p>
                </td>
                <td className="px-4 py-3 capitalize">{item.crime_type.replace(/_/g, ' ')}</td>
                <td className="px-4 py-3">
                  <Badge value={item.priority} />
                </td>
                <td className="px-4 py-3">
                  <Badge value={item.status} />
                </td>
                <td className="px-4 py-3">₹{item.loss_amount.toLocaleString('en-IN')}</td>
              </tr>
            ))}
            {cases.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No cases found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function NewCaseForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    crime_type: 'other',
    priority: 'medium',
    complainant_name: '',
    complainant_contact: '',
    location: '',
    loss_amount: 0,
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/cases', { ...form, loss_amount: Number(form.loss_amount) });
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create case');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card grid gap-4 md:grid-cols-2">
      <div className="md:col-span-2">
        <label className="label">Title</label>
        <input
          className="input"
          required
          minLength={3}
          value={form.title}
          onChange={(event) => setForm({ ...form, title: event.target.value })}
        />
      </div>
      <div className="md:col-span-2">
        <label className="label">Complaint description</label>
        <textarea
          className="input h-28"
          value={form.description}
          onChange={(event) => setForm({ ...form, description: event.target.value })}
        />
      </div>
      <div>
        <label className="label">Crime type</label>
        <select
          className="input"
          value={form.crime_type}
          onChange={(event) => setForm({ ...form, crime_type: event.target.value })}
        >
          {CRIME_TYPES.map((type) => (
            <option key={type} value={type}>
              {type.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="label">Priority</label>
        <select
          className="input"
          value={form.priority}
          onChange={(event) => setForm({ ...form, priority: event.target.value })}
        >
          {PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>
              {priority}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="label">Complainant</label>
        <input
          className="input"
          value={form.complainant_name}
          onChange={(event) => setForm({ ...form, complainant_name: event.target.value })}
        />
      </div>
      <div>
        <label className="label">Contact</label>
        <input
          className="input"
          value={form.complainant_contact}
          onChange={(event) => setForm({ ...form, complainant_contact: event.target.value })}
        />
      </div>
      <div>
        <label className="label">Location</label>
        <input
          className="input"
          value={form.location}
          onChange={(event) => setForm({ ...form, location: event.target.value })}
        />
      </div>
      <div>
        <label className="label">Loss amount (₹)</label>
        <input
          type="number"
          min={0}
          className="input"
          value={form.loss_amount}
          onChange={(event) => setForm({ ...form, loss_amount: Number(event.target.value) })}
        />
      </div>
      {error && <p className="md:col-span-2 text-red-600">{error}</p>}
      <div className="md:col-span-2">
        <button className="btn-primary" disabled={saving}>
          {saving ? 'Saving…' : 'Create case'}
        </button>
      </div>
    </form>
  );
}
