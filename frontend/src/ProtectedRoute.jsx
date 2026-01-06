import { Navigate } from "react-router-dom";

function ProtectedRoute({ user, onRequireAuth, children }) {
  if (!user) {
    onRequireAuth();
    return null;
  }

  if (!user.isSubscribed) {
    return <Navigate to="/subscribe" replace />;
  }

  return children;
}

export default ProtectedRoute;
