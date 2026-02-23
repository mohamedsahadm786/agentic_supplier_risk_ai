import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, X, Shield, Loader2 } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { getRedirectPath } from '../../utils/auth';

export default function SignupModal({ onClose, onSwitchToLogin }) {
  const navigate = useNavigate();
  const { signup, loading, error } = useAuth();

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    company_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  // Password strength indicator
  const getPasswordStrength = (pwd) => {
    if (pwd.length === 0) return { label: '', color: '' };
    if (pwd.length < 6)  return { label: 'Weak',   color: '#EF4444' };
    if (pwd.length < 10) return { label: 'Medium',  color: '#F59E0B' };
    return                      { label: 'Strong',  color: '#10B981' };
  };
  const strength = getPasswordStrength(formData.password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await signup(formData);
      onClose();
      navigate(getRedirectPath(user.role));
    } catch {
      // error shown via useAuth error state
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(5, 11, 24, 0.85)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
    >
      <div
        className="glass-card w-full max-w-md p-8 relative animate-fadeInUp"
        onClick={(e) => e.stopPropagation()}
        style={{ maxHeight: '90vh', overflowY: 'auto' }}
      >
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #00D4FF, #3B82F6)' }}>
            <Shield size={20} className="text-cyber-black" />
          </div>
          <div>
            <h2 className="font-display text-xl font-bold text-white">Create Account</h2>
            <p className="text-slate-400 text-sm">Start your free trial today</p>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-3 rounded-lg text-sm text-red-400"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Full Name */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="cyber-input"
              placeholder="John Smith"
              required
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="cyber-input"
              placeholder="you@company.com"
              required
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="cyber-input pr-12"
                placeholder="Min. 8 characters"
                required
                minLength={6}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-cyan-400 transition-colors"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {/* Strength indicator */}
            {formData.password && (
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1 rounded-full bg-slate-700">
                  <div
                    className="h-1 rounded-full transition-all duration-300"
                    style={{
                      width: strength.label === 'Weak' ? '33%' : strength.label === 'Medium' ? '66%' : '100%',
                      backgroundColor: strength.color,
                    }}
                  />
                </div>
                <span className="text-xs font-medium" style={{ color: strength.color }}>
                  {strength.label}
                </span>
              </div>
            )}
          </div>

          {/* Company Name */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Company Name</label>
            <input
              type="text"
              name="company_name"
              value={formData.company_name}
              onChange={handleChange}
              className="cyber-input"
              placeholder="Acme Corporation"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              You will be the admin for this company account.
            </p>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="btn-cyber w-full flex items-center justify-center gap-2 py-3"
          >
            {loading ? (
              <><Loader2 size={18} className="animate-spin" /> Creating account...</>
            ) : (
              'Create Free Account'
            )}
          </button>
        </form>

        {/* Switch to Login */}
        <p className="text-center text-sm text-slate-400 mt-6">
          Already have an account?{' '}
          <button
            onClick={onSwitchToLogin}
            className="text-cyber-cyan font-medium hover:underline"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}