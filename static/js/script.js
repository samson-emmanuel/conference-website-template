// const setupCountdown = (id, eventTime) => {
//     const timerElement = document.getElementById(id);
//     const cardElement = timerElement.closest(".event-card"); // Assume timer is inside an event card

//     const updateTimer = () => {
//         const now = new Date().getTime();
//         const timeLeft = eventTime - now;

//         if (timeLeft < 0) {
//             timerElement.innerHTML = "Event Done!";
//             timerElement.style.color = "red";
//             timerElement.style.justifyContent = "center";
//             cardElement.classList.remove("active");
//             cardElement.classList.add("expired");
//             return;
//         }

//         const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
//         const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//         const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
//         const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

//         timerElement.innerHTML = `
//             <div class="time-box"><span>${days}</span><small>Days</small></div>
//             <div class="time-box"><span>${hours}</span><small>Hours</small></div>
//             <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
//             <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
//         `;

//         cardElement.classList.add("active");
//         cardElement.classList.remove("expired");
//     };

//     updateTimer(); // Initial call to display immediately
//     setInterval(updateTimer, 1000);
// };

// // Initialize countdowns for each session
// setupCountdown("morning-session-timer", new Date("2025-01-29T16:00:00").getTime());
// setupCountdown("afternoon-session-timer", new Date("2025-01-30T13:00:00").getTime());
// setupCountdown("evening-session-timer", new Date("2025-01-31T09:00:00").getTime());
// setupCountdown("night-session-timer", new Date("2025-01-31T13:00:00").getTime());

const setupCountdown = (id, eventTime, nextId) => {
    const timerElement = document.getElementById(id);
    const cardElement = timerElement.closest(".event-card");
    let isHappeningNow = false; // Track if the event is happening now

    const updateTimer = () => {
        const now = new Date().getTime();
        const timeLeft = eventTime - now;

        if (timeLeft <= 0 && !isHappeningNow) {
             {
                // Mark as Happening Now
                timerElement.innerHTML = "Happening Now!"; timerElement.style.color = "green"; cardElement.classList.add("happening-now");
                timerElement.style.color = "green";
                cardElement.classList.add("happening-now");
                isHappeningNow = true; setTimeout(() => { if (isHappeningNow) { timerElement.innerHTML = "Event Done!"; timerElement.style.color = "red"; cardElement.classList.remove("happening-now"); cardElement.classList.add("expired"); } }, 60000);

                // Mark previous "Happening Now" as "Event Done"
                const previousHappening = document.querySelector(".happening-now");
                if (previousHappening && previousHappening !== timerElement) {
                    previousHappening.innerHTML = "Event Done!";
                    previousHappening.style.color = "red";
                    previousHappening.closest(".event-card").classList.remove("happening-now");
                    previousHappening.closest(".event-card").classList.add("expired");
                }
            }
        } else {
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            timerElement.innerHTML = `
                <div class="time-box"><span>${days}</span><small>Days</small></div>
                <div class="time-box"><span>${hours}</span><small>Hours</small></div>
                <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
                <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
            `;

            cardElement.classList.add("active");
            cardElement.classList.remove("expired");
        }
    };

    updateTimer(); // Initial call to display immediately
    setInterval(updateTimer, 1000);
};

// Initialize countdowns for each session
setupCountdown("morning-session-timer", new Date("2025-01-29T14:00:00").getTime());
setupCountdown("afternoon-session-timer", new Date("2025-01-29T17:50:00").getTime());
setupCountdown("evening-session-timer", new Date("2025-01-30T09:00:00").getTime());
setupCountdown("night-session-timer", new Date("2025-01-30T15:30:00").getTime());

// section for navbar
function toggleMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

