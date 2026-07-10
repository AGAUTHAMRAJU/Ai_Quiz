/*==================================================
AiQuiz Dark Mode
==================================================*/

document.addEventListener("DOMContentLoaded", function () {

    const body = document.getElementById("body");

    const themeToggle = document.getElementById("themeToggle");

    const STORAGE_KEY = "aiquiz-theme";

    function setIcon() {

        if (!themeToggle) return;

        const icon = themeToggle.querySelector("i");

        if (!icon) return;

        if (body.classList.contains("dark")) {

            icon.className = "bi bi-sun-fill";

            themeToggle.setAttribute("title", "Light Mode");

        }

        else {

            icon.className = "bi bi-moon-stars-fill";

            themeToggle.setAttribute("title", "Dark Mode");

        }

    }

    function enableDark() {

        body.classList.add("dark");

        localStorage.setItem(STORAGE_KEY, "dark");

        setIcon();

    }

    function enableLight() {

        body.classList.remove("dark");

        localStorage.setItem(STORAGE_KEY, "light");

        setIcon();

    }

    const savedTheme = localStorage.getItem(STORAGE_KEY);

    if (savedTheme === "dark") {

        enableDark();

    }

    else {

        enableLight();

    }

    if (themeToggle) {

        themeToggle.addEventListener("click", function () {

            if (body.classList.contains("dark")) {

                enableLight();

            }

            else {

                enableDark();

            }

        });

    }

    window.matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", function (e) {

            if (localStorage.getItem(STORAGE_KEY) === null) {

                if (e.matches) {

                    enableDark();

                }

                else {

                    enableLight();

                }

            }

        });

});