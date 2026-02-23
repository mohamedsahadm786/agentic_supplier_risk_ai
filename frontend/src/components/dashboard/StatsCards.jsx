import { Package, ClipboardList, AlertTriangle, Clock } from 'lucide-react';

const cards = [
  {
    label:   'Total Suppliers',
    icon:    Package,
    color:   '#00D4FF',
    bg:      'rgba(0,212,255,0.1)',
    border:  'rgba(0,212,255,0.2)',
    key:     'total_suppliers',
  },
  {
    label:   'Total Evaluations',
    icon:    ClipboardList,
    color:   '#3B82F6',
    bg:      'rgba(59,130,246,0.1)',
    border:  'rgba(59,130,246,0.2)',
    key:     'total_evaluations',
  },
  {
    label:   'High Risk Suppliers',
    icon:    AlertTriangle,
    color:   '#EF4444',
    bg:      'rgba(239,68,68,0.1)',
    border:  'rgba(239,68,68,0.2)',
    key:     'high_risk',
  },
  {
    label:   'Pending Evaluations',
    icon:    Clock,
    color:   '#F59E0B',
    bg:      'rgba(245,158,11,0.1)',
    border:  'rgba(245,158,11,0.2)',
    key:     'pending',
  },
];

export default function StatsCards({ suppliers = [], evaluations = [] }) {
  // Calculate stats from the data passed in
  const highRisk  = suppliers.filter(s => s.risk_level === 'High').length;
  const pending   = evaluations.filter(
    e => e.status === 'pending' || e.status === 'processing'
  ).length;

  const values = {
    total_suppliers:   suppliers.length,
    total_evaluations: evaluations.length,
    high_risk:         highRisk,
    pending:           pending,
  };

  return (
    <div style={{
      display:             'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap:                 '20px',
      marginBottom:        '28px',
    }}>
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.key}
            className="glass-card"
            style={{
              padding: '24px',
              border:  `1px solid ${card.border}`,
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
            }}
          >
            {/* Icon */}
            <div style={{
              width:          '48px',
              height:         '48px',
              borderRadius:   '12px',
              background:     card.bg,
              border:         `1px solid ${card.border}`,
              display:        'flex',
              alignItems:     'center',
              justifyContent: 'center',
              flexShrink:     0,
            }}>
              <Icon size={22} color={card.color} />
            </div>

            {/* Text */}
            <div>
              <div style={{
                fontFamily: 'Syne, sans-serif',
                fontSize:   '1.75rem',
                fontWeight: 700,
                color:      '#E2E8F0',
                lineHeight: 1,
                marginBottom: '4px',
              }}>
                {values[card.key]}
              </div>
              <div style={{
                fontFamily: 'DM Sans, sans-serif',
                fontSize:   '0.8rem',
                color:      '#64748B',
              }}>
                {card.label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}