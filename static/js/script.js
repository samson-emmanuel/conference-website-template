const setupCountdown = (id, eventTime) => {
    const timerElement = document.getElementById(id);
    const cardElement = timerElement.closest(".event-card");

    const eventDuration = 3 * 24 * 60 * 60 * 1000; // 3 days in milliseconds
    const endEventTime = eventTime + eventDuration;

    const updateTimer = () => {
        const now = new Date().getTime();

        if (now < eventTime) {
            // Countdown before the event starts
            const timeLeft = eventTime - now;

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
            cardElement.classList.remove("expired", "happening-now");
        } else if (now >= eventTime && now <= endEventTime) {
            // Count up after the event starts
            const timeSinceEventStart = now - eventTime;

            const days = Math.floor(timeSinceEventStart / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeSinceEventStart % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeSinceEventStart % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeSinceEventStart % (1000 * 60)) / 1000);

            timerElement.style.color = "blue";
            timerElement.innerHTML = `
                <div class="time-box"><span>${days}</span><small>Days</small></div>
                <div class="time-box"><span>${hours}</span><small>Hours</small></div>
                <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
                <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
            `;

            cardElement.classList.add("happening-now");
            cardElement.classList.remove("expired", "active");
        } else if (now > endEventTime) {
            // Event has ended
            timerElement.innerHTML = "Event Ended!";
            timerElement.style.color = "red";
            cardElement.classList.add("expired");
            cardElement.classList.remove("happening-now", "active");
            clearInterval(timerInterval);
        }
    };

    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);
};

// Example usage
setupCountdown("afternoon-session-timer1", new Date("2025-01-29T14:00:00").getTime());
