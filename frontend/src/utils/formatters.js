// ── Date Formatters ──────────────────────────────────────────────

export const formatDate = (dateString) => {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year:  'numeric',
    month: 'short',
    day:   'numeric',
  });
};

export const formatDateTime = (dateString) => {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year:   'numeric',
    month:  'short',
    day:    'numeric',
    hour:   '2-digit',
    minute: '2-digit',
  });
};

export const formatRelativeTime = (dateString) => {
  if (!dateString) return '—';
  const now  = new Date();
  const date = new Date(dateString);
  const diffMs      = now - date;
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours   = Math.floor(diffMinutes / 60);
  const diffDays    = Math.floor(diffHours / 24);

  if (diffMinutes < 1)  return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24)   return `${diffHours}h ago`;
  if (diffDays < 7)     return `${diffDays}d ago`;
  return formatDate(dateString);
};

// ── Currency / Number Formatters ─────────────────────────────────

export const formatCost = (amount) => {
  if (amount === null || amount === undefined) return '$0.000000';
  return `$${parseFloat(amount).toFixed(6)}`;
};

export const formatCostShort = (amount) => {
  if (amount === null || amount === undefined) return '$0.00';
  return `$${parseFloat(amount).toFixed(4)}`;
};

export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return Number(num).toLocaleString('en-US');
};

export const formatTokens = (tokens) => {
  if (!tokens) return '0';
  if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}k`;
  return tokens.toString();
};

export const formatConfidence = (score) => {
  if (score === null || score === undefined) return '—';
  return `${Math.round(parseFloat(score) * 100)}%`;
};

// ── File Size Formatter ───────────────────────────────────────────

export const formatFileSize = (bytes) => {
  if (!bytes) return '—';
  if (bytes < 1024)        return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

// ── Risk Level Helpers ────────────────────────────────────────────

export const getRiskBadgeClass = (riskLevel) => {
  if (!riskLevel) return 'badge-medium';
  const level = riskLevel.toLowerCase();
  if (level === 'low')    return 'badge-low';
  if (level === 'high')   return 'badge-high';
  return 'badge-medium';
};

export const getRiskColor = (riskLevel) => {
  if (!riskLevel) return '#F59E0B';
  const level = riskLevel.toLowerCase();
  if (level === 'low')  return '#10B981';
  if (level === 'high') return '#EF4444';
  return '#F59E0B';
};

// ── Status Badge Helper ───────────────────────────────────────────

export const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'completed': return { bg: 'rgba(16,185,129,0.15)', color: '#10B981' };
    case 'pending':   return { bg: 'rgba(245,158,11,0.15)', color: '#F59E0B' };
    case 'failed':    return { bg: 'rgba(239,68,68,0.15)',  color: '#EF4444' };
    default:          return { bg: 'rgba(148,163,184,0.15)', color: '#94A3B8' };
  }
};