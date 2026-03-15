document.addEventListener("DOMContentLoaded", function () {

    /* =================================
       ELEMENTS
    ================================= */
    const navbar = document.getElementById("navbar");
    const intro = document.getElementById("intro");
    const oval = document.getElementById("oval");
    const about = document.getElementById("about");
    const logo = document.getElementById("logo");
    const hamburger = document.getElementById("hamburger");
    const navLinks = document.getElementById("navLinks");

    /* =================================
       HAMBURGER MENU
    ================================= */
    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navLinks.classList.toggle("active");
        });
    }

    /* =================================
       INTRO ANIMATION LOGIC
    ================================= */
    let introPlayed = false;

    // Initially hide navbar on desktop to prevent it from showing early
    if (window.innerWidth >= 900 && navbar) {
    navbar.style.top = "-100px";
    } else {
        if(navbar) navbar.style.top = "0";
    }

    function playIntro() {
        if (introPlayed) return;
        introPlayed = true;

        /* Desktop Animation Sequence */
        if (window.innerWidth >= 900 && logo && oval && about) {
            about.classList.add("hide-text");
            
            // Spinning logo animation start
            logo.style.transform = "translateX(-350px) rotate(-1080deg)";

            setTimeout(() => {
                logo.style.transform = "none";
                oval.classList.add("swap-layout");
                intro.classList.add("move-down");
                about.classList.remove("hide-text");
                about.classList.add("show-right");

                /* Reveal navbar ONLY after wheel animation finishes */
                if (navbar) {
                    navbar.style.top = "0";
                }
                
                // Allow scrolling again once animation is complete
                document.body.style.overflow = "auto";
            }, 1200); 
        }
    }

    /* ===== INITIAL LOAD LOGIC ===== */
    if (window.innerWidth >= 900) {
        // Prevent user from scrolling during the 3s wait + animation
        document.body.style.overflow = "hidden";

        setTimeout(() => {
            playIntro();
        }, 3000);
    } else {
        // Mobile: Show navbar immediately & ensure scrolling is active
        if (navbar) {
            navbar.style.top = "0";
        }
        document.body.style.overflow = "auto";
    }

    /* =================================
       SPORTS CAROUSEL
    ================================= */
    const sportNameEl = document.getElementById("active-sport-name");
    const startEl = document.getElementById("start-date");
    const endEl = document.getElementById("end-date");
    const iconEl = document.getElementById("portal-icon");

    if (!sportNameEl) return;

    const sportsData = [
        { name: "Archery", start: "JUL 05", end: "JUL 07", icon: "fa-bullseye" },
        { name: "Athletics", start: "JUL 05", end: "JUL 12", icon: "fa-person-running" },
        { name: "Badminton", start: "JUL 08", end: "JUL 14", icon: "fa-table-tennis-paddle-ball" },
        { name: "Basketball", start: "JUL 08", end: "JUL 15", icon: "fa-basketball" },
        { name: "Beach Handball", start: "JUL 12", end: "JUL 16", icon: "fa-volleyball" },
        { name: "Beach Volleyball", start: "JUL 12", end: "JUL 17", icon: "fa-umbrella-beach" },
        { name: "Boxing", start: "JUL 14", end: "JUL 18", icon: "fa-hand-fist" },
        { name: "Carrom", start: "JUL 14", end: "JUL 18", icon: "fa-square" },
        { name: "Chess", start: "JUL 16", end: "JUL 20", icon: "fa-chess" },
        { name: "Cricket", start: "JUN 07", end: "JUL 04", icon: "fa-cricket-bat-ball" },
        { name: "Cycling", start: "JUL 16", end: "JUL 20", icon: "fa-bicycle" },
        { name: "Diving", start: "JUL 18", end: "JUL 22", icon: "fa-water" },
        { name: "Fencing", start: "JUL 18", end: "JUL 22", icon: "fa-fencing-fights" },
        { name: "Football", start: "JUN 07", end: "JUN 27", icon: "fa-soccer-ball" },
        { name: "Handball", start: "JUL 20", end: "JUL 24", icon: "fa-circle-dot" },
        { name: "Hockey", start: "JUL 20", end: "JUL 24", icon: "fa-hockey-puck" },
        { name: "Ice Hockey", start: "JUL 21", end: "JUL 25", icon: "fa-icicles" },
        { name: "Judo", start: "JUL 22", end: "JUL 25", icon: "fa-user-ninja" },
        { name: "Kabaddi", start: "JUN 28", end: "JUL 10", icon: "fa-users-rays" },
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
            if (startEl) startEl.innerText = sport.start;
            if (endEl) endEl.innerText = sport.end;
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