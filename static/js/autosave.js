/*
const AUTOSAVE_INTERVAL = 60000; // 1 minute

/**
 * Saves the values of all form inputs on the page to localStorage.
 * The data is stored as a JSON object, keyed by the page's path.
 */
function saveData() {
  const inputs = document.querySelectorAll('input, textarea, select');
  if (inputs.length === 0) {
    return;
  }

  const data = {};
  inputs.forEach(input => {
    if (input.id) {
      if (input.type === 'checkbox' || input.type === 'radio') {
        data[input.id] = input.checked;
      } else {
        data[input.id] = input.value;
      }
    }
  });

  const pageKey = `autosave_${window.location.pathname}`;
  localStorage.setItem(pageKey, JSON.stringify(data));
  console.log(`[Autosave] Data saved for ${window.location.pathname} at ${new Date().toLocaleTimeString()}`);
}

/**
 * Loads and populates form inputs from data stored in localStorage.
 */
function loadData() {
  const pageKey = `autosave_${window.location.pathname}`;
  const savedData = localStorage.getItem(pageKey);

  if (savedData) {
    const data = JSON.parse(savedData);
    Object.keys(data).forEach(inputId => {
      const input = document.getElementById(inputId);
      if (input) {
        if (input.type === 'checkbox' || input.type === 'radio') {
          input.checked = data[inputId];
        } else {
          input.value = data[inputId];
        }
      }
    });
    console.log(`[Autosave] Data loaded for ${window.location.pathname}`);
  }
}

// Load the saved data as soon as the DOM is ready.
document.addEventListener('DOMContentLoaded', () => {
  loadData();

  // Start the autosave interval.
  setInterval(saveData, AUTOSAVE_INTERVAL);
  console.log('[Autosave] Service started. Data will be saved every 1 minute.');
});
*/