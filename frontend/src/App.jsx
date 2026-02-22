import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { getUser } from './utils/auth';

// Pages
import LandingPage          from './pages/LandingPage';
import Dashboard            from './pages/Dashboard';
import SuppliersPage        from './pages/SuppliersPage';
import SupplierDetailPage   from './pages/SupplierDetailPage';
import NewEvaluationPage    from './pages/NewEvaluationPage';
import EvaluationResultsPage from './pages/EvaluationResultsPage';
import AllEvaluationsPage   from './pages/AllEvaluationsPage';
import TeamPage             from './pages/TeamPage';
import SettingsPage         from './pages/SettingsPage';
import PlatformAdminPage    from './pages/PlatformAdminPage';
import NotFoundPage         from './pages/NotFoundPage';

// ── Protected Route Component ─────────────────────────────────────
// Checks if user is logged in and has the correct role
function ProtectedRoute({ children, allowedRoles }) {
  const user = getUser();

  // Not logged in → send to landing page
  if (!user) {
    return <Navigate to="/" replace />;
  }

  // Wrong role → send to dashboard
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// ── Public Route Component ────────────────────────────────────────
// If already logged in, redirect away from landing page
function PublicRoute({ children }) {
  const user = getUser();

  if (user) {
    if (user.role === 'super_admin') return <Navigate to="/platform-admin" replace />;
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// ── Main App ──────────────────────────────────────────────────────
function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ── Public Route ── */}
        <Route
          path="/"
          element={
            <PublicRoute>
              <LandingPage />
            </PublicRoute>
          }
        />

        {/* ── Dashboard (admin, analyst, viewer) ── */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst', 'viewer']}>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* ── Suppliers ── */}
        <Route
          path="/suppliers"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst', 'viewer']}>
              <SuppliersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/suppliers/:supplierId"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst', 'viewer']}>
              <SupplierDetailPage />
            </ProtectedRoute>
          }
        />

        {/* ── Evaluations ── */}
        <Route
          path="/evaluations/new"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst']}>
              <NewEvaluationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evaluations/:evaluationId"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst', 'viewer']}>
              <EvaluationResultsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evaluations"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst', 'viewer']}>
              <AllEvaluationsPage />
            </ProtectedRoute>
          }
        />

        {/* ── Team (admin only) ── */}
        <Route
          path="/team"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <TeamPage />
            </ProtectedRoute>
          }
        />

        {/* ── Settings (all roles) ── */}
        <Route
          path="/settings"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst', 'viewer']}>
              <SettingsPage />
            </ProtectedRoute>
          }
        />

        {/* ── Platform Admin (super_admin only) ── */}
        <Route
          path="/platform-admin"
          element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <PlatformAdminPage />
            </ProtectedRoute>
          }
        />

        {/* ── 404 ── */}
        <Route path="*" element={<NotFoundPage />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;