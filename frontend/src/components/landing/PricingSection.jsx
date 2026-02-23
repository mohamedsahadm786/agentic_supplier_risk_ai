import { Check } from 'lucide-react';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    desc: 'Perfect for trying out the platform.',
    features: ['50 evaluations/month', '5 team members', 'Basic risk reports', 'Email notifications', '3 document uploads per evaluation'],
    cta: 'Start Free',
    highlight: false,
  },
  {
    name: 'Standard',
    price: '$49',
    period: '/month',
    desc: 'For growing compliance teams.',
    features: ['500 evaluations/month', 'Unlimited team members', 'Full risk reports + audit trail', 'Priority email support', 'Unlimited documents', 'API access'],
    cta: 'Get Started',
    highlight: true,
  },
  {
    name: 'Premium',
    price: '$149',
    period: '/month',
    desc: 'For enterprise compliance operations.',
    features: ['Unlimited evaluations', 'Unlimited team members', 'Custom compliance policies', 'Dedicated support', 'SLA guarantee', 'Custom integrations'],
    cta: 'Contact Sales',
    highlight: false,
  },
];

export default function PricingSection({ onGetStarted }) {
  return (
    <section className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-slate-400 text-lg">No hidden fees. Cancel anytime.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <div
              key={i}
              className={`glass-card p-8 relative flex flex-col ${plan.highlight ? 'ring-2' : ''}`}
              style={plan.highlight ? {
                ringColor: '#00D4FF',
                border: '1px solid rgba(0,212,255,0.5)',
                boxShadow: '0 0 30px rgba(0,212,255,0.15)',
              } : {}}
            >
              {/* Most Popular badge */}
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-display font-bold text-cyber-black"
                  style={{ background: 'linear-gradient(135deg, #00D4FF, #3B82F6)' }}>
                  MOST POPULAR
                </div>
              )}

              <div className="mb-6">
                <h3 className="font-display text-xl font-bold text-white mb-1">{plan.name}</h3>
                <p className="text-slate-400 text-sm mb-4">{plan.desc}</p>
                <div className="flex items-baseline gap-1">
                  <span className="font-display text-4xl font-bold text-white">{plan.price}</span>
                  <span className="text-slate-400">{plan.period}</span>
                </div>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((feat, j) => (
                  <li key={j} className="flex items-center gap-3 text-sm text-slate-300">
                    <Check size={16} className="text-cyber-cyan flex-shrink-0" />
                    {feat}
                  </li>
                ))}
              </ul>

              <button
                onClick={onGetStarted}
                className={plan.highlight ? 'btn-cyber w-full py-3' : 'btn-outline w-full py-3'}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}