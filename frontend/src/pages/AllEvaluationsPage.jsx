import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ExternalLink } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { evaluationsAPI, suppliersAPI } from '../services/api';

function RiskBadge({ level }) {
  if (!level) return <span style={{ color: '#4A6080', fontSize: '0.8rem' }}>—</span>;
  const cls = { Low: 'badge-low', Medium: 'badge-medium', High: 'badge-high' }[level] || 'badge-low';
  return <span className={cls}>{level}</span>;
}

function StatusBadge({ status }) {
  const s = status?.toLowerCase();
  const config = {
    completed:  { bg: 'rgba(16,185,129,0.1)',  color: '#10B981', border: 'rgba(16,185,129,0.3)'  },
    pending:    { bg: 'rgba(245,158,11,0.1)',  color: '#F59E0B', border: 'rgba(245,158,11,0.3)'  },
    processing: { bg: 'rgba(59,130,246,0.1)',  color: '#3B82F6', border: 'rgba(59,130,246,0.3)'  },
    failed:     { bg: 'rgba(239,68,68,0.1)',   color: '#EF4444', border: 'rgba(239,68,68,0.3)'   },
  }[s] || { bg: 'rgba(26,58,92,0.3)', color: '#64748B', border: 'rgba(26,58,92,0.5)' };

  return (
    <span style={{
      fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600,
      padding: '2px 10px', borderRadius: '999px', textTransform: 'capitalize',
      background: config.bg, color: config.color, border: `1px solid ${config.border}`,
    }}>
      {status || 'unknown'}
    </span>
  );
}

function formatDate(d) {
  if (!d) return '—';
  try {
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return '—'; }
}

export default function AllEvaluationsPage() {
  const navigate = useNavigate();

  const [evaluations, setEvaluations] = useState([]);
  const [suppliers,   setSuppliers]   = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);
  const [search,      setSearch]      = useState('');
  const [filterRisk,  setFilterRisk]  = useState('All');
  const [filterStatus,setFilterStatus]= useState('All');
  const [page,        setPage]        = useState(1);
  const PER_PAGE = 10;

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [evalRes, suppRes] = await Promise.all([
          evaluationsAPI.getAll(),
          suppliersAPI.getAll(),
        ]);
        const evalsRaw = evalRes.data;
        const evArr = Array.isArray(evalsRaw) ? evalsRaw
          : Array.isArray(evalsRaw?.items) ? evalsRaw.items : [];
        setEvaluations(evArr);

        const suppArr = Array.isArray(suppRes.data) ? suppRes.data : [];
        setSuppliers(suppArr);
      } catch {
        setError('Failed to load evaluations.');
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  // Build supplier lookup map
  const supplierMap = {};
  suppliers.forEach(s => { supplierMap[s.supplier_id] = s.supplier_name; });

  // Filter
  const filtered = evaluations
    .filter(ev => {
      const name = supplierMap[ev.supplier_id] || ev.supplier_name || '';
      const matchSearch = name.toLowerCase().includes(search.toLowerCase());
      const matchRisk   = filterRisk   === 'All' || ev.risk_level === filterRisk;
      const matchStatus = filterStatus === 'All' || ev.status?.toLowerCase() === filterStatus.toLowerCase();
      return matchSearch && matchRisk && matchStatus;
    })
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  // Pagination
  const totalPages = Math.ceil(filtered.length / PER_PAGE);
  const paginated  = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE);

  return (
    <AppLayout>

      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 700, color: '#E2E8F0' }}>
          All Evaluations
        </h1>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
          {evaluations.length} total evaluation{evaluations.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Filters */}
      <div className="glass-card" style={{
        padding: '16px 20px', marginBottom: '20px',
        display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center',
      }}>
        <div style={{ position: 'relative', flex: '1', minWidth: '200px' }}>
          <Search size={16} style={{
            position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#4A6080',
          }} />
          <input
            type="text"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            className="cyber-input"
            placeholder="Search by supplier name..."
            style={{ paddingLeft: '36px' }}
          />
        </div>
        <select
          value={filterRisk}
          onChange={e => { setFilterRisk(e.target.value); setPage(1); }}
          className="cyber-input"
          style={{ width: 'auto', minWidth: '150px', cursor: 'pointer' }}
        >
          <option value="All">All Risk Levels</option>
          <option value="Low">Low Risk</option>
          <option value="Medium">Medium Risk</option>
          <option value="High">High Risk</option>
        </select>
        <select
          value={filterStatus}
          onChange={e => { setFilterStatus(e.target.value); setPage(1); }}
          className="cyber-input"
          style={{ width: 'auto', minWidth: '150px', cursor: 'pointer' }}
        >
          <option value="All">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '10px', padding: '14px 18px', marginBottom: '20px',
          color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Table */}
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif', gap: '12px' }}>
            <div style={{ width: '20px', height: '20px', border: '2px solid rgba(0,212,255,0.2)', borderTop: '2px solid #00D4FF', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            Loading evaluations...
          </div>
        ) : paginated.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif' }}>
            {search || filterRisk !== 'All' || filterStatus !== 'All'
              ? 'No evaluations match your filters.'
              : 'No evaluations yet. Create your first one!'}
          </div>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Risk Level</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {paginated.map(ev => (
                <tr
                  key={ev.evaluation_id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/evaluations/${ev.evaluation_id}`)}
                >
                  <td style={{ fontWeight: 500, color: '#E2E8F0', fontFamily: 'DM Sans, sans-serif' }}>
                    {supplierMap[ev.supplier_id] || ev.supplier_name || 'Unknown Supplier'}
                  </td>
                  <td><RiskBadge level={ev.risk_level} /></td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#94A3B8' }}>
                    {ev.confidence_score != null
                      ? `${Math.round(ev.confidence_score * 100)}%`
                      : '—'}
                  </td>
                  <td><StatusBadge status={ev.status} /></td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
                    {formatDate(ev.created_at)}
                  </td>
                  <td><ExternalLink size={14} color="#4A6080" /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: '8px', marginTop: '20px',
        }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-outline"
            style={{ padding: '7px 16px', fontSize: '0.8rem', opacity: page === 1 ? 0.4 : 1 }}
          >
            ← Prev
          </button>
          <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#64748B', padding: '0 8px' }}>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn-outline"
            style={{ padding: '7px 16px', fontSize: '0.8rem', opacity: page === totalPages ? 0.4 : 1 }}
          >
            Next →
          </button>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}