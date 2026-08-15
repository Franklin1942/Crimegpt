'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, BadgeIndianRupee, FolderOpen, Layers } from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import Badge from '@/components/Badge';
import StatCard from '@/components/StatCard';
import { api } from '@/lib/api';
import type { DashboardStats, RecentActivity } from '@/types';

const COLORS = ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#0ea5e9', '#f97316'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<RecentActivity[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.get<DashboardStats>('/analytics/dashboard'),
      api.get<RecentActivity[]>('/analytics/recent-activity'),
    ])
      .then(([dashboard, recent]) => {
        setStats(dashboard);
        setActivity(recent);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load dashboard'));
  }, []);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!stats) return <p className="text-slate-500">Loading dashboard…</p>;

  const crimeData = stats.crime_distribution.map((item) => ({
    name: item.crime_type.replace(/_/g, ' '),
    value: item.count,
  }));

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-slate-500">Case analytics across the Cyber Crime Branch</p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total cases" value={stats.total_cases} icon={Layers} />
        <StatCard label="Open cases" value={stats.open_cases} icon={FolderOpen} accent="text-blue-600" />
        <StatCard
          label="Critical cases"
          value={stats.critical_cases}
          icon={AlertTriangle}
          accent="text-red-600"
        />
        <StatCard
          label="Reported loss"
          value={`₹${stats.total_loss_amount.toLocaleString('en-IN')}`}
          icon={BadgeIndianRupee}
          accent="text-emerald-600"
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-4 font-semibold">Crime type distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={crimeData} dataKey="value" nameKey="name" outerRadius={90} label>
                  {crimeData.map((entry, index) => (
                    <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h2 className="mb-4 font-semibold">Severity analysis</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.severity_distribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="priority" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card lg:col-span-2">
          <h2 className="mb-4 font-semibold">Monthly case trend</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="card">
        <h2 className="mb-4 font-semibold">Recent activity</h2>
        <ul className="divide-y divide-slate-100">
          {activity.map((item) => (
            <li key={item.case_id} className="flex items-center justify-between py-3">
              <div>
                <Link href={`/cases/${item.case_id}`} className="font-medium text-brand-600 hover:underline">
                  {item.case_number}
                </Link>
                <p className="text-sm text-slate-600">{item.title}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge value={item.priority} />
                <Badge value={item.status} />
              </div>
            </li>
          ))}
          {activity.length === 0 && <li className="py-3 text-sm text-slate-500">No activity yet.</li>}
        </ul>
      </section>
    </div>
  );
}
