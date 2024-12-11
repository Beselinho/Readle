import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAm3DxirtchWD6ttc74CSTGHiivh-M4qEY",
  authDomain: "readle-36c98.firebaseapp.com", 
  projectId: "readle-36c98",
  storageBucket: "readle-36c98.firebasestorage.app",
  messagingSenderId: "110706883935",
  appId: "1:110706883935:web:b5e5319865791507f70aea",
  measurementId: "G-B8TYWZGVVW"
};

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };