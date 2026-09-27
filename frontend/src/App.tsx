import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';

// Pages
import { PublicHome } from './pages/PublicHome';
import { PublicVerify } from './pages/PublicVerify';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

// Trader Pages
import { TraderDashboard } from './pages/TraderDashboard';
import { TraderInstruments } from './pages/TraderInstruments';
import { TraderApplications } from './pages/TraderApplications';
import { TraderCertificates } from './pages/TraderCertificates';

// Admin Pages
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminModelCatalog } from './pages/AdminModelCatalog';
import { AdminDataQuality } from './pages/AdminDataQuality';
import { AdminApplications } from './pages/AdminApplications';
import { AdminRules } from './pages/AdminRules';
import { AdminOCR } from './pages/AdminOCR';
import { AdminAuditLogs } from './pages/AdminAuditLogs';

// LMO Pages
import { LMODashboard } from './pages/LMODashboard';
import { LMOInspectionExecution } from './pages/LMOInspectionExecution';

const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoles?: string[] }> = ({ children, allowedRoles }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-xs text-slate-500">Loading LegalMet Verify session...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<PublicHome />} />
              <Route path="/verify/:certNo" element={<PublicVerify />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Trader Routes */}
              <Route path="/trader/dashboard" element={<ProtectedRoute allowedRoles={['TRADER', 'ADMIN']}><TraderDashboard /></ProtectedRoute>} />
              <Route path="/trader/instruments" element={<ProtectedRoute allowedRoles={['TRADER', 'ADMIN']}><TraderInstruments /></ProtectedRoute>} />
              <Route path="/trader/applications" element={<ProtectedRoute allowedRoles={['TRADER', 'ADMIN']}><TraderApplications /></ProtectedRoute>} />
              <Route path="/trader/certificates" element={<ProtectedRoute allowedRoles={['TRADER', 'ADMIN']}><TraderCertificates /></ProtectedRoute>} />

              {/* Admin Routes */}
              <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>} />
              <Route path="/admin/models" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminModelCatalog /></ProtectedRoute>} />
              <Route path="/admin/data-quality" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDataQuality /></ProtectedRoute>} />
              <Route path="/admin/applications" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminApplications /></ProtectedRoute>} />
              <Route path="/admin/rules" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminRules /></ProtectedRoute>} />
              <Route path="/admin/ocr" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminOCR /></ProtectedRoute>} />
              <Route path="/admin/audit" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminAuditLogs /></ProtectedRoute>} />

              {/* LMO Routes */}
              <Route path="/lmo/dashboard" element={<ProtectedRoute allowedRoles={['LMO', 'ADMIN']}><LMODashboard /></ProtectedRoute>} />
              <Route path="/lmo/inspections/:id/verification" element={<ProtectedRoute allowedRoles={['LMO', 'ADMIN']}><LMOInspectionExecution /></ProtectedRoute>} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};
