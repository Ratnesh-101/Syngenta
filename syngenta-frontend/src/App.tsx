import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { LangProvider } from './context/LangContext'
import { useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Register from './pages/Register'
import Today from './pages/rep/Today'
import GrowerDetail from './pages/rep/GrowerDetail'
import Anomalies from './pages/rep/Anomalies'
import Devices from './pages/rep/Devices'
import Overview from './pages/manager/Overview'
import Reps from './pages/manager/Reps'
import RepDetail from './pages/manager/RepDetail'

function RoleRedirect() {
  const { rep, isLoading } = useAuth()
  if (isLoading) {
    return (
      <div className="min-h-screen bg-forest-50 dark:bg-forest-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-forest-700 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (!rep) return <Navigate to="/login" replace />
  if (rep.role === 'rep') return <Navigate to="/today" replace />
  return <Navigate to="/manager" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <LangProvider>
          <AuthProvider>
            <Routes>
              <Route path="/" element={<RoleRedirect />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route element={<ProtectedRoute requiredRole="rep" />}>
                <Route path="/today" element={<Today />} />
                <Route path="/grower/:entity_id" element={<GrowerDetail />} />
                <Route path="/anomalies" element={<Anomalies />} />
                <Route path="/devices" element={<Devices />} />
              </Route>
              <Route element={<ProtectedRoute requiredRole="manager" />}>
                <Route path="/manager" element={<Overview />} />
                <Route path="/manager/reps" element={<Reps />} />
                <Route path="/manager/reps/:rep_id" element={<RepDetail />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AuthProvider>
        </LangProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}