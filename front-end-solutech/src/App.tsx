/**
 * =============================================================================
 * APPLICATION PRINCIPALE SOLUTECH v2.0
 * Router, authentification, et structure globale
 * =============================================================================
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from '@/context/AppContext';
import { Layout } from '@/components/Layout';
import { Auth } from '@/components/Auth';
import { Dashboard } from '@/components/Dashboard';
import { StudentManagement } from '@/components/StudentManagement';
import { TeacherManagement } from '@/components/TeacherManagement';
import { GradeManagement } from '@/components/GradeManagement';
import { AttendanceTracker } from '@/components/AttendanceTracker';
import { Statistics } from '@/components/Statistics';
import { Settings } from '@/components/Settings';
import { LandingPage } from '@/components/LandingPage';

/** Route protégée par authentification */
function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useApp();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

/** Composant racine avec routing */
function AppRoutes() {
  const { isAuthenticated } = useApp();

  return (
    <Routes>
      {/* Routes publiques */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Auth />} />
      
      {/* Routes protégées */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/eleves"
        element={
          <PrivateRoute>
            <Layout>
              <StudentManagement />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/enseignants"
        element={
          <PrivateRoute>
            <Layout>
              <TeacherManagement />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/notes"
        element={
          <PrivateRoute>
            <Layout>
              <GradeManagement />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/presences"
        element={
          <PrivateRoute>
            <Layout>
              <AttendanceTracker />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/statistiques"
        element={
          <PrivateRoute>
            <Layout>
              <Statistics />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/parametres"
        element={
          <PrivateRoute>
            <Layout>
              <Settings />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AppProvider>
  );
}
