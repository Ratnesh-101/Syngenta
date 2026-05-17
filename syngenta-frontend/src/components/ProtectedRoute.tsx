import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  requiredRole?: 'rep' | 'manager';
}

export default function ProtectedRoute({ requiredRole }: ProtectedRouteProps) {
  const { rep, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-forest-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-forest-700 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-3 text-sm text-sage-500 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (!rep) return <Navigate to="/login" replace />;

  if (requiredRole === 'manager' && rep.role === 'rep') {
    return <Navigate to="/today" replace />;
  }

  if (requiredRole === 'rep' && (rep.role === 'manager' || rep.role === 'admin')) {
    return <Navigate to="/manager" replace />;
  }

  return <Outlet />;
}
