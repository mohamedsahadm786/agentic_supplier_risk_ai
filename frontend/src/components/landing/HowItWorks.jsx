const agents = [
  {
    icon: '📋',
    title: 'Planner Agent',
    description: 'Analyzes your request and creates a structured 5-8 task evaluation strategy.',
    color: '#00D4FF',
  },
  {
    icon: '📄',
    title: 'Document Intelligence',
    description: 'Reads and extracts structured data from all uploaded PDFs — registration, financials, licenses.',
    color: '#3B82F6',
  },
  {
    icon: '📚',
    title: 'Compliance Knowledge',
    description: 'Checks against internal policy database — OECD guidelines, export control, trade law.',
    color: '#8B5CF6',
  },
  {
    icon: '🔍',
    title: 'External Intelligence',
    description: 'Scans live news, EU/OFAC/UN sanctions lists, and UK Companies House registry.',
    color: '#EC4899',
  },
  {
    icon: '⚖️',
    title: 'Decision Engine',
    description: 'Synthesizes all findings into a Low/Medium/High risk verdict with full reasoning.',
    color: '#10B981',
  },
];

export default function HowItWorks() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
            From Documents to Decision{' '}
            <span style={{
              background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              in Minutes
            </span>
          </h2>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Five specialized AI agents work in sequence to deliver a comprehensive risk assessment.
          </p>
        </div>

        {/* Agent Cards */}
        <div className="flex flex-col md:flex-row items-stretch gap-0">
          {agents.map((agent, index) => (
            <div key={index} className="flex flex-col md:flex-row items-center flex-1">
              {/* Card */}
              <div className="glass-card p-6 flex-1 w-full glow-border hover:scale-105 transition-transform duration-300"
                style={{ borderColor: `${agent.color}33` }}>
                <div className="text-3xl mb-3">{agent.icon}</div>
                <div className="text-xs font-display font-bold mb-1" style={{ color: agent.color }}>
                  AGENT {index + 1}
                </div>
                <h3 className="font-display text-white font-bold mb-2">{agent.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{agent.description}</p>
              </div>

              {/* Arrow between cards */}
              {index < agents.length - 1 && (
                <div className="text-2xl my-2 md:mx-2 md:my-0 flex-shrink-0"
                  style={{ color: '#1A3A5C' }}>
                  <span className="hidden md:block">→</span>
                  <span className="block md:hidden">↓</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}