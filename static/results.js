// Get references to UI elements
const tableContainer = document.getElementById('table-container');
const downloadPdfBtn = document.getElementById('download-pdf');
const downloadCsvBtn = document.getElementById('download-csv');
const resultsSummary = document.getElementById('results-summary');
const backBtn = document.getElementById('back-btn');

// Store current table data for PDF generation
let currentTableData = null;
// Store the filename for the CSV download
let currentCsvFilename = null; // <-- NEW: Variable to store the filename

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get results from sessionStorage
    const resultsDataString = sessionStorage.getItem('analysisResults');
    
    if (!resultsDataString) {
        // No results found - redirect back to upload page using the correct static path
        alert('No analysis results found. Redirecting to upload page.');
        window.location.href = '/static/index.html'; // <-- CORRECTED REDIRECT
        return;
    }

    try {
        const result = JSON.parse(resultsDataString);
        displayResults(result); // This function will now handle enabling/disabling buttons based on result data

        // Store the CSV filename if available and enable the button
        if (result.csv_generated && result.generated_csv_filename) {
            currentCsvFilename = result.generated_csv_filename; // <-- Store the filename
            downloadCsvBtn.disabled = false; // Ensure button is enabled if filename is present
        } else {
            currentCsvFilename = null; // Clear filename if not generated
            downloadCsvBtn.disabled = true; // Disable button if no filename
        }
    } catch (err) {
        console.error('Error parsing results:', err);
        alert('Error loading results. Redirecting to upload page.');
        window.location.href = '/static/index.html'; // <-- CORRECTED REDIRECT
    }
});

// Function to display results
function displayResults(result) {
    // Display summary information
    let summaryHtml = `<p><strong>Files Uploaded:</strong> ${result.total_files_uploaded || 0}</p>`;
    summaryHtml += `<p><strong>Successfully Processed:</strong> ${result.files_processed_successfully || 0}</p>`;
    summaryHtml += `<p><strong>Failed/Skipped:</strong> ${result.files_failed_or_skipped || 0}</p>`;
    
    if (result.failed_files_details && result.failed_files_details.length > 0) {
        summaryHtml += `<p class="error-message">Failed files: ${result.failed_files_details.join(', ')}</p>`;
    }
    
    resultsSummary.innerHTML = summaryHtml;

    // Display results table
    if (result.results_preview && result.results_preview.length > 0) {
        renderTable(result.results_preview);
        currentTableData = result.results_preview;
        downloadPdfBtn.disabled = false;
    } else {
        tableContainer.innerHTML = '<p class="text-center">No structured data returned for display.</p>';
        downloadPdfBtn.disabled = true;
    }

    // Enable CSV download button if a filename is available from the analysis results
    // This logic is somewhat redundant with the DOMContentLoaded section but ensures it's updated if displayResults is called elsewhere.
    if (result.csv_generated && result.generated_csv_filename) {
        downloadCsvBtn.disabled = false;
    } else {
        downloadCsvBtn.disabled = true;
    }
}

// Function to render the HTML table
function renderTable(data) {
    if (!data || !data.length) {
        tableContainer.innerHTML = '<p class="text-center">No data available to display.</p>';
        return;
    }

    const headers = Object.keys(data[0]);
    let html = '<table id="result-table">';
    
    // Table Header
    html += '<thead><tr>';
    for (const header of headers) {
        // Format header for display (e.g., "title_of_paper" -> "Title Of Paper")
        const formattedHeader = header.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
        html += `<th>${formattedHeader}</th>`;
    }
    html += '</tr></thead>';
    
    // Table Body
    html += '<tbody>';
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(header => {
            // Handle null, empty strings, or 'N/A' for display
            const cellContent = row[header] === null || row[header] === '' || row[header] === 'N/A' 
                ? 'N/A' 
                : row[header];
            
            // IMPORTANT: Ensure newlines are correctly represented for autoTable to break lines.
            // If your text extraction might produce escaped newlines like '\\n', convert them.
            // Assuming typical text extraction, '\n' should be fine. If issues arise, uncomment the replace line.
            let processedContent = String(cellContent);
            // processedContent = processedContent.replace(/\\n/g, "\n"); // Uncomment if your text has escaped newlines

            html += `<td>${escapeHtml(processedContent)}</td>`; // Use escaped content
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    
    tableContainer.innerHTML = html;
}

// Helper function to escape HTML characters for safe rendering
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Event listener for PDF download
downloadPdfBtn.addEventListener('click', () => {
    if (!currentTableData || !currentTableData.length) {
        alert("No data available to download.");
        return;
    }

    try {
        const headers = Object.keys(currentTableData[0]);
        const formattedHeaders = headers.map(h => 
            h.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase())
        );
        
        const rows = currentTableData.map(row => {
            return headers.map(header => {
                const cellContent = row[header] === null || row[header] === '' || row[header] === 'N/A' 
                    ? 'N/A' 
                    : row[header];
                
                let processedContent = String(cellContent);
                // processedContent = processedContent.replace(/\\n/g, "\n"); // Uncomment if your text has escaped newlines

                return processedContent;
            });
        });

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        doc.setFontSize(16);
        doc.text("Research Paper Review Results", 10, 15);

        // Define common styles for all cells, improving readability
        const commonCellStyles = { 
            fontSize: 11,       // INCREASED FONT SIZE for better readability
            cellPadding: 5,     // INCREASED CELL PADDING for more space around text
            overflow: 'linebreak', // Use line breaks to wrap text within cells
            valign: 'middle',   // Vertically align text in the middle of the cell
            // Consider adding 'halign: "left"' if alignment isn't correct, though usually default is left.
        };

        // Add specific styles for headers for consistency
        const headerStyles = {
            ...commonCellStyles, // Inherit common styles
            fontSize: 12,         // Slightly larger font for headers
            fontStyle: 'bold',
            fillColor: [233, 236, 239], // Light grey background
            textColor: [73, 80, 87],    // Dark grey text
            lineWidth: 0.5,             // Border width for headers
            lineColor: [221, 221, 221]  // Light grey border color
        };
        
        // If specific columns need fixed widths (e.g., long titles)
        // const columnStyles = {
        //     'title_of_paper': { cellWidth: 70 }, 
        //     'research_objective': { cellWidth: 80 }
        // };

        doc.autoTable({
            head: [formattedHeaders], // Headers for the table
            body: rows,               // Data rows for the table
            startY: 25,               // Start table below the title
            theme: 'striped',         // Use a striped theme (alternating row colors)
            headStyles: headerStyles, // Apply header styles
            styles: commonCellStyles, // Apply common styles to all cells (unless overridden by columnStyles)
            // columnStyles: columnStyles, // Uncomment and define if specific column tuning is needed
            margin: { top: 20, left: 10, right: 10, bottom: 20 }, // Margins for the PDF page
            didDrawPage: function(data) {
                // Add page numbers if the table spans multiple pages
                if (data.pageCount > 1) { // Only add page numbers if there's more than one page
                    let pageText = `Page ${data.pageNumber}`;
                    doc.setFontSize(10); // Smaller font for page number
                    // Position the page number at the bottom center
                    const pageSize = doc.internal.pageSize;
                    const pageHeight = pageSize.height;
                    const pageWidth = pageSize.width;
                    doc.text(pageText, pageWidth / 2, pageHeight - 10, { align: 'center' });
                }
            }
        });

        doc.save('review_results.pdf');
    } catch (err) {
        console.error('PDF generation error:', err);
        alert('Error generating PDF. Please try again.');
    }
});

// Event listener for CSV download
downloadCsvBtn.addEventListener('click', async () => {
    // --- MODIFIED SECTION START ---
    // Check if we have a filename stored from the upload process
    if (!currentCsvFilename) {
        alert("No specific CSV file available for download. Please ensure analysis was completed successfully.");
        return;
    }

    try {
        // Construct the download URL using the specific filename
        // encodeURIComponent is used to safely include the filename in the URL
        const downloadUrl = `/download/csv/${encodeURIComponent(currentCsvFilename)}`; 
        
        const response = await fetch(downloadUrl);

        if (!response.ok) {
            // Attempt to parse error message from server response
            let errorDetail = `Server responded with status ${response.status}`;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (jsonError) {
                // If response is not JSON or empty, use the status code
            }
            alert(`Failed to download CSV: ${errorDetail}`);
            return;
        }

        // The server now includes the filename in Content-Disposition, but we can use our stored filename as a fallback.
        const disposition = response.headers.get('Content-Disposition');
        let filename = currentCsvFilename; // Default to the filename we know
        if (disposition && disposition.includes('filename=')) {
            // Extract filename from header if present
            filename = disposition.split('filename=')[1].replace(/"/g, '');
        }

        // Download the file using Blob and createObjectURL
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename; // Set the download attribute to the filename
        document.body.appendChild(a);
        a.click(); // Programmatically click the link to trigger download
        window.URL.revokeObjectURL(url); // Clean up the object URL
        document.body.removeChild(a);

    } catch (err) {
        console.error("Error during CSV download:", err);
        alert("An error occurred while downloading the CSV file.");
    }
    // --- MODIFIED SECTION END ---
});

// Event listener for back button
backBtn.addEventListener('click', () => {
    // Clear stored results when navigating back
    sessionStorage.removeItem('analysisResults');
    // Redirect to upload page using the correct static path
    window.location.href = '/static/index.html'; // <-- CORRECTED REDIRECT
});