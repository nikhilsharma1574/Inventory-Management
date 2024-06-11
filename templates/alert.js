
// app.js

// Function to show the alert box
function showAlertBox(message, type) {
    var alertBox = document.getElementById('alert-box');
    var alertMessage = document.getElementById('alert-message');

    alertMessage.innerText = message;
    if (type === 'success') {
        alertBox.classList.remove('bg-red-500', 'border-red-700', 'text-white');
        alertBox.classList.add('bg-green-500', 'border-green-700', 'text-white');
    } else {
        alertBox.classList.remove('bg-green-500', 'border-green-700', 'text-white');
        alertBox.classList.add('bg-red-500', 'border-red-700', 'text-white');
    }

    alertBox.classList.remove('hidden');
}

// Function to hide the alert box
function hideAlertBox() {
    var alertBox = document.getElementById('alert-box');
    alertBox.classList.add('hidden');
}

// Function to handle form submission
document.getElementById('assign-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: '/assign-item',
        data: formData,
        success: function(response) {
            showAlertBox(response.message, 'success');
            if (response.success) {
                setTimeout(function() {
                    window.location.href = '/admin';
                }, 2000); // Redirect after 2 seconds
            }
        },
        error: function(xhr) {
            var response = JSON.parse(xhr.responseText);
            showAlertBox(response.message, 'error');
        }
    });
});


// JavaScript code
document.addEventListener('DOMContentLoaded', function() {
    var flashMessages = document.getElementById('flash-messages');
    var messages = document.getElementsByClassName('flash-message');

    setTimeout(function() {
        while (messages[0]) {
            flashMessages.removeChild(messages[0]);
        }
    }, 3000); // Remove messages after 3 seconds
});

