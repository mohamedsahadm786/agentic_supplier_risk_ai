import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  ClipboardList,
  FileText,
  Users,
  Settings,
  Shield,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import { getUser } from '../../utils/auth';
import { authAPI } from '../../services/api';

// ── Nav items config ──────────────────────────────────────────────
const NAV_ITEMS = [
  {
    label: 'Dashboard',
    path:  '/dashboard',
    icon:  LayoutDashboard,
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    label: 'Suppliers',
    path:  '/suppliers',
    icon:  Package,
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    label: 'Evaluations',
    path:  '/evaluations',
    icon:  ClipboardList,
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    label: 'Documents',
    path:  '/documents',
    icon:  FileText,
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    label: 'Team',
    path:  '/team',
    icon:  Users,
    roles: ['admin'], // admin only
  },
  {
    label: 'Settings',
    path:  '/settings',
    icon:  Settings,
    roles: ['admin', 'analyst', 'viewer'],
  },
];

// ── Role badge colors ─────────────────────────────────────────────
const ROLE_STYLES = {
  admin:       { bg: 'rgba(59,130,246,0.15)',  color: '#3B82F6',  label: 'Admin'   },
  analyst:     { bg: 'rgba(0,212,255,0.15)',   color: '#00D4FF',  label: 'Analyst' },
  viewer:      { bg: 'rgba(148,163,184,0.15)', color: '#94A3B8',  label: 'Viewer'  },
  super_admin: { bg: 'rgba(168,85,247,0.15)',  color: '#A855F7',  label: 'Super Admin' },
};

export default function Sidebar() {
  const user     = getUser();
  const navigate = useNavigate();
  const role     = user?.role || 'viewer';
  const roleStyle = ROLE_STYLES[role] || ROLE_STYLES.viewer;

  // Filter nav items by role
  const visibleItems = NAV_ITEMS.filter((item) =>
    item.roles.includes(role)
  );

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch {
      // ignore error
    } finally {
      localStorage.removeItem('token');
      navigate('/');
    }
  };

  return (
    <aside
      className="sidebar"
      style={{
        width:     '240px',
        minHeight: '100vh',
        display:   'flex',
        flexDirection: 'column',
        position:  'fixed',
        left:      0,
        top:       0,
        zIndex:    50,
      }}
    >
      {/* ── Logo ── */}
      <div
        style={{
          padding:     '24px 20px',
          borderBottom: '1px solid rgba(26,58,92,0.6)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width:        '36px',
              height:       '36px',
              borderRadius: '8px',
              background:   'linear-gradient(135deg, #00D4FF, #3B82F6)',
              display:      'flex',
              alignItems:   'center',
              justifyContent: 'center',
              boxShadow:    '0 0 15px rgba(0,212,255,0.4)',
            }}
          >
            <Shield size={20} color="#050B18" strokeWidth={2.5} />
          </div>
          <div>
            <div
              style={{
                fontFamily: 'Syne, sans-serif',
                fontWeight: 700,
                fontSize:   '1rem',
                color:      '#E2E8F0',
                lineHeight: 1.2,
              }}
            >
              RiskGuard
            </div>
            <div
              style={{
                fontSize: '0.65rem',
                color:    '#00D4FF',
                fontFamily: 'Syne, sans-serif',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
              }}
            >
              AI Platform
            </div>
          </div>
        </div>
      </div>

      {/* ── Navigation ── */}
      <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto' }}>
        <div
          style={{
            fontSize:      '0.65rem',
            color:         '#4A6080',
            fontFamily:    'Syne, sans-serif',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            padding:       '0 8px 8px',
          }}
        >
          Navigation
        </div>

        {visibleItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display:       'flex',
                alignItems:    'center',
                gap:           '10px',
                padding:       '10px 12px',
                borderRadius:  '8px',
                marginBottom:  '4px',
                textDecoration: 'none',
                transition:    'all 0.2s ease',
                background:    isActive
                  ? 'rgba(0,212,255,0.1)'
                  : 'transparent',
                border: isActive
                  ? '1px solid rgba(0,212,255,0.2)'
                  : '1px solid transparent',
                color: isActive ? '#00D4FF' : '#94A3B8',
              })}
            >
              {({ isActive }) => (
                <>
                  <Icon
                    size={18}
                    strokeWidth={isActive ? 2 : 1.5}
                  />
                  <span
                    style={{
                      fontFamily: 'DM Sans, sans-serif',
                      fontSize:   '0.875rem',
                      fontWeight: isActive ? 600 : 400,
                      flex:       1,
                    }}
                  >
                    {item.label}
                  </span>
                  {isActive && (
                    <ChevronRight size={14} />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* ── User Profile + Logout ── */}
      <div
        style={{
          padding:    '16px 12px',
          borderTop:  '1px solid rgba(26,58,92,0.6)',
        }}
      >
        {/* User info */}
        <div
          style={{
            display:      'flex',
            alignItems:   'center',
            gap:          '10px',
            padding:      '10px 12px',
            borderRadius: '8px',
            background:   'rgba(26,58,92,0.3)',
            marginBottom: '8px',
          }}
        >
          {/* Avatar */}
          <div
            style={{
              width:           '32px',
              height:          '32px',
              borderRadius:    '50%',
              background:      'linear-gradient(135deg, #00D4FF, #3B82F6)',
              display:         'flex',
              alignItems:      'center',
              justifyContent:  'center',
              fontFamily:      'Syne, sans-serif',
              fontWeight:      700,
              fontSize:        '0.8rem',
              color:           '#050B18',
              flexShrink:      0,
            }}
          >
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>

          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize:     '0.8rem',
                fontWeight:   600,
                color:        '#E2E8F0',
                fontFamily:   'DM Sans, sans-serif',
                whiteSpace:   'nowrap',
                overflow:     'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {user?.email || 'User'}
            </div>
            {/* Role badge */}
            <span
              style={{
                fontSize:     '0.65rem',
                fontFamily:   'Syne, sans-serif',
                fontWeight:   600,
                padding:      '1px 6px',
                borderRadius: '999px',
                background:   roleStyle.bg,
                color:        roleStyle.color,
              }}
            >
              {roleStyle.label}
            </span>
          </div>
        </div>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          style={{
            display:       'flex',
            alignItems:    'center',
            gap:           '8px',
            width:         '100%',
            padding:       '9px 12px',
            borderRadius:  '8px',
            background:    'transparent',
            border:        '1px solid rgba(239,68,68,0.2)',
            color:         '#EF4444',
            cursor:        'pointer',
            fontFamily:    'DM Sans, sans-serif',
            fontSize:      '0.875rem',
            transition:    'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239,68,68,0.1)';
            e.currentTarget.style.borderColor = 'rgba(239,68,68,0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.borderColor = 'rgba(239,68,68,0.2)';
          }}
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  );
}