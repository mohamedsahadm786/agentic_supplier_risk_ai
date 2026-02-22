/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors
        'cyber-black':    '#050B18',
        'cyber-navy':     '#0A1628',
        'cyber-card':     '#0D1F35',
        'cyber-border':   '#1A3A5C',
        'cyber-cyan':     '#00D4FF',
        'cyber-blue':     '#3B82F6',
        'cyber-glow':     '#00D4FF33',
        // Risk colors
        'risk-low':       '#10B981',
        'risk-medium':    '#F59E0B',
        'risk-high':      '#EF4444',
      },
      fontFamily: {
        'display': ['Syne', 'sans-serif'],
        'body':    ['DM Sans', 'sans-serif'],
      },
      boxShadow: {
        'cyber':      '0 0 20px rgba(0, 212, 255, 0.15)',
        'cyber-lg':   '0 0 40px rgba(0, 212, 255, 0.2)',
        'glow-blue':  '0 0 20px rgba(59, 130, 246, 0.3)',
      },
      backgroundImage: {
        'grid-pattern': 
          "linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)",
      },
      backgroundSize: {
        'grid': '50px 50px',
      },
      animation: {
        'pulse-slow':   'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float':        'float 6s ease-in-out infinite',
        'glow':         'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%':   { boxShadow: '0 0 5px rgba(0,212,255,0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(0,212,255,0.6)' },
        },
      },
    },
  },
  plugins: [],
}