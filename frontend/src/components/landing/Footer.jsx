import { Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="py-10 px-6 border-t" style={{ borderColor: 'rgba(26,58,92,0.5)' }}>
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Shield size={18} className="text-cyber-cyan" />
          <span className="font-display font-bold text-white">
            Risk<span style={{ color: '#00D4FF' }}>Guard</span> AI
          </span>
        </div>

        {/* Links */}
        <div className="flex items-center gap-6 text-sm text-slate-400">
          <a href="#" className="hover:text-cyber-cyan transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-cyber-cyan transition-colors">Terms of Service</a>
        </div>

        {/* Copyright */}
        <p className="text-slate-500 text-sm">
          © {new Date().getFullYear()} RiskGuard AI. All rights reserved.
        </p>
      </div>
    </footer>
  );
}