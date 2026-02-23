import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart2, DollarSign, Building2, ClipboardList,
  TrendingUp, AlertTriangle,
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import AppLayout          from '../components/layout/AppLayout';
import DeleteConfirmModal from '../components/admin/DeleteConfirmModal';
import { adminAPI }       from '../services/api';

// ── Stat Card ─────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, color, bg, border }) {
  return (
    <div className="glass-card" style={{ padding: '24px', border: `1px solid ${border}`, display: 'flex', alignItems: 'center', gap: '16px' }}>
      <div style={{
        width: '48px', height: '48px', borderRadius: '12px',
        background: bg, border: `1px solid ${border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon size={22} color={color} />
      </div>
      <div>
        <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.6rem', fontWeight: 700, color: '#E2E8F0', lineHeight: 1 }}>
          {value}
        </div>
        <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>
          {label}
        </div>
      </div>
    </div>
  );
}

// Custom chart tooltip
function ChartTooltip({ active, payload, label }) {
  if (active && payload?.length) {
    const d = payload[0]?.payload || {};
    return (
      <div style={{ background: 'rgba(13,31,53,0.95)', border: '1px solid rgba(26,58,92,0.8)', borderRadius: '8px', padding: '12px 16px' }}>
        <p style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', color: '#00D4FF', marginBottom: '6px' }}>{label}</p>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#E2E8F0', marginBottom: '2px' }}>
          Cost: ${Number(payload[0].value).toFixed(4)}
        </p>
        {d.evaluations != null && (
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#94A3B8' }}>
            Evaluations: {d.evaluations}
          </p>
        )}
        {d.tokens != null && (
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#94A3B8' }}>
            Tokens: {d.tokens.toLocaleString()}
          </p>
        )}
      </div>
    );
  }
  return null;
}


// ── Main Page ─────────────────────────────────────────────────────
export default function PlatformAdminPage() {
  const navigate = useNavigate();

  const [summary,      setSummary]      = useState(null);
  const [companyUsage, setCompanyUsage] = useState([]);
  const [monthlyCost,  setMonthlyCost]  = useState([]);
  const [topExpensive, setTopExpensive] = useState([]);
  const [companies,    setCompanies]    = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);

  // Delete modal state
  const [deleteTarget, setDeleteTarget] = useState(null); // { company_id, company_name }

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, cuRes, mcRes, teRes, coRes] = await Promise.all([
        adminAPI.getUsageSummary(),
        adminAPI.getCompanyUsage(),
        adminAPI.getMonthlyCost(),
        adminAPI.getTopExpensive(),
        adminAPI.getCompanies(),
      ]);

      // Usage summary — nested under "summary" key
      const sumData = sumRes.data?.summary || sumRes.data || {};
      setSummary({
        total_evaluations:          sumData.total_evaluations_all_time      || 0,
        total_cost_this_month:      sumData.total_cost_usd_this_month        || 0,
        avg_cost_per_evaluation:    sumData.average_cost_per_evaluation_usd  || 0,
        total_tokens:               sumData.total_tokens_used                || 0,
        total_evaluations_month:    sumData.total_evaluations_this_month     || 0,
      });

      // Company usage — nested under "companies" key
      const cuArr = cuRes.data?.companies || (Array.isArray(cuRes.data) ? cuRes.data : []);
      setCompanyUsage(cuArr.map(c => ({
        ...c,
        total_tokens: c.total_tokens_used || c.total_tokens || 0,
        total_cost:   c.total_cost_usd    || c.total_cost   || 0,
      })));

      // Monthly cost — nested under "monthly_cost_trend" key
      const mcArr = mcRes.data?.monthly_cost_trend || (Array.isArray(mcRes.data) ? mcRes.data : []);
      setMonthlyCost(mcArr.map(m => ({
        month:       m.month || m.period || '',
        cost:        parseFloat(m.total_cost_usd || m.total_cost || 0),
        evaluations: m.total_evaluations || 0,
        tokens:      m.total_tokens_used || 0,
      })));

      // Top expensive — nested under "top_expensive_evaluations" key
      const teArr = teRes.data?.top_expensive_evaluations || (Array.isArray(teRes.data) ? teRes.data : []);
      setTopExpensive(teArr.map(e => ({
        ...e,
        total_cost: e.total_cost_usd || e.total_cost || 0,
      })));

      // Companies list — nested under "companies" key
      const coArr = coRes.data?.companies || (Array.isArray(coRes.data) ? coRes.data : []);
      setCompanies(coArr);

    } catch (err) {
      console.error('Platform admin fetch error:', err);
      setError('Failed to load platform data. Make sure you are logged in as super_admin.');
    } finally {
      setLoading(false);
    }
  };


  const handleDeactivate = async (companyId) => {
    try {
      await adminAPI.deactivateCompany(companyId);
      setCompanies(prev => prev.map(c =>
        c.company_id === companyId ? { ...c, is_active: false } : c
      ));
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to deactivate company.');
    }
  };

  const handleReactivate = async (companyId) => {
    try {
      await adminAPI.reactivateCompany(companyId);
      setCompanies(prev => prev.map(c =>
        c.company_id === companyId ? { ...c, is_active: true } : c
      ));
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to reactivate company.');
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await adminAPI.deleteCompany(deleteTarget.company_id);
      setCompanies(prev => prev.filter(c => c.company_id !== deleteTarget.company_id));
      setDeleteTarget(null);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete company.');
      setDeleteTarget(null);
    }
  };

  const formatCost = (val) => `$${Number(val || 0).toFixed(4)}`;
  const formatDate = (d) => {
    if (!d) return '—';
    try { return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }); }
    catch { return '—'; }
  };

  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif', gap: '12px' }}>
          <div style={{ width: '20px', height: '20px', border: '2px solid rgba(0,212,255,0.2)', borderTop: '2px solid #00D4FF', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          Loading platform data...
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
          <span style={{
            fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600,
            padding: '2px 10px', borderRadius: '999px',
            background: 'rgba(168,85,247,0.15)', color: '#A855F7', border: '1px solid rgba(168,85,247,0.3)',
          }}>
            SUPER ADMIN
          </span>
        </div>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 700, color: '#E2E8F0' }}>
          Platform Dashboard
        </h1>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
          System-wide analytics and company management
        </p>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '10px', padding: '14px 18px', marginBottom: '24px',
          color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── Stat Cards ── */}
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        <StatCard icon={ClipboardList} label="Total Evaluations (All Time)" value={summary?.total_evaluations        || 0}                              color="#00D4FF" bg="rgba(0,212,255,0.1)"   border="rgba(0,212,255,0.2)"   />
        <StatCard icon={Building2}     label="Total Companies"              value={companies.length                  || 0}                              color="#3B82F6" bg="rgba(59,130,246,0.1)"  border="rgba(59,130,246,0.2)"  />
        <StatCard icon={DollarSign}    label="Cost This Month"              value={formatCost(summary?.total_cost_this_month)}                          color="#10B981" bg="rgba(16,185,129,0.1)" border="rgba(16,185,129,0.2)" />
        <StatCard icon={TrendingUp}    label="Avg Cost / Evaluation"        value={formatCost(summary?.avg_cost_per_evaluation)}                        color="#F59E0B" bg="rgba(245,158,11,0.1)" border="rgba(245,158,11,0.2)" />
       </div>

      {/* ── Monthly Cost Chart ── */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <BarChart2 size={18} color="#00D4FF" />
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
            Monthly Cost Trend
          </h2>
        </div>
        {monthlyCost.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif' }}>
            No cost data available yet.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={monthlyCost}>
              <CartesianGrid stroke="rgba(26,58,92,0.4)" strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fill: '#64748B', fontFamily: 'DM Sans', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748B', fontFamily: 'DM Sans', fontSize: 11 }} />
              <Tooltip content={<ChartTooltip />} />
              <Line type="monotone" dataKey="cost" stroke="#00D4FF" strokeWidth={2} dot={{ fill: '#00D4FF', r: 4 }} activeDot={{ r: 6, fill: '#00D4FF' }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* ── Company Usage Table ── */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <DollarSign size={18} color="#00D4FF" />
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
            Company Usage (by cost)
          </h2>
        </div>
        {companyUsage.length === 0 ? (
          <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', padding: '20px 0' }}>No usage data yet.</p>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Subscription</th>
                <th>Evaluations</th>
                <th>Total Tokens</th>
                <th>Total Cost</th>
              </tr>
            </thead>
            <tbody>
              {companyUsage.map((c, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 500, color: '#E2E8F0', fontFamily: 'DM Sans, sans-serif' }}>{c.company_name}</td>
                  <td>
                    <span style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600, padding: '2px 8px', borderRadius: '999px', background: 'rgba(59,130,246,0.1)', color: '#3B82F6', border: '1px solid rgba(59,130,246,0.2)', textTransform: 'capitalize' }}>
                      {c.subscription_tier || 'free'}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', color: '#94A3B8' }}>{c.total_evaluations || 0}</td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', color: '#94A3B8' }}>{(c.total_tokens || 0).toLocaleString()}</td>
                  <td style={{ fontFamily: 'Syne, sans-serif', fontWeight: 600, color: '#10B981' }}>{formatCost(c.total_cost || c.total_cost_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Top Expensive Evaluations ── */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <AlertTriangle size={18} color="#F59E0B" />
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
            Most Expensive Evaluations
          </h2>
        </div>
        {topExpensive.length === 0 ? (
          <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', padding: '20px 0' }}>No evaluation cost data yet.</p>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Company</th>
                <th>Risk Level</th>
                <th>Cost</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {topExpensive.map((ev, i) => {
                const riskCls = { Low: 'badge-low', Medium: 'badge-medium', High: 'badge-high' }[ev.risk_level] || 'badge-low';
                return (
                  <tr key={i}>
                    <td style={{ fontWeight: 500, color: '#E2E8F0', fontFamily: 'DM Sans, sans-serif' }}>{ev.supplier_name || '—'}</td>
                    <td style={{ color: '#94A3B8', fontFamily: 'DM Sans, sans-serif' }}>{ev.company_name || '—'}</td>
                    <td>{ev.risk_level ? <span className={riskCls}>{ev.risk_level}</span> : <span style={{ color: '#4A6080' }}>—</span>}</td>
                    <td style={{ fontFamily: 'Syne, sans-serif', fontWeight: 600, color: '#F59E0B' }}>{formatCost(ev.total_cost || ev.total_cost_usd)}</td>
            
                    <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>{formatDate(ev.created_at)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Company Management ── */}
      <div className="glass-card" style={{ padding: '24px', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <Building2 size={18} color="#00D4FF" />
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
            Company Management
          </h2>
        </div>

        {companies.length === 0 ? (
          <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', padding: '20px 0' }}>No companies registered yet.</p>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Company Name</th>
                <th>Tier</th>
                <th>Status</th>
                <th>Users</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {companies.map(c => (
                <tr key={c.company_id}>
                  <td style={{ fontWeight: 500, color: '#E2E8F0', fontFamily: 'DM Sans, sans-serif' }}>{c.company_name}</td>
                  <td>
                    <span style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600, padding: '2px 8px', borderRadius: '999px', background: 'rgba(59,130,246,0.1)', color: '#3B82F6', border: '1px solid rgba(59,130,246,0.2)', textTransform: 'capitalize' }}>
                      {c.subscription_tier || 'free'}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600,
                      padding: '2px 10px', borderRadius: '999px',
                      background: c.is_active !== false ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                      color: c.is_active !== false ? '#10B981' : '#EF4444',
                      border: `1px solid ${c.is_active !== false ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
                    }}>
                      {c.is_active !== false ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', color: '#94A3B8' }}>{c.user_count || c.total_users || 0}</td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>{formatDate(c.created_at)}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {/* Deactivate / Reactivate */}
                      {c.is_active !== false ? (
                        <button
                          onClick={() => handleDeactivate(c.company_id)}
                          style={{
                            padding: '4px 10px', borderRadius: '6px', border: 'none',
                            background: 'rgba(245,158,11,0.15)', color: '#F59E0B',
                            cursor: 'pointer', fontFamily: 'Syne, sans-serif',
                            fontSize: '0.7rem', fontWeight: 600,
                          }}
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          onClick={() => handleReactivate(c.company_id)}
                          style={{
                            padding: '4px 10px', borderRadius: '6px', border: 'none',
                            background: 'rgba(16,185,129,0.15)', color: '#10B981',
                            cursor: 'pointer', fontFamily: 'Syne, sans-serif',
                            fontSize: '0.7rem', fontWeight: 600,
                          }}
                        >
                          Reactivate
                        </button>
                      )}
                      {/* Delete */}
                      <button
                        onClick={() => setDeleteTarget({ company_id: c.company_id, company_name: c.company_name })}
                        style={{
                          padding: '4px 10px', borderRadius: '6px', border: 'none',
                          background: 'rgba(239,68,68,0.15)', color: '#EF4444',
                          cursor: 'pointer', fontFamily: 'Syne, sans-serif',
                          fontSize: '0.7rem', fontWeight: 600,
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Delete confirm modal */}
      {deleteTarget && (
        <DeleteConfirmModal
          companyName={deleteTarget.company_name}
          onClose={() => setDeleteTarget(null)}
          onConfirm={handleDelete}
        />
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}