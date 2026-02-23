import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import AppLayout           from '../components/layout/AppLayout';
import StatsCards          from '../components/dashboard/StatsCards';
import RiskChart           from '../components/dashboard/RiskChart';
import RecentEvaluations   from '../components/dashboard/RecentEvaluations';
import { suppliersAPI, evaluationsAPI } from '../services/api';
import { getUser } from '../utils/auth';

export default function Dashboard() {
  const navigate = useNavigate();
  const user = getUser();

  const [suppliers,    setSuppliers]    = useState([]);
  const [evaluations,  setEvaluations]  = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);

  // Greeting based on time of day
  const getGreeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  // Role label for display
  const roleLabel = {
    admin:       'Admin',
    analyst:     'Analyst',
    viewer:      'Viewer',
    super_admin: 'Super Admin',
  }[user?.role] || 'User';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [suppRes, evalRes] = await Promise.all([
          suppliersAPI.getAll(),
          evaluationsAPI.getAll(),
        ]);
        setSuppliers(suppRes.data   || []);
        setEvaluations(evalRes.data || []);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
        setError('Failed to load dashboard data. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <AppLayout>

      {/* ── Welcome Banner ── */}
      <div
        className="glass-card"
        style={{
          padding:      '24px 28px',
          marginBottom: '28px',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'space-between',
          flexWrap:     'wrap',
          gap:          '16px',
          border:       '1px solid rgba(0,212,255,0.15)',
        }}
      >
        <div>
          <h1 style={{
            fontFamily: 'Syne, sans-serif',
            fontSize:   '1.5rem',
            fontWeight: 700,
            color:      '#E2E8F0',
            marginBottom: '4px',
          }}>
            {getGreeting()}, {user?.email?.split('@')[0] || 'User'} 👋
          </h1>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize:   '0.875rem',
            color:      '#64748B',
          }}>
            Role:{' '}
            <span style={{ color: '#00D4FF', fontWeight: 600 }}>
              {roleLabel}
            </span>
            {' · '}
            {new Date().toLocaleDateString('en-GB', {
              weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
            })}
          </p>
        </div>

        {/* Quick action — only admin and analyst can create evaluations */}
        {(user?.role === 'admin' || user?.role === 'analyst') && (
          <button
            onClick={() => navigate('/evaluations/new')}
            className="btn-cyber"
            style={{
              display:    'flex',
              alignItems: 'center',
              gap:        '8px',
              padding:    '10px 20px',
            }}
          >
            <Plus size={18} />
            New Evaluation
          </button>
        )}
      </div>

      {/* ── Error State ── */}
      {error && (
        <div style={{
          background:   'rgba(239,68,68,0.1)',
          border:       '1px solid rgba(239,68,68,0.3)',
          borderRadius: '10px',
          padding:      '14px 18px',
          marginBottom: '24px',
          color:        '#EF4444',
          fontFamily:   'DM Sans, sans-serif',
          fontSize:     '0.875rem',
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── Loading State ── */}
      {loading ? (
        <div style={{
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          height:         '300px',
          color:          '#4A6080',
          fontFamily:     'DM Sans, sans-serif',
          gap:            '12px',
        }}>
          <div style={{
            width:        '20px',
            height:       '20px',
            border:       '2px solid rgba(0,212,255,0.2)',
            borderTop:    '2px solid #00D4FF',
            borderRadius: '50%',
            animation:    'spin 1s linear infinite',
          }} />
          Loading dashboard...
        </div>
      ) : (
        <>
          {/* ── Stats Cards ── */}
          <StatsCards
            suppliers={suppliers}
            evaluations={evaluations}
          />

          {/* ── Chart + Quick Actions Row ── */}
          <div style={{
            display:             'grid',
            gridTemplateColumns: '1fr 300px',
            gap:                 '24px',
            marginBottom:        '0',
          }}>
            {/* Risk donut chart */}
            <RiskChart evaluations={evaluations} />

            {/* Quick Actions card */}
            <div
              className="glass-card"
              style={{ padding: '24px' }}
            >
              <h3 style={{
                fontFamily:   'Syne, sans-serif',
                fontSize:     '1rem',
                fontWeight:   700,
                color:        '#E2E8F0',
                marginBottom: '4px',
              }}>
                Quick Actions
              </h3>
              <p style={{
                fontFamily:   'DM Sans, sans-serif',
                fontSize:     '0.8rem',
                color:        '#64748B',
                marginBottom: '20px',
              }}>
                Common tasks
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(user?.role === 'admin' || user?.role === 'analyst') && (
                  <>
                    <button
                      onClick={() => navigate('/evaluations/new')}
                      style={{
                        display:      'flex',
                        alignItems:   'center',
                        gap:          '10px',
                        padding:      '12px 14px',
                        borderRadius: '8px',
                        background:   'rgba(0,212,255,0.07)',
                        border:       '1px solid rgba(0,212,255,0.2)',
                        color:        '#00D4FF',
                        cursor:       'pointer',
                        fontFamily:   'DM Sans, sans-serif',
                        fontSize:     '0.875rem',
                        textAlign:    'left',
                        transition:   'all 0.2s ease',
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,212,255,0.13)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'rgba(0,212,255,0.07)'}
                    >
                      ⚡ Run New Evaluation
                    </button>

                    <button
                      onClick={() => navigate('/suppliers')}
                      style={{
                        display:      'flex',
                        alignItems:   'center',
                        gap:          '10px',
                        padding:      '12px 14px',
                        borderRadius: '8px',
                        background:   'rgba(59,130,246,0.07)',
                        border:       '1px solid rgba(59,130,246,0.2)',
                        color:        '#3B82F6',
                        cursor:       'pointer',
                        fontFamily:   'DM Sans, sans-serif',
                        fontSize:     '0.875rem',
                        textAlign:    'left',
                        transition:   'all 0.2s ease',
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(59,130,246,0.13)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'rgba(59,130,246,0.07)'}
                    >
                      ➕ Add New Supplier
                    </button>
                  </>
                )}

                <button
                  onClick={() => navigate('/evaluations')}
                  style={{
                    display:      'flex',
                    alignItems:   'center',
                    gap:          '10px',
                    padding:      '12px 14px',
                    borderRadius: '8px',
                    background:   'rgba(16,185,129,0.07)',
                    border:       '1px solid rgba(16,185,129,0.2)',
                    color:        '#10B981',
                    cursor:       'pointer',
                    fontFamily:   'DM Sans, sans-serif',
                    fontSize:     '0.875rem',
                    textAlign:    'left',
                    transition:   'all 0.2s ease',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(16,185,129,0.13)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(16,185,129,0.07)'}
                >
                  📊 View All Evaluations
                </button>

                <button
                  onClick={() => navigate('/suppliers')}
                  style={{
                    display:      'flex',
                    alignItems:   'center',
                    gap:          '10px',
                    padding:      '12px 14px',
                    borderRadius: '8px',
                    background:   'rgba(168,85,247,0.07)',
                    border:       '1px solid rgba(168,85,247,0.2)',
                    color:        '#A855F7',
                    cursor:       'pointer',
                    fontFamily:   'DM Sans, sans-serif',
                    fontSize:     '0.875rem',
                    textAlign:    'left',
                    transition:   'all 0.2s ease',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(168,85,247,0.13)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(168,85,247,0.07)'}
                >
                  📦 Browse Suppliers
                </button>
              </div>
            </div>
          </div>

          {/* ── Recent Evaluations Table ── */}
          <RecentEvaluations
            evaluations={evaluations}
            suppliers={suppliers}
          />
        </>
      )}

      {/* Spinner keyframe — added inline so no extra CSS file needed */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </AppLayout>
  );
}