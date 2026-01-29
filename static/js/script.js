const setupCountdown = (timerId, eventTime) => {
        const timerElement = document.getElementById(timerId);

        const updateTimer = () => {
            const now = new Date().getTime();
            const timeLeft = eventTime - now;

            if (timeLeft > 0) {
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
            } else {
                timerElement.style.display = "none"; // Hide countdown when it ends
                clearInterval(interval);
            }
        };

        updateTimer();
        const interval = setInterval(updateTimer, 1000);
    };

    // Initialize the countdown timer
// setupCountdown("countdown-timer", new Date("2026-01-29T08:00:00").getTime());
    



const setupCountUp = (timerId, startTime, endTime) => {
    const timerElement = document.getElementById(timerId);
    const floatingContainer = document.getElementById("floating-container");

    const updateTimer = () => {
        const now = new Date().getTime();

        if (now >= startTime && now <= endTime) {
            if (floatingContainer) floatingContainer.classList.add("visible");
            const elapsedTime = now - startTime;

            const days = Math.floor(elapsedTime / (1000 * 60 * 60 * 24));
            const hours = Math.floor((elapsedTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);

            if (timerElement) {
                timerElement.innerHTML = `
                    <div class="time-box"><span>${days}</span><small>Days</small></div>
                    <div class="time-box"><span>${hours}</span><small>Hours</small></div>
                    <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
                    <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
                `;
            }
        } else {
            if (floatingContainer) floatingContainer.classList.remove("visible");
            if (now > endTime) {
                clearInterval(interval);
            }
        }
    };

    const interval = setInterval(updateTimer, 1000);
    updateTimer(); // Initial call to set the state correctly
};

// Initialize the count-up timer for the 3-day event
setupCountUp(
    "count-up-timer",
    new Date("2026-01-29T08:00:00").getTime(), // Day 1: Starts Jan 29, 8 AM
    new Date("2026-01-31T23:00:00").getTime()  // Day 3: Ends Jan 31, 11 PM
);