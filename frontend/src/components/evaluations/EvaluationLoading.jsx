import { useEffect, useState } from 'react';
import { CheckCircle, Circle, Loader2 } from 'lucide-react';

const STEPS = [
  { label: 'Planner Agent',            desc: 'Creating evaluation strategy...'         },
  { label: 'Document Intelligence',    desc: 'Reading and extracting PDF data...'      },
  { label: 'Compliance Knowledge',     desc: 'Searching internal policy database...'   },
  { label: 'External Intelligence',    desc: 'Checking sanctions, news & registry...'  },
  { label: 'Decision Engine',          desc: 'Generating final risk assessment...'     },
];

export default function EvaluationLoading({ status }) {
  const [activeStep, setActiveStep] = useState(0);

  // Simulate step progress every 8 seconds (evaluation takes ~10 min total)
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep(prev => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      display:        'flex',
      flexDirection:  'column',
      alignItems:     'center',
      justifyContent: 'center',
      minHeight:      '60vh',
      padding:        '40px 20px',
    }}>
      {/* Spinning orb */}
      <div style={{ position: 'relative', marginBottom: '40px' }}>
        <div style={{
          width:        '80px',
          height:       '80px',
          borderRadius: '50%',
          border:       '3px solid rgba(0,212,255,0.15)',
          borderTop:    '3px solid #00D4FF',
          animation:    'spin 1s linear infinite',
        }} />
        <div style={{
          position:       'absolute',
          inset:          0,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          fontSize:       '1.8rem',
        }}>
          🤖
        </div>
      </div>

      <h2 style={{
        fontFamily:   'Syne, sans-serif',
        fontSize:     '1.4rem',
        fontWeight:   700,
        color:        '#E2E8F0',
        marginBottom: '8px',
        textAlign:    'center',
      }}>
        Running AI Evaluation...
      </h2>
      <p style={{
        fontFamily:   'DM Sans, sans-serif',
        fontSize:     '0.875rem',
        color:        '#64748B',
        marginBottom: '40px',
        textAlign:    'center',
      }}>
        Our 5-agent system is analysing your supplier. This takes ~10 minutes.
      </p>

      {/* Step indicators */}
      <div style={{
        width:    '100%',
        maxWidth: '480px',
        display:  'flex',
        flexDirection: 'column',
        gap:      '12px',
      }}>
        {STEPS.map((step, i) => {
          const isDone    = i < activeStep;
          const isActive  = i === activeStep;
          const isPending = i > activeStep;

          return (
            <div
              key={i}
              style={{
                display:      'flex',
                alignItems:   'center',
                gap:          '14px',
                padding:      '14px 18px',
                borderRadius: '10px',
                background:   isActive
                  ? 'rgba(0,212,255,0.07)'
                  : isDone
                    ? 'rgba(16,185,129,0.05)'
                    : 'rgba(26,58,92,0.2)',
                border: isActive
                  ? '1px solid rgba(0,212,255,0.25)'
                  : isDone
                    ? '1px solid rgba(16,185,129,0.2)'
                    : '1px solid rgba(26,58,92,0.4)',
                transition: 'all 0.4s ease',
              }}
            >
              {/* Icon */}
              {isDone ? (
                <CheckCircle size={20} color="#10B981" />
              ) : isActive ? (
                <Loader2 size={20} color="#00D4FF" style={{ animation: 'spin 1s linear infinite' }} />
              ) : (
                <Circle size={20} color="#1A3A5C" />
              )}

              {/* Text */}
              <div>
                <div style={{
                  fontFamily: 'Syne, sans-serif',
                  fontSize:   '0.875rem',
                  fontWeight: 600,
                  color:      isDone ? '#10B981' : isActive ? '#00D4FF' : '#4A6080',
                }}>
                  {i + 1}. {step.label}
                </div>
                {isActive && (
                  <div style={{
                    fontFamily: 'DM Sans, sans-serif',
                    fontSize:   '0.75rem',
                    color:      '#64748B',
                    marginTop:  '2px',
                  }}>
                    {step.desc}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <p style={{
        fontFamily: 'DM Sans, sans-serif',
        fontSize:   '0.75rem',
        color:      '#4A6080',
        marginTop:  '28px',
        textAlign:  'center',
      }}>
        Checking every 3 seconds for updates. You can safely leave this page.
      </p>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}