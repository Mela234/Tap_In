import { Navigate } from "react-router-dom";

function AdminProtectedRoute({ user, children }) {
  if (!user) {
    // Not logged in
    return <Navigate to="/" replace />;
  }

  if (!user.isAdmin) {
    // Logged in but not an admin
    return <Navigate to="/" replace />;
  }

  return children;
}

export default AdminProtectedRoute;
