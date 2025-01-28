// const setupCountdown = (id, eventTime) => {
//     const timerElement = document.getElementById(id);
//     const cardElement = timerElement.closest(".event-card");

//     const eventDuration = 3 * 24 * 60 * 60 * 1000; // 3 days in milliseconds
//     const endEventTime = eventTime + eventDuration;

//     const updateTimer = () => {
//         const now = new Date().getTime();

//         if (now < eventTime) {
//             // Countdown before the event starts
//             const timeLeft = eventTime - now;

//             const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
//             const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//             const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
//             const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

//             timerElement.innerHTML = `
//                 <div class="time-box"><span>${days}</span><small>Days</small></div>
//                 <div class="time-box"><span>${hours}</span><small>Hours</small></div>
//                 <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
//                 <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
//             `;

//             cardElement.classList.add("active");
//             cardElement.classList.remove("expired", "happening-now");
//         } else if (now >= eventTime && now <= endEventTime) {
//             // Count up after the event starts
//             const timeSinceEventStart = now - eventTime;

//             const days = Math.floor(timeSinceEventStart / (1000 * 60 * 60 * 24));
//             const hours = Math.floor((timeSinceEventStart % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//             const minutes = Math.floor((timeSinceEventStart % (1000 * 60 * 60)) / (1000 * 60));
//             const seconds = Math.floor((timeSinceEventStart % (1000 * 60)) / 1000);

//             timerElement.style.color = "blue";
//             timerElement.innerHTML = `
//                 <div class="time-box"><span>${days}</span><small>Days</small></div>
//                 <div class="time-box"><span>${hours}</span><small>Hours</small></div>
//                 <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
//                 <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
//             `;

//             cardElement.classList.add("happening-now");
//             cardElement.classList.remove("expired", "active");
//         } else if (now > endEventTime) {
//             // Event has ended
//             timerElement.innerHTML = "Event Ended!";
//             timerElement.style.color = "red";
//             cardElement.classList.add("expired");
//             cardElement.classList.remove("happening-now", "active");
//             clearInterval(timerInterval);
//         }
//     };

//     updateTimer();
//     const timerInterval = setInterval(updateTimer, 1000);
// };

// // Example usage
// setupCountdown("afternoon-session-timer1", new Date("2025-01-29T14:00:00").getTime());





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
setupCountdown("countdown-timer", new Date("2025-01-29T14:00:00").getTime());
    



const setupCountUp = (timerId, startTime, endTime) => {
    const timerElement = document.getElementById(timerId);
    const headerElement = document.getElementById("event-header");

    const updateTimer = () => {
        const now = new Date().getTime();

        if (now >= startTime && now <= endTime) {
            let elapsedTime = now - startTime;

            // Show timer and header
            timerElement.style.display = "block";
            headerElement.style.display = "block";

            // Handle Day 1 (ends at 11:59 PM of the same day)
            const day1End = new Date(startTime);
            day1End.setHours(23, 59, 59, 999);

            let days, hours, minutes, seconds;

            if (now <= day1End.getTime()) {
                // Calculate time for Day 1
                days = 0;
                hours = Math.floor((elapsedTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60));
                seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);
            } else {
                // Handle Day 2 onwards
                elapsedTime = now - day1End.getTime();

                // Day 2 (normal 24-hour day)
                const day2End = new Date(day1End);
                day2End.setDate(day2End.getDate() + 1);

                if (now <= day2End.getTime()) {
                    days = 1;
                    hours = Math.floor((elapsedTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60));
                    seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);
                } else {
                    // Handle Day 3 (ends at 11:00 PM)
                    const day3End = new Date(day2End);
                    day3End.setHours(23, 0, 0, 0);

                    if (now <= day3End.getTime()) {
                        elapsedTime = now - day2End.getTime();
                        days = 2;
                        hours = Math.floor((elapsedTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                        minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60));
                        seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);
                    } else {
                        // Hide timer and header after Day 3 ends
                        timerElement.style.display = "none";
                        headerElement.style.display = "none";
                        clearInterval(interval);
                        return;
                    }
                }
            }

            timerElement.innerHTML = `
                <div class="time-box"><span>${days}</span><small>Days</small></div>
                <div class="time-box"><span>${hours}</span><small>Hours</small></div>
                <div class="time-box"><span>${minutes}</span><small>Minutes</small></div>
                <div class="time-box"><span>${seconds}</span><small>Seconds</small></div>
            `;
        } else {
            // Hide timer and header when the event is not active
            timerElement.style.display = "none";
            headerElement.style.display = "none";
            clearInterval(interval);
        }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
};

// Initialize the count-up timer
setupCountUp(
    "count-up-timer",
    new Date("2025-01-29T14:00:00").getTime(), // Start at 2 PM
    new Date("2025-01-31T23:00:00").getTime() // End at 11 PM on the 3rd day
);    