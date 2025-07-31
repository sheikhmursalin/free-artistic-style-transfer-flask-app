document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const processBtn = document.getElementById('processBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const btnText = document.getElementById('btnText');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const resultContainer = document.getElementById('resultContainer');
    const errorContainer = document.getElementById('errorContainer');
    const resultPreview = document.getElementById('resultPreview');
    const downloadLink = document.getElementById('downloadLink');
    const errorMessage = document.getElementById('errorMessage');
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        const style = document.getElementById('styleSelect').value;
        
        if (!file) {
            showError('Please select a file');
            return;
        }
        
        // Show loading state
        setLoadingState(true);
        hideContainers();
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('style', style);
        
        try {
            // Show progress
            showProgress();
            simulateProgress();
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                showResult(result.result_url, result.download_url, file.type);
            } else {
                showError(result.error || 'Processing failed');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            setLoadingState(false);
        }
    });
    
    function setLoadingState(loading) {
        if (loading) {
            processBtn.disabled = true;
            loadingSpinner.classList.remove('d-none');
            btnText.textContent = 'Processing...';
            processBtn.classList.add('processing');
        } else {
            processBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
            btnText.textContent = '🎨 Transform';
            processBtn.classList.remove('processing');
        }
    }
    
    function showProgress() {
        progressContainer.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressText.textContent = 'Processing your file...';
    }
    
    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            progressBar.style.width = progress + '%';
            
            if (progress < 30) {
                progressText.textContent = 'Analyzing file...';
            } else if (progress < 60) {
                progressText.textContent = 'Applying artistic style...';
            } else {
                progressText.textContent = 'Finalizing result...';
            }
        }, 500);
        
        // Clear interval when done (will be called when result is shown)
        uploadForm.progressInterval = interval;
    }
    
    function showResult(resultUrl, downloadUrl, fileType) {
        if (uploadForm.progressInterval) {
            clearInterval(uploadForm.progressInterval);
        }
        
        // Complete progress
        progressBar.style.width = '100%';
        progressText.textContent = 'Complete!';
        
        setTimeout(() => {
            progressContainer.classList.add('d-none');
            resultContainer.classList.remove('d-none');
            
            // Show preview
            if (fileType.startsWith('video/')) {
                resultPreview.innerHTML = `
                    <video controls class="img-fluid">
                        <source src="${resultUrl}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                `;
            } else {
                resultPreview.innerHTML = `
                    <img src="${resultUrl}" alt="Styled result" class="img-fluid">
                `;
            }
            
            // Set download link
            downloadLink.href = downloadUrl;
        }, 1000);
    }
    
    function showError(message) {
        if (uploadForm.progressInterval) {
            clearInterval(uploadForm.progressInterval);
        }
        
        hideContainers();
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
    }
    
    function hideContainers() {
        progressContainer.classList.add('d-none');
        resultContainer.classList.add('d-none');
        errorContainer.classList.add('d-none');
    }
    
    // File input change handler
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Reset any previous results
            hideContainers();
            
            // Validate file size (100MB)
            if (file.size > 100 * 1024 * 1024) {
                showError('File size must be less than 100MB');
                this.value = '';
                return;
            }
            
            // Show file info
            const fileInfo = document.createElement('div');
            fileInfo.className = 'mt-2 text-muted small';
            fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            
            // Remove any existing file info
            const existingInfo = this.parentNode.querySelector('.file-info');
            if (existingInfo) {
                existingInfo.remove();
            }
            
            fileInfo.className += ' file-info';
            this.parentNode.appendChild(fileInfo);
        }
    });
});

function resetForm() {
    document.getElementById('uploadForm').reset();
    document.getElementById('resultContainer').classList.add('d-none');
    document.getElementById('errorContainer').classList.add('d-none');
    document.getElementById('progressContainer').classList.add('d-none');
    
    // Remove file info
    const fileInfo = document.querySelector('.file-info');
    if (fileInfo) {
        fileInfo.remove();
    }
}

// Drag and drop functionality
function setupDragAndDrop() {
    const fileInput = document.getElementById('fileInput');
    const dropZone = fileInput.parentNode;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropZone.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }
    
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    }
}

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', setupDragAndDrop);