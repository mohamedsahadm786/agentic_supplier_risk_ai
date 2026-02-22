import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, ChevronDown, User } from 'lucide-react';
import { getUser } from '../../utils/auth';

// ── Page title mapping ────────────────────────────────────────────
const PAGE_TITLES = {
  '/dashboard':    { title: 'Dashboard',         subtitle: 'Overview of your supplier risk landscape' },
  '/suppliers':    { title: 'Suppliers',          subtitle: 'Manage and monitor your supplier portfolio' },
  '/evaluations':  { title: 'Evaluations',        subtitle: 'AI-powered risk assessment history' },
  '/evaluations/new': { title: 'New Evaluation',  subtitle: 'Start a new AI risk assessment' },
  '/documents':    { title: 'Documents',          subtitle: 'Uploaded supplier documents' },
  '/team':         { title: 'Team Management',    subtitle: 'Manage your team members and roles' },
  '/settings':     { title: 'Settings',           subtitle: 'Account and platform preferences' },
  '/platform-admin': { title: 'Platform Admin',   subtitle: 'System-wide analytics and management' },
};

export default function TopBar() {
  const location  = useLocation();
  const user      = getUser();
  const [showDropdown, setShowDropdown] = useState(false);

  // Get page info — check exact match first, then partial match
  const pageInfo =
    PAGE_TITLES[location.pathname] ||
    Object.entries(PAGE_TITLES).find(([key]) =>
      location.pathname.startsWith(key) && key !== '/'
    )?.[1] ||
    { title: 'RiskGuard AI', subtitle: '' };

  return (
    <header
      style={{
        position:     'fixed',
        top:          0,
        left:         '240px', // same as sidebar width
        right:        0,
        height:       '64px',
        background:   'rgba(5,11,24,0.9)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(26,58,92,0.6)',
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'space-between',
        padding:      '0 28px',
        zIndex:       40,
      }}
    >
      {/* ── Left: Page Title ── */}
      <div>
        <h1
          style={{
            fontFamily: 'Syne, sans-serif',
            fontWeight: 700,
            fontSize:   '1.1rem',
            color:      '#E2E8F0',
            lineHeight: 1.2,
          }}
        >
          {pageInfo.title}
        </h1>
        {pageInfo.subtitle && (
          <p
            style={{
              fontSize:   '0.72rem',
              color:      '#4A6080',
              fontFamily: 'DM Sans, sans-serif',
              marginTop:  '1px',
            }}
          >
            {pageInfo.subtitle}
          </p>
        )}
      </div>

      {/* ── Right: Notification + User ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>

        {/* Notification bell */}
        <button
          style={{
            width:         '36px',
            height:        '36px',
            borderRadius:  '8px',
            background:    'rgba(26,58,92,0.4)',
            border:        '1px solid rgba(26,58,92,0.6)',
            color:         '#94A3B8',
            cursor:        'pointer',
            display:       'flex',
            alignItems:    'center',
            justifyContent:'center',
            transition:    'all 0.2s ease',
            position:      'relative',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'rgba(0,212,255,0.3)';
            e.currentTarget.style.color = '#00D4FF';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'rgba(26,58,92,0.6)';
            e.currentTarget.style.color = '#94A3B8';
          }}
        >
          <Bell size={16} />
          {/* Notification dot */}
          <span
            style={{
              position:     'absolute',
              top:          '8px',
              right:        '8px',
              width:        '6px',
              height:       '6px',
              borderRadius: '50%',
              background:   '#00D4FF',
              boxShadow:    '0 0 6px rgba(0,212,255,0.8)',
            }}
          />
        </button>

        {/* User dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            style={{
              display:      'flex',
              alignItems:   'center',
              gap:          '8px',
              padding:      '6px 12px',
              borderRadius: '8px',
              background:   'rgba(26,58,92,0.4)',
              border:       '1px solid rgba(26,58,92,0.6)',
              color:        '#E2E8F0',
              cursor:       'pointer',
              fontFamily:   'DM Sans, sans-serif',
              fontSize:     '0.85rem',
              transition:   'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'rgba(0,212,255,0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(26,58,92,0.6)';
            }}
          >
            {/* Avatar circle */}
            <div
              style={{
                width:          '24px',
                height:         '24px',
                borderRadius:   '50%',
                background:     'linear-gradient(135deg, #00D4FF, #3B82F6)',
                display:        'flex',
                alignItems:     'center',
                justifyContent: 'center',
                fontSize:       '0.7rem',
                fontWeight:     700,
                color:          '#050B18',
                fontFamily:     'Syne, sans-serif',
              }}
            >
              {user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            <span style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user?.email || 'User'}
            </span>
            <ChevronDown
              size={14}
              style={{
                transition: 'transform 0.2s ease',
                transform: showDropdown ? 'rotate(180deg)' : 'rotate(0deg)',
              }}
            />
          </button>

          {/* Dropdown menu */}
          {showDropdown && (
            <div
              style={{
                position:     'absolute',
                top:          'calc(100% + 8px)',
                right:        0,
                width:        '180px',
                background:   'rgba(13,31,53,0.98)',
                border:       '1px solid rgba(26,58,92,0.8)',
                borderRadius: '10px',
                boxShadow:    '0 8px 32px rgba(0,0,0,0.4)',
                backdropFilter: 'blur(12px)',
                overflow:     'hidden',
                zIndex:       100,
              }}
            >
              {/* User info */}
              <div
                style={{
                  padding:      '12px 14px',
                  borderBottom: '1px solid rgba(26,58,92,0.6)',
                }}
              >
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontFamily: 'DM Sans, sans-serif' }}>
                  Signed in as
                </div>
                <div
                  style={{
                    fontSize:     '0.8rem',
                    color:        '#E2E8F0',
                    fontFamily:   'DM Sans, sans-serif',
                    fontWeight:   600,
                    overflow:     'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace:   'nowrap',
                  }}
                >
                  {user?.email}
                </div>
              </div>

              {/* Menu items */}
              {[
                { label: 'Profile', icon: User, path: '/settings' },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    onClick={() => {
                      setShowDropdown(false);
                      window.location.href = item.path;
                    }}
                    style={{
                      display:    'flex',
                      alignItems: 'center',
                      gap:        '8px',
                      width:      '100%',
                      padding:    '10px 14px',
                      background: 'transparent',
                      border:     'none',
                      color:      '#CBD5E1',
                      cursor:     'pointer',
                      fontFamily: 'DM Sans, sans-serif',
                      fontSize:   '0.85rem',
                      textAlign:  'left',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(0,212,255,0.05)';
                      e.currentTarget.style.color = '#00D4FF';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = '#CBD5E1';
                    }}
                  >
                    <Icon size={15} />
                    {item.label}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}