$(document).ready(function () {
    // Event listener for create event link
    $('#create-event-link').on('click', function () {
        loadCreateEventForm();
    });

    // Event listener for list event link
    $('#list-event-link').on('click', function () {
        loadListEvents();
    });

    $(document).ready(function () {
        $('#payment-link').on('click', function (e) {
            e.preventDefault();
            loadPaymentForm();
        });
    
        function loadPaymentForm() {
            var url = '/payment/form'; // Correct URL for the payment form
            fetch(url)
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    }
                    throw new Error('Network response was not ok.');
                })
                .then(html => {
                    $('.user-dashboard.main-content').html(html);
                    initializePaymentForm(); // Initialize payment form after loading
                })
                .catch(error => console.error('Error:', error));
        }
    
        function initializePaymentForm() {
            const stripe = Stripe('your-publishable-key-here'); // Replace with your actual publishable key
            const elements = stripe.elements();
            const card = elements.create('card');
            card.mount('#card-element');
    
            card.on('change', function (event) {
                const displayError = document.getElementById('card-errors');
                if (event.error) {
                    displayError.textContent = event.error.message;
                } else {
                    displayError.textContent = '';
                }
            });
    
            const form = document.getElementById('payment-form');
            form.addEventListener('submit', async function (event) {
                event.preventDefault();
    
                const { token, error } = await stripe.createToken(card);
    
                if (error) {
                    const errorElement = document.getElementById('card-errors');
                    errorElement.textContent = error.message;
                } else {
                    const formData = new FormData(form);
                    formData.append('stripeToken', token.id);
    
                    try {
                        const response = await fetch(form.action, {
                            method: 'POST',
                            body: formData
                        });
    
                        const result = await response.json();
                        if (response.ok) {
                            alert('Payment successful!');
                            // Optionally redirect or update the UI
                        } else {
                            alert('Payment failed: ' + result.error);
                        }
                    } catch (error) {
                        console.error('Error:', error);
                    }
                }
            });
        }
    });    

    // Event listener for booking event link
    $('#book-event-link').on('click', function () {
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
                    loadBookingConfirmation(result.booking_id);
                } else {
                    alert('Error booking tickets: ' + result.error);
                }
            } catch (error) {
                console.error('Error booking tickets:', error);
            }
        });
    }

    function loadBookingConfirmation(bookingId) {
        var url = `/dashboard/booking/confirmation/${bookingId}`;
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
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
            .catch(error => {
                console.error('Error loading edit event page:', error);
                alert('An error occurred while loading the edit event page. Please try again later.');
            });
    });

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
            success: function (data) {
                // On successful response, load the event details page
                loadEventDetails(data.event_id);
            },
            error: function () {
                // Handle any errors if the request fails
                alert('An error occurred while updating the event. Please try again later.');
            }
        });
    });

    // Function to load the create event form
    function loadCreateEventForm() {
        var url = '/dashboard/events/create'; // Adjust URL according to your Flask route
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to load the list events page
    function loadListEvents() {
        var url = '/dashboard/events/list'; // Adjust URL according to your Flask route
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to load event details
    function loadEventDetails(eventId) {
        var url = '/dashboard/events/' + eventId;
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to delete an event
    function deleteEvent(eventId) {
        var url = '/dashboard/events/' + eventId + '/delete'; // Adjust URL according to your Flask route
        fetch(url, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadListEvents(); // Reload the list of events after deletion
                } else {
                    alert('Error deleting event.');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to load manage tickets page
    function loadManageTickets(eventId) {
        var url = '/dashboard/events/' + eventId + '/manage_tickets'; // Adjust URL according to your Flask route
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to delete a ticket
    function deleteTicket(eventId, ticketId) {
        var url = '/dashboard/events/' + eventId + '/tickets/' + ticketId + '/delete'; // Adjust URL according to your Flask route
        fetch(url, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadManageTickets(eventId); // Reload the manage tickets page after deletion
                } else {
                    alert('Error deleting ticket.');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to load success page
    function loadSuccessPage() {
        var url = '/dashboard/success';
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('.user-dashboard.main-content').html(html);
            })
            .catch(error => console.error('Error:', error));
    }
});
