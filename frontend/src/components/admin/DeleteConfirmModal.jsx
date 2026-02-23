import { useState } from 'react';
import { X, Trash2, Loader2 } from 'lucide-react';

export default function DeleteConfirmModal({ companyName, onClose, onConfirm }) {
  const REQUIRED_TEXT = 'DELETE_COMPANY_PERMANENTLY';
  const [inputText, setInputText] = useState('');
  const [loading,   setLoading]   = useState(false);

  const isMatch = inputText === REQUIRED_TEXT;

  const handleConfirm = async () => {
    if (!isMatch) return;
    setLoading(true);
    await onConfirm();
    setLoading(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(5,11,24,0.9)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
    >
      <div
        className="glass-card animate-fadeInUp"
        style={{ width: '100%', maxWidth: '440px', padding: '32px', position: 'relative', border: '1px solid rgba(239,68,68,0.3)' }}
        onClick={e => e.stopPropagation()}
      >
        <button onClick={onClose} style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer' }}>
          <X size={20} />
        </button>

        {/* Warning icon */}
        <div style={{
          width: '52px', height: '52px', borderRadius: '50%',
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px',
        }}>
          <Trash2 size={24} color="#EF4444" />
        </div>

        <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.1rem', fontWeight: 700, color: '#E2E8F0', textAlign: 'center', marginBottom: '8px' }}>
          Permanently Delete Company?
        </h2>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem', color: '#64748B', textAlign: 'center', marginBottom: '8px' }}>
          You are about to delete <strong style={{ color: '#E2E8F0' }}>{companyName}</strong> and ALL their data.
        </p>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#EF4444', textAlign: 'center', marginBottom: '24px' }}>
          This action is irreversible. All users, suppliers, evaluations, and documents will be permanently deleted.
        </p>

        {/* Type to confirm */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '8px' }}>
            Type <strong style={{ color: '#EF4444', fontFamily: 'monospace' }}>{REQUIRED_TEXT}</strong> to confirm:
          </label>
          <input
            type="text"
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            className="cyber-input"
            placeholder="Type the confirmation text..."
            style={{ borderColor: isMatch ? 'rgba(239,68,68,0.6)' : undefined }}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={onClose} className="btn-outline" style={{ flex: 1, padding: '10px' }}>
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!isMatch || loading}
            style={{
              flex: 1, padding: '10px', borderRadius: '8px',
              background: isMatch ? '#EF4444' : 'rgba(239,68,68,0.2)',
              border: 'none', color: isMatch ? 'white' : '#64748B',
              cursor: isMatch && !loading ? 'pointer' : 'not-allowed',
              fontFamily: 'Syne, sans-serif', fontWeight: 600, fontSize: '0.875rem',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
              transition: 'all 0.2s ease',
            }}
          >
            {loading ? <><Loader2 size={16} className="animate-spin" /> Deleting...</> : '🗑️ Delete Permanently'}
          </button>
        </div>
      </div>
    </div>
  );
}