function ProtectedRoute({ user, onRequireAuth, children }) {
  if (!user) {
    onRequireAuth();
    return null;
  }

  return children;
}

export default ProtectedRoute;
