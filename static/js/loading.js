document.addEventListener("DOMContentLoaded", function () {

    const loader = document.getElementById("loader");

    if (loader) {
        loader.style.display = "none";
    }

    window.addEventListener("pageshow", function () {
        if (loader) {
            loader.style.display = "none";
        }
    });

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            if (loader) {
                loader.style.display = "flex";
            }

        });

    });

});