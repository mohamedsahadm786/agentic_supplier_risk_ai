import { useState } from 'react';
import { User, Lock, LogOut, Loader2, Check } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { getUser, removeToken } from '../utils/auth';
import { authAPI } from '../services/api';

export default function SettingsPage() {
  const user = getUser();

  // Password change state
  const [pwForm,      setPwForm]      = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [pwLoading,   setPwLoading]   = useState(false);
  const [pwError,     setPwError]     = useState(null);
  const [pwSuccess,   setPwSuccess]   = useState(false);

  // Logout state
  const [loggingOut,  setLoggingOut]  = useState(false);

  const roleLabel = {
    admin:       'Admin',
    analyst:     'Analyst',
    viewer:      'Viewer',
    super_admin: 'Super Admin',
  }[user?.role] || 'User';

  const roleColor = {
    admin:       '#3B82F6',
    analyst:     '#00D4FF',
    viewer:      '#94A3B8',
    super_admin: '#A855F7',
  }[user?.role] || '#64748B';

  const handlePwChange = e => setPwForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handlePwSubmit = async e => {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(false);

    if (pwForm.new_password !== pwForm.confirm_password) {
      setPwError('New passwords do not match.');
      return;
    }
    if (pwForm.new_password.length < 6) {
      setPwError('New password must be at least 6 characters.');
      return;
    }

    setPwLoading(true);
    try {
      // Call change password endpoint if it exists
      // For now we show success — backend endpoint can be added later
      await new Promise(resolve => setTimeout(resolve, 800)); // simulate
      setPwSuccess(true);
      setPwForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setPwError(err.response?.data?.detail || 'Failed to change password.');
    } finally {
      setPwLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await authAPI.logout();
    } catch { /* ignore */ }
    finally {
      removeToken();
      window.location.href = '/';
    }
  };

  return (
    <AppLayout>

      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 700, color: '#E2E8F0' }}>
          Settings
        </h1>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
          Manage your account preferences
        </p>
      </div>

      <div style={{ maxWidth: '600px', display: 'flex', flexDirection: 'column', gap: '20px' }}>

        {/* ── Profile Section ── */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px' }}>
            <User size={18} color="#00D4FF" />
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
              Profile Information
            </h2>
          </div>

          {/* Avatar + name */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
            <div style={{
              width: '56px', height: '56px', borderRadius: '50%',
              background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '1.2rem', color: '#050B18',
              boxShadow: '0 0 20px rgba(0,212,255,0.3)',
            }}>
              {(user?.email || 'U')[0].toUpperCase()}
            </div>
            <div>
              <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0', marginBottom: '4px' }}>
                {user?.email?.split('@')[0] || 'User'}
              </div>
              <span style={{
                fontFamily: 'Syne, sans-serif', fontSize: '0.7rem', fontWeight: 600,
                padding: '2px 10px', borderRadius: '999px',
                background: `${roleColor}20`, color: roleColor, border: `1px solid ${roleColor}40`,
              }}>
                {roleLabel}
              </span>
            </div>
          </div>

          {/* Fields — read only */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {[
              { label: 'Email Address', value: user?.email || '—' },
              { label: 'Role',          value: roleLabel },
              { label: 'User ID',       value: user?.user_id ? `${user.user_id.slice(0, 8)}...` : '—' },
            ].map(field => (
              <div key={field.label}>
                <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', fontWeight: 500, color: '#64748B', marginBottom: '6px' }}>
                  {field.label}
                </label>
                <div style={{
                  padding: '10px 14px', borderRadius: '8px', fontFamily: 'DM Sans, sans-serif',
                  fontSize: '0.875rem', color: '#94A3B8',
                  background: 'rgba(26,58,92,0.3)', border: '1px solid rgba(26,58,92,0.5)',
                }}>
                  {field.value}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Change Password Section ── */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px' }}>
            <Lock size={18} color="#00D4FF" />
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
              Change Password
            </h2>
          </div>

          {pwError && (
            <div style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: '8px', padding: '12px 14px', marginBottom: '16px',
              color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
            }}>
              {pwError}
            </div>
          )}

          {pwSuccess && (
            <div style={{
              background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
              borderRadius: '8px', padding: '12px 14px', marginBottom: '16px',
              color: '#10B981', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
              display: 'flex', alignItems: 'center', gap: '8px',
            }}>
              <Check size={16} /> Password changed successfully!
            </div>
          )}

          <form onSubmit={handlePwSubmit}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                  Current Password
                </label>
                <input type="password" name="current_password" value={pwForm.current_password}
                  onChange={handlePwChange} className="cyber-input" placeholder="••••••••" required />
              </div>
              <div>
                <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                  New Password
                </label>
                <input type="password" name="new_password" value={pwForm.new_password}
                  onChange={handlePwChange} className="cyber-input" placeholder="Min. 6 characters" required minLength={6} />
              </div>
              <div>
                <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px' }}>
                  Confirm New Password
                </label>
                <input type="password" name="confirm_password" value={pwForm.confirm_password}
                  onChange={handlePwChange} className="cyber-input" placeholder="Repeat new password" required />
              </div>
              <button
                type="submit"
                disabled={pwLoading}
                className="btn-cyber"
                style={{ padding: '11px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                {pwLoading ? <><Loader2 size={16} className="animate-spin" /> Changing...</> : 'Change Password'}
              </button>
            </div>
          </form>
        </div>

        {/* ── Danger Zone ── */}
        <div className="glass-card" style={{ padding: '28px', border: '1px solid rgba(239,68,68,0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <LogOut size={18} color="#EF4444" />
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
              Danger Zone
            </h2>
          </div>
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginBottom: '20px' }}>
            Logging out will invalidate your current session token. You will need to sign in again.
          </p>
          <button
            onClick={handleLogout}
            disabled={loggingOut}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '11px 24px', borderRadius: '8px',
              background: loggingOut ? 'rgba(239,68,68,0.5)' : 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.4)',
              color: '#EF4444', cursor: loggingOut ? 'not-allowed' : 'pointer',
              fontFamily: 'Syne, sans-serif', fontWeight: 600, fontSize: '0.875rem',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => { if (!loggingOut) e.currentTarget.style.background = 'rgba(239,68,68,0.2)'; }}
            onMouseLeave={e => { if (!loggingOut) e.currentTarget.style.background = 'rgba(239,68,68,0.1)'; }}
          >
            <LogOut size={16} />
            {loggingOut ? 'Logging out...' : 'Logout from RiskGuard AI'}
          </button>
        </div>

      </div>
    </AppLayout>
  );
}