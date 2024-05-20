    $(document).ready(function () {

        // Event listener for create event link
        $('#create-event-link').on('click', function () {
            loadCreateEventForm();
        });

        // Event listener for list event link
        $('#list-event-link').on('click', function () {
            loadListEvents();
        });

        // Event listener for list ticket link
        // $('#list-ticket-link').on('click', function () {
        //     loadListTickets();
        // });

        // Function to load list of tickets
        // function loadListTickets(eventId) {
        //     var url = `/dashboard/events/${eventId}/tickets`; // Update URL according to your Flask route
        //     fetch(url)
        //         .then(response => response.text())
        //         .then(html => {
        //             $('.user-dashboard.main-content').html(html);
        //         })
        //         .catch(error => console.error('Error:', error));
        // }

        // Event listener for booking event link
        $('#book-event-link').on('click', function (event) {
            loadBookEventForm();
        });
    
        function loadBookEventForm() {
            var url = '/dashboard/events/book/form';
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    $('.user-dashboard.main-content').html(html);
                    initializeBookEventForm();
                })
                .catch(error => console.error('Error:', error));
        }
    
        function initializeBookEventForm() {
            $('#event').change(async function () {
                var eventId = $(this).val();
                if (eventId) {
                    try {
                        const response = await fetch(`/dashboard/ticket_types/${eventId}`);
                        const data = await response.json();
                        const ticketTypeSelect = $('#ticket-type');
                        ticketTypeSelect.empty();
                        ticketTypeSelect.append('<option value="">Select Ticket Type</option>');
                        data.forEach(ticketType => {
                            ticketTypeSelect.append(`<option value="${ticketType.id}">${ticketType.name} - ${ticketType.available_tickets} tickets available</option>`);
                        });
                    } catch (error) {
                        console.error('Error fetching ticket types:', error);
                    }
                }
            });
    
            $('#book-ticket-form').on('submit', async function (e) {
                e.preventDefault();
                const formData = new FormData(this);
                try {
                    const response = await fetch('/dashboard/events/book', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    if (response.ok) {
                        window.location.href = `/dashboard/booking/confirmation/${result.booking_id}`; // Redirect to the confirmation page
                    } else {
                        alert('Error booking tickets: ' + result.error);
                    }
                } catch (error) {
                    console.error('Error booking tickets:', error);
                }
            });
        }
        

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

        // Event listener for manage tickets link
        $(document).on('click', '.manage-tickets-btn', function (event) {
            event.preventDefault(); // Prevent default link behavior
            var eventId = $(this).data('event-id');
            loadManageTickets(eventId);
        });

        // Event listener for delete ticket button
        $(document).on('click', '.delete-ticket-btn', function (event) {
            event.preventDefault(); // Prevent default link behavior
            var ticketId = $(this).data('ticket-id');
            var eventId = $(this).closest('.container').data('event-id'); // Assuming you store event ID in a parent container

            deleteTicket(eventId, ticketId);
        });

        // Event listener for submitting the create ticket type form
        $(document).on('submit', '#create-ticket-type-form', function (event) {
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
                    alert('An error occurred while creating the ticket type. Please try again later.');
                }
            });
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
            var url = '/dashboard/events/' + eventId + '/details'; // Construct the URL for fetching event details
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
            var url = '/dashboard/events/create'; // Construct the URL for creating event
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

        // Function to load list of events
        function loadListEvents() {
            var url = '/dashboard/events/list'; // Construct the URL for listing events
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

        // Function to delete a ticket
        function deleteTicket(eventId, ticketId) {
            console.log('Deleting ticket with ID:', ticketId); // Debugging statement
            // Send an AJAX POST request to delete the ticket
            $.ajax({
                url: '/dashboard/events/' + eventId + '/tickets/' + ticketId + '/delete',
                type: 'POST',
                success: function () {
                    // On successful response, load the success page
                    loadSuccessPage();
                },
                error: function (xhr, status, error) {
                    var errorMessage = xhr.responseText; // Get the specific error message from the response
                    alert('An error occurred while deleting the ticket: ' + errorMessage); // Display the error message
                }
            });
        }

        // Fetch and load list of events when the page loads
        // loadListEvents(); // Uncomment to automatically load events on page load
    });
