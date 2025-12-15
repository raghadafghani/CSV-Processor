const API_URL = 'http://localhost:8000';

let currentData = null;

// File upload area interactions
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('csv-file');
const fileName = document.getElementById('file-name');

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.endsWith('.csv')) {
        fileInput.files = files;
        updateFileName(files[0].name);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        updateFileName(e.target.files[0].name);
    }
});

function updateFileName(name) {
    fileName.textContent = name;
    fileName.style.color = '#007AFF';
}

// Operation change handler
document.getElementById('csv-operation').addEventListener('change', (e) => {
    const operation = e.target.value;
    
    // Hide all option groups
    document.querySelectorAll('.option-group').forEach(g => g.style.display = 'none');
    
    // Show relevant option group
    if (operation === 'filter') {
        document.getElementById('filter-options').style.display = 'block';
    } else if (operation === 'transform') {
        document.getElementById('transform-options').style.display = 'block';
    } else if (operation === 'aggregate') {
        document.getElementById('aggregate-options').style.display = 'block';
    } else if (operation === 'sort') {
        document.getElementById('sort-options').style.display = 'block';
    }
});

async function processCSV() {
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a CSV file');
        return;
    }
    
    const operation = document.getElementById('csv-operation').value;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('operation', operation);
    
    // Add operation-specific parameters
    if (operation === 'filter') {
        const column = document.getElementById('filter-column').value.trim();
        const value = document.getElementById('filter-value').value.trim();
        if (!column || !value) {
            alert('Please enter both column name and filter value');
            return;
        }
        formData.append('filter_column', column);
        formData.append('filter_value', value);
    } else if (operation === 'transform') {
        const column = document.getElementById('transform-column').value.trim();
        const op = document.getElementById('transform-op').value;
        if (!column) {
            alert('Please enter column name');
            return;
        }
        formData.append('transform_column', column);
        formData.append('transform_operation', op);
    } else if (operation === 'aggregate') {
        const column = document.getElementById('aggregate-column').value.trim();
        if (!column) {
            alert('Please enter column name');
            return;
        }
        formData.append('filter_column', column);
    } else if (operation === 'sort') {
        const column = document.getElementById('sort-column').value.trim();
        if (!column) {
            alert('Please enter column name');
            return;
        }
        formData.append('filter_column', column);
    }
    
    const resultDiv = document.getElementById('result-section');
    resultDiv.innerHTML = '<div class="loading">Processing CSV file</div>';
    
    const processBtn = document.getElementById('process-btn');
    processBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/api/process/csv`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Processing failed');
        }
        
        const data = await response.json();
        currentData = data;
        displayCSVResult(data, operation);
    } catch (error) {
        resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    } finally {
        processBtn.disabled = false;
    }
}

function displayCSVResult(data, operation) {
    const resultDiv = document.getElementById('result-section');
    let html = '';
    
    if (operation === 'aggregate') {
        html = '<div class="success">✓ Aggregation completed successfully</div>';
        html += '<h3>Aggregation Results</h3>';
        html += '<div class="result-stats">';
        for (const [key, value] of Object.entries(data.aggregation)) {
            html += `
                <div class="stat-card">
                    <div class="stat-value">${value}</div>
                    <div class="stat-label">${key || '(empty)'}</div>
                </div>
            `;
        }
        html += '</div>';
        html += `<p class="result-info">Total rows processed: <strong>${data.total_rows}</strong></p>`;
    } else if (data.rows && data.rows.length > 0) {
        html = '<div class="success">✓ Processing completed successfully</div>';
        html += `<h3>Results</h3>`;
        html += `<p class="result-info">Showing <strong>${data.count}</strong> row${data.count !== 1 ? 's' : ''}</p>`;
        
        // Create table with scrolling
        const headers = data.columns || Object.keys(data.rows[0]);
        html += '<div class="result-table-container">';
        html += '<table class="result-table"><thead><tr>';
        headers.forEach(h => html += `<th>${h}</th>`);
        html += '</tr></thead><tbody>';
        
        // Show all rows - scrolling will handle large datasets
        data.rows.forEach(row => {
            html += '<tr>';
            headers.forEach(h => {
                const cellValue = row[h] || '';
                // Escape HTML to prevent XSS, but allow long text
                const escapedValue = String(cellValue).replace(/</g, '&lt;').replace(/>/g, '&gt;');
                html += `<td title="${escapedValue}">${escapedValue}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        html += '<p class="result-info" style="margin-top: 12px; font-size: 13px; color: #86868B;">';
        html += '💡 Scroll vertically and horizontally to view all data';
        html += '</p>';
        
        // Download button
        html += `
            <button class="download-button" onclick="downloadCSV()">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download CSV
            </button>
        `;
    } else {
        html = '<div class="error">No results found</div>';
    }
    
    resultDiv.innerHTML = html;
}

async function downloadCSV() {
    if (!currentData || !currentData.rows) {
        alert('No data to download');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/download/csv`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentData)
        });
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `processed_${new Date().getTime()}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert(`Error downloading file: ${error.message}`);
    }
}
