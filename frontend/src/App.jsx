import React, { useState } from "react";
import "./App.css";
import { Routes, Route, useNavigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth"; // ← Import the hook
import ProtectedRoute from "./ProtectedRoute";
import Subscribe from "./Subscribe";
import AdminCreateTrend from "./pages/adminPage";
import AdminProtectedRoute from "./adminProtectedRoute";
import HighlightCarousel from "./HighlightCarousel";
import ContactModal from "./Modals/contactModal";
import SignInModal from "./Modals/signInModal";
import CreateAccountModal from "./Modals/createAccountModal";
import AboutModal from "./Modals/aboutModal";
import TrendWeekly from "./pages/trendWeekly";
import Archive from "./pages/archive";

function App() {
  // Use the custom hook
  const {
    user,
    loading,
    handleGoogleSignIn,
    handleEmailSignIn,
    handleEmailSignUp,
    handleLogout,
  } = useAuth();

  const [showSignIn, setShowSignIn] = useState(false);
  const [dismissedSignIn, setDismissedSignIn] = useState(false);
  const [showContact, setShowContact] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showCreateAccount, setShowCreateAccount] = useState(false);
  console.log("this is the user", user);

  const navigate = useNavigate();

  const handleProtectedNav = (path) => {
    if (!user && !dismissedSignIn) {
      setShowSignIn(true);
      return;
    }

    if (!user?.isSubscribed) {
      navigate("/subscribe");
      return;
    }

    navigate(path);
  };

  if (loading) {
    return <div className="App">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-nav">
          <button
            className="link-btn"
            onClick={() => handleProtectedNav("/archive")}
          >
            Archive
          </button>

          <button
            className="link-btn"
            onClick={() => handleProtectedNav("/weekly")}
          >
            Trend Weekly
          </button>
        </div>

        <h1 className="header-title">Tap In</h1>

        <nav className="header-nav">
          <button className="link-btn" onClick={() => setShowAbout(true)}>
            About
          </button>
          <button className="link-btn" onClick={() => setShowContact(true)}>
            Contact Us
          </button>
          {/* Admin button */}
          {user?.isAdmin && (
            <button
              className="link-btn"
              onClick={() => navigate("/admin")}
            >
              Admin
            </button>
          )}


          {/* Conditional rendering */}
          {user ? (
            <>
              <span className="user-email">{user.email}</span>
              <button className="link-btn" onClick={handleLogout}>
                Sign Out
              </button>
            </>
          ) : (
            <button className="link-btn" onClick={() => setShowSignIn(true)}>
              Sign In
            </button>
          )}
        </nav>
      </header>

      <Routes>
        <Route
          path="/"
          element={
            <main className="App-body">
              <p className="firstLine">All the trends</p>
              <p className="secondLine">With zero scrolling</p>
              <p className="description">
                For parents, teachers, or anyone wanting the scoop without the
                scroll—catch up on weekly trends here!
              </p>
              <HighlightCarousel />
            </main>
          }
        />

        <Route
          path="/weekly"
          element={
            <ProtectedRoute
              user={user}
              onRequireAuth={() => setShowSignIn(true)}
            >
              <TrendWeekly />
            </ProtectedRoute>
          }
        />

        <Route
          path="/archive"
          element={
            <ProtectedRoute
              user={user}
              onRequireAuth={() => setShowSignIn(true)}
            >
              <Archive />
            </ProtectedRoute>
          }
        />

        <Route path="/subscribe" element={<Subscribe user={user} />} />

        <Route
            path="/admin"
            element={
              <AdminProtectedRoute user={user}>
                <AdminCreateTrend />
              </AdminProtectedRoute>
            }
        />

      </Routes>

      {showAbout && <AboutModal onClose={() => setShowAbout(false)} />}
      {showContact && <ContactModal onClose={() => setShowContact(false)} />}
      {showSignIn && (
        <SignInModal
          onClose={() => {
            setShowSignIn(false);
            setDismissedSignIn(true);
          }}
          onGoogleSignIn={async () => {
            await handleGoogleSignIn();
            setShowSignIn(false);
          }}
          onEmailSignIn={async (email, password) => {
            await handleEmailSignIn(email, password);
            setShowSignIn(false);
          }}
          onCreateAccount={() => {
            setShowSignIn(false);
            setShowCreateAccount(true);
          }}
        />
      )}
      {showCreateAccount && (
        <CreateAccountModal
          onClose={() => setShowCreateAccount(false)}
          onEmailSignUp={async (email, password) => {
            await handleEmailSignUp(email, password);
            setShowCreateAccount(false);
          }}
        />
      )}
    </div>
  );
}

export default App;
