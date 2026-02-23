const features = [
  { icon: '🛡️', title: 'Real Sanctions Data', desc: 'EU, OFAC, and UN databases checked in real time with 6,400+ tracked entities.' },
  { icon: '📰', title: 'Live News Analysis', desc: 'Sentiment analysis on latest news articles to detect reputational risk.' },
  { icon: '🏢', title: 'Company Registry', desc: 'UK Companies House and international registry verification in seconds.' },
  { icon: '💰', title: 'Cost Tracking', desc: 'Per-evaluation OpenAI token usage monitoring for full transparency.' },
  { icon: '🔐', title: 'Role-Based Access', desc: 'Admin, Analyst, and Viewer permission levels for your entire team.' },
  { icon: '⚡', title: 'Background Processing', desc: 'Non-blocking async pipeline — trigger evaluations and check back later.' },
];

export default function FeaturesSection() {
  return (
    <section className="py-24 px-6" style={{ background: 'rgba(10,22,40,0.5)' }}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
            Enterprise-Grade Features
          </h2>
          <p className="text-slate-400 text-lg">
            Built for real compliance workflows — not demos.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <div key={i} className="glass-card p-6 glow-border group hover:scale-105 transition-transform duration-300">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="font-display text-white font-bold mb-2">{f.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}