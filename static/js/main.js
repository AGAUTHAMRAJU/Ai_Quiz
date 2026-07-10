/*==================================================
AiQuiz Global JavaScript
==================================================*/

document.addEventListener("DOMContentLoaded", function () {

    /*==========================================
      Auto Hide Messages ONLY
    ==========================================*/

    const alerts = document.querySelectorAll(".alert.auto-dismiss");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.classList.remove("show");

            setTimeout(function () {

                alert.remove();

            }, 300);

        }, 4000);

    });

    /*==========================================
      Back To Top
    ==========================================*/

    const topBtn = document.getElementById("topBtn");

    window.addEventListener("scroll", function () {

        if (!topBtn) return;

        if (window.scrollY > 250) {

            topBtn.style.display = "flex";

        }

        else {

            topBtn.style.display = "none";

        }

    });

    if (topBtn) {

        topBtn.addEventListener("click", function () {

            window.scrollTo({

                top: 0,

                behavior: "smooth"

            });

        });

    }

    /*==========================================
      Navbar Shadow
    ==========================================*/

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", function () {

        if (!navbar) return;

        if (window.scrollY > 20) {

            navbar.classList.add("shadow-lg");

        }

        else {

            navbar.classList.remove("shadow-lg");

        }

    });

    /*==========================================
      Smooth Scroll
    ==========================================*/

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {

        anchor.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {

                e.preventDefault();

                target.scrollIntoView({

                    behavior: "smooth"

                });

            }

        });

    });

    /*==========================================
      Card Hover Animation
    ==========================================*/

    document.querySelectorAll(".card").forEach(function (card) {

        card.addEventListener("mouseenter", function () {

            card.style.transform = "translateY(-6px)";

        });

        card.addEventListener("mouseleave", function () {

            card.style.transform = "translateY(0px)";

        });

    });

    /*==========================================
      Counter Animation
    ==========================================*/

    const counters = document.querySelectorAll(".counter");

    counters.forEach(function (counter) {

        const target = Number(counter.dataset.target);

        if (!target) return;

        let current = 0;

        const step = Math.max(1, Math.ceil(target / 80));

        const timer = setInterval(function () {

            current += step;

            if (current >= target) {

                current = target;

                clearInterval(timer);

            }

            counter.innerText = current;

        }, 20);

    });

    /*==========================================
      Fade Animation
    ==========================================*/

    const observer = new IntersectionObserver(function (entries) {

        entries.forEach(function (entry) {

            if (entry.isIntersecting) {

                entry.target.classList.add("fade-up");

            }

        });

    }, {

        threshold: 0.2

    });

    document.querySelectorAll("section, .card").forEach(function (el) {

        observer.observe(el);

    });

    /*==========================================
      Disable Multiple Form Submit
    ==========================================*/

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitBtn = form.querySelector(
                'button[type="submit"],input[type="submit"]'
            );

            if (!submitBtn) return;

            submitBtn.disabled = true;

            if (submitBtn.tagName === "BUTTON") {

                submitBtn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>Please Wait...';

            }

        });

    });

});