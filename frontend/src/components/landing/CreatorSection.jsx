import { Globe, Linkedin, Github } from 'lucide-react';

export default function CreatorSection() {
  const portfolioUrl = import.meta.env.VITE_PORTFOLIO_URL || '#';
  const linkedinUrl  = import.meta.env.VITE_LINKEDIN_URL  || '#';
  const githubUrl    = import.meta.env.VITE_GITHUB_URL    || '#';

  return (
    <section className="py-24 px-6" style={{ background: 'rgba(10,22,40,0.5)' }}>
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="font-display text-3xl font-bold text-white mb-4">
          Built by a Passionate AI Engineer
        </h2>

        <p className="text-slate-400 mb-8 leading-relaxed">
          This platform was designed and built as a production-grade portfolio project,
          demonstrating senior-level AI engineering — multi-agent orchestration, RAG pipelines,
          real-time data integrations, and a complete SaaS architecture. Every component
          is built the way real systems are built.
        </p>

        <div
        className="w-24 h-24 rounded-full mx-auto mb-6 overflow-hidden"
        style={{
            boxShadow: '0 0 30px rgba(0,212,255,0.4)',
        }}
        >
        <img
            src="/profile.jpg"
            alt="Creator"
            className="w-full h-full object-cover"
        />
        </div>



        <div className="flex items-center justify-center gap-4 flex-wrap">

          {/* Portfolio */}
          <a
            href={"https://d5qb6gsuemmzn.cloudfront.net/"}
            target="_blank"
            rel="noopener noreferrer"
            className="glass-card glow-border px-5 py-3 flex items-center gap-2 text-sm text-slate-300 hover:text-cyber-cyan transition-colors"
          >
            <Globe size={16} />
            Portfolio
          </a>

          {/* LinkedIn */}
          <a
            href={"https://www.linkedin.com/in/mohamed-sahad-m/"}
            target="_blank"
            rel="noopener noreferrer"
            className="glass-card glow-border px-5 py-3 flex items-center gap-2 text-sm text-slate-300 hover:text-cyber-cyan transition-colors"
          >
            <Linkedin size={16} />
            LinkedIn
          </a>

          {/* GitHub */}
          <a
            href={"https://github.com/mohamedsahadm786"}
            target="_blank"
            rel="noopener noreferrer"
            className="glass-card glow-border px-5 py-3 flex items-center gap-2 text-sm text-slate-300 hover:text-cyber-cyan transition-colors"
          >
            <Github size={16} />
            GitHub
          </a>

        </div>
      </div>
    </section>
  );
}