const API_BASE_URL = "http://localhost:8000";

// Register Form Submission
document.getElementById("register-form").addEventListener("submit", async function (event) {
  event.preventDefault();

  // Get input values from the form
  const firstName = document.getElementById("first-name").value;
  const lastName = document.getElementById("last-name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const cityName = document.getElementById("city").value;

  // Prepare data to be sent in the request
  const registerData = {
      first_name: firstName,
      last_name: lastName,
      email: email,
      password: password,
      city_name: cityName
  };

  try {
      // Send POST request to the /register endpoint
      const response = await fetch(`${API_BASE_URL}/register`, {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify(registerData) // Convert the data to JSON format
      });

      // Handle the response
      if (response.ok) {
          const responseData = await response.json();
          // Display success message or handle success logic
          document.getElementById("message").innerText = `Registration successful! Welcome, ${responseData.first_name}`;
          document.getElementById("message").style.color = "green";
      } else {
          const errorData = await response.json();
          // Display error message if registration failed
          document.getElementById("message").innerText = `Error: ${errorData.detail}`;
          document.getElementById("message").style.color = "red";
      }
  } catch (error) {
      // Handle any network or unexpected errors
      document.getElementById("message").innerText = `Network error: ${error.message}`;
      document.getElementById("message").style.color = "red";
  }
});

// Login Form Submission
document.getElementById("login-form").addEventListener("submit", async function (event) {
  event.preventDefault();

  // Get input values from the form
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  // Prepare data to be sent in the request
  const loginData = {
      username: email, // 'username' is used to match FastAPI's OAuth2PasswordRequestForm
      password: password
  };

  try {
      // Send POST request to the /token endpoint
      const response = await fetch(`${API_BASE_URL}/token`, {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded" // Content type expected by FastAPI
          },
          body: new URLSearchParams(loginData) // Convert the data to URL-encoded format
      });

      // Handle the response
      if (response.ok) {
          const responseData = await response.json();
          // Store the access token in local storage (or session storage)
          localStorage.setItem("access_token", responseData.access_token);
          document.getElementById("message").innerText = "Login successful!";
          document.getElementById("message").style.color = "green";
          // Optionally, you can redirect the user or show the subscription section
          document.getElementById("subscribe-section").style.display = "block"; // Show subscription management
      } else {
          const errorData = await response.json();
          // Display error message if login failed
          document.getElementById("message").innerText = `Error: ${errorData.detail}`;
          document.getElementById("message").style.color = "red";
      }
  } catch (error) {
      // Handle any network or unexpected errors
      document.getElementById("message").innerText = `Network error: ${error.message}`;
      document.getElementById("message").style.color = "red";
  }
});

// Unsubscribe Button
document.getElementById("unsubscribe-button").addEventListener("click", async function () {
  const token = localStorage.getItem("access_token"); // Retrieve the stored access token

  if (!token) {
      document.getElementById("subscription-message").innerText = "You need to log in to unsubscribe.";
      document.getElementById("subscription-message").style.color = "red";
      return;
  }

  try {
      // Send POST request to the /unsubscribe endpoint with the token
      const response = await fetch(`${API_BASE_URL}/unsubscribe`, {
          method: "POST",
          headers: {
              "Authorization": `Bearer ${token}`, // Include the token in the Authorization header
              "Content-Type": "application/json" // Optional: Specify content type
          }
      });

      // Handle the response
      if (response.ok) {
          const responseData = await response.json();
          document.getElementById("subscription-message").innerText = responseData.detail;
          document.getElementById("subscription-message").style.color = "green";
      } else {
          const errorData = await response.json();
          document.getElementById("subscription-message").innerText = `Error: ${errorData.detail}`;
          document.getElementById("subscription-message").style.color = "red";
      }
  } catch (error) {
      // Handle any network or unexpected errors
      document.getElementById("subscription-message").innerText = `Network error: ${error.message}`;
      document.getElementById("subscription-message").style.color = "red";
  }
});

// Resubscribe Button
document.getElementById("subscribe-button").addEventListener("click", async function () {
  const token = localStorage.getItem("access_token"); // Retrieve the stored access token

  if (!token) {
      document.getElementById("subscription-message").innerText = "You need to log in to resubscribe.";
      document.getElementById("subscription-message").style.color = "red";
      return;
  }

  try {
      // Send POST request to the /resubscribe endpoint with the token
      const response = await fetch(`${API_BASE_URL}/resubscribe`, {
          method: "POST",
          headers: {
              "Authorization": `Bearer ${token}`, // Include the token in the Authorization header
              "Content-Type": "application/json" // Optional: Specify content type
          }
      });

      // Handle the response
      if (response.ok) {
          const responseData = await response.json();
          document.getElementById("subscription-message").innerText = responseData.detail;
          document.getElementById("subscription-message").style.color = "green";
      } else {
          const errorData = await response.json();
          document.getElementById("subscription-message").innerText = `Error: ${errorData.detail}`;
          document.getElementById("subscription-message").style.color = "red";
      }
  } catch (error) {
      // Handle any network or unexpected errors
      document.getElementById("subscription-message").innerText = `Network error: ${error.message}`;
      document.getElementById("subscription-message").style.color = "red";
  }
});
