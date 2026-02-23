import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Eye, Pencil, Trash2, Package } from 'lucide-react';
import AppLayout         from '../components/layout/AppLayout';
import AddSupplierModal  from '../components/suppliers/AddSupplierModal';
import EditSupplierModal from '../components/suppliers/EditSupplierModal';
import { suppliersAPI }  from '../services/api';
import { getUser }       from '../utils/auth';

// Risk badge helper
function RiskBadge({ level }) {
  if (!level) return <span style={{ color: '#4A6080', fontSize: '0.8rem' }}>—</span>;
  const cls = { Low: 'badge-low', Medium: 'badge-medium', High: 'badge-high' }[level] || 'badge-low';
  return <span className={cls}>{level}</span>;
}

// Format date
function formatDate(d) {
  if (!d) return '—';
  try {
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return '—'; }
}

export default function SuppliersPage() {
  const navigate = useNavigate();
  const user = getUser();
  const canEdit = user?.role === 'admin' || user?.role === 'analyst';
  const canDelete = user?.role === 'admin';

  const [suppliers,   setSuppliers]   = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);
  const [search,      setSearch]      = useState('');
  const [filterRisk,  setFilterRisk]  = useState('All');
  const [showAdd,     setShowAdd]     = useState(false);
  const [editTarget,  setEditTarget]  = useState(null); // supplier object to edit
  const [deleteId,    setDeleteId]    = useState(null); // supplier_id to delete
  const [deleting,    setDeleting]    = useState(false);

  // Fetch all suppliers on mount
  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await suppliersAPI.getAll();
      setSuppliers(res.data || []);
    } catch (err) {
      setError('Failed to load suppliers. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  // Filter + search
  const filtered = suppliers.filter(s => {
    const matchSearch = s.supplier_name?.toLowerCase().includes(search.toLowerCase())
      || s.country?.toLowerCase().includes(search.toLowerCase());
    const matchRisk = filterRisk === 'All' || s.risk_level === filterRisk;
    return matchSearch && matchRisk;
  });

  // Delete supplier
  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await suppliersAPI.delete(deleteId);
      setSuppliers(prev => prev.filter(s => s.supplier_id !== deleteId));
      setDeleteId(null);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete supplier.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <AppLayout>

      {/* ── Page Header ── */}
      <div style={{
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '16px',
      }}>
        <div>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 700, color: '#E2E8F0' }}>
            Suppliers
          </h1>
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            {suppliers.length} supplier{suppliers.length !== 1 ? 's' : ''} registered
          </p>
        </div>
        {canEdit && (
          <button
            onClick={() => setShowAdd(true)}
            className="btn-cyber"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px' }}
          >
            <Plus size={18} /> Add Supplier
          </button>
        )}
      </div>

      {/* ── Search + Filter Bar ── */}
      <div className="glass-card" style={{
        padding: '16px 20px', marginBottom: '20px',
        display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center',
      }}>
        {/* Search */}
        <div style={{ position: 'relative', flex: '1', minWidth: '200px' }}>
          <Search size={16} style={{
            position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)',
            color: '#4A6080',
          }} />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="cyber-input"
            placeholder="Search by name or country..."
            style={{ paddingLeft: '36px' }}
          />
        </div>

        {/* Risk filter */}
        <select
          value={filterRisk}
          onChange={e => setFilterRisk(e.target.value)}
          className="cyber-input"
          style={{ width: 'auto', minWidth: '150px', cursor: 'pointer' }}
        >
          <option value="All">All Risk Levels</option>
          <option value="Low">Low Risk</option>
          <option value="Medium">Medium Risk</option>
          <option value="High">High Risk</option>
        </select>
      </div>

      {/* ── Error ── */}
      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '10px', padding: '14px 18px', marginBottom: '20px',
          color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── Table Card ── */}
      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            height: '300px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif', gap: '12px',
          }}>
            <div style={{
              width: '20px', height: '20px',
              border: '2px solid rgba(0,212,255,0.2)', borderTop: '2px solid #00D4FF',
              borderRadius: '50%', animation: 'spin 1s linear infinite',
            }} />
            Loading suppliers...
          </div>
        ) : filtered.length === 0 ? (
          /* Empty state */
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            justifyContent: 'center', padding: '64px 24px', gap: '16px',
          }}>
            <div style={{
              width: '60px', height: '60px', borderRadius: '16px',
              background: 'rgba(0,212,255,0.07)', border: '1px solid rgba(0,212,255,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Package size={28} color="#4A6080" />
            </div>
            <p style={{ fontFamily: 'DM Sans, sans-serif', color: '#4A6080', fontSize: '0.9rem' }}>
              {search || filterRisk !== 'All'
                ? 'No suppliers match your filters.'
                : 'No suppliers yet. Add your first supplier!'}
            </p>
            {canEdit && !search && filterRisk === 'All' && (
              <button onClick={() => setShowAdd(true)} className="btn-cyber" style={{ padding: '9px 20px', fontSize: '0.875rem' }}>
                <Plus size={16} style={{ display: 'inline', marginRight: '6px' }} />
                Add First Supplier
              </button>
            )}
          </div>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Supplier Name</th>
                <th>Country</th>
                <th>Reg. Number</th>
                <th>Risk Level</th>
                <th>Added</th>
                {(canEdit || canDelete) && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.supplier_id} style={{ cursor: 'pointer' }}>
                  <td
                    onClick={() => navigate(`/suppliers/${s.supplier_id}`)}
                    style={{ fontWeight: 500, color: '#E2E8F0', fontFamily: 'DM Sans, sans-serif' }}
                  >
                    {s.supplier_name}
                  </td>
                  <td onClick={() => navigate(`/suppliers/${s.supplier_id}`)}>
                    {s.country || '—'}
                  </td>
                  <td onClick={() => navigate(`/suppliers/${s.supplier_id}`)}>
                    <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#64748B' }}>
                      {s.registration_number || '—'}
                    </span>
                  </td>
                  <td onClick={() => navigate(`/suppliers/${s.supplier_id}`)}>
                    <RiskBadge level={s.risk_level} />
                  </td>
                  <td
                    onClick={() => navigate(`/suppliers/${s.supplier_id}`)}
                    style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}
                  >
                    {formatDate(s.created_at)}
                  </td>
                  {(canEdit || canDelete) && (
                    <td>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        {/* View */}
                        <button
                          onClick={() => navigate(`/suppliers/${s.supplier_id}`)}
                          title="View details"
                          style={{
                            background: 'transparent', border: 'none',
                            color: '#64748B', cursor: 'pointer', padding: '4px',
                            borderRadius: '6px', transition: 'color 0.2s',
                          }}
                          onMouseEnter={e => e.currentTarget.style.color = '#00D4FF'}
                          onMouseLeave={e => e.currentTarget.style.color = '#64748B'}
                        >
                          <Eye size={16} />
                        </button>
                        {/* Edit */}
                        {canEdit && (
                          <button
                            onClick={() => setEditTarget(s)}
                            title="Edit supplier"
                            style={{
                              background: 'transparent', border: 'none',
                              color: '#64748B', cursor: 'pointer', padding: '4px',
                              borderRadius: '6px', transition: 'color 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.color = '#3B82F6'}
                            onMouseLeave={e => e.currentTarget.style.color = '#64748B'}
                          >
                            <Pencil size={16} />
                          </button>
                        )}
                        {/* Delete */}
                        {canDelete && (
                          <button
                            onClick={() => setDeleteId(s.supplier_id)}
                            title="Delete supplier"
                            style={{
                              background: 'transparent', border: 'none',
                              color: '#64748B', cursor: 'pointer', padding: '4px',
                              borderRadius: '6px', transition: 'color 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.color = '#EF4444'}
                            onMouseLeave={e => e.currentTarget.style.color = '#64748B'}
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Modals ── */}
      {showAdd && (
        <AddSupplierModal
          onClose={() => setShowAdd(false)}
          onSuccess={(newSupplier) => setSuppliers(prev => [newSupplier, ...prev])}
        />
      )}
      {editTarget && (
        <EditSupplierModal
          supplier={editTarget}
          onClose={() => setEditTarget(null)}
          onSuccess={(updated) => {
            setSuppliers(prev => prev.map(s =>
              s.supplier_id === updated.supplier_id ? updated : s
            ));
            setEditTarget(null);
          }}
        />
      )}

      {/* ── Delete Confirm Modal ── */}
      {deleteId && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: 'rgba(5,11,24,0.85)', backdropFilter: 'blur(8px)' }}
        >
          <div className="glass-card animate-fadeInUp" style={{
            width: '100%', maxWidth: '400px', padding: '32px', textAlign: 'center',
          }}>
            <div style={{
              width: '52px', height: '52px', borderRadius: '50%',
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 16px',
            }}>
              <Trash2 size={22} color="#EF4444" />
            </div>
            <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.1rem', fontWeight: 700, color: '#E2E8F0', marginBottom: '8px' }}>
              Delete Supplier?
            </h3>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginBottom: '24px' }}>
              This will permanently delete the supplier and all associated data. This cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setDeleteId(null)}
                className="btn-outline"
                style={{ flex: 1, padding: '10px' }}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                style={{
                  flex: 1, padding: '10px', borderRadius: '8px',
                  background: deleting ? 'rgba(239,68,68,0.5)' : '#EF4444',
                  border: 'none', color: 'white', cursor: deleting ? 'not-allowed' : 'pointer',
                  fontFamily: 'Syne, sans-serif', fontWeight: 600, fontSize: '0.875rem',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                }}
              >
                {deleting ? 'Deleting...' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}