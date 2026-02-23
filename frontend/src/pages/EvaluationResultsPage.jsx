import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { evaluationsAPI, suppliersAPI } from '../services/api';
import { getUser } from '../utils/auth';

// ── Helpers ───────────────────────────────────────────────────────
function RiskBanner({ risk, supplierName, confidence, createdAt }) {
  const config = {
    High:   { bg: 'linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.05))',   border: 'rgba(239,68,68,0.4)',   color: '#EF4444', label: 'HIGH RISK'   },
    Medium: { bg: 'linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.05))', border: 'rgba(245,158,11,0.4)',  color: '#F59E0B', label: 'MEDIUM RISK' },
    Low:    { bg: 'linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05))', border: 'rgba(16,185,129,0.4)',  color: '#10B981', label: 'LOW RISK'    },
  }[risk] || {
    bg: 'linear-gradient(135deg, rgba(26,58,92,0.4), rgba(26,58,92,0.1))',
    border: 'rgba(26,58,92,0.6)', color: '#64748B', label: 'PENDING',
  };

  return (
    <div style={{
      padding: '32px', borderRadius: '14px', marginBottom: '24px',
      background: config.bg, border: `1px solid ${config.border}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '6px' }}>
            Supplier Evaluated
          </p>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.6rem', fontWeight: 700, color: '#E2E8F0', marginBottom: '12px' }}>
            {supplierName || 'Unknown Supplier'}
          </h1>
          <div style={{
            display: 'inline-block',
            fontFamily: 'Syne, sans-serif', fontSize: '2rem', fontWeight: 800,
            color: config.color,
            textShadow: `0 0 30px ${config.color}50`,
          }}>
            {config.label}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          {confidence != null && (
            <div style={{ marginBottom: '8px' }}>
              <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#64748B' }}>Confidence</div>
              <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.4rem', fontWeight: 700, color: config.color }}>
                {Math.round(confidence * 100)}%
              </div>
            </div>
          )}
          {createdAt && (
            <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#64748B' }}>
              {new Date(createdAt).toLocaleString('en-GB', {
                day: '2-digit', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Expandable accordion section
function Accordion({ title, icon, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="glass-card" style={{ marginBottom: '16px', overflow: 'hidden' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '18px 22px', background: 'transparent', border: 'none', cursor: 'pointer',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '10px', fontFamily: 'Syne, sans-serif', fontSize: '0.95rem', fontWeight: 700, color: '#E2E8F0' }}>
          {icon} {title}
        </span>
        {open ? <ChevronUp size={18} color="#64748B" /> : <ChevronDown size={18} color="#64748B" />}
      </button>
      {open && (
        <div style={{ padding: '0 22px 22px', borderTop: '1px solid rgba(26,58,92,0.5)' }}>
          {children}
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────
export default function EvaluationResultsPage() {
  const { evaluationId } = useParams();
  const navigate         = useNavigate();
  const user             = getUser();

  const [evaluation,    setEvaluation]    = useState(null);
  const [supplierName,  setSupplierName]  = useState('');
  const [loading,       setLoading]       = useState(true);
  const [error,         setError]         = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await evaluationsAPI.getOne(evaluationId);
        const ev  = res.data;
        setEvaluation(ev);

        // Fetch supplier name
        if (ev?.supplier_id) {
          try {
            const sRes = await suppliersAPI.getOne(ev.supplier_id);
            setSupplierName(sRes.data?.supplier_name || '');
          } catch { /* ignore */ }
        }
      } catch {
        setError('Failed to load evaluation results.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [evaluationId]);

  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif', gap: '12px' }}>
          <div style={{ width: '20px', height: '20px', border: '2px solid rgba(0,212,255,0.2)', borderTop: '2px solid #00D4FF', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          Loading results...
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  if (error || !evaluation) {
    return (
      <AppLayout>
        <div style={{ textAlign: 'center', padding: '60px' }}>
          <p style={{ color: '#EF4444', fontFamily: 'DM Sans, sans-serif', marginBottom: '16px' }}>
            {error || 'Evaluation not found.'}
          </p>
          <button onClick={() => navigate('/evaluations')} className="btn-outline" style={{ padding: '9px 20px' }}>
            ← Back to Evaluations
          </button>
        </div>
      </AppLayout>
    );
  }

  // If still pending/processing, show waiting message
  const status = evaluation.status?.toLowerCase();
  if (status === 'pending' || status === 'processing') {
    return (
      <AppLayout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '16px' }}>
          <div style={{ fontSize: '3rem' }}>⏳</div>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.2rem', fontWeight: 700, color: '#E2E8F0' }}>
            Evaluation In Progress
          </h2>
          <p style={{ fontFamily: 'DM Sans, sans-serif', color: '#64748B', textAlign: 'center', maxWidth: '400px' }}>
            This evaluation is still running. Results will appear here when complete.
          </p>
          <button onClick={() => window.location.reload()} className="btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '9px 20px' }}>
            <RotateCcw size={16} /> Refresh
          </button>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  // Parse agent outputs safely
  const agentOutputs  = evaluation.agent_outputs  || {};
  const docOutput     = agentOutputs.document_output  || agentOutputs.document_agent  || {};
  const ragOutput     = agentOutputs.rag_output        || agentOutputs.rag_agent       || {};
  const extOutput     = agentOutputs.external_output   || agentOutputs.external_agent  || {};
  const finalDecision = agentOutputs.final_decision    || {};

  const riskFactors       = evaluation.risk_factors       || finalDecision.risk_factors       || {};
  const positiveFactors   = riskFactors.positive          || [];
  const negativeFactors   = riskFactors.negative          || [];
  const recommendedActions= evaluation.recommended_actions|| finalDecision.recommended_actions|| [];

  return (
    <AppLayout>

      {/* Back button */}
      <button
        onClick={() => navigate('/evaluations')}
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          background: 'transparent', border: 'none', color: '#64748B',
          cursor: 'pointer', fontFamily: 'DM Sans, sans-serif',
          fontSize: '0.875rem', marginBottom: '20px', transition: 'color 0.2s',
        }}
        onMouseEnter={e => e.currentTarget.style.color = '#00D4FF'}
        onMouseLeave={e => e.currentTarget.style.color = '#64748B'}
      >
        <ArrowLeft size={16} /> Back to Evaluations
      </button>

      {/* ── Risk Banner ── */}
      <RiskBanner
        risk={evaluation.risk_level}
        supplierName={supplierName}
        confidence={evaluation.confidence_score}
        createdAt={evaluation.created_at}
      />

      {/* ── Decision Summary ── */}
      {evaluation.reasoning && (
        <div className="glass-card" style={{ padding: '24px', marginBottom: '16px' }}>
          <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0', marginBottom: '12px' }}>
            🧠 Decision Summary
          </h3>
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.9rem', color: '#CBD5E1', lineHeight: 1.7 }}>
            {evaluation.reasoning}
          </p>
        </div>
      )}

      {/* ── Risk Factors ── */}
      {(positiveFactors.length > 0 || negativeFactors.length > 0) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          {/* Positive */}
          <div style={{
            padding: '20px', borderRadius: '12px',
            background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)',
          }}>
            <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.875rem', fontWeight: 700, color: '#10B981', marginBottom: '14px' }}>
              ✅ POSITIVE FACTORS
            </h3>
            {positiveFactors.length === 0 ? (
              <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem' }}>None identified</p>
            ) : (
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {positiveFactors.map((f, i) => (
                  <li key={i} style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#CBD5E1', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#10B981', flexShrink: 0 }}>•</span> {f}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Negative */}
          <div style={{
            padding: '20px', borderRadius: '12px',
            background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)',
          }}>
            <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.875rem', fontWeight: 700, color: '#EF4444', marginBottom: '14px' }}>
              ❌ NEGATIVE FACTORS
            </h3>
            {negativeFactors.length === 0 ? (
              <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem' }}>None identified</p>
            ) : (
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {negativeFactors.map((f, i) => (
                  <li key={i} style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#CBD5E1', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#EF4444', flexShrink: 0 }}>•</span> {f}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* ── Recommended Actions ── */}
      {recommendedActions.length > 0 && (
        <div className="glass-card" style={{ padding: '24px', marginBottom: '16px' }}>
          <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0', marginBottom: '16px' }}>
            📋 Recommended Actions
          </h3>
          <ol style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recommendedActions.map((action, i) => (
              <li key={i} style={{
                display: 'flex', gap: '12px', alignItems: 'flex-start',
                padding: '12px 14px', borderRadius: '8px',
                background: 'rgba(59,130,246,0.07)', border: '1px solid rgba(59,130,246,0.15)',
              }}>
                <span style={{
                  fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.8rem',
                  color: '#3B82F6', minWidth: '24px',
                }}>
                  {i + 1}.
                </span>
                <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#CBD5E1', lineHeight: 1.6 }}>
                  {action}
                </span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* ── Accordion Sections ── */}

      {/* Document Analysis */}
      <Accordion title="Document Analysis" icon="📄" defaultOpen={false}>
        <div style={{ paddingTop: '16px' }}>
          {docOutput.extracted_data && Object.keys(docOutput.extracted_data).length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {Object.entries(docOutput.extracted_data).map(([key, val]) => (
                <div key={key} style={{ display: 'flex', gap: '12px', padding: '8px 0', borderBottom: '1px solid rgba(26,58,92,0.3)' }}>
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', minWidth: '160px', textTransform: 'capitalize' }}>
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#CBD5E1' }}>
                    {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', paddingTop: '8px' }}>
              No document data extracted.
            </p>
          )}
          {docOutput.missing_data && docOutput.missing_data.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <h4 style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 700, color: '#F59E0B', marginBottom: '8px' }}>
                ⚠️ Missing Information
              </h4>
              {docOutput.missing_data.map((m, i) => (
                <div key={i} style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#94A3B8', padding: '4px 0' }}>
                  • {m}
                </div>
              ))}
            </div>
          )}
        </div>
      </Accordion>

      {/* External Intelligence */}
      <Accordion title="External Intelligence" icon="🔍" defaultOpen={false}>
        <div style={{ paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Sanctions */}
          <div style={{ padding: '14px', borderRadius: '8px', background: 'rgba(26,58,92,0.3)' }}>
            <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 700, color: '#94A3B8', marginBottom: '6px' }}>
              🛡️ SANCTIONS CHECK
            </div>
            <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#CBD5E1' }}>
              {extOutput.sanctions_check || 'No data available'}
            </div>
          </div>
          {/* Registry */}
          <div style={{ padding: '14px', borderRadius: '8px', background: 'rgba(26,58,92,0.3)' }}>
            <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 700, color: '#94A3B8', marginBottom: '6px' }}>
              🏢 COMPANY REGISTRY
            </div>
            <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#CBD5E1' }}>
              {extOutput.company_registry
                ? typeof extOutput.company_registry === 'object'
                  ? `Status: ${extOutput.company_registry.status || 'Unknown'}`
                  : extOutput.company_registry
                : 'No registry data available'}
            </div>
          </div>
          {/* News */}
          <div style={{ padding: '14px', borderRadius: '8px', background: 'rgba(26,58,92,0.3)' }}>
            <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 700, color: '#94A3B8', marginBottom: '6px' }}>
              📰 NEWS SIGNALS
            </div>
            {extOutput.news_signals && Array.isArray(extOutput.news_signals) && extOutput.news_signals.length > 0 ? (
              extOutput.news_signals.slice(0, 3).map((n, i) => (
                <div key={i} style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#CBD5E1', padding: '4px 0', borderBottom: i < 2 ? '1px solid rgba(26,58,92,0.4)' : 'none' }}>
                  {n.headline || n.title || String(n)}
                </div>
              ))
            ) : (
              <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#CBD5E1' }}>
                {extOutput.news_signals || 'No news data available'}
              </div>
            )}
          </div>
          {/* Watchlist */}
          <div style={{ padding: '14px', borderRadius: '8px', background: 'rgba(26,58,92,0.3)' }}>
            <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 700, color: '#94A3B8', marginBottom: '6px' }}>
              ⚠️ WATCHLIST CHECK
            </div>
            <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#CBD5E1' }}>
              {extOutput.watchlist_check || 'No watchlist data available'}
            </div>
          </div>
        </div>
      </Accordion>

      {/* Compliance Knowledge */}
      <Accordion title="Compliance Knowledge (RAG)" icon="📚" defaultOpen={false}>
        <div style={{ paddingTop: '16px' }}>
          {ragOutput.answers && Array.isArray(ragOutput.answers) && ragOutput.answers.length > 0 ? (
            ragOutput.answers.map((item, i) => (
              <div key={i} style={{ marginBottom: '16px', padding: '14px', borderRadius: '8px', background: 'rgba(26,58,92,0.3)' }}>
                <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 700, color: '#00D4FF', marginBottom: '6px' }}>
                  Q: {item.question}
                </div>
                <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#CBD5E1', lineHeight: 1.6 }}>
                  {item.answer}
                </div>
                {item.confidence && (
                  <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#64748B', marginTop: '6px' }}>
                    Confidence: {Math.round(item.confidence * 100)}%
                  </div>
                )}
              </div>
            ))
          ) : (
            <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', paddingTop: '8px' }}>
              {ragOutput.answer || 'No compliance knowledge data available.'}
            </p>
          )}
        </div>
      </Accordion>

      {/* ── Footer Actions ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexWrap: 'wrap', gap: '12px', marginTop: '24px', paddingTop: '24px',
        borderTop: '1px solid rgba(26,58,92,0.4)',
      }}>
        <button
          onClick={() => navigate('/evaluations')}
          className="btn-outline"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px' }}
        >
          <ArrowLeft size={16} /> Back to Evaluations
        </button>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {evaluation.supplier_id && (
            <button
              onClick={() => navigate(`/evaluations/new?supplier_id=${evaluation.supplier_id}`)}
              className="btn-cyber"
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', fontSize: '0.875rem' }}
            >
              <RotateCcw size={16} /> Re-evaluate Supplier
            </button>
          )}
          {/* Show cost only to admin */}
          {(user?.role === 'admin' || user?.role === 'super_admin') && evaluation.openai_cost_usd && (
            <div style={{
              padding: '10px 16px', borderRadius: '8px',
              background: 'rgba(26,58,92,0.3)', border: '1px solid rgba(26,58,92,0.5)',
              fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B',
            }}>
              💰 Cost: ${Number(evaluation.openai_cost_usd).toFixed(4)}
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}