'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Download, FileText, Sparkles, Upload } from 'lucide-react';
import Badge from '@/components/Badge';
import { api } from '@/lib/api';
import type { Analysis, Case, CaseDocument } from '@/types';

const STATUSES = ['open', 'in_progress', 'pending', 'closed'];

export default function CaseDetailPage() {
  const params = useParams<{ id: string }>();
  const caseId = params.id;

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [documents, setDocuments] = useState<CaseDocument[]>([]);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [checklist, setChecklist] = useState<string[]>([]);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [detail, docs, results] = await Promise.all([
        api.get<Case>(`/cases/${caseId}`),
        api.get<CaseDocument[]>(`/documents/case/${caseId}`),
        api.get<Analysis[]>(`/ai/cases/${caseId}/analyses`),
      ]);
      setCaseData(detail);
      setDocuments(docs);
      setAnalyses(results);
      const checklistResponse = await api.get<{ items: string[] }>(
        `/legal/evidence-checklist?case_id=${caseId}`,
      );
      setChecklist(checklistResponse.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    }
  }, [caseId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy('upload');
    try {
      const formData = new FormData();
      formData.append('file', file);
      await api.upload(`/documents/case/${caseId}`, formData);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setBusy('');
      event.target.value = '';
    }
  }

  async function runAnalysis(documentId: number) {
    setBusy(`analyze-${documentId}`);
    try {
      await api.post(`/ai/documents/${documentId}/analyze`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setBusy('');
    }
  }

  async function updateStatus(status: string) {
    await api.patch(`/cases/${caseId}`, { status });
    await load();
  }

  async function downloadChargeSheet() {
    setBusy('charge-sheet');
    try {
      const blob = await api.download(`/reports/cases/${caseId}/charge-sheet`);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `charge-sheet-${caseData?.case_number ?? caseId}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not generate charge sheet');
    } finally {
      setBusy('');
    }
  }

  if (error) return <p className="text-red-600">{error}</p>;
  if (!caseData) return <p className="text-slate-500">Loading case…</p>;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{caseData.case_number}</p>
          <h1 className="text-2xl font-bold">{caseData.title}</h1>
          <div className="mt-2 flex items-center gap-2">
            <Badge value={caseData.priority} />
            <Badge value={caseData.status} />
            <span className="text-sm capitalize text-slate-600">
              {caseData.crime_type.replace(/_/g, ' ')}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="input w-44"
            value={caseData.status}
            onChange={(event) => updateStatus(event.target.value)}
          >
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {status.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
          <button className="btn-primary" onClick={downloadChargeSheet} disabled={busy === 'charge-sheet'}>
            <Download className="h-4 w-4" /> Charge sheet
          </button>
        </div>
      </header>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-2">
          <h2 className="mb-2 font-semibold">Complaint details</h2>
          <p className="whitespace-pre-line text-sm text-slate-700">{caseData.description || '—'}</p>
          <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-slate-500">Complainant</dt>
              <dd>{caseData.complainant_name || '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Contact</dt>
              <dd>{caseData.complainant_contact || '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Location</dt>
              <dd>{caseData.location || '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Reported loss</dt>
              <dd>₹{caseData.loss_amount.toLocaleString('en-IN')}</dd>
            </div>
          </dl>
        </div>

        <div className="card">
          <h2 className="mb-2 font-semibold">Evidence checklist</h2>
          <ul className="space-y-2 text-sm text-slate-700">
            {checklist.map((item) => (
              <li key={item} className="flex gap-2">
                <input type="checkbox" className="mt-1" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="card">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-semibold">Documents</h2>
          <label className="btn-secondary cursor-pointer">
            <Upload className="h-4 w-4" />
            {busy === 'upload' ? 'Uploading…' : 'Upload evidence'}
            <input type="file" className="hidden" onChange={handleUpload} />
          </label>
        </div>
        <ul className="divide-y divide-slate-100">
          {documents.map((document) => (
            <li key={document.id} className="flex items-center justify-between py-3 text-sm">
              <span className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-slate-400" />
                {document.filename}
                <span className="text-slate-400">({Math.round(document.size_bytes / 1024)} KB)</span>
              </span>
              <button
                className="btn-secondary"
                onClick={() => runAnalysis(document.id)}
                disabled={busy === `analyze-${document.id}`}
              >
                <Sparkles className="h-4 w-4" />
                {busy === `analyze-${document.id}` ? 'Analysing…' : 'Run AI analysis'}
              </button>
            </li>
          ))}
          {documents.length === 0 && (
            <li className="py-3 text-sm text-slate-500">No documents uploaded yet.</li>
          )}
        </ul>
      </section>

      {analyses.map((analysis) => (
        <section key={analysis.id} className="card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">
              AI analysis · <span className="capitalize">{analysis.crime_type.replace(/_/g, ' ')}</span>
            </h2>
            <span className="text-xs text-slate-500">
              {analysis.confidence}% confidence · {analysis.engine}
            </span>
          </div>
          <p className="text-sm text-slate-700">{analysis.summary}</p>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h3 className="mb-2 text-sm font-medium">Extracted entities</h3>
              <ul className="space-y-1 text-sm text-slate-700">
                {Object.entries(analysis.entities)
                  .filter(([, values]) => values.length > 0)
                  .map(([key, values]) => (
                    <li key={key}>
                      <span className="capitalize text-slate-500">{key.replace(/_/g, ' ')}: </span>
                      {values.join(', ')}
                    </li>
                  ))}
              </ul>
            </div>
            <div>
              <h3 className="mb-2 text-sm font-medium">Recommended sections</h3>
              <ul className="space-y-1 text-sm text-slate-700">
                {analysis.legal_sections.map((section) => (
                  <li key={`${section.act}-${section.section}`}>
                    <span className="font-medium">
                      {section.act} {section.section}
                    </span>{' '}
                    — {section.title} ({section.confidence}%)
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {analysis.timeline.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-medium">Timeline</h3>
              <ol className="space-y-1 border-l border-slate-200 pl-4 text-sm text-slate-700">
                {analysis.timeline.map((event) => (
                  <li key={`${event.date}-${event.event}`}>
                    <span className="font-medium">{event.date}</span> — {event.event}
                  </li>
                ))}
              </ol>
            </div>
          )}

          <div>
            <h3 className="mb-2 text-sm font-medium">Investigation recommendations</h3>
            <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
              {analysis.recommendations.map((recommendation) => (
                <li key={recommendation}>{recommendation}</li>
              ))}
            </ul>
          </div>
        </section>
      ))}
    </div>
  );
}
