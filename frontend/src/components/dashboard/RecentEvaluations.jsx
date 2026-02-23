import { useNavigate } from 'react-router-dom';
import { ArrowRight, ExternalLink } from 'lucide-react';

// Helper — returns the correct badge class from index.css
function RiskBadge({ level }) {
  if (!level) return <span style={{ color: '#4A6080', fontSize: '0.8rem' }}>—</span>;
  const cls = {
    Low:    'badge-low',
    Medium: 'badge-medium',
    High:   'badge-high',
  }[level] || 'badge-low';
  return <span className={cls}>{level}</span>;
}

// Helper — status dot
function StatusDot({ status }) {
  const color = {
    completed:  '#10B981',
    pending:    '#F59E0B',
    processing: '#3B82F6',
    failed:     '#EF4444',
  }[status] || '#64748B';

  return (
    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <span style={{
        width: '7px', height: '7px',
        borderRadius: '50%',
        background: color,
        display: 'inline-block',
      }} />
      <span style={{
        fontFamily: 'DM Sans, sans-serif',
        fontSize:   '0.8rem',
        color:      '#94A3B8',
        textTransform: 'capitalize',
      }}>
        {status || 'unknown'}
      </span>
    </span>
  );
}

// Format date nicely
function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  } catch {
    return '—';
  }
}

export default function RecentEvaluations({ evaluations = [], suppliers = [] }) {
  const navigate = useNavigate();

  // Build a quick lookup map: supplier_id → supplier_name
  const supplierMap = {};
  suppliers.forEach((s) => {
    supplierMap[s.supplier_id] = s.supplier_name;
  });

  // Only show the 10 most recent
  const recent = [...evaluations]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 10);

  return (
    <div
      className="glass-card"
      style={{ padding: '24px', marginTop: '24px' }}
    >
      {/* Header */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        marginBottom:   '20px',
      }}>
        <div>
          <h3 style={{
            fontFamily: 'Syne, sans-serif',
            fontSize:   '1rem',
            fontWeight: 700,
            color:      '#E2E8F0',
          }}>
            Recent Evaluations
          </h3>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize:   '0.8rem',
            color:      '#64748B',
            marginTop:  '2px',
          }}>
            Last 10 evaluations across all suppliers
          </p>
        </div>
        <button
          onClick={() => navigate('/evaluations')}
          style={{
            display:    'flex',
            alignItems: 'center',
            gap:        '6px',
            background: 'transparent',
            border:     '1px solid rgba(0,212,255,0.3)',
            color:      '#00D4FF',
            borderRadius: '8px',
            padding:    '7px 14px',
            cursor:     'pointer',
            fontFamily: 'Syne, sans-serif',
            fontSize:   '0.8rem',
            fontWeight: 600,
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,212,255,0.1)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          View All <ArrowRight size={14} />
        </button>
      </div>

      {/* Empty state */}
      {recent.length === 0 ? (
        <div style={{
          textAlign:  'center',
          padding:    '48px 0',
          color:      '#4A6080',
          fontFamily: 'DM Sans, sans-serif',
          fontSize:   '0.875rem',
        }}>
          No evaluations yet. Create your first one!
        </div>
      ) : (
        <table className="cyber-table">
          <thead>
            <tr>
              <th>Supplier</th>
              <th>Risk Level</th>
              <th>Status</th>
              <th>Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {recent.map((ev) => (
              <tr
                key={ev.evaluation_id}
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/evaluations/${ev.evaluation_id}`)}
              >
                <td>
                  <span style={{
                    fontFamily: 'DM Sans, sans-serif',
                    color:      '#E2E8F0',
                    fontWeight: 500,
                  }}>
                    {/* Show supplier name — never show UUID */}
                    {supplierMap[ev.supplier_id] || ev.supplier_name || 'Unknown Supplier'}
                  </span>
                </td>
                <td>
                  <RiskBadge level={ev.risk_level} />
                </td>
                <td>
                  <StatusDot status={ev.status} />
                </td>
                <td style={{
                  fontFamily: 'DM Sans, sans-serif',
                  fontSize:   '0.8rem',
                  color:      '#64748B',
                }}>
                  {formatDate(ev.created_at)}
                </td>
                <td>
                  <ExternalLink size={14} color="#4A6080" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}