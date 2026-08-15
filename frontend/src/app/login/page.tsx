'use client';

import { useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const DEMO_ACCOUNTS = [
  { role: 'Administrator', username: 'admin', password: 'admin123' },
  { role: 'Investigating Officer', username: 'officer1', password: 'officer123' },
  { role: 'Cyber Analyst', username: 'analyst1', password: 'analyst123' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
        <div className="mb-6 flex items-center gap-3">
          <ShieldCheck className="h-10 w-10 text-brand-600" />
          <div>
            <h1 className="text-2xl font-bold">CrimeGPT</h1>
            <p className="text-sm text-slate-500">Cyber Crime Investigation Platform</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              className="input"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <div className="mt-6 rounded-lg bg-slate-50 p-4 text-sm">
          <p className="mb-2 font-medium text-slate-700">Demo accounts</p>
          <ul className="space-y-1 text-slate-600">
            {DEMO_ACCOUNTS.map((account) => (
              <li key={account.username}>
                <button
                  type="button"
                  className="text-brand-600 hover:underline"
                  onClick={() => {
                    setUsername(account.username);
                    setPassword(account.password);
                  }}
                >
                  {account.role}: {account.username} / {account.password}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  );
}
