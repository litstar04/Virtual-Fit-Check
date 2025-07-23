// Function to validate email format
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Function to handle login
function login() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value.trim();

    // Validate email format
    if (!validateEmail(email)) {
        alert("Invalid email address.");
        return;
    }

    // Check if all fields are filled
    if (!email || !password) {
        alert("Please enter both email and password.");
        return;
    }

    // Retrieve users from localStorage
    let users = JSON.parse(localStorage.getItem('users')) || [];

    // Find the user with matching credentials
    const user = users.find(user => user.email === email);

    if (user) {
        // If user exists but wrong password
        if (user.password === password) {
            // Store user gender and email in sessionStorage for later use
            sessionStorage.setItem('loggedInUserGender', user.gender);
            sessionStorage.setItem('loggedInUserEmail', user.email);

            alert(`Welcome back! Redirecting you to the recommendations...`);
            window.location.href = 'homepage.html';  // Redirects to recommendations page
        } else {
            alert("Incorrect password.");
        }
    } else {
        // If no matching user found, prompt to sign up
        let confirmSignup = confirm("This email is not registered. Would you like to sign up?");
        if (confirmSignup) {
            showSignupPage(email); // Redirect to signup and pre-fill email
        }
    }
}

// Function to show the signup page
function showSignupPage(email = '') {
   document.getElementById('loginPage').style.display = 'none';
   document.getElementById('signupPage').style.display = 'block';

   // Pre-fill email if provided
   if (email) {
       document.getElementById('signupEmail').value = email;
   }
}

// Function to check password strength (for signup)
function checkPasswordStrength() {
   const password = document.getElementById('signupPassword').value.trim();
   const strengthBar = document.getElementById('strengthBar');
   const bar = strengthBar.querySelector('div');
   
   let score = [
       /[a-z]/.test(password), // lowercase
       /[A-Z]/.test(password), // uppercase
       /\d/.test(password), // digit
       /[!@#$%^&*]/.test(password) // special character
   ].filter(Boolean).length;

   strengthBar.style.display = 'block';

   switch (score) {
      case 4:
         bar.style.width = '100%';
         bar.style.backgroundColor = 'green';
         break;
      case 3:
         bar.style.width = '75%';
         bar.style.backgroundColor = 'orange';
         break;
      case 2:
         bar.style.width = '50%';
         bar.style.backgroundColor = 'yellow';
         break;
      default:
         bar.style.width = '25%';
         bar.style.backgroundColor = 'red';
   }
}

// Function to handle signup
// During signup, after successful registration, store the gender in the session
function signup() {
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value.trim();
    const gender = document.getElementById('gender').value.trim();
 
    // Validate email format
    if (!validateEmail(email)) {
        alert("Invalid email address.");
        return;
    }
 
    // Check if all fields are filled
    if (!email || !password || !gender) {
        alert("Please fill all fields.");
        return;
    }
 
    // Check if the email is already registered
    let users = JSON.parse(localStorage.getItem('users')) || [];
    if (users.some(user => user.email === email)) {
        alert("This email is already registered.");
        return;
    }
 
    const newUser = { email, password, gender };
    
    // Save the user in localStorage
    users.push(newUser);
    localStorage.setItem('users', JSON.stringify(users));
 
    // Update session file (you'll need some backend API for this, since frontend can't modify files directly)
    fetch("/update-session", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ gender: gender })  // Send gender to update session
    });
 
    alert("Sign up successful! You can now log in.");
    login()
 }
 function getUserGender() {
    const gender = localStorage.getItem('loggedInUserGender');
    return gender ? gender : 'Male'; // Default to 'Male' if no gender is found
}

// Function to send gender to backend and get recommendations
function getRecommendations() {
    const userGender = getUserGender();  // Retrieve gender from localStorage

    // Send gender to backend via a POST request
    fetch('/get-recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gender: userGender }),  // Send gender as JSON
    })
    .then(response => response.json())
    .then(data => {
        // Process and display the recommendations
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
