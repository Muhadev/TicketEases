$(document).ready(function () {

    // Event listener for create event link
    $('#create-event-link').on('click', function () {
        loadCreateEventForm();
    });

    // Event listener for list event link
    $('#list-event-link').on('click', function () {
        loadListEvents();
    });

    // Event listener for submitting the create event form
    $(document).on('submit', '#create-event-form', function (event) {
        event.preventDefault(); // Prevent default form submission behavior

        var form = $(this); // Get the form element
        var url = form.attr('action'); // Get the form action URL
        var formData = form.serialize(); // Serialize the form data

        // Send an AJAX POST request to the server
        $.ajax({
            url: url,
            type: 'POST',
            data: formData,
            success: function (data) {
                // On successful response, load the event details page
                loadEventDetails(data.event_id);
            },
            error: function () {
                // Handle any errors if the request fails
                alert('An error occurred while creating the event. Please try again later.');
            }
        });
    });

    $(document).on('click', '.view-details-btn', function (event) {
        event.preventDefault(); // Prevent default link behavior
        var eventId = $(this).data('event-id');
        loadEventDetails(eventId);
    });

    $(document).on('click', '.delete-event-btn', function (event) {
        event.preventDefault(); // Prevent default link behavior
        var eventId = $(this).data('event-id');
        deleteEvent(eventId);
    });

     // Event listen er for manage tickets link
     $(document).on('click', '.manage-tickets-btn', function (event) {
        event.preventDefault(); // Prevent default link behavior
        var eventId = $(this).data('event-id');
        loadManageTickets(eventId);
    });

    $(document).on('click', '#edit-event-btn', function (event) {
        event.preventDefault(); // Prevent default link behavior

        // Fetch the edit event page content from the server
        var eventId = $(this).data('event-id');
        var url = '/dashboard/events/' + eventId + '/edit'; // Check if eventId is properly defined here
        fetch(url)
            .then(response => response.text())
            .then(html => {
                // Replace the content of the main dashboard area with the edit event page content
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }); 

    // Event listener for submitting the edit event form
    $(document).on('submit', '#edit-event-form', function (event) {
        event.preventDefault(); // Prevent default form submission behavior

        var form = $(this); // Get the form element
        var url = form.attr('action'); // Get the form action URL
        var formData = form.serialize(); // Serialize the form data

        // Send an AJAX POST request to the server
        $.ajax({
            url: url,
            type: 'POST',
            data: formData,
            success: function () {
                // On successful response, load the success page
                loadSuccessPage();
            },
            error: function () {
                // Handle any errors if the request fails
                alert('An error occurred while updating the event. Please try again later.');
            }
        });
    });

    // Function to load the success page
    function loadSuccessPage() {
        $.get('/dashboard/success', function (data) {
            // Replace the content of the main dashboard area with the success page content
            $('.user-dashboard.main-content').html(data);
        });
    }

    // Function to load event details
    function loadEventDetails(eventId) {
        var url = '/dashboard/events/' + eventId + '/details'; // Construct the URL for fetching event details with the prefix
        fetch(url)
            .then(response => response.text())
            .then(html => {
                // Replace the content of the main dashboard area with event details
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to load create event form
    function loadCreateEventForm() {
        // Example: load the create event form
        var url = '/dashboard/events/create'; // Construct the URL for creating event with the prefix
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to load manage tickets page
    function loadManageTickets(eventId) {
        var url = '/dashboard/events/' + eventId + '/tickets';
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }
    // Event listener for manage tickets link


    // Function to load list of events
    function loadListEvents() {
        // Example: load the list of events
        var url = '/dashboard/events/list'; // Construct the URL for listing events with the prefix
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to delete an event
    function deleteEvent(eventId) {
        console.log('Deleting event with ID:', eventId); // Debugging statement
        // Send an AJAX POST request to delete the event
        $.ajax({
            url: '/dashboard/events/' + eventId + '/delete',
            type: 'POST',
            success: function () {
                // Reload the list of events after successful deletion
                loadListEvents();
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseText; // Get the specific error message from the response
                alert('An error occurred while deleting the event: ' + errorMessage); // Display the error message
            }
        }); 
    }
    // Fetch and load list of events when the page loads
    // loadListEvents();
});
