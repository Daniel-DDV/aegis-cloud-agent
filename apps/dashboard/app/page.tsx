"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import clsx from "clsx";

const API_BASE = process.env.NEXT_PUBLIC_AEGIS_API_URL || "http://127.0.0.1:8000";

type Locale = "en" | "nl";

type AgentResult = {
  agent: string;
  status: string;
  risk_tier?: string | null;
  score?: number | null;
  rationale?: string;
  findings?: Array<{
    code: string;
    title: string;
    severity: string;
    evidence: string;
    articles: string[];
    remediation: string;
  }>;
  trace?: string[];
  error?: string | null;
};

type Scan = {
  id: string;
  label: string;
  status: string;
  overall_risk_tier?: string | null;
  created_at: string;
  self_audit: boolean;
  agents?: AgentResult[];
  top_remediations?: string[];
  report_markdown?: string | null;
  disclaimer?: string;
};

const copy = {
  en: {
    title: "Aegis Governance Lab",
    subtitle: "Multi-agent EU AI Act conformity drafts — observable, auditable, self-aware.",
    runMunicipal: "Scan municipal chatbot",
    runSelf: "Self-audit Aegis",
    agents: "Specialist agents",
    remediations: "Top remediations",
    report: "Audit report",
    scans: "Recent scans",
    disclaimer: "Draft conformity assessment for demonstration — not legal advice.",
    waiting: "Waiting for agent traces…",
    empty: "No scans yet. Launch one to watch five agents work in parallel.",
  },
  nl: {
    title: "Aegis Governance Lab",
    subtitle: "Multi-agent EU AI-verordening concept-beoordelingen — zichtbaar, auditbaar, zelfanalyserend.",
    runMunicipal: "Scan gemeentelijke chatbot",
    runSelf: "Zelfaudit Aegis",
    agents: "Specialistische agenten",
    remediations: "Belangrijkste maatregelen",
    report: "Auditrapport",
    scans: "Recente scans",
    disclaimer: "Conceptconformiteitsbeoordeling ter demonstratie — geen juridisch advies.",
    waiting: "Wachten op agent-traces…",
    empty: "Nog geen scans. Start er één om vijf agenten parallel te zien werken.",
  },
};

function tierColor(tier?: string | null) {
  switch (tier) {
    case "prohibited":
      return "text-danger border-danger/40 bg-danger/10";
    case "high":
      return "text-orange-300 border-orange-400/40 bg-orange-400/10";
    case "limited":
      return "text-warn border-warn/40 bg-warn/10";
    case "minimal":
      return "text-accent border-accent/40 bg-accent/10";
    default:
      return "text-muted border-line bg-slate-900/40";
  }
}

function statusPulse(status: string) {
  if (status === "running" || status === "pending") return "animate-pulse";
  return "";
}

export default function HomePage() {
  const [locale, setLocale] = useState<Locale>("en");
  const t = copy[locale];
  const [scans, setScans] = useState<Scan[]>([]);
  const [active, setActive] = useState<Scan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshList = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/scans`);
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      setScans(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "API unreachable");
    }
  }, []);

  const loadScan = useCallback(async (id: string) => {
    const res = await fetch(`${API_BASE}/api/scans/${id}`);
    if (!res.ok) return;
    const data = await res.json();
    setActive(data);
  }, []);

  useEffect(() => {
    refreshList();
    const id = setInterval(refreshList, 2000);
    return () => clearInterval(id);
  }, [refreshList]);

  useEffect(() => {
    if (!active?.id) return;
    if (active.status === "completed" || active.status === "failed") return;
    const id = setInterval(() => loadScan(active.id), 800);
    return () => clearInterval(id);
  }, [active?.id, active?.status, loadScan]);

  const startScan = async (kind: "municipal" | "self") => {
    setBusy(true);
    setError(null);
    try {
      const body =
        kind === "self"
          ? {
              target_path: ".",
              label: "Aegis self-audit",
              self_audit: true,
              metadata: { annex_iii_domains: ["essential_services"] },
            }
          : {
              target_path: "samples/municipal-chatbot-stub",
              label: "Municipal citizen chatbot (Mai-inspired stub)",
              metadata: { is_chatbot: true, annex_iii_domains: ["essential_services"] },
            };
      const res = await fetch(`${API_BASE}/api/scans`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`Scan failed (${res.status})`);
      const scan = await res.json();
      setActive(scan);
      await refreshList();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setBusy(false);
    }
  };

  const agents = useMemo(() => active?.agents || [], [active]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-8">
      <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 font-mono text-xs uppercase tracking-[0.2em] text-accent">
            Cursor Cloud Agent × CiviQs-grade governance
          </p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{t.title}</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted sm:text-base">{t.subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className={clsx(
              "rounded-full border px-3 py-1 text-xs font-medium",
              locale === "en" ? "border-accent text-accent" : "border-line text-muted"
            )}
            onClick={() => setLocale("en")}
          >
            EN
          </button>
          <button
            className={clsx(
              "rounded-full border px-3 py-1 text-xs font-medium",
              locale === "nl" ? "border-accent text-accent" : "border-line text-muted"
            )}
            onClick={() => setLocale("nl")}
          >
            NL
          </button>
        </div>
      </header>

      <section className="mb-6 flex flex-wrap gap-3">
        <button
          disabled={busy}
          onClick={() => startScan("municipal")}
          className="rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-ink hover:brightness-110 disabled:opacity-50"
        >
          {t.runMunicipal}
        </button>
        <button
          disabled={busy}
          onClick={() => startScan("self")}
          className="rounded-xl border border-line bg-panel px-4 py-2.5 text-sm font-semibold hover:border-accent/50 disabled:opacity-50"
        >
          {t.runSelf}
        </button>
        {error && <span className="self-center text-sm text-danger">{error}</span>}
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="card p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-lg font-medium">{t.agents}</h2>
            {active && (
              <span
                className={clsx(
                  "rounded-full border px-3 py-1 font-mono text-xs uppercase",
                  tierColor(active.overall_risk_tier)
                )}
              >
                {active.overall_risk_tier || active.status}
              </span>
            )}
          </div>
          {!active && <p className="text-sm text-muted">{t.empty}</p>}
          {active && (
            <div className="space-y-3">
              <div className="text-sm text-muted">
                <span className="font-mono text-accent">{active.label}</span>
                <span className="mx-2">·</span>
                <span className={statusPulse(active.status)}>{active.status}</span>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {agents.map((a) => (
                  <article key={a.agent} className="rounded-xl border border-line bg-ink/50 p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <h3 className="font-mono text-sm text-accent">{a.agent}</h3>
                      <span className={clsx("text-xs uppercase", statusPulse(a.status))}>
                        {a.status}
                      </span>
                    </div>
                    <p className="mb-2 text-xs text-muted">{a.rationale || t.waiting}</p>
                    {a.risk_tier && (
                      <span
                        className={clsx(
                          "mb-2 inline-block rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase",
                          tierColor(a.risk_tier)
                        )}
                      >
                        {a.risk_tier}
                        {typeof a.score === "number" ? ` · ${a.score.toFixed(2)}` : ""}
                      </span>
                    )}
                    {a.trace && a.trace.length > 0 && (
                      <ul className="mt-2 space-y-1 border-t border-line pt-2 font-mono text-[11px] text-slate-400">
                        {a.trace.map((line, i) => (
                          <li key={i}>› {line}</li>
                        ))}
                      </ul>
                    )}
                    {a.findings && a.findings.length > 0 && (
                      <p className="mt-2 text-xs text-slate-300">
                        {a.findings.length} finding(s)
                      </p>
                    )}
                  </article>
                ))}
              </div>
            </div>
          )}
        </section>

        <aside className="space-y-6">
          <section className="card p-5">
            <h2 className="mb-3 text-lg font-medium">{t.scans}</h2>
            <ul className="space-y-2">
              {scans.slice(0, 8).map((s) => (
                <li key={s.id}>
                  <button
                    onClick={() => loadScan(s.id)}
                    className={clsx(
                      "w-full rounded-lg border px-3 py-2 text-left text-sm transition",
                      active?.id === s.id
                        ? "border-accent/50 bg-accent/5"
                        : "border-line hover:border-accent/30"
                    )}
                  >
                    <div className="font-medium">{s.label}</div>
                    <div className="mt-1 flex items-center gap-2 font-mono text-[11px] text-muted">
                      <span>{s.status}</span>
                      {s.overall_risk_tier && (
                        <span className={clsx("rounded border px-1.5", tierColor(s.overall_risk_tier))}>
                          {s.overall_risk_tier}
                        </span>
                      )}
                    </div>
                  </button>
                </li>
              ))}
              {scans.length === 0 && <li className="text-sm text-muted">{t.empty}</li>}
            </ul>
          </section>

          <section className="card p-5">
            <h2 className="mb-3 text-lg font-medium">{t.remediations}</h2>
            {active?.top_remediations && active.top_remediations.length > 0 ? (
              <ol className="list-decimal space-y-2 pl-4 text-sm text-slate-300">
                {active.top_remediations.slice(0, 3).map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ol>
            ) : (
              <p className="text-sm text-muted">{t.waiting}</p>
            )}
          </section>
        </aside>
      </div>

      {active?.report_markdown && (
        <section className="card mt-6 p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-medium">{t.report}</h2>
            <a
              className="text-xs text-accent underline"
              href={`${API_BASE}/api/scans/${active.id}/report.md`}
              target="_blank"
              rel="noreferrer"
            >
              Open Markdown
            </a>
          </div>
          <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap rounded-xl bg-ink/70 p-4 font-mono text-xs text-slate-300">
            {active.report_markdown}
          </pre>
        </section>
      )}

      <footer className="mt-8 text-center text-xs text-muted">{t.disclaimer}</footer>
    </main>
  );
}
