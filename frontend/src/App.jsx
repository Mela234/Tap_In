import React, { useState } from "react";
import "./App.css";
import { Routes, Route, useNavigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
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
import SubscribeSuccess from "./subscribeSuccess";

function App() {
  const {
    user,
    loading,
    handleGoogleSignIn,
    handleEmailSignIn,
    handleEmailSignUp,
    handleLogout,
  } = useAuth();

  const [showSignIn, setShowSignIn] = useState(false);
  const [showContact, setShowContact] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showCreateAccount, setShowCreateAccount] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigate = useNavigate();

  const handleProtectedNav = (path) => {
    if (!user) {
      setShowSignIn(true);
      return;
    }
    setMobileMenuOpen(false);
    navigate(path);
  };

  if (loading) {
    return <div className="App">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="header-title" onClick={() => navigate("/")}>
          Tap In
        </h1>

        <button
          className="hamburger-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <nav className={`header-nav ${mobileMenuOpen ? "mobile-open" : ""}`}>
          <button
            className="link-btn"
            onClick={() => {
              handleProtectedNav("/archive");
              setMobileMenuOpen(false);
            }}
          >
            Archive
          </button>

          <button
            className="link-btn"
            onClick={() => {
              handleProtectedNav("/weekly");
              setMobileMenuOpen(false);
            }}
          >
            Trend Weekly
          </button>

          <button
            className="link-btn"
            onClick={() => {
              setShowAbout(true);
              setMobileMenuOpen(false);
            }}
          >
            About
          </button>

          <button
            className="link-btn"
            onClick={() => {
              setShowContact(true);
              setMobileMenuOpen(false);
            }}
          >
            Contact Us
          </button>

          {user?.isAdmin && (
            <button
              className="link-btn"
              onClick={() => {
                navigate("/admin");
                setMobileMenuOpen(false);
              }}
            >
              Admin
            </button>
          )}

          {user ? (
            <>
              <span className="user-email">{user.email}</span>
              <button
                className="link-btn"
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
              >
                Sign Out
              </button>
            </>
          ) : (
            <button
              className="link-btn"
              onClick={() => {
                setShowSignIn(true);
                setMobileMenuOpen(false);
              }}
            >
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
        <Route path="/SubscriveSuccess" element={<SubscribeSuccess />} />

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
