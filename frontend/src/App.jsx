import React, { useState } from 'react';
import './App.css'
import { Routes, Route, useNavigate } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import Subscribe from "./Subscribe";
import HighlightCarousel from "./HighlightCarousel";
import ContactModal from "./Modals/contactModal";
import SignInModal from "./Modals/signInModal";
import CreateAccountModal from "./Modals/createAccountModal";
import AboutModal from "./Modals/aboutModal";
import TrendWeekly from "./pages/trendWeekly";
import Archive from "./pages/archive";
import { GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signInWithEmailAndPassword, createUserWithEmailAndPassword} from "firebase/auth";
import { auth, db } from "./firebase";
import { useEffect } from "react";
import { doc, setDoc } from "firebase/firestore";

function App() {
  const [user, setUser] = useState(null);
  const [showSignIn, setShowSignIn] = useState(false);
  const [dismissedSignIn, setDismissedSignIn] = useState(false);
  const [showContact, setShowContact] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showCreateAccount, setShowCreateAccount] = useState(false);

  const navigate = useNavigate();

  const handleProtectedNav = (path) => {
    if (!user && !dismissedSignIn) {
      setShowSignIn(true);
      return;
    }

    if (!user.isSubscribed) {
      navigate("/subscribe");
      return;
    }

    navigate(path);
  };
  
  const handleGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
  
      const userDocRef = doc(db, "users", result.user.uid);
      const userDoc = await getDoc(userDocRef);
  
      // If this is the first time the user logs in, create their Firestore record
      if (!userDoc.exists()) {
        await setDoc(userDocRef, {
          uid: result.user.uid,
          email: result.user.email,
          isSubscribed: false,
          createdAt: new Date(),
        });
      }
  
      // Set local state
      setUser({
        uid: result.user.uid,
        email: result.user.email,
        name: result.user.displayName,
        isSubscribed: userDoc.exists() ? userDoc.data().isSubscribed : false,
      });
  
      setShowSignIn(false);
    } catch (error) {
      console.error("Google sign-in error:", error);
      alert(error.message);
    }
  };
  

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        setUser({
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          name: firebaseUser.displayName,
          isSubscribed: false,
        });
      } else {
        setUser(null);
      }
    });
  
    return () => unsubscribe();
  }, []);

const handleEmailSignUp = async (email, password) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);

    const newUser = {
      uid: userCredential.user.uid,
      email: userCredential.user.email,
      isSubscribed: false, // default value
      createdAt: new Date(),
    };

    await setDoc(doc(db, "users", newUser.uid), newUser);

    setUser(newUser);

    alert("Account created successfully!");

    setShowCreateAccount(false);
    setShowSignIn(false);

  } catch (error) {
    if (error.code === "auth/email-already-in-use") {
      alert("This email is already registered. Please sign in.");
    } else {
      console.error("Sign-up error:", error);
      alert(error.message);
    }
  }
};

  const handleEmailSignIn = async (email, password) => {
    try {
      // Try signing in
      const result = await signInWithEmailAndPassword(auth, email, password);
  
      // User exists, sign them in
      setUser({
        uid: result.user.uid,
        email: result.user.email,
        name: result.user.displayName,
        isSubscribed: false,
      });
  
      setShowSignIn(false);
  
    } catch (error) {
      if (error.code === "auth/user-not-found") {
        alert("User not found. Please register first.");
      } else if (error.code === "auth/wrong-password") {
        alert("Incorrect password.");
      } else {
        console.error("Email sign-in error:", error);
        alert(error.message);
      }
    }
  };  

  return (
    <div className="App">
      <header className="App-header">
      <div className="header-nav">
        <button className="link-btn" onClick={() => handleProtectedNav("/archive")}>
          Archive
        </button>

        <button className="link-btn" onClick={() => handleProtectedNav("/weekly")}>
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
          <button className="link-btn" onClick={() => setShowSignIn(true)}>
            Sign In
          </button>
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
                For parents, teachers, or anyone wanting the scoop without the scroll—catch up on weekly trends here!
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
      
        <Route
          path="/subscribe"
          element={
            <Subscribe
              onSubscribe={() =>
                setUser((prev) => ({
                  ...prev,
                  isSubscribed: true,
                }))
              }
            />
          }
        />
    </Routes>
      {showAbout && <AboutModal onClose={() => setShowAbout(false)} />}
      {showContact && <ContactModal onClose={() => setShowContact(false)} />}
      {showSignIn && (<SignInModal onClose={() => {
        setShowSignIn(false);
        setDismissedSignIn(true);
        }}
        onGoogleSignIn={handleGoogle}
        onEmailSignIn={handleEmailSignIn}
        onCreateAccount={() => {
        setShowSignIn(false);
        setShowCreateAccount(true);
      }}
      />
      )}
      {showCreateAccount && (
        <CreateAccountModal 
        onClose={() => setShowCreateAccount(false)} 
        onEmailSignUp={handleEmailSignUp} 
      />
      )}
    </div>
  );
}

export default App;