import { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';

export default function Navbar({ onLoginClick, onSignupClick }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-40 transition-all duration-300"
      style={{
        background: scrolled
          ? 'rgba(5, 11, 24, 0.95)'
          : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(26,58,92,0.5)' : 'none',
      }}
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #00D4FF, #3B82F6)', boxShadow: '0 0 15px rgba(0,212,255,0.4)' }}
          >
            <Shield size={18} className="text-cyber-black" />
          </div>
          <span className="font-display text-lg font-bold text-white">
            Risk<span style={{ color: '#00D4FF' }}>Guard</span> AI
          </span>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3">
          <button onClick={onLoginClick} className="btn-outline py-2 px-5 text-sm">
            Login
          </button>
          <button onClick={onSignupClick} className="btn-cyber py-2 px-5 text-sm">
            Get Started Free
          </button>
        </div>
      </div>
    </nav>
  );
}