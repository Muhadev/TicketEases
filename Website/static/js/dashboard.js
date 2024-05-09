document.addEventListener('DOMContentLoaded', function () {
    // Load dashboard content by default
    loadDashboardContent();

    // Event listener for dashboard link
    document.getElementById('dashboard-view').addEventListener('click', function () {
        loadDashboardContent();
    });

    // Event listener for create event link
    document.getElementById('create-event-link').addEventListener('click', function () {
        loadCreateEventForm();
    });

    // Event listener for list event link
    document.getElementById('list-event-link').addEventListener('click', function () {
        loadListEvents();
    });
});

function loadDashboardContent() {
    // Example: load some dashboard content
    document.querySelector('.main-content').innerHTML = '<h1>Welcome to the Dashboard</h1>';
}

function loadCreateEventForm() {
    // Example: load the create event form
    fetch(createEventUrl)
        .then(response => response.text())
        .then(html => {
            document.querySelector('.main-content').innerHTML = html;
        })
        .catch(error => console.error('Error:', error));
}

function loadListEvents() {
    // Example: load the list of events
    fetch(listEventsUrl)
        .then(response => response.text())
        .then(html => {
            document.querySelector('.main-content').innerHTML = html;
        })
        .catch(error => console.error('Error:', error));
}
