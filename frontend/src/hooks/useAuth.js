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
      console.log(
        "🔥 Firebase auth state:",
        firebaseUser?.email || "not logged in",
      );

      if (firebaseUser) {
        try {
          const userDocRef = doc(db, "users", firebaseUser.uid);
          const userDoc = await getDoc(userDocRef);

          console.log("📄 Firestore doc exists:", userDoc.exists());
          console.log("📄 Firestore data:", userDoc.data());

          setUser({
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            name: firebaseUser.displayName,
            isSubscribed: userDoc.exists()
              ? userDoc.data().isSubscribed
              : false,
            isAdmin: userDoc.exists() ? userDoc.data().isAdmin : false,
          });
        } catch (error) {
          console.error("❌ Firestore error in auth listener:", error);

          // Still set user from Firebase auth even if Firestore fails
          setUser({
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            name: firebaseUser.displayName,
            isSubscribed: false,
            isAdmin: false,
          });
        }
      } else {
        console.log("👤 No user logged in");
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

      // First time user - create Firestore document
      if (!userDoc.exists()) {
        console.log("🆕 New Google user - creating Firestore document");
        await setDoc(userDocRef, {
          uid: result.user.uid,
          email: result.user.email,
          isSubscribed: false,
          isAdmin: false,
          createdAt: new Date(),
        });
      }

      // Fetch updated doc after potential creation
      const updatedDoc = await getDoc(userDocRef);
      console.log("✅ Google sign in - user data:", updatedDoc.data());

      setUser({
        uid: result.user.uid,
        email: result.user.email,
        name: result.user.displayName,
        isSubscribed: updatedDoc.exists()
          ? updatedDoc.data().isSubscribed
          : false,
        isAdmin: updatedDoc.exists() ? updatedDoc.data().isAdmin : false,
      });
    } catch (error) {
      console.error("❌ Google sign-in error:", error);
      throw error;
    }
  };

  // Email Sign In
  const handleEmailSignIn = async (email, password) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);

      const userDocRef = doc(db, "users", result.user.uid);
      const userDoc = await getDoc(userDocRef);

      console.log("✅ Email sign in - user data:", userDoc.data());

      setUser({
        uid: result.user.uid,
        email: result.user.email,
        name: result.user.displayName,
        isSubscribed: userDoc.exists() ? userDoc.data().isSubscribed : false,
        isAdmin: userDoc.exists() ? userDoc.data().isAdmin : false,
      });
    } catch (error) {
      console.error("❌ Email sign-in error:", error);
      throw error;
    }
  };

  // Email Sign Up
  const handleEmailSignUp = async (email, password) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password,
      );

      const newUser = {
        uid: userCredential.user.uid,
        email: userCredential.user.email,
        isSubscribed: false,
        isAdmin: false,
        createdAt: new Date(),
      };

      console.log("🆕 New email user - creating Firestore document");
      await setDoc(doc(db, "users", newUser.uid), newUser);

      console.log("✅ Email sign up - user created:", newUser);
      setUser(newUser);
    } catch (error) {
      console.error("❌ Sign-up error:", error);
      throw error;
    }
  };

  // Logout
  const handleLogout = async () => {
    try {
      await signOut(auth);
      console.log("👋 User logged out");
      setUser(null);
    } catch (error) {
      console.error("❌ Logout error:", error);
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
