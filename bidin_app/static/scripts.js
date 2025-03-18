// Improved interactivity
document.addEventListener("DOMContentLoaded", function () {
  console.log("Bidin App is ready!");

  const registerForm = document.querySelector("form[action='/auth/register']");
  if (registerForm) {
    registerForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent actual submission for demo
      alert("✅ Registration form submitted!");
      // registerForm.submit(); // Uncomment to allow real submission
    });
  }

  const loginForm = document.querySelector("form[action='/auth/login']");
  if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent actual submission for demo
      alert("✅ Login form submitted!");
      // loginForm.submit(); // Uncomment to allow real submission
    });
  }
});
