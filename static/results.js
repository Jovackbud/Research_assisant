// Get references to UI elements
const tableContainer = document.getElementById('table-container');
const downloadPdfBtn = document.getElementById('download-pdf');
const downloadCsvBtn = document.getElementById('download-csv');
const resultsSummaryDiv = document.getElementById('results-summary'); // Renamed for clarity
const backBtn = document.getElementById('back-btn');
const apiKeyWarningDiv = document.getElementById('api-key-warning'); // Get the new warning div

// Store ALL processed data for PDF generation and table display
let currentFullTableData = null;
// Store the filename for the CSV download
let currentCsvFilename = null;
// Store the filename for the PDF download
let currentPdfFilename = null; // <-- NEW: Variable to store the PDF filename

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get results from sessionStorage
    const resultsDataString = sessionStorage.getItem('analysisResults');
    
    if (!resultsDataString) {
        alert('No analysis results found. Redirecting to upload page.');
        window.location.href = '/static/index.html'; // CORRECTED REDIRECT
        return;
    }

    try {
        const result = JSON.parse(resultsDataString);
        
        displaySummary(result);

        // Store ALL processed data for PDF generation and table display
        currentFullTableData = result.all_processed_data || []; 
        
        // Display table with ALL data if available, otherwise show a message
        if (currentFullTableData.length > 0) {
            renderTable(currentFullTableData); // Render the full data
            downloadPdfBtn.disabled = false; // Enable PDF button only if we have data
        } else {
            tableContainer.innerHTML = '<p class="text-center">No structured data returned for display.</p>';
            downloadPdfBtn.disabled = true;
        }

        // Handle CSV download button enablement
        if (result.csv_generated && result.generated_csv_filename) {
            currentCsvFilename = result.generated_csv_filename;
            downloadCsvBtn.disabled = false;
        } else {
            currentCsvFilename = null;
            downloadCsvBtn.disabled = true;
        }
        
        // --- Store PDF Filename ---
        // Use the new 'generated_pdf_filename' key from the backend response
        if (result.generated_pdf_filename) {
            currentPdfFilename = result.generated_pdf_filename;
            // The PDF button enablement is already handled by checking currentFullTableData.length
        } else {
            currentPdfFilename = null; // Ensure filename is cleared if not generated
        }
        // --- END Store PDF Filename ---

        // API Key Warning Logic
        const isApiKeyIssue = result.files_processed_successfully === 0 && 
                              result.files_failed_or_skipped > 0 &&
                              result.failed_files_details.some(detail => detail.includes("API key missing or invalid"));

        if (isApiKeyIssue) {
            apiKeyWarningDiv.textContent = "Error: Google AI API key is missing or invalid. AI review could not be performed. Please check your server configuration and ensure the 'google_ai_studio_key' is set in your .env file.";
            apiKeyWarningDiv.classList.remove('hidden');
            // Disable download buttons if no data was processed due to API key issue
            downloadPdfBtn.disabled = true;
            downloadCsvBtn.disabled = true;
        } else {
            // Ensure the warning div is hidden if it's not an API key issue
            apiKeyWarningDiv.classList.add('hidden'); 
        }

    } catch (err) {
        console.error('Error parsing results:', err);
        alert('Error loading results. Redirecting to upload page.');
        window.location.href = '/static/index.html'; // CORRECTED REDIRECT
    }
});

// Function to display summary information
function displaySummary(result) {
    let summaryHtml = `<p><strong>Files Uploaded:</strong> ${result.total_files_uploaded || 0}</p>`;
    summaryHtml += `<p><strong>Successfully Processed:</strong> ${result.files_processed_successfully || 0}</p>`;
    summaryHtml += `<p><strong>Failed/Skipped:</strong> ${result.files_failed_or_skipped || 0}</p>`;
    
    if (result.failed_files_details && result.failed_files_details.length > 0) {
        // Filter out API key errors from the general list if we're showing the specific warning above
        const nonApiKeyErrors = result.failed_files_details.filter(detail => !detail.includes("API key missing or invalid"));
        if (nonApiKeyErrors.length > 0) {
            summaryHtml += `<p class="error-message">Failed files: ${nonApiKeyErrors.join(', ')}</p>`;
        }
    }
    
    resultsSummaryDiv.innerHTML = summaryHtml;
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
        const formattedHeader = header.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
        html += `<th>${formattedHeader}</th>`;
    }
    html += '</tr></thead>';
    
    // Table Body
    html += '<tbody>';
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(header => {
            const cellContent = row[header] === null || row[header] === '' || row[header] === 'N/A' 
                ? 'N/A' 
                : row[header];
            
            let processedContent = String(cellContent);
            html += `<td>${escapeHtml(processedContent)}</td>`;
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
    if (!currentFullTableData || !currentFullTableData.length) {
        alert("No data available to generate PDF.");
        return;
    }

    try {
        const headers = Object.keys(currentFullTableData[0]);
        const formattedHeaders = headers.map(h => 
            h.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase())
        );
        
        const rows = currentFullTableData.map(row => {
            return headers.map(header => {
                const cellContent = row[header] === null || row[header] === '' || row[header] === 'N/A' 
                    ? 'N/A' 
                    : row[header];
                
                let processedContent = String(cellContent);
                return processedContent;
            });
        });

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'landscape' }); 

        doc.setFontSize(16);
        doc.text("Research Paper Review Results", 10, 15);

        const commonCellStyles = { 
            fontSize: 9,
            cellPadding: 3,
            overflow: 'linebreak',
            valign: 'top',
        };

        const headerStyles = {
            ...commonCellStyles,
            fontSize: 10,
            fontStyle: 'bold',
            fillColor: [233, 236, 239],
            textColor: [73, 80, 87],
            lineWidth: 0.5,
            lineColor: [221, 221, 221]
        };

        const columnStyles = {
            'title_of_paper': { columnWidth: 50 },
            'author': { columnWidth: 40 },
            'year_of_publication': { columnWidth: 20 },
            'country_of_publication': { columnWidth: 25 },
            'research_objective': { columnWidth: 50 },
            'independent_variable_or_cause': { columnWidth: 40 },
            'dependent_variable_or_effect': { columnWidth: 40 },
            'estimation_techniques': { columnWidth: 40 },
            'theory': { columnWidth: 40 },
            'methods': { columnWidth: 45 },
            'findings': { columnWidth: 55 },
            'recommendations': { columnWidth: 50 },
            'research_gap': { columnWidth: 45 },
            'references': { columnWidth: 35 },
            'remarks': { columnWidth: 35 }
        };

        doc.autoTable({
            head: [formattedHeaders],
            body: rows,
            startY: 25,
            theme: 'striped',
            headStyles: headerStyles,
            styles: commonCellStyles,
            columnStyles: columnStyles,
            margin: { top: 20, left: 5, right: 5, bottom: 20 },
            didDrawPage: function(data) {
                if (data.pageCount > 1) {
                    let pageText = `Page ${data.pageNumber}`;
                    doc.setFontSize(10);
                    const pageSize = doc.internal.pageSize;
                    const pageHeight = pageSize.height;
                    const pageWidth = pageSize.width;
                    doc.text(pageText, pageWidth / 2, pageHeight - 10, { align: 'center' });
                }
            }
        });

        // MODIFIED PDF Save: Use the dynamically generated filename
        doc.save(currentPdfFilename || 'review_results.pdf'); // <-- Use dynamic filename, with fallback
    } catch (err) {
        console.error('PDF generation error:', err);
        alert('Error generating PDF. Please try again.');
    }
});

// Event listener for CSV download (remains the same)
downloadCsvBtn.addEventListener('click', async () => {
    if (!currentCsvFilename) {
        alert("No specific CSV file available for download. Please ensure analysis was completed successfully.");
        return;
    }

    try {
        const downloadUrl = `/download/csv/${encodeURIComponent(currentCsvFilename)}`; 
        
        const response = await fetch(downloadUrl);

        if (!response.ok) {
            let errorDetail = `Server responded with status ${response.status}`;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (jsonError) {}
            alert(`Failed to download CSV: ${errorDetail}`);
            return;
        }

        const disposition = response.headers.get('Content-Disposition');
        let filename = currentCsvFilename;
        if (disposition && disposition.includes('filename=')) {
            filename = disposition.split('filename=')[1].replace(/"/g, '');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (err) {
        console.error("Error during CSV download:", err);
        alert("An error occurred while downloading the CSV file.");
    }
});

// Event listener for back button
backBtn.addEventListener('click', () => {
    sessionStorage.removeItem('analysisResults');
    window.location.href = '/static/index.html'; // CORRECTED REDIRECT
});