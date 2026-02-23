import { Play, ArrowRight } from 'lucide-react';

export default function HeroSection({ onGetStarted }) {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 px-6">
      {/* Glow orbs in background */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #00D4FF, transparent)' }} />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #3B82F6, transparent)' }} />

      <div className="max-w-5xl mx-auto text-center relative z-10">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8 text-sm"
          style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00D4FF' }}>
          <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-pulse" />
          AI-Powered Supplier Intelligence Platform
        </div>

        {/* Headline */}
        <h1 className="font-display text-5xl md:text-7xl font-bold text-white leading-tight mb-6">
          Evaluate Suppliers{' '}
          <span style={{
            background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            in 10 Minutes
          </span>
          <br />Not 3 Days.
        </h1>

        {/* Subtitle */}
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Our 5-agent AI system checks documents, sanctions lists, news sentiment,
          company registries, and compliance policies — delivering a structured
          risk verdict with full audit trail.
        </p>

        {/* CTA Buttons */}
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <button
            onClick={onGetStarted}
            className="btn-cyber flex items-center gap-2 py-4 px-8 text-base"
          >
            Start Free Trial <ArrowRight size={18} />
          </button>
          <button
            className="btn-outline flex items-center gap-2 py-4 px-8 text-base"
          >
            <Play size={16} /> Watch Demo
          </button>
        </div>

        {/* Social proof */}
        <p className="text-slate-500 text-sm mt-8">
          Trusted for evaluating suppliers across{' '}
          <span className="text-cyber-cyan font-medium">50+ countries</span>
        </p>

        {/* Mock dashboard preview */}
        <div className="mt-16 relative">
          <div className="glass-card p-6 max-w-3xl mx-auto glow-border">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-slate-500 text-xs ml-2 font-mono">RiskGuard AI — Evaluation Report</span>
            </div>
            <div className="space-y-3 text-left">
              <div className="flex items-center justify-between p-3 rounded-lg"
                style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)' }}>
                <span className="text-slate-300 text-sm">TechTextiles Ltd — UK Supplier</span>
                <span className="badge-low">LOW RISK</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg"
                style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)' }}>
                <span className="text-slate-300 text-sm">GlobalFabrics Inc — US Supplier</span>
                <span className="badge-medium">MEDIUM RISK</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg"
                style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
                <span className="text-slate-300 text-sm">FastShip Trading Co — Unknown</span>
                <span className="badge-high">HIGH RISK</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}