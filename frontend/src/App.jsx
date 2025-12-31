import React, { useState } from 'react';
import './App.css'
import HighlightsCarousel from "./HighlightCarousel";
import ContactModal from "./Modals/contactModal";
import SignInModal from "./Modals/signInModal";
import CreateAccountModal from "./Modals/createAccountModal";
import AboutModal from "./Modals/aboutModal";

function App() {
  const [showContact, setShowContact] = useState(false);
  const [showSignIn, setShowSignIn] = useState(false);
  const [showCreateAccount, setShowCreateAccount] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-nav">
          <a href="#trends">Archive</a>
          <a href="#week">Trend Weekly</a>
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

      <main className="App-body">
        <p className="firstLine">All the trends</p>
        <p className="secondLine">With zero scrolling</p>
        <p className="description">
          For parents, teachers, or anyone wanting the scoop without the scroll—catch up on weekly trends here!
        </p>

        <HighlightsCarousel />
      </main>

      {showAbout && <AboutModal onClose={() => setShowAbout(false)} />}
      {showContact && <ContactModal onClose={() => setShowContact(false)} />}
      {showSignIn && (
        <SignInModal
          onClose={() => setShowSignIn(false)}
          onCreateAccount={() => {
            setShowSignIn(false);
            setShowCreateAccount(true);
          }}
        />
      )}
      {showCreateAccount && (
        <CreateAccountModal onClose={() => setShowCreateAccount(false)} />
      )}
    </div>
  );
}

export default App;