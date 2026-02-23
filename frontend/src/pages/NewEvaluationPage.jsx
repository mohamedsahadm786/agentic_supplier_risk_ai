import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Rocket, FileText, Package, AlignLeft } from 'lucide-react';
import AppLayout       from '../components/layout/AppLayout';
import EvaluationLoading from '../components/evaluations/EvaluationLoading';
import { suppliersAPI, documentsAPI, evaluationsAPI } from '../services/api';
import { useEvaluationPolling } from '../hooks/usePolling';

// ── Step indicator at top ─────────────────────────────────────────
function StepBar({ current }) {
  const steps = ['Select Supplier', 'Select Documents', 'Review & Submit'];
  return (
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '36px' }}>
      {steps.map((label, i) => {
        const isDone   = i < current;
        const isActive = i === current;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', flex: i < steps.length - 1 ? 1 : 'none' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width:          '36px',
                height:         '36px',
                borderRadius:   '50%',
                display:        'flex',
                alignItems:     'center',
                justifyContent: 'center',
                fontFamily:     'Syne, sans-serif',
                fontWeight:     700,
                fontSize:       '0.875rem',
                background:     isDone
                  ? 'linear-gradient(135deg, #10B981, #059669)'
                  : isActive
                    ? 'linear-gradient(135deg, #00D4FF, #3B82F6)'
                    : 'rgba(26,58,92,0.5)',
                color:          isDone || isActive ? '#050B18' : '#4A6080',
                border:         isActive ? '2px solid rgba(0,212,255,0.5)' : '2px solid transparent',
                boxShadow:      isActive ? '0 0 15px rgba(0,212,255,0.3)' : 'none',
                transition:     'all 0.3s ease',
              }}>
                {isDone ? '✓' : i + 1}
              </div>
              <span style={{
                fontFamily: 'DM Sans, sans-serif',
                fontSize:   '0.72rem',
                color:      isActive ? '#00D4FF' : isDone ? '#10B981' : '#4A6080',
                whiteSpace: 'nowrap',
              }}>
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div style={{
                flex:        1,
                height:      '2px',
                margin:      '0 8px',
                marginBottom:'22px',
                background:  isDone
                  ? 'linear-gradient(90deg, #10B981, #059669)'
                  : 'rgba(26,58,92,0.5)',
                transition:  'all 0.3s ease',
              }} />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────
export default function NewEvaluationPage() {
  const navigate        = useNavigate();
  const [searchParams]  = useSearchParams();
  const preselectedId   = searchParams.get('supplier_id');

  // Wizard state
  const [step,            setStep]            = useState(0);
  const [suppliers,       setSuppliers]       = useState([]);
  const [selectedSupplier,setSelectedSupplier]= useState(preselectedId || '');
  const [documents,       setDocuments]       = useState([]);
  const [selectedDocs,    setSelectedDocs]    = useState([]);
  const [businessContext, setBusinessContext] = useState('');
  const [loadingSuppliers,setLoadingSuppliers]= useState(true);
  const [loadingDocs,     setLoadingDocs]     = useState(false);
  const [submitting,      setSubmitting]      = useState(false);
  const [submitError,     setSubmitError]     = useState(null);

  // After submission — track evaluation ID for polling
  const [evaluationId,    setEvaluationId]    = useState(null);
  const { evaluation, isComplete } = useEvaluationPolling(
    evaluationId,
    !!evaluationId
  );

  // Auto-redirect when evaluation completes
  useEffect(() => {
    if (isComplete && evaluationId) {
      navigate(`/evaluations/${evaluationId}`);
    }
  }, [isComplete, evaluationId]);

  // Load suppliers on mount
  useEffect(() => {
    suppliersAPI.getAll()
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : [];
        setSuppliers(data);
        // If preselected supplier from URL, jump to step 1
        if (preselectedId && data.find(s => s.supplier_id === preselectedId)) {
          setSelectedSupplier(preselectedId);
        }
      })
      .catch(() => {})
      .finally(() => setLoadingSuppliers(false));
  }, []);

  // Load documents when supplier is selected
  useEffect(() => {
    if (!selectedSupplier) { setDocuments([]); return; }
    setLoadingDocs(true);
    documentsAPI.getBySupplier(selectedSupplier)
      .then(res => {
        const raw = res.data;
        const arr = Array.isArray(raw) ? raw
          : Array.isArray(raw?.items) ? raw.items
          : Array.isArray(raw?.documents) ? raw.documents
          : [];
        setDocuments(arr);
      })
      .catch(() => setDocuments([]))
      .finally(() => setLoadingDocs(false));
  }, [selectedSupplier]);

  // Submit evaluation
  const handleSubmit = async () => {
    if (!selectedSupplier) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await evaluationsAPI.create({
        supplier_id:      selectedSupplier,
        business_context: businessContext,
        document_ids:     selectedDocs,
      });
      const newEvalId = res.data?.evaluation_id || res.data?.id;
      setEvaluationId(newEvalId);
      // Step 3 = loading screen
      setStep(3);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || 'Failed to start evaluation.');
      setSubmitting(false);
    }
  };

  // Helper — get supplier name from id
  const getSupplierName = (id) => {
    const s = suppliers.find(s => s.supplier_id === id);
    return s?.supplier_name || 'Unknown';
  };

  // ── LOADING SCREEN (step 3) ─────────────────────────────────────
  if (step === 3 && evaluationId) {
    return (
      <AppLayout>
        <EvaluationLoading status={evaluation?.status} />
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      {/* Page header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 700, color: '#E2E8F0' }}>
          New Evaluation
        </h1>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
          Run a 5-agent AI risk assessment on a supplier
        </p>
      </div>

      {/* Wizard card */}
      <div className="glass-card" style={{ padding: '32px', maxWidth: '680px', margin: '0 auto' }}>

        <StepBar current={step} />

        {/* ── STEP 0: Select Supplier ── */}
        {step === 0 && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <Package size={20} color="#00D4FF" />
              <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
                Select a Supplier
              </h2>
            </div>

            {loadingSuppliers ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif' }}>
                Loading suppliers...
              </div>
            ) : suppliers.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', marginBottom: '16px' }}>
                  No suppliers found. Add a supplier first.
                </p>
                <button onClick={() => navigate('/suppliers')} className="btn-cyber" style={{ padding: '9px 20px' }}>
                  Go to Suppliers
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {suppliers.map(s => (
                  <div
                    key={s.supplier_id}
                    onClick={() => setSelectedSupplier(s.supplier_id)}
                    style={{
                      display:      'flex',
                      alignItems:   'center',
                      gap:          '14px',
                      padding:      '16px 18px',
                      borderRadius: '10px',
                      cursor:       'pointer',
                      background:   selectedSupplier === s.supplier_id
                        ? 'rgba(0,212,255,0.07)'
                        : 'rgba(26,58,92,0.2)',
                      border: selectedSupplier === s.supplier_id
                        ? '2px solid rgba(0,212,255,0.4)'
                        : '2px solid transparent',
                      transition:   'all 0.2s ease',
                    }}
                  >
                    {/* Radio circle */}
                    <div style={{
                      width:          '20px',
                      height:         '20px',
                      borderRadius:   '50%',
                      border:         selectedSupplier === s.supplier_id
                        ? '2px solid #00D4FF'
                        : '2px solid #1A3A5C',
                      display:        'flex',
                      alignItems:     'center',
                      justifyContent: 'center',
                      flexShrink:     0,
                    }}>
                      {selectedSupplier === s.supplier_id && (
                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#00D4FF' }} />
                      )}
                    </div>

                    <div>
                      <div style={{ fontFamily: 'DM Sans, sans-serif', fontWeight: 600, color: '#E2E8F0', fontSize: '0.9rem' }}>
                        {s.supplier_name}
                      </div>
                      <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.78rem', color: '#64748B', marginTop: '2px' }}>
                        {s.country || 'Unknown country'}
                        {s.registration_number && ` · Reg: ${s.registration_number}`}
                      </div>
                    </div>

                    {s.risk_level && (
                      <span
                        className={`badge-${s.risk_level.toLowerCase()}`}
                        style={{ marginLeft: 'auto' }}
                      >
                        {s.risk_level}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Next button */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '28px' }}>
              <button
                onClick={() => setStep(1)}
                disabled={!selectedSupplier}
                className="btn-cyber"
                style={{
                  display:   'flex',
                  alignItems:'center',
                  gap:       '8px',
                  padding:   '11px 24px',
                  opacity:   !selectedSupplier ? 0.4 : 1,
                  cursor:    !selectedSupplier ? 'not-allowed' : 'pointer',
                }}
              >
                Next <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 1: Select Documents ── */}
        {step === 1 && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <FileText size={20} color="#00D4FF" />
              <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
                Select Documents
              </h2>
            </div>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', marginBottom: '20px' }}>
              Select which documents to include in this evaluation for{' '}
              <span style={{ color: '#00D4FF', fontWeight: 600 }}>{getSupplierName(selectedSupplier)}</span>
            </p>

            {loadingDocs ? (
              <div style={{ textAlign: 'center', padding: '32px', color: '#4A6080', fontFamily: 'DM Sans, sans-serif' }}>
                Loading documents...
              </div>
            ) : documents.length === 0 ? (
              <div style={{
                textAlign: 'center', padding: '32px', borderRadius: '10px',
                background: 'rgba(26,58,92,0.2)', border: '1px dashed rgba(26,58,92,0.6)',
              }}>
                <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', marginBottom: '8px' }}>
                  No documents uploaded for this supplier.
                </p>
                <p style={{ color: '#4A6080', fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem' }}>
                  You can still run the evaluation — agents will use external sources only.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {/* Select all */}
                <div
                  onClick={() => {
                    if (selectedDocs.length === documents.length) {
                      setSelectedDocs([]);
                    } else {
                      setSelectedDocs(documents.map(d => d.document_id));
                    }
                  }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '10px',
                    padding: '10px 14px', borderRadius: '8px', cursor: 'pointer',
                    background: 'rgba(0,212,255,0.05)', border: '1px solid rgba(0,212,255,0.15)',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedDocs.length === documents.length && documents.length > 0}
                    onChange={() => {}}
                    style={{ cursor: 'pointer', accentColor: '#00D4FF', width: '16px', height: '16px' }}
                  />
                  <span style={{ fontFamily: 'Syne, sans-serif', fontSize: '0.8rem', fontWeight: 600, color: '#00D4FF' }}>
                    Select All Documents
                  </span>
                </div>

                {/* Document checkboxes */}
                {documents.map(doc => (
                  <div
                    key={doc.document_id}
                    onClick={() => {
                      setSelectedDocs(prev =>
                        prev.includes(doc.document_id)
                          ? prev.filter(id => id !== doc.document_id)
                          : [...prev, doc.document_id]
                      );
                    }}
                    style={{
                      display:      'flex',
                      alignItems:   'center',
                      gap:          '12px',
                      padding:      '14px 16px',
                      borderRadius: '10px',
                      cursor:       'pointer',
                      background:   selectedDocs.includes(doc.document_id)
                        ? 'rgba(0,212,255,0.05)'
                        : 'rgba(26,58,92,0.2)',
                      border: selectedDocs.includes(doc.document_id)
                        ? '1px solid rgba(0,212,255,0.25)'
                        : '1px solid rgba(26,58,92,0.4)',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.document_id)}
                      onChange={() => {}}
                      style={{ cursor: 'pointer', accentColor: '#00D4FF', width: '16px', height: '16px', flexShrink: 0 }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', color: '#E2E8F0', fontWeight: 500 }}>
                        📄 {doc.file_name || doc.original_filename || 'Document'}
                      </div>
                      <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.75rem', color: '#64748B', marginTop: '2px' }}>
                        {(doc.document_type || 'other').replace('_', ' ')} · {doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : 'Unknown size'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Navigation */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '28px' }}>
              <button
                onClick={() => setStep(0)}
                className="btn-outline"
                style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px' }}
              >
                <ChevronLeft size={18} /> Back
              </button>
              <button
                onClick={() => setStep(2)}
                className="btn-cyber"
                style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px' }}
              >
                Next <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 2: Business Context + Submit ── */}
        {step === 2 && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <AlignLeft size={20} color="#00D4FF" />
              <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1rem', fontWeight: 700, color: '#E2E8F0' }}>
                Review & Submit
              </h2>
            </div>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', marginBottom: '24px' }}>
              Add context to help the AI make a better assessment.
            </p>

            {/* Summary panel */}
            <div style={{
              padding: '16px 18px', borderRadius: '10px', marginBottom: '20px',
              background: 'rgba(26,58,92,0.3)', border: '1px solid rgba(26,58,92,0.6)',
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', minWidth: '120px' }}>Supplier:</span>
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#E2E8F0', fontWeight: 600 }}>
                    {getSupplierName(selectedSupplier)}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#64748B', minWidth: '120px' }}>Documents:</span>
                  <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.8rem', color: '#E2E8F0' }}>
                    {selectedDocs.length === 0
                      ? 'None selected (external sources only)'
                      : `${selectedDocs.length} document${selectedDocs.length > 1 ? 's' : ''} selected`}
                  </span>
                </div>
              </div>
            </div>

            {/* Business Context */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block', fontFamily: 'DM Sans, sans-serif',
                fontSize: '0.85rem', fontWeight: 500, color: '#94A3B8', marginBottom: '8px',
              }}>
                Business Context
                <span style={{ color: '#4A6080', fontWeight: 400, marginLeft: '6px' }}>(recommended)</span>
              </label>
              <textarea
                value={businessContext}
                onChange={e => setBusinessContext(e.target.value)}
                className="cyber-input"
                rows={4}
                placeholder="e.g. Textile manufacturer for large import deal. Verify legitimacy, check sanctions, and confirm export compliance for India-UK trade route."
                style={{ resize: 'vertical', minHeight: '100px' }}
              />
            </div>

            {/* Submit error */}
            {submitError && (
              <div style={{
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: '8px', padding: '12px 14px', marginBottom: '16px',
                color: '#EF4444', fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem',
              }}>
                ⚠️ {submitError}
              </div>
            )}

            {/* Navigation */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
              <button
                onClick={() => setStep(1)}
                className="btn-outline"
                style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px' }}
              >
                <ChevronLeft size={18} /> Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="btn-cyber"
                style={{
                  display: 'flex', alignItems: 'center', gap: '8px',
                  padding: '11px 28px', fontSize: '0.95rem',
                  opacity: submitting ? 0.7 : 1,
                  cursor:  submitting ? 'not-allowed' : 'pointer',
                }}
              >
                <Rocket size={18} />
                {submitting ? 'Starting...' : 'Start Evaluation'}
              </button>
            </div>
          </div>
        )}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}