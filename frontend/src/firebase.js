import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
    apiKey: "AIzaSyB8qBUmO7kYEVbbAIgKNQYQ7K4nxXJqtaY",
    authDomain: "tapin-49ea9.firebaseapp.com",
    projectId: "tapin-49ea9",
    storageBucket: "tapin-49ea9.firebasestorage.app",
    messagingSenderId: "856274469386",
    appId: "1:856274469386:web:d2011d435e9898dfd295f3",
    measurementId: "G-XL3XJRM0GZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;