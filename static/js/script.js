// DOM Content Loaded - FIXED VERSION
document.addEventListener("DOMContentLoaded", function () {
  console.log("🔵 DOM loaded, initializing app...");
  initializeApp();
});

const backendURL =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:10000" // ✅ Flask is running here
    : "https://cleanifyservice.com";

console.log("Using backend URL:", backendURL);

// TEST: Check if user is logged in
function checkLoginStatus() {
  fetch(`${backendURL}/check-auth`, {
    method: "GET",
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Login status:", data);
      if (data.logged_in) {
        console.log("✅ User is logged in as:", data.user);
        // Update UI to show logged-in state
        updateLoginUI(data.user);
      } else {
        console.log("❌ User is NOT logged in");
      }
    })
    .catch((error) => console.error("Auth check failed:", error));
}

// Helper to update UI based on login status
function updateLoginUI(user) {
  const loginBtn = document.getElementById("login-btn");
  const userMenu = document.getElementById("user-menu");

  if (loginBtn && userMenu) {
    loginBtn.style.display = "none";
    userMenu.style.display = "block";
    document.getElementById("user-name").textContent = user.name;
  }
}

function initializeApp() {
  console.log("🔵 Initializing all components...");

  // Initialize components in order
  initNavbar();
  initScrollAnimations();
  initSmoothScrolling();
  // Initialize forms with error handling
  try {
    initBookingModal();
  } catch (error) {
    console.log("⚠️ Booking modal init failed, will retry:", error);
  }

  try {
    initContactForm();
  } catch (error) {
    console.log("⚠️ Contact form init failed:", error);
  }

  // Set minimum date for booking to today
  const today = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("date");
  if (dateInput) {
    dateInput.min = today;
  }

  console.log("✅ App initialization complete");
}

// Contact form initialization - ADD THIS FUNCTION
function initContactForm() {
  const contactForm = document.getElementById("contactForm");
  if (contactForm) {
    contactForm.addEventListener("submit", handleContactSubmission);
    console.log("✅ Contact form event listener attached");
  } else {
    console.log("⚠️ Contact form not found on this page");
  }
}

// Navigation functionality
function initNavbar() {
  const navbar = document.querySelector(".navbar");
  const toggler = document.querySelector(".navbar-toggler");
  const collapse = document.getElementById("navbarNavDropdown");
  const navLinks = document.querySelectorAll(".nav-link");

  if (!toggler || !collapse) return;

  const bsCollapse =
    bootstrap.Collapse.getInstance(collapse) ||
    new bootstrap.Collapse(collapse, { toggle: false });

  /* =========================
     1️⃣ Hamburger ↔ Close icon
     ========================= */
collapse.addEventListener("shown.bs.collapse", () => {
  toggler.classList.add("open");
});

collapse.addEventListener("hidden.bs.collapse", () => {
  toggler.classList.remove("open");
});


  /* =========================
     2️⃣ Close on nav link click (mobile)
     ========================= */
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth < 992 && collapse.classList.contains("show")) {
        bsCollapse.hide();
      }
    });
  });

  /* =========================
     3️⃣ Close when clicking outside
     ========================= */
  document.addEventListener("click", (e) => {
    if (
      window.innerWidth < 992 &&
      collapse.classList.contains("show") &&
      !navbar.contains(e.target)
    ) {
      bsCollapse.hide();
    }
  });

  /* =========================
     4️⃣ Close on ESC key
     ========================= */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && collapse.classList.contains("show")) {
      bsCollapse.hide();
    }
  });

  /* =========================
     5️⃣ Sticky navbar on scroll
     ========================= */
  window.addEventListener("scroll", () => {
    navbar.classList.toggle("scrolled", window.scrollY > 100);
  });
}

// Smooth scrolling for anchor links - FIXED VERSION
function initSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");

      // Skip if it's just '#' (dropdown toggles, empty links)
      if (href === "#" || href === "") {
        return; // Let Bootstrap handle dropdowns and other functionality
      }

      // Only prevent default and handle smooth scrolling for actual section links
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

        // Close mobile menu if open
        const navMenu = document.getElementById("nav-menu");
        const navToggle = document.getElementById("nav-toggle");
        if (navMenu && navMenu.classList.contains("active")) {
          navMenu.classList.remove("active");
          if (navToggle) navToggle.classList.remove("active");
        }
      }
    });
  });
}

// Scroll animations
function initScrollAnimations() {
  const fadeElements = document.querySelectorAll(".fade-in");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    },
  );

  fadeElements.forEach((element) => {
    observer.observe(element);
  });
}

// Remove this duplicate function - DELETE THESE LINES:
/*
function handleBookingSubmission(e) {
  e.preventDefault();
  // Add your booking form submission logic here
  console.log("Booking form submitted");
  closeBookingModal();
}
*/

// Keep only this full implementation:
// UPDATED Booking Submission Function
async function handleBookingSubmission(e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  // Basic validation
  if (!validateBookingForm(data)) {
    return;
  }

  // Show loading state
  const submitBtn = form.querySelector(".submit-btn");
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Booking...";
  submitBtn.disabled = true;

  try {
    console.log("📤 Sending booking request to:", `${backendURL}/book`);

    // FIX: Use the SAME backendURL variable
    const response = await fetch(`${backendURL}/book`, {
      method: "POST",
      credentials: "include", // 🔐 REQUIRED for session cookies
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    console.log("📥 Response status:", response.status);

    // Check if response is JSON
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error(
        "Server returned non-JSON response:",
        text.substring(0, 200),
      );
      throw new Error("Server error: Invalid response format");
    }

    const result = await response.json();
    console.log("📦 Response data:", result);

    // 🔐 Login required handling
    if (response.status === 401 && result.error === "LOGIN_REQUIRED") {
      showAlert("Please login to book a service", "warning");

      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);

      return;
    }

    if (response.ok && result.success) {
      // Success - show confirmation in modal
      form.innerHTML = `
        <div class="success-message">
          <i class="fas fa-check-circle" style="font-size: 48px; color: #28a745; margin-bottom: 15px;"></i>
          <h3>Booking Confirmed!</h3>
          <p>${result.message}</p>
          <p><strong>Booking ID:</strong> ${result.booking_id}</p>
          <p style="margin-top: 15px; font-size: 14px; color: #666;">
            We've sent a confirmation to the admin. You'll be contacted shortly.
          </p>
          <button onclick="closeBookingModal()" style="margin-top: 15px; padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
            Close
          </button>
        </div>
      `;
    } else {
      // Error from server
      showAlert(result.error || "Booking failed. Please try again.", "error");
    }
  } catch (error) {
    console.error("❌ Error:", error);
    if (error.message.includes("JSON") || error.message.includes("Network")) {
      showAlert(
        "Server error. Please try again later or contact support.",
        "error",
      );
    } else {
      showAlert(error.message || "Booking failed. Please try again.", "error");
    }
  } finally {
    // Reset button state only if not successful
    if (!form.querySelector(".success-message")) {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  }
}

// Fix the initialization to handle dynamic modal loading
function initBookingModal() {
  const modal = document.getElementById("bookingModal");
  const form = document.getElementById("bookingForm");

  if (!modal || !form) {
    console.log("Booking modal or form not found, will retry when modal opens");
    return;
  }

  // Close modal when clicking outside
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      closeBookingModal();
    }
  });

  // Close modal with Escape key
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal.style.display === "block") {
      closeBookingModal();
    }
  });

  // Form submission - only add if not already added
  if (!form.hasBookingListener) {
    form.addEventListener("submit", handleBookingSubmission);
    form.hasBookingListener = true;
    console.log("✅ Booking form event listener attached");
  }
}

// Enhanced openBookingModal to ensure form is initialized
// Enhanced openBookingModal with login check
function openBookingModal(service = "", packageInfo = "") {
  // First check if user is logged in
  fetch(`${backendURL}/check-auth`, {
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.logged_in) {
        // User not logged in, redirect to login
        showAlert("Please login to book a service", "warning");
        setTimeout(() => {
          window.location.href = "/login";
        }, 1500);
        return;
      }

      // User is logged in, show booking modal
      const modal = document.getElementById("bookingModal");
      const serviceInput = document.getElementById("service");
      const packageInput = document.getElementById("package");

      if (modal && serviceInput && packageInput) {
        if (service) serviceInput.value = service;
        if (packageInfo) packageInput.value = packageInfo;

        modal.style.display = "block";
        document.body.style.overflow = "hidden";

        // Re-initialize form event listener when modal opens
        const form = document.getElementById("bookingForm");
        if (form && !form.hasBookingListener) {
          form.addEventListener("submit", handleBookingSubmission);
          form.hasBookingListener = true;
          console.log(
            "✅ Booking form event listener attached (on modal open)",
          );
        }

        // Scroll modal to top when opened
        const modalContent = modal.querySelector(".modal-content");
        if (modalContent) {
          modalContent.scrollTop = 0;
        }
      } else {
        console.error("❌ Modal or form elements not found");
      }
    })
    .catch((error) => {
      console.error("Error checking auth:", error);
      showAlert("Cannot verify login status. Please try again.", "error");
    });
}

// Add this function to your JavaScript

// Contact form submission
async function handleContactSubmission(e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  // Basic validation
  if (!validateContactForm(data)) {
    return;
  }

  // Show loading state
  const submitBtn = form.querySelector(".submit-btn");
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Sending...";
  submitBtn.disabled = true;

  try {
    // Send data to Flask backend
    const response = await fetch("/contact-form", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (response.ok) {
      // Success
      showAlert(
        result.message ||
          "Thank you for your message! We'll get back to you soon.",
        "success",
      );
      form.reset();
    } else {
      // Error from server
      showAlert(
        result.error || "Message sending failed. Please try again.",
        "error",
      );
    }
  } catch (error) {
    console.error("Error:", error);
    showAlert(
      "Network error. Please check your connection and try again.",
      "error",
    );
  } finally {
    // Reset button state
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
  }
}

function validateBookingForm(data) {
  // Check required fields
  const required = [
    "fullName",
    "email",
    "phone",
    "address",
    "service",
    "package",
    "date",
    "time",
    "payment",
  ];
  for (let field of required) {
    if (!data[field] || data[field].trim() === "") {
      showAlert(
        `Please fill in the ${field.replace(/([A-Z])/g, " $1").toLowerCase()}`,
        "error",
      );
      return false;
    }
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    showAlert("Please enter a valid email address", "error");
    return false;
  }

  // Phone validation (basic)
  const phoneRegex = /^[0-9]{10}$/;
  if (!phoneRegex.test(data.phone.replace(/\D/g, ""))) {
    showAlert("Please enter a valid 10-digit phone number", "error");
    return false;
  }

  // Date validation
  const selectedDate = new Date(data.date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (selectedDate < today) {
    showAlert("Please select a future date", "error");
    return false;
  }

  return true;
}

function validateContactForm(data) {
  // Check required fields
  const required = ["name", "email", "phone", "message"];
  for (let field of required) {
    if (!data[field] || data[field].trim() === "") {
      showAlert(
        `Please fill in the ${field.replace(/([A-Z])/g, " $1").toLowerCase()}`,
        "error",
      );
      return false;
    }
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    showAlert("Please enter a valid email address", "error");
    return false;
  }

  // Phone validation (basic)
  const phoneRegex = /^[0-9]{10}$/;
  if (!phoneRegex.test(data.phone.replace(/\D/g, ""))) {
    showAlert("Please enter a valid 10-digit phone number", "error");
    return false;
  }

  return true;
}

// Alert notification system
function showAlert(message, type = "info") {
  // Remove existing alerts
  const existingAlert = document.querySelector(".custom-alert");
  if (existingAlert) {
    existingAlert.remove();
  }

  // Create alert element
  const alert = document.createElement("div");
  alert.className = `custom-alert ${type}`;
  alert.innerHTML = `
        <div class="alert-content">
            <span class="alert-message">${message}</span>
            <button class="alert-close">&times;</button>
        </div>
    `;

  // Add styles
  alert.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${
          type === "error"
            ? "#ef4444"
            : type === "success"
              ? "#10b981"
              : "#3b82f6"
        };
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 3000;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;

  alert.querySelector(".alert-content").style.cssText = `
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    `;

  alert.querySelector(".alert-close").style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        margin: 0;
    `;

  // Add close functionality
  alert.querySelector(".alert-close").addEventListener("click", () => {
    alert.remove();
  });

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (alert.parentElement) {
      alert.style.animation = "slideOutRight 0.3s ease";
      setTimeout(() => alert.remove(), 300);
    }
  }, 5000);

  document.body.appendChild(alert);

  // Add keyframes for animation
  if (!document.querySelector("#alert-styles")) {
    const style = document.createElement("style");
    style.id = "alert-styles";
    style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
    document.head.appendChild(style);
  }
}

// STAR RATING
let selectedRating = 0;

const stars = document.querySelectorAll(".star-rating i");
stars.forEach((star) => {
  star.addEventListener("click", () => {
    selectedRating = star.getAttribute("data-star");

    stars.forEach((s, i) => {
      if (i < selectedRating) s.classList.add("active");
      else s.classList.remove("active");
    });
  });
});

// ARRAY TO STORE REVIEWS
let allReviews = [];

// HANDLE REVIEW SUBMIT - WITH NULL CHECK
const reviewForm = document.getElementById("reviewForm");
if (reviewForm) {
  reviewForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("reviewName").value;
    const message = document.getElementById("reviewMessage").value;

    if (selectedRating === 0) {
      alert("Please select a star rating!");
      return;
    }

    const review = {
      name: name,
      rating: selectedRating,
      message: message,
    };

    allReviews.push(review);
    displayReviews();

    // Reset form
    document.getElementById("reviewForm").reset();
    stars.forEach((s) => s.classList.remove("active"));
    selectedRating = 0;
  });
} else {
  console.log("⚠️ Review form not found on this page");
}

// DISPLAY ONLY FIRST 3 & SHOW MORE OPTION
function displayReviews() {
  const container = document.getElementById("reviewsList");
  container.innerHTML = "";

  const initialCount = 3;

  const visibleReviews = allReviews.slice(0, initialCount);
  const remainingReviews = allReviews.slice(initialCount);

  visibleReviews.forEach((review) => {
    container.innerHTML += `
      <div class="review-item">
        <h4>${review.name}</h4>
        <div class="review-stars">
          ${'<i class="fa-solid fa-star"></i>'.repeat(review.rating)}
        </div>
        <p>${review.message}</p>
      </div>
    `;
  });

  const showMoreBtn = document.getElementById("showMoreBtn");

  if (remainingReviews.length > 0) {
    showMoreBtn.style.display = "inline-block";

    showMoreBtn.onclick = function () {
      remainingReviews.forEach((review) => {
        container.innerHTML += `
          <div class="review-item">
            <h4>${review.name}</h4>
            <div class="review-stars">
              ${'<i class="fa-solid fa-star"></i>'.repeat(review.rating)}
            </div>
            <p>${review.message}</p>
          </div>
        `;
      });

      showMoreBtn.style.display = "none";
    };
  } else {
    showMoreBtn.style.display = "none";
  }
}

function closeBookingModal() {
  const modal = document.getElementById("bookingModal");

  if (modal) {
    modal.style.display = "none";
    document.body.style.overflow = "auto";
  }
}

