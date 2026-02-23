import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = {
  Low:    '#10B981',
  Medium: '#F59E0B',
  High:   '#EF4444',
};

// Custom tooltip that appears when you hover over a slice
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const item = payload[0];
    return (
      <div style={{
        background:   'rgba(13,31,53,0.95)',
        border:       '1px solid rgba(26,58,92,0.8)',
        borderRadius: '8px',
        padding:      '10px 14px',
      }}>
        <p style={{
          fontFamily: 'Syne, sans-serif',
          fontSize:   '0.85rem',
          color:      COLORS[item.name] || '#E2E8F0',
          fontWeight: 600,
        }}>
          {item.name} Risk
        </p>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize:   '0.8rem',
          color:      '#94A3B8',
        }}>
          {item.value} evaluation{item.value !== 1 ? 's' : ''}
        </p>
      </div>
    );
  }
  return null;
};

export default function RiskChart({ evaluations = [] }) {
  // Count how many evaluations are Low / Medium / High
  const counts = { Low: 0, Medium: 0, High: 0 };
  evaluations.forEach((e) => {
    if (e.risk_level && counts[e.risk_level] !== undefined) {
      counts[e.risk_level]++;
    }
  });

  const data = Object.entries(counts)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }));

  const isEmpty = data.length === 0;

  return (
    <div
      className="glass-card"
      style={{
        padding:      '24px',
        height:       '320px',
        display:      'flex',
        flexDirection:'column',
      }}
    >
      {/* Title */}
      <h3 style={{
        fontFamily:   'Syne, sans-serif',
        fontSize:     '1rem',
        fontWeight:   700,
        color:        '#E2E8F0',
        marginBottom: '4px',
      }}>
        Risk Distribution
      </h3>
      <p style={{
        fontFamily:   'DM Sans, sans-serif',
        fontSize:     '0.8rem',
        color:        '#64748B',
        marginBottom: '16px',
      }}>
        Breakdown of all evaluations by risk level
      </p>

      {/* Chart or empty state */}
      {isEmpty ? (
        <div style={{
          flex:           1,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          color:          '#4A6080',
          fontFamily:     'DM Sans, sans-serif',
          fontSize:       '0.875rem',
        }}>
          No evaluations yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={COLORS[entry.name]}
                  stroke="transparent"
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => (
                <span style={{
                  color:      '#94A3B8',
                  fontFamily: 'DM Sans, sans-serif',
                  fontSize:   '0.8rem',
                }}>
                  {value} Risk
                </span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}