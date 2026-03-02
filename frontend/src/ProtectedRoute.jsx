import { useEffect } from "react";

function ProtectedRoute({ user, onRequireAuth, children }) {
  useEffect(() => {
    if (!user) {
      onRequireAuth();
    }
  }, [user, onRequireAuth]);

  if (!user) {
    return null;
  }

  return children;
}

export default ProtectedRoute;
