import { auth, provider } from "./firebase-config.js";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  sendPasswordResetEmail,
  updateProfile
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

/* == UI - Elements == */
const signInWithGoogleButtonEl = document.getElementById("sign-in-with-google-btn");
const signUpWithGoogleButtonEl = document.getElementById("sign-up-with-google-btn");
const emailInputEl = document.getElementById("email-input");
const passwordInputEl = document.getElementById("password-input");
// New username input element
const usernameInputEl = document.getElementById("username-input");

const signInButtonEl = document.getElementById("sign-in-btn");
const createAccountButtonEl = document.getElementById("create-account-btn");
const emailForgotPasswordEl = document.getElementById("email-forgot-password");
const forgotPasswordButtonEl = document.getElementById("forgot-password-btn");

const errorMsgUsername = document.getElementById("username-error-message");
const errorMsgEmail = document.getElementById("email-error-message");
const errorMsgPassword = document.getElementById("password-error-message");
const errorMsgGoogleSignIn = document.getElementById("google-signin-error-message");

/* == UI - Event Listeners == */
if (signInWithGoogleButtonEl && signInButtonEl) {
  signInWithGoogleButtonEl.addEventListener("click", authSignInWithGoogle);
  signInButtonEl.addEventListener("click", authSignInWithEmail);
}

if (createAccountButtonEl) {
  createAccountButtonEl.addEventListener("click", authCreateAccountWithEmail);
}

if (signUpWithGoogleButtonEl) {
  signUpWithGoogleButtonEl.addEventListener("click", authSignUpWithGoogle);
}

if (forgotPasswordButtonEl) {
  forgotPasswordButtonEl.addEventListener("click", resetPassword);
}

/* === Main Code === */

/* = Functions - Firebase - Authentication = */

// Function to sign in with Google authentication
async function authSignInWithGoogle() {
  provider.setCustomParameters({
    prompt: "select_account"
  });

  try {
    const result = await signInWithPopup(auth, provider);
    if (!result || !result.user) {
      throw new Error("Authentication failed: No user data returned.");
    }
    const user = result.user;
    const email = user.email;
    if (!email) {
      throw new Error("Authentication failed: No email address returned.");
    }
    // Get the latest token
    const idToken = await user.getIdToken(true);
    loginUser(user, idToken);
  } catch (error) {
    // Log the error for debugging purposes
    console.error("Error during sign-in with Google:", error);
    // Optionally update UI with error message:
    errorMsgGoogleSignIn.textContent = error.message;
  }
}

// Function to create new account with Google auth - will also sign in existing users
async function authSignUpWithGoogle() {
  provider.setCustomParameters({
    prompt: "select_account"
  });

  try {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    const email = user.email;
    const idToken = await user.getIdToken(true);
    loginUser(user, idToken);
  } catch (error) {
    console.error("Error during Google signup:", error.message);
    errorMsgGoogleSignIn.textContent = error.message;
  }
}

function authSignInWithEmail() {
  const email = emailInputEl.value;
  const password = passwordInputEl.value;

  signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      const user = userCredential.user;
      user.getIdToken().then(function (idToken) {
        loginUser(user, idToken);
      });
      console.log("User signed in:", user);
    })
    .catch((error) => {
      const errorCode = error.code;
      console.error("Error code during email sign-in:", errorCode);
      if (errorCode === "auth/invalid-email") {
        errorMsgEmail.textContent = "Invalid email";
      } else if (errorCode === "auth/invalid-credential") {
        errorMsgPassword.textContent = "Login failed - invalid email or password";
      } else {
        errorMsgEmail.textContent = error.message;
      }
    });
}

async function authCreateAccountWithEmail() {
  const username = usernameInputEl.value.trim();
  const email = emailInputEl.value;
  const password = passwordInputEl.value;

  if (!username) {
    errorMsgUsername.textContent = "Username is required";
    return;
  }

  try {
    console.log("Attempting account creation for:", email);
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Update the user's profile with the provided username.
    await updateProfile(user, { displayName: username });

    // Force a token refresh to include the updated displayName.
    const idToken = await user.getIdToken(true);

    // Send the token (and displayName from user) to your backend.
    await loginUser(user, idToken);

    // Clear the authentication input fields.
    clearAuthFields();
  } catch (error) {
    console.error("Error during account creation:", error);
    errorMsgEmail.textContent = error.message; // Display the error
  }
}

function resetPassword() {
  const emailToReset = emailForgotPasswordEl.value;
  clearInputField(emailForgotPasswordEl);
  sendPasswordResetEmail(auth, emailToReset)
    .then(() => {
      const resetFormView = document.getElementById("reset-password-view");
      const resetSuccessView = document.getElementById("reset-password-confirmation-page");
      resetFormView.style.display = "none";
      resetSuccessView.style.display = "block";
    })
    .catch((error) => {
      console.error("Error during password reset:", error);
      // Optionally update UI with error message
    });
}

/**
 * Helper function to add a delay.
 * @param {number} ms - Number of milliseconds to delay.
 */
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Modified loginUser function with an added delay.
async function loginUser(user, idToken, retryCount = 0) {
  console.log("Attempt login with token (preview):", idToken.substring(0, 50));

  // Adding a delay before making the fetch call
  await delay(1000);

  try {
    const response = await fetch("/auth", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${idToken}`
      },
      credentials: "same-origin",
      body: JSON.stringify({
        displayName: user.displayName || ""
      })
    });

    console.log("Response status:", response.status);

    if (response.ok) {
      const data = await response.json();
      console.log("Successful response:", data);
      // Manually redirect if needed.
      window.location.href = data.redirect || "/";
    } else if (response.status === 401 && retryCount < 1) {
      console.warn("Received 401 error. Refreshing token and retrying login...");
      // Adding a delay before retrying
      await delay(1000);
      const newToken = await user.getIdToken(true);
      await loginUser(user, newToken, retryCount + 1);
    } else {
      console.error("Failed to login. Server responded with:", response.status);
    }
  } catch (error) {
    console.error("Error with Fetch operation:", error);
  }
}

/* = Functions - UI = */
function clearInputField(field) {
  field.value = "";
}

function clearAuthFields() {
  clearInputField(emailInputEl);
  clearInputField(passwordInputEl);
  clearInputField(usernameInputEl); // Clear username as well
}
