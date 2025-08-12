document.addEventListener('DOMContentLoaded', () => {
    // Get references to UI elements - MUST BE INSIDE DOMContentLoaded
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadErrorDiv = document.getElementById('upload-error');
    const loadingIndicator = document.getElementById('loading-indicator');
    const uploadArea = document.getElementById('upload-area');
    const fileNameDisplay = document.getElementById('file-name-display');

    // Check if essential elements exist before proceeding
    if (!uploadForm || !fileInput || !uploadErrorDiv || !loadingIndicator || !uploadArea || !fileNameDisplay) {
        console.error("One or more essential UI elements not found. Check HTML IDs.");
        return; // Stop script execution if elements are missing
    }

    // Add event listener to update filename display when files are selected
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length === 0) {
            fileNameDisplay.textContent = 'No files chosen';
        } else if (files.length === 1) {
            fileNameDisplay.textContent = files[0].name;
        } else {
            // Display count if multiple files are selected
            fileNameDisplay.textContent = `${files.length} files selected`;
        }
    });

    // Event listener for file upload submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        console.log("Submit event triggered."); // Debug 1: Confirms the submit listener fires

        uploadErrorDiv.textContent = ''; // Clear previous error

        const files = fileInput.files; // Access fileInput here, now guaranteed to exist
        if (!files.length) {
            console.log("No files selected, showing error."); // Debug 2: For when no files are picked
            uploadErrorDiv.textContent = 'Please select at least one file.';
            // Ensure loading indicator is hidden if an error occurs before upload
            loadingIndicator.classList.add('hidden');
            uploadArea.classList.remove('hidden');
            return; // Exit if no files are selected
        }

        console.log("Files selected. About to hide upload area and show loading indicator."); // Debug 3: Indicates files were selected

        // Show loading state
        uploadArea.classList.add('hidden');
        loadingIndicator.classList.remove('hidden'); // This is where the "Processing..." message should appear

        const formData = new FormData();
        let appendedFilesCount = 0;
        for (const file of files) {
            formData.append('files', file);
            appendedFilesCount++;
        }
        
        if (appendedFilesCount === 0) {
            console.log("Appended files count is zero, showing error."); // Debug 4: Handles edge case of empty file list despite selection
            uploadErrorDiv.textContent = 'No files were successfully selected.';
            loadingIndicator.classList.add('hidden'); // Hide loading indicator again
            uploadArea.classList.remove('hidden');   // Show upload area again
            fileNameDisplay.textContent = 'No files chosen'; // Reset filename display
            fileInput.value = ''; // Clear the file input
            return; // Exit
        }

        try {
            console.log("Initiating fetch request to /upload/"); // Debug 5: Indicates the upload process is starting
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();

            if (!response.ok) {
                // If response is not OK, throw an error that will be caught below
                const errorMessage = result.detail || `Upload failed with status ${response.status}`;
                throw new Error(errorMessage);
            }

            console.log("Fetch successful, storing results and redirecting.");
            sessionStorage.setItem('analysisResults', JSON.stringify(result));
            window.location.href = '/static/results.html'; // Redirect to results page

        } catch (err) {
            console.error('Upload error caught:', err); // Debug 7: Catches any errors during fetch or JSON parsing
            // Handle errors: show upload area again and display the error message
            loadingIndicator.classList.add('hidden'); // Hide the loading indicator on error
            uploadArea.classList.remove('hidden');   // Show upload area again
            uploadErrorDiv.textContent = err.message || 'An unexpected error occurred.';
            // Reset filename display on error
            fileNameDisplay.textContent = 'No files chosen';
            fileInput.value = ''; // Clear the file input
        }
    });

    // Reset UI elements on page load - this part was already correctly wrapped
    console.log("DOM fully loaded. Resetting UI elements.");
    fileInput.value = '';
    fileNameDisplay.textContent = 'No files chosen';
    uploadErrorDiv.textContent = '';
    loadingIndicator.classList.add('hidden'); // Ensure loading indicator is hidden on initial load
});