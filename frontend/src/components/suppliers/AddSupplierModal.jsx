import { useState } from 'react';
import { X, Loader2, Package } from 'lucide-react';
import { suppliersAPI } from '../../services/api';

const COUNTRIES = [
  'United Kingdom', 'United States', 'India', 'China', 'Germany',
  'France', 'Japan', 'Canada', 'Australia', 'Singapore', 'UAE',
  'Brazil', 'South Africa', 'Mexico', 'Italy', 'Spain', 'Netherlands',
  'Sweden', 'Switzerland', 'South Korea', 'Other',
];

export default function AddSupplierModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    supplier_name:       '',
    country:             '',
    registration_number: '',
    business_context:    '',
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await suppliersAPI.create(formData);
      onSuccess(res.data); // pass new supplier back to parent
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create supplier.');
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
        style={{ width: '100%', maxWidth: '480px', padding: '32px', position: 'relative' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Close */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute', top: '16px', right: '16px',
            background: 'transparent', border: 'none',
            color: '#64748B', cursor: 'pointer',
          }}
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <div style={{
            width: '40px', height: '40px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Package size={20} color="#050B18" />
          </div>
          <div>
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.1rem', fontWeight: 700, color: '#E2E8F0' }}>
              Add New Supplier
            </h2>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
              Register a supplier for evaluation
            </p>
          </div>
        </div>

        {/* Error */}
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>

            {/* Supplier Name */}
            <div>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Supplier Name *
              </label>
              <input
                type="text"
                name="supplier_name"
                value={formData.supplier_name}
                onChange={handleChange}
                className="cyber-input"
                placeholder="e.g. TechTextiles Ltd"
                required
              />
            </div>

            {/* Country */}
            <div>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Country *
              </label>
              <select
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="cyber-input"
                required
                style={{ cursor: 'pointer' }}
              >
                <option value="" disabled>Select a country...</option>
                {COUNTRIES.map(c => (
                  <option key={c} value={c} style={{ background: '#0A1628' }}>{c}</option>
                ))}
              </select>
            </div>

            {/* Registration Number */}
            <div>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Registration Number
                <span style={{ color: '#4A6080', fontWeight: 400, marginLeft: '6px' }}>(optional)</span>
              </label>
              <input
                type="text"
                name="registration_number"
                value={formData.registration_number}
                onChange={handleChange}
                className="cyber-input"
                placeholder="e.g. 12345678"
              />
            </div>

            {/* Business Context */}
            <div>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Business Context
                <span style={{ color: '#4A6080', fontWeight: 400, marginLeft: '6px' }}>(optional)</span>
              </label>
              <textarea
                name="business_context"
                value={formData.business_context}
                onChange={handleChange}
                className="cyber-input"
                placeholder="e.g. Textile manufacturer for import deal — verify legitimacy and sanctions status"
                rows={3}
                style={{ resize: 'vertical', minHeight: '80px' }}
              />
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
              <button
                type="button"
                onClick={onClose}
                className="btn-outline"
                style={{ flex: 1, padding: '11px' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="btn-cyber"
                style={{ flex: 1, padding: '11px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                {loading ? <><Loader2 size={16} className="animate-spin" /> Creating...</> : 'Add Supplier'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}