import { useState, useEffect } from "react";
import {
  onAuthStateChanged,
  signOut,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
} from "firebase/auth";
import { doc, setDoc, getDoc } from "firebase/firestore";
import { auth, db } from "../firebase";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Listen for auth changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        const userDocRef = doc(db, "users", firebaseUser.uid);
        const userDoc = await getDoc(userDocRef);

        setUser({
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          name: firebaseUser.displayName,
          isSubscribed: userDoc.exists() ? userDoc.data().isSubscribed : false,
        });
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Google Sign In
  const handleGoogleSignIn = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);

      const userDocRef = doc(db, "users", result.user.uid);
      const userDoc = await getDoc(userDocRef);

      if (!userDoc.exists()) {
        await setDoc(userDocRef, {
          uid: result.user.uid,
          email: result.user.email,
          isSubscribed: false,
          createdAt: new Date(),
        });
      }

      setUser({
        uid: result.user.uid,
        email: result.user.email,
        name: result.user.displayName,
        isSubscribed: userDoc.exists() ? userDoc.data().isSubscribed : false,
      });
    } catch (error) {
      console.error("Google sign-in error:", error);
      throw error;
    }
  };

  // Email Sign In
  const handleEmailSignIn = async (email, password) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);

      const userDocRef = doc(db, "users", result.user.uid);
      const userDoc = await getDoc(userDocRef);

      setUser({
        uid: result.user.uid,
        email: result.user.email,
        name: result.user.displayName,
        isSubscribed: userDoc.exists() ? userDoc.data().isSubscribed : false,
      });
    } catch (error) {
      console.error("Email sign-in error:", error);
      throw error;
    }
  };

  // Email Sign Up
  const handleEmailSignUp = async (email, password) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

      const newUser = {
        uid: userCredential.user.uid,
        email: userCredential.user.email,
        isSubscribed: false,
        createdAt: new Date(),
      };

      await setDoc(doc(db, "users", newUser.uid), newUser);
      setUser(newUser);
    } catch (error) {
      console.error("Sign-up error:", error);
      throw error;
    }
  };

  // Logout
  const handleLogout = async () => {
    try {
      await signOut(auth);
      setUser(null);
    } catch (error) {
      console.error("Logout error:", error);
      throw error;
    }
  };

  return {
    user,
    loading,
    handleGoogleSignIn,
    handleEmailSignIn,
    handleEmailSignUp,
    handleLogout,
  };
}
