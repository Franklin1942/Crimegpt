'use client';

import { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { api } from '@/lib/api';
import type { Case } from '@/types';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const SUGGESTIONS = [
  'What evidence should I collect for this case?',
  'Which sections apply to a UPI fraud complaint?',
  'How do I freeze the fraudulent funds?',
  'What goes into the charge sheet?',
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [cases, setCases] = useState<Case[]>([]);
  const [caseId, setCaseId] = useState<string>('');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.get<Case[]>('/cases').then(setCases).catch(() => setCases([]));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function send(text: string) {
    if (!text.trim()) return;
    setMessages((current) => [...current, { role: 'user', content: text }]);
    setInput('');
    setSending(true);
    setError('');
    try {
      const response = await api.post<{ session_id: number; reply: string }>('/chat', {
        message: text,
        case_id: caseId ? Number(caseId) : undefined,
        session_id: sessionId ?? undefined,
      });
      setSessionId(response.session_id);
      setMessages((current) => [...current, { role: 'assistant', content: response.reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Copilot request failed');
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col space-y-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Investigator Copilot</h1>
          <p className="text-sm text-slate-500">Procedural and legal guidance for your cases</p>
        </div>
        <select className="input w-72" value={caseId} onChange={(event) => setCaseId(event.target.value)}>
          <option value="">No case context</option>
          {cases.map((item) => (
            <option key={item.id} value={item.id}>
              {item.case_number} — {item.title.slice(0, 40)}
            </option>
          ))}
        </select>
      </header>

      <div className="card flex-1 space-y-4 overflow-y-auto">
        {messages.length === 0 && (
          <div className="space-y-3">
            <p className="text-sm text-slate-500">Try one of these:</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  className="btn-secondary"
                  onClick={() => send(suggestion)}
                  disabled={sending}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`max-w-3xl whitespace-pre-line rounded-xl px-4 py-3 text-sm ${
              message.role === 'user'
                ? 'ml-auto bg-brand-600 text-white'
                : 'bg-slate-100 text-slate-800'
            }`}
          >
            {message.content}
          </div>
        ))}
        {sending && <p className="text-sm text-slate-500">Copilot is thinking…</p>}
        <div ref={bottomRef} />
      </div>

      {error && <p className="text-red-600">{error}</p>}

      <form
        className="flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          send(input);
        }}
      >
        <input
          className="input"
          placeholder="Ask about evidence, legal sections, procedure…"
          value={input}
          onChange={(event) => setInput(event.target.value)}
        />
        <button className="btn-primary" disabled={sending}>
          <Send className="h-4 w-4" /> Send
        </button>
      </form>
    </div>
  );
}
