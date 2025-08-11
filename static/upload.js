// Get references to UI elements
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const uploadErrorDiv = document.getElementById('upload-error');
const loadingIndicator = document.getElementById('loading-indicator');
const uploadArea = document.getElementById('upload-area');

// Event listener for file upload submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous error messages
    uploadErrorDiv.textContent = '';

    const files = fileInput.files;
    if (!files.length) {
        uploadErrorDiv.textContent = 'Please select at least one file.';
        return;
    }

    // Show loading state
    uploadArea.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    try {
        // Make the POST request to the API
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        
        // Parse the JSON response from the server
        const result = await response.json();

        // Check if the response indicates an error (e.g., status code not in 2xx range)
        if (!response.ok) {
            // Extract error message from the server response if available
            const errorMessage = result.detail || `Upload failed with status ${response.status}`;
            throw new Error(errorMessage);
        }

        // Store the entire result object (which now includes generated_csv_filename) 
        // in sessionStorage for the results page.
        sessionStorage.setItem('analysisResults', JSON.stringify(result));
        
        // Redirect to the results page
        window.location.href = '/static/results.html';

    } catch (err) {
        // Handle errors: show upload area again and display the error message
        loadingIndicator.classList.add('hidden');
        uploadArea.classList.remove('hidden');
        uploadErrorDiv.textContent = err.message || 'An unexpected error occurred.';
        console.error('Upload error:', err);
    }
});

// Clear file input and error messages when the page loads
// This ensures a clean slate for new uploads.
document.addEventListener('DOMContentLoaded', () => {
    // Reset the file input value
    fileInput.value = '';
    // Clear any potential error messages from a previous failed attempt
    uploadErrorDiv.textContent = '';
});