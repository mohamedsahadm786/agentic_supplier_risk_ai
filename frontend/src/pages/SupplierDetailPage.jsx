import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Package, FileText, ClipboardList,
  Upload, Plus, Trash2, Loader2, X,
} from 'lucide-react';
import AppLayout        from '../components/layout/AppLayout';
import { suppliersAPI, documentsAPI, evaluationsAPI } from '../services/api';
import { getUser }      from '../utils/auth';

function RiskBadge({ level }) {
  if (!level) return <span style={{ color: '#4A6080' }}>Not evaluated</span>;
  const cls = { Low: 'badge-low', Medium: 'badge-medium', High: 'badge-high' }[level] || 'badge-low';
  return <span className={cls}>{level}</span>;
}

function formatDate(d) {
  if (!d) return '—';
  try {
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return '—'; }
}

function formatSize(bytes) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ── Upload Document Modal ──────────────────────────────────────────
function UploadDocumentModal({ supplierId, onClose, onSuccess }) {
  const [docType, setDocType] = useState('registration');
  const [file,    setFile]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const DOC_TYPES = [
    { value: 'registration',        label: 'Company Registration' },
    { value: 'financial_statement', label: 'Financial Statement' },
    { value: 'license',             label: 'Export / Import License' },
    { value: 'invoice',             label: 'Invoice' },
    { value: 'vat_certificate',     label: 'VAT Certificate' },
    { value: 'other',               label: 'Other Document' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { setError('Please select a PDF file.'); return; }
    setLoading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append('supplier_id',   supplierId);
      fd.append('document_type', docType);
      fd.append('file',          file);
      const res = await documentsAPI.upload(fd);
      onSuccess(res.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(5,11,24,0.85)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
    >
      <div
        className="glass-card animate-fadeInUp"
        style={{ width: '100%', maxWidth: '460px', padding: '32px', position: 'relative' }}
        onClick={e => e.stopPropagation()}
      >
        <button onClick={onClose} style={{
          position: 'absolute', top: '16px', right: '16px',
          background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer',
        }}>
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{
            width: '40px', height: '40px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #00D4FF, #3B82F6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Upload size={18} color="#050B18" />
          </div>
          <div>
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.1rem', fontWeight: 700, color: '#E2E8F0' }}>
              Upload Document
            </h2>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
              PDF files only
            </p>
          </div>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: '8px', padding: '10px 14px', marginBottom: '16px',
            color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.85rem',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Document Type *
              </label>
              <select
                value={docType}
                onChange={e => setDocType(e.target.value)}
                className="cyber-input"
                style={{ cursor: 'pointer' }}
              >
                {DOC_TYPES.map(t => (
                  <option key={t.value} value={t.value} style={{ background: '#0A1628' }}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Select PDF File *
              </label>
              {/* Drag & drop area */}
              <label
                htmlFor="pdf-upload"
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center',
                  justifyContent: 'center', gap: '8px', padding: '28px',
                  border: `2px dashed ${file ? '#00D4FF' : 'rgba(26,58,92,0.8)'}`,
                  borderRadius: '10px', cursor: 'pointer',
                  background: file ? 'rgba(0,212,255,0.05)' : 'rgba(10,22,40,0.5)',
                  transition: 'all 0.2s ease',
                }}
              >
                <Upload size={24} color={file ? '#00D4FF' : '#4A6080'} />
                <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: file ? '#00D4FF' : '#4A6080' }}>
                  {file ? file.name : 'Click to select PDF or drag & drop'}
                </span>
                {file && (
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#64748B' }}>
                    {formatSize(file.size)}
                  </span>
                )}
                <input
                  id="pdf-upload"
                  type="file"
                  accept=".pdf"
                  style={{ display: 'none' }}
                  onChange={e => setFile(e.target.files[0] || null)}
                />
              </label>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '4px' }}>
              <button type="button" onClick={onClose} className="btn-outline" style={{ flex: 1, padding: '11px' }}>
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="btn-cyber"
                style={{ flex: 1, padding: '11px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                {loading ? <><Loader2 size={16} className="animate-spin" /> Uploading...</> : 'Upload'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────
export default function SupplierDetailPage() {
  const { supplierId } = useParams();
  const navigate       = useNavigate();
  const user           = getUser();
  const canEdit        = user?.role === 'admin' || user?.role === 'analyst';

  const [supplier,    setSupplier]    = useState(null);
  const [documents,   setDocuments]   = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);
  const [showUpload,  setShowUpload]  = useState(false);

  useEffect(() => {
    fetchAll();
  }, [supplierId]);


  const fetchAll = async () => {
      setLoading(true);
      setError(null);
      try {
        const [suppRes, docsRes, evalsRes] = await Promise.all([
          suppliersAPI.getOne(supplierId),
          documentsAPI.getBySupplier(supplierId),
          evaluationsAPI.getAll({ supplier_id: supplierId }),
        ]);

        // Supplier — single object
        setSupplier(suppRes.data || null);

        // Documents — extract array safely from whatever shape backend returns
        const docsRaw = docsRes.data;
        if (Array.isArray(docsRaw)) {
          setDocuments(docsRaw);
        } else if (docsRaw && Array.isArray(docsRaw.items)) {
          setDocuments(docsRaw.items);
        } else if (docsRaw && Array.isArray(docsRaw.documents)) {
          setDocuments(docsRaw.documents);
        } else {
          setDocuments([]);
        }

        // Evaluations — extract array safely
        const evalsRaw = evalsRes.data;
        if (Array.isArray(evalsRaw)) {
          setEvaluations(evalsRaw);
        } else if (evalsRaw && Array.isArray(evalsRaw.items)) {
          setEvaluations(evalsRaw.items);
        } else if (evalsRaw && Array.isArray(evalsRaw.evaluations)) {
          setEvaluations(evalsRaw.evaluations);
        } else {
          setEvaluations([]);
        }

      } catch (err) {
        console.error('Supplier detail fetch error:', err);
        setError('Failed to load supplier details.');
      } finally {
        setLoading(false);
      }
    };



  if (loading) {
    return (
      <AppLayout>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          height: '400px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif', gap: '12px',
        }}>
          <div style={{
            width: '20px', height: '20px',
            border: '2px solid rgba(0,212,255,0.2)', borderTop: '2px solid #00D4FF',
            borderRadius: '50%', animation: 'spin 1s linear infinite',
          }} />
          Loading supplier...
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  if (error || !supplier) {
    return (
      <AppLayout>
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <p style={{ color: '#EF4444', fontFamily: 'DM Sans, sans-serif', marginBottom: '16px' }}>
            {error || 'Supplier not found.'}
          </p>
          <button onClick={() => navigate('/suppliers')} className="btn-outline" style={{ padding: '9px 20px' }}>
            ← Back to Suppliers
          </button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      {/* ── Back Button ── */}
      <button
        onClick={() => navigate('/suppliers')}
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          background: 'transparent', border: 'none', color: '#64748B',
          cursor: 'pointer', fontFamily: 'DM Sans, sans-serif',
          fontSize: '0.875rem', marginBottom: '20px',
          transition: 'color 0.2s',
        }}
        onMouseEnter={e => e.currentTarget.style.color = '#00D4FF'}
        onMouseLeave={e => e.currentTarget.style.color = '#64748B'}
      >
        <ArrowLeft size={16} /> Back to Suppliers
      </button>

      {/* ── Supplier Header Card ── */}
      <div className="glass-card" style={{
        padding: '28px', marginBottom: '24px',
        display: 'flex', alignItems: 'flex-start',
        justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px',
        border: '1px solid rgba(0,212,255,0.15)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '56px', height: '56px', borderRadius: '14px',
            background: 'linear-gradient(135deg, rgba(0,212,255,0.15), rgba(59,130,246,0.15))',
            border: '1px solid rgba(0,212,255,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Package size={26} color="#00D4FF" />
          </div>
          <div>
            <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.4rem', fontWeight: 700, color: '#E2E8F0', marginBottom: '6px' }}>
              {supplier.supplier_name}
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B' }}>
                🌍 {supplier.country || 'Unknown country'}
              </span>
              {supplier.registration_number && (
                <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#4A6080' }}>
                  Reg: {supplier.registration_number}
                </span>
              )}
              <RiskBadge level={supplier.risk_level} />
            </div>
          </div>
        </div>

        {/* Action buttons */}
        {canEdit && (
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => navigate(`/evaluations/new?supplier_id=${supplierId}`)}
              className="btn-cyber"
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '9px 18px', fontSize: '0.875rem' }}
            >
              <Plus size={16} /> Run Evaluation
            </button>
          </div>
        )}
      </div>

      {/* ── Documents Section ── */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px',
        }}>
          <div>
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
              <FileText size={16} style={{ display: 'inline', marginRight: '8px', color: '#00D4FF' }} />
              Uploaded Documents
            </h2>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>
              {documents.length} document{documents.length !== 1 ? 's' : ''} uploaded
            </p>
          </div>
          {canEdit && (
            <button
              onClick={() => setShowUpload(true)}
              className="btn-outline"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', fontSize: '0.8rem' }}
            >
              <Upload size={14} /> Upload Document
            </button>
          )}
        </div>

        {documents.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '40px',
            color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
          }}>
            No documents uploaded yet.
            {canEdit && (
              <span
                onClick={() => setShowUpload(true)}
                style={{ color: '#00D4FF', cursor: 'pointer', marginLeft: '6px' }}
              >
                Upload the first one.
              </span>
            )}
          </div>
        ) : (
          <table className="cyber-table">
            <thead>
              <tr>
                <th>File Name</th>
                <th>Document Type</th>
                <th>Size</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr key={doc.document_id}>
                  <td style={{ color: '#E2E8F0', fontFamily: 'DM Sans, sans-serif' }}>
                    📄 {doc.file_name || doc.original_filename || 'Document'}
                  </td>
                  <td>
                    <span style={{
                      fontFamily: 'Syne, sans-serif', fontSize: '0.72rem', fontWeight: 600,
                      padding: '2px 8px', borderRadius: '999px',
                      background: 'rgba(59,130,246,0.1)', color: '#3B82F6',
                      border: '1px solid rgba(59,130,246,0.2)', textTransform: 'capitalize',
                    }}>
                      {(doc.document_type || 'other').replace('_', ' ')}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
                    {formatSize(doc.file_size)}
                  </td>
                  <td style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
                    {formatDate(doc.uploaded_at || doc.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Evaluation History Section ── */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px',
        }}>
          <div>
            <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
              <ClipboardList size={16} style={{ display: 'inline', marginRight: '8px', color: '#00D4FF' }} />
              Evaluation History
            </h2>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>
              {evaluations.length} evaluation{evaluations.length !== 1 ? 's' : ''} completed
            </p>
          </div>
          {canEdit && (
            <button
              onClick={() => navigate(`/evaluations/new?supplier_id=${supplierId}`)}
              className="btn-cyber"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', fontSize: '0.8rem' }}
            >
              <Plus size={14} /> New Evaluation
            </button>
          )}
        </div>

        {evaluations.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '40px',
            color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
          }}>
            No evaluations yet.
            {canEdit && (
              <span
                onClick={() => navigate(`/evaluations/new?supplier_id=${supplierId}`)}
                style={{ color: '#00D4FF', cursor: 'pointer', marginLeft: '6px' }}
              >
                Run the first evaluation.
              </span>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {evaluations
              .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
              .map(ev => (
                <div
                  key={ev.evaluation_id}
                  onClick={() => navigate(`/evaluations/${ev.evaluation_id}`)}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '16px 18px', borderRadius: '10px', cursor: 'pointer',
                    background: 'rgba(26,58,92,0.2)', border: '1px solid rgba(26,58,92,0.5)',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = 'rgba(0,212,255,0.05)';
                    e.currentTarget.style.borderColor = 'rgba(0,212,255,0.2)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = 'rgba(26,58,92,0.2)';
                    e.currentTarget.style.borderColor = 'rgba(26,58,92,0.5)';
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                      <RiskBadge level={ev.risk_level} />
                      {ev.confidence_score && (
                        <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B' }}>
                          {Math.round((ev.confidence_score || 0) * 100)}% confidence
                        </span>
                      )}
                    </div>
                    <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#4A6080' }}>
                      {formatDate(ev.created_at)}
                    </span>
                  </div>
                  <button
                    style={{
                      background: 'transparent', border: '1px solid rgba(0,212,255,0.3)',
                      color: '#00D4FF', borderRadius: '7px', padding: '6px 14px',
                      cursor: 'pointer', fontFamily: 'Syne, sans-serif',
                      fontSize: '0.75rem', fontWeight: 600,
                    }}
                  >
                    View Report →
                  </button>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Upload modal */}
      {showUpload && (
        <UploadDocumentModal
          supplierId={supplierId}
          onClose={() => setShowUpload(false)}
          onSuccess={(newDoc) => setDocuments(prev => [...prev, newDoc])}
        />
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}