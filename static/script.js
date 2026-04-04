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
        { name: "Archery", start: "MAY 30", end: "JUN 02", icon: "fa-bullseye" },
        { name: "Athletics", start: "MAY 01", end: "MAY 10", icon: "fa-person-running" },
        { name: "Badminton", start: "MAY 09", end: "MAY 15", icon: "fa-table-tennis-paddle-ball" },
        { name: "Basketball", start: "MAY 09", end: "MAY 16", icon: "fa-basketball" },
        { name: "Beach Handball", start: "MAY 26", end: "MAY 29", icon: "fa-volleyball" },
        { name: "Beach Volleyball", start: "MAY 23", end: "MAY 27", icon: "fa-umbrella-beach" },
        { name: "Boxing", start: "MAY 16", end: "MAY 20", icon: "fa-hand-fist" },
        { name: "Carrom", start: "JUN 02", end: "JUN 05", icon: "fa-square" },
        { name: "Chess", start: "JUN 02", end: "JUN 05", icon: "fa-chess" },

        // ✅ KEEP SAME
        { name: "Cricket", start: "JUN 07", end: "JUL 04", icon: "fa-cricket-bat-ball" },

        { name: "Cycling", start: "MAY 21", end: "MAY 26", icon: "fa-bicycle" },
        { name: "Diving", start: "MAY 31", end: "JUN 03", icon: "fa-water" },
        { name: "Fencing", start: "MAY 30", end: "JUN 02", icon: "fa-fencing-fights" },

        // ✅ KEEP SAME
        { name: "Football", start: "JUN 07", end: "JUN 27", icon: "fa-soccer-ball" },

        { name: "Handball", start: "MAY 23", end: "MAY 27", icon: "fa-circle-dot" },
        { name: "Hockey", start: "MAY 11", end: "MAY 18", icon: "fa-hockey-puck" },
        { name: "Ice Hockey", start: "JUN 04", end: "JUN 06", icon: "fa-icicles" },
        { name: "Judo", start: "MAY 28", end: "MAY 31", icon: "fa-user-ninja" },

        // ✅ KEEP SAME
        { name: "Kabaddi", start: "JUN 28", end: "JUL 10", icon: "fa-users-rays" },

        { name: "Karate", start: "MAY 28", end: "MAY 31", icon: "fa-hand-back-fist" },
        { name: "Kho Kho", start: "MAY 26", end: "MAY 29", icon: "fa-arrows-left-right" },
        { name: "Rowing", start: "MAY 31", end: "JUN 03", icon: "fa-ship" },
        { name: "Shooting", start: "MAY 21", end: "MAY 25", icon: "fa-crosshairs" },
        { name: "Speed Skating", start: "JUN 01", end: "JUN 04", icon: "fa-bolt" },
        { name: "Squash", start: "JUN 01", end: "JUN 04", icon: "fa-baseball-bat-ball" },
        { name: "Swimming", start: "MAY 01", end: "MAY 08", icon: "fa-person-swimming" },
        { name: "Table Tennis", start: "MAY 18", end: "MAY 22", icon: "fa-table-tennis-paddle-ball" },
        { name: "Tennis", start: "MAY 18", end: "MAY 23", icon: "fa-baseball" },
        { name: "Trampoline", start: "JUN 03", end: "JUN 06", icon: "fa-up-down" },
        { name: "Volleyball", start: "MAY 11", end: "MAY 17", icon: "fa-volleyball" },
        { name: "Weightlifting", start: "JUN 03", end: "JUN 06", icon: "fa-weight-hanging" },
        { name: "Wrestling", start: "MAY 16", end: "MAY 20", icon: "fa-child-reaching" }
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