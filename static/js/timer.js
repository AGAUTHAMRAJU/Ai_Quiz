const QUIZ_ID = window.location.pathname.split("/")[2];

const STORAGE_KEY = "quiz_timer_" + QUIZ_ID;

const totalSeconds = 30 * 60;

let secondsLeft = localStorage.getItem(STORAGE_KEY);

if (secondsLeft === null) {

    secondsLeft = totalSeconds;

} else {

    secondsLeft = parseInt(secondsLeft);

}

const timer = document.getElementById("timer");

const progressFill = document.getElementById("progressFill");

function updateTimer() {

    if (secondsLeft <= 0) {

        localStorage.removeItem(STORAGE_KEY);

        document.getElementById("assessmentForm").submit();

        return;

    }

    const minutes = Math.floor(secondsLeft / 60);

    const seconds = secondsLeft % 60;

    timer.innerHTML =
        String(minutes).padStart(2, "0") +
        ":" +
        String(seconds).padStart(2, "0");

    const percentage =
        (secondsLeft / totalSeconds) * 100;

    progressFill.style.width = percentage + "%";

    if (percentage <= 60) {

        progressFill.style.background = "#f59e0b";

    }

    if (percentage <= 30) {

        progressFill.style.background = "#ef4444";

    }

    localStorage.setItem(STORAGE_KEY, secondsLeft);

    secondsLeft--;

}

updateTimer();

setInterval(updateTimer, 1000);