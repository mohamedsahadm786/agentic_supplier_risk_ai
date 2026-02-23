import { useState, useEffect } from 'react';
import { Users, Plus, X, Loader2, Shield } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { usersAPI } from '../services/api';
import { getUser } from '../utils/auth';

// Role badge
function RoleBadge({ role }) {
  const config = {
    admin:   { bg: 'rgba(59,130,246,0.15)',  color: '#3B82F6',  label: 'Admin'   },
    analyst: { bg: 'rgba(0,212,255,0.15)',   color: '#00D4FF',  label: 'Analyst' },
    viewer:  { bg: 'rgba(148,163,184,0.15)', color: '#94A3B8',  label: 'Viewer'  },
  }[role] || { bg: 'rgba(26,58,92,0.3)', color: '#64748B', label: role };

  return (
    <span style={{
      fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600,
      padding: '2px 10px', borderRadius: '999px',
      background: config.bg, color: config.color,
      border: `1px solid ${config.color}33`,
    }}>
      {config.label}
    </span>
  );
}

// Add Member Modal
function AddMemberModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    full_name: '', email: '', password: '', role: 'analyst',
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleChange = e => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await usersAPI.create(formData);
      onSuccess(res.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create team member.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(5,11,24,0.85)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
    >
      <div
        className="glass-card animate-fadeInUp"
        style={{ width: '100%', maxWidth: '460px', padding: '32px', position: 'relative' }}
        onClick={e => e.stopPropagation()}
      >
        <button onClick={onClose} style={{
          position: 'absolute', top: '16px', right: '16px',
          background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer',
        }}>
          <X size={20} />
        </button>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <div style={{
            width: '40px', height: '40px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Users size={20} color="#050B18" />
          </div>
          <div>
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.1rem', fontWeight: 700, color: '#E2E8F0' }}>
              Add Team Member
            </h2>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
              Invite someone to your company
            </p>
          </div>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: '8px', padding: '12px 14px', marginBottom: '16px',
            color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

            {/* Full Name */}
            <div>
              <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                Full Name *
              </label>
              <input type="text" name="full_name" value={formData.full_name}
                onChange={handleChange} className="cyber-input" placeholder="Jane Smith" required />
            </div>

            {/* Email */}
            <div>
              <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                Email Address *
              </label>
              <input type="email" name="email" value={formData.email}
                onChange={handleChange} className="cyber-input" placeholder="jane@company.com" required />
            </div>

            {/* Temporary Password */}
            <div>
              <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                Temporary Password *
              </label>
              <input type="password" name="password" value={formData.password}
                onChange={handleChange} className="cyber-input" placeholder="Min. 6 characters" required minLength={6} />
              <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#4A6080', marginTop: '4px' }}>
                Share this with the team member. They can change it in Settings.
              </p>
            </div>

            {/* Role */}
            <div>
              <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                Role *
              </label>
              <select name="role" value={formData.role} onChange={handleChange}
                className="cyber-input" style={{ cursor: 'pointer' }}>
                <option value="analyst" style={{ background: '#0A1628' }}>Analyst — Can create suppliers and evaluations</option>
                <option value="viewer"  style={{ background: '#0A1628' }}>Viewer — Read only access</option>
              </select>
              <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#4A6080', marginTop: '4px' }}>
                Admins can only be created via the signup flow.
              </p>
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '4px' }}>
              <button type="button" onClick={onClose} className="btn-outline" style={{ flex: 1, padding: '11px' }}>
                Cancel
              </button>
              <button type="submit" disabled={loading} className="btn-cyber"
                style={{ flex: 1, padding: '11px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                {loading ? <><Loader2 size={16} className="animate-spin" /> Adding...</> : 'Add Member'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────
export default function TeamPage() {
  const currentUser = getUser();
  const [members,  setMembers]  = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);
  const [showAdd,  setShowAdd]  = useState(false);

  useEffect(() => {
    fetchMembers();
  }, []);

  const fetchMembers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await usersAPI.getAll();
      const raw = res.data;
      const arr = Array.isArray(raw) ? raw
        : Array.isArray(raw?.users) ? raw.users
        : Array.isArray(raw?.items) ? raw.items
        : [];
      setMembers(arr);
    } catch (err) {
      // If endpoint doesn't exist yet, show empty state gracefully
      if (err.response?.status === 404) {
        setMembers([]);
      } else {
        setError('Failed to load team members.');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = d => {
    if (!d) return '—';
    try {
      return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch { return '—'; }
  };

  return (
    <AppLayout>

      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: '28px', flexWrap: 'wrap', gap: '16px',
      }}>
        <div>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 700, color: '#E2E8F0' }}>
            Team Management
          </h1>
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            Manage who has access to your company account
          </p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="btn-cyber"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px' }}
        >
          <Plus size={18} /> Add Team Member
        </button>
      </div>

      {/* Info banner */}
      <div style={{
        padding: '14px 18px', borderRadius: '10px', marginBottom: '24px',
        background: 'rgba(59,130,246,0.07)', border: '1px solid rgba(59,130,246,0.2)',
        display: 'flex', alignItems: 'flex-start', gap: '12px',
      }}>
        <Shield size={18} color="#3B82F6" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#94A3B8', lineHeight: 1.6 }}>
          <strong style={{ color: '#3B82F6' }}>Role permissions:</strong>{' '}
          <strong style={{ color: '#E2E8F0' }}>Admin</strong> — full access including team management.{' '}
          <strong style={{ color: '#E2E8F0' }}>Analyst</strong> — can create suppliers and run evaluations.{' '}
          <strong style={{ color: '#E2E8F0' }}>Viewer</strong> — read-only access to all data.
        </div>
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

      {/* Team Table */}
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif', gap: '12px' }}>
            <div style={{ width: '20px', height: '20px', border: '2px solid rgba(0,212,255,0.2)', borderTop: '2px solid #00D4FF', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            Loading team...
          </div>
        ) : members.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif' }}>
            <Users size={40} color="#1A3A5C" style={{ marginBottom: '12px' }} />
            <p style={{ marginBottom: '16px' }}>No team members found.</p>
            <button onClick={() => setShowAdd(true)} className="btn-cyber" style={{ padding: '9px 20px', fontSize: '0.875rem' }}>
              Add First Member
            </button>
          </div>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {members.map(member => (
                <tr key={member.user_id || member.email}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {/* Avatar */}
                      <div style={{
                        width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
                        background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.8rem', color: '#050B18',
                      }}>
                        {(member.full_name || member.email || 'U')[0].toUpperCase()}
                      </div>
                      <span style={{ fontFamily: 'DM Sans, sans-serif', fontWeight: 500, color: '#E2E8F0' }}>
                        {member.full_name || '—'}
                        {member.user_id === currentUser?.user_id && (
                          <span style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.65rem', color: '#00D4FF', marginLeft: '6px' }}>YOU</span>
                        )}
                      </span>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#94A3B8' }}>
                    {member.email}
                  </td>
                  <td><RoleBadge role={member.role} /></td>
                  <td>
                    <span style={{
                      fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600,
                      padding: '2px 10px', borderRadius: '999px',
                      background: member.is_active !== false ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                      color: member.is_active !== false ? '#10B981' : '#EF4444',
                      border: `1px solid ${member.is_active !== false ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
                    }}>
                      {member.is_active !== false ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
                    {formatDate(member.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add modal */}
      {showAdd && (
        <AddMemberModal
          onClose={() => setShowAdd(false)}
          onSuccess={newMember => setMembers(prev => [...prev, newMember])}
        />
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}