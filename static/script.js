/**
 * Indian League 4 - Main Interaction Script
 */

document.addEventListener("DOMContentLoaded", function () {

    let isTransitionTriggered = false;

    const logo = document.getElementById("logo");
    const navbar = document.getElementById("navbar");
    const about = document.getElementById("about");
    const intro = document.getElementById("intro");
    const oval = document.getElementById("oval");

    // Intro animation only if homepage elements exist
    if (logo && navbar && about && intro && oval) {

        // Skip animation if page reloads below top
        if (window.scrollY > 50) {

            navbar.style.top = "0";
            oval.classList.add("swap-layout");
            intro.classList.add("move-down");

            document.body.style.overflow = "auto";
            isTransitionTriggered = true;
        }

        window.addEventListener("wheel", function () {

            if (isTransitionTriggered) return;

            isTransitionTriggered = true;

            about.classList.add("hide-text");
            logo.style.transform = "translateX(-350px) rotate(-1080deg)";

            setTimeout(() => {

                logo.style.transform = "none";
                oval.classList.add("swap-layout");
                navbar.style.top = "0";

                intro.classList.add("move-down");

                about.classList.remove("hide-text");
                about.classList.add("show-right");

                document.body.style.overflow = "auto";

            }, 1200);

        });

    }

    // -----------------------------------
    // SPORTS CAROUSEL
    // -----------------------------------

    const sportNameEl = document.getElementById('active-sport-name');
    const startEl = document.getElementById('start-date');
    const endEl = document.getElementById('end-date');
    const iconEl = document.getElementById('portal-icon');

    if (!sportNameEl) return;

    const sportsData = [
        { name: "Cricket", start: "JUN 07", end: "JUL 04", icon: "fa-cricket-bat-ball" },
        { name: "Football", start: "JUN 07", end: "JUN 27", icon: "fa-soccer-ball" },
        { name: "Kabaddi", start: "JUN 28", end: "JUL 11", icon: "fa-users-rays" },
        { name: "Archery", start: "JUL 05", end: "JUL 07", icon: "fa-bullseye" },
        { name: "Athletics", start: "JUL 05", end: "JUL 12", icon: "fa-person-running" },
        { name: "Badminton", start: "JUL 08", end: "JUL 14", icon: "fa-table-tennis-paddle-ball" },
        { name: "Basketball", start: "JUL 08", end: "JUL 15", icon: "fa-basketball" },
        { name: "Beach Handball", start: "JUL 12", end: "JUL 16", icon: "fa-volleyball" },
        { name: "Beach Volleyball", start: "JUL 12", end: "JUL 17", icon: "fa-umbrella-beach" },
        { name: "Boxing", start: "JUL 14", end: "JUL 18", icon: "fa-hand-fist" },
        { name: "Carrom", start: "JUL 14", end: "JUL 18", icon: "fa-square" },
        { name: "Chess", start: "JUL 16", end: "JUL 20", icon: "fa-chess" },
        { name: "Cycling", start: "JUL 16", end: "JUL 20", icon: "fa-bicycle" },
        { name: "Diving", start: "JUL 18", end: "JUL 22", icon: "fa-water" },
        { name: "Fencing", start: "JUL 18", end: "JUL 22", icon: "fa-fencing-fights" },
        { name: "Handball", start: "JUL 20", end: "JUL 24", icon: "fa-circle-dot" },
        { name: "Hockey", start: "JUL 20", end: "JUL 24", icon: "fa-hockey-puck" },
        { name: "Ice Hockey", start: "JUL 21", end: "JUL 25", icon: "fa-icicles" },
        { name: "Judo", start: "JUL 22", end: "JUL 25", icon: "fa-user-ninja" },
        { name: "Karate", start: "JUL 22", end: "JUL 26", icon: "fa-hand-back-fist" },
        { name: "Kho Kho", start: "JUL 23", end: "JUL 26", icon: "fa-arrows-left-right" },
        { name: "Rowing", start: "JUL 23", end: "JUL 27", icon: "fa-ship" },
        { name: "Shooting", start: "JUL 24", end: "JUL 27", icon: "fa-crosshairs" },
        { name: "Speed Skating", start: "JUL 24", end: "JUL 27", icon: "fa-bolt" },
        { name: "Squash", start: "JUL 25", end: "JUL 28", icon: "fa-baseball-bat-ball" },
        { name: "Swimming", start: "JUL 25", end: "JUL 28", icon: "fa-person-swimming" },
        { name: "Table Tennis", start: "JUL 26", end: "JUL 28", icon: "fa-table-tennis-paddle-ball" },
        { name: "Tennis", start: "JUL 26", end: "JUL 28", icon: "fa-baseball" },
        { name: "Trampoline", start: "JUL 27", end: "JUL 28", icon: "fa-up-down" },
        { name: "Volleyball", start: "JUL 27", end: "JUL 28", icon: "fa-volleyball" },
        { name: "Weightlifting", start: "JUL 27", end: "JUL 28", icon: "fa-weight-hanging" },
        { name: "Wrestling", start: "JUL 27", end: "JUL 28", icon: "fa-child-reaching" }
    ];

    let currentIndex = 0;

    function updateDisplay(index) {

        const sport = sportsData[index];

        sportNameEl.style.opacity = 0;

        setTimeout(() => {

            sportNameEl.innerText = sport.name;
            startEl.innerText = sport.start;
            endEl.innerText = sport.end;

            if (iconEl) iconEl.className = `fas ${sport.icon}`;

            sportNameEl.style.opacity = 1;

        }, 200);
    }

    window.nextSport = function () {
        currentIndex = (currentIndex + 1) % sportsData.length;
        updateDisplay(currentIndex);
    }

    window.prevSport = function () {
        currentIndex = (currentIndex - 1 + sportsData.length) % sportsData.length;
        updateDisplay(currentIndex);
    }

    setInterval(() => {
        nextSport();
    }, 4000);

});