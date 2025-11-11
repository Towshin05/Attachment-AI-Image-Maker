
const API_URL = 'http://localhost:8000';
let currentImageData = null;
let currentInputMode = 'text'; 


function showGenerator() {
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('generatorPage').classList.add('active');
}


function showHome() {
    document.getElementById('homePage').style.display = 'flex';
    document.getElementById('generatorPage').classList.remove('active');
    resetForm();
}


function switchInputMode(mode) {
    currentInputMode = mode;
    
    const textModeBtn = document.getElementById('textModeBtn');
    const pdfModeBtn = document.getElementById('pdfModeBtn');
    const textForm = document.getElementById('generatorForm');
    const pdfForm = document.getElementById('pdfUploadForm');
    
    if (mode === 'text') {
        textModeBtn.classList.add('active');
        pdfModeBtn.classList.remove('active');
        textForm.classList.add('active');
        pdfForm.classList.remove('active');
    } else {
        pdfModeBtn.classList.add('active');
        textModeBtn.classList.remove('active');
        pdfForm.classList.add('active');
        textForm.classList.remove('active');
    }
    
   
    hideImageResult();
    hideStatus();
}


function handleFileSelect(event) {
    const file = event.target.files[0];
    const fileDisplay = document.getElementById('fileDisplay');
    
    if (file) {
        fileDisplay.innerHTML = `
            <span class="file-icon">📄</span>
            <span class="file-text">${file.name}</span>
            <span class="file-size">(${(file.size / 1024).toFixed(2)} KB)</span>
        `;
        fileDisplay.classList.add('file-selected');
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const textForm = document.getElementById('generatorForm');
    const pdfForm = document.getElementById('pdfUploadForm');
    
    if (textForm) {
        textForm.addEventListener('submit', handleTextFormSubmit);
    }
    
    if (pdfForm) {
        pdfForm.addEventListener('submit', handlePdfFormSubmit);
    }
    
    const fileInput = document.getElementById('pdfFile');
    const fileDisplay = document.getElementById('fileDisplay');
    
    if (fileDisplay && fileInput) {
        fileDisplay.addEventListener('click', () => fileInput.click());
        
        fileDisplay.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileDisplay.classList.add('drag-over');
        });
        
        fileDisplay.addEventListener('dragleave', () => {
            fileDisplay.classList.remove('drag-over');
        });
        
        fileDisplay.addEventListener('drop', (e) => {
            e.preventDefault();
            fileDisplay.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                fileInput.files = files;
                handleFileSelect({ target: { files: files } });
            } else {
                showStatus('Please drop a PDF file', 'error');
            }
        });
    }
});


async function handleTextFormSubmit(e) {
    e.preventDefault();
    await generateImage();
}


async function handlePdfFormSubmit(e) {
    e.preventDefault();
    await generateFromPDF();
}

async function generateImage() {
    const description = document.getElementById('imageDescription').value.trim();
    const negativePrompt = document.getElementById('negativePrompt') ? 
        document.getElementById('negativePrompt').value.trim() : 
        "blurry, low quality, distorted, ugly, deformed";
    const size = document.getElementById('imageSize').value;
    
    if (!description) {
        showStatus('Please enter an image description', 'error');
        return;
    }

    const [width, height] = size.split('x').map(Number);
    const currentUserId = parseInt(sessionStorage.getItem('userId') || '1');

    const requestData = {
        prompt: description,
        negative_prompt: negativePrompt || "",
        width: width,
        height: height,
        steps: 50,
        user_id: currentUserId
    };

    showLoader(true);
    setGenerateButtonState(false, 'text');
    hideImageResult();
    hideStatus();

    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate image');
        }

        const data = await response.json();
        currentImageData = data;

        displayGeneratedImage(data);
        showStatus('Image generated successfully! 🎉', 'success');

    } catch (error) {
        console.error('Generation error:', error);
        showStatus(
            'Error: ' + error.message + '. Please make sure the backend server is running at ' + API_URL,
            'error'
        );
    } finally {
        showLoader(false);
        setGenerateButtonState(true, 'text');
    }
}


async function generateFromPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('Please select a PDF file', 'error');
        return;
    }
    
    if (!file.name.endsWith('.pdf')) {
        showStatus('Please upload a PDF file', 'error');
        return;
    }
    
    const negativePrompt = document.getElementById('pdfNegativePrompt').value.trim();
    const size = document.getElementById('pdfImageSize').value;
    const [width, height] = size.split('x').map(Number);
    const currentUserId = parseInt(sessionStorage.getItem('userId') || '1');
    
    showLoader(true);
    setGenerateButtonState(false, 'pdf');
    hideImageResult();
    hideStatus();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('negative_prompt', negativePrompt);
        formData.append('width', width.toString());
        formData.append('height', height.toString());
        formData.append('steps', '50');
        formData.append('user_id', currentUserId.toString());
        
        const response = await fetch(`${API_URL}/generate-from-pdf`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate image from PDF');
        }
        
        const data = await response.json();
        currentImageData = data;
        
        displayGeneratedImage(data);
        showStatus('Image generated from PDF successfully! 🎉', 'success');
        
    } catch (error) {
        console.error('PDF generation error:', error);
        showStatus(
            'Error: ' + error.message + '. Please make sure the PDF contains readable text.',
            'error'
        );
    } finally {
        showLoader(false);
        setGenerateButtonState(true, 'pdf');
    }
}


function displayGeneratedImage(data) {
    const imageUrl = `${API_URL}${data.image_path}?t=${Date.now()}`;
    const imageElement = document.getElementById('generatedImage');
    
    imageElement.src = imageUrl;
    imageElement.alt = data.prompt;
    
    showImageResult();
}


function regenerateImage() {
    if (currentInputMode === 'text') {
        const description = document.getElementById('imageDescription').value.trim();
        
        if (!description) {
            showStatus('Please enter an image description first', 'error');
            return;
        }
        
        if (confirm('Do you want to regenerate this image with the same description?')) {
            generateImage();
        }
    } else {
        const fileInput = document.getElementById('pdfFile');
        
        if (!fileInput.files[0]) {
            showStatus('Please upload a PDF file first', 'error');
            return;
        }
        
        if (confirm('Do you want to regenerate this image from the same PDF?')) {
            generateFromPDF();
        }
    }
}


async function deleteImage() {
    if (!currentImageData) {
        showStatus('No image to delete', 'error');
        return;
    }

    if (!confirm('Are you sure you want to delete this image? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/delete/${currentImageData.image_id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete image');
        }

        hideImageResult();
        currentImageData = null;
        showStatus('Image deleted successfully', 'success');

    } catch (error) {
        console.error('Delete error:', error);
        showStatus('Error deleting image: ' + error.message, 'error');
    }
}


async function saveImage() {
    if (!currentImageData) {
        showStatus('No image to save', 'error');
        return;
    }

    try {
        const imageUrl = `${API_URL}${currentImageData.image_path}`;
        
        const response = await fetch(imageUrl);
        if (!response.ok) {
            throw new Error('Failed to fetch image');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-generated-image-${Date.now()}.png`;
        
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showStatus('Image saved to your Downloads folder! 💾', 'success');

    } catch (error) {
        console.error('Save error:', error);
        showStatus('Error saving image: ' + error.message, 'error');
    }
}


function showLoader(show) {
    const loader = document.getElementById('loader');
    if (show) {
        loader.classList.add('active');
    } else {
        loader.classList.remove('active');
    }
}


function setGenerateButtonState(enabled, mode = 'text') {
    const buttonId = mode === 'text' ? 'generateBtn' : 'generatePdfBtn';
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = !enabled;
    }
}


function showImageResult() {
    document.getElementById('imageResult').classList.add('active');
}


function hideImageResult() {
    document.getElementById('imageResult').classList.remove('active');
}


function showStatus(message, type) {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    
    if (type === 'success') {
        setTimeout(() => {
            hideStatus();
        }, 5000);
    }
}


function hideStatus() {
    const statusEl = document.getElementById('statusMessage');
    statusEl.className = 'status-message hidden';
}


function resetForm() {
    const textForm = document.getElementById('generatorForm');
    const pdfForm = document.getElementById('pdfUploadForm');
    
    if (textForm) textForm.reset();
    if (pdfForm) pdfForm.reset();
    
    const fileDisplay = document.getElementById('fileDisplay');
    if (fileDisplay) {
        fileDisplay.innerHTML = `
            <span class="file-icon">📄</span>
            <span class="file-text">Choose a PDF file or drag & drop</span>
        `;
        fileDisplay.classList.remove('file-selected');
    }
    
    hideImageResult();
    hideStatus();
    showLoader(false);
    setGenerateButtonState(true, 'text');
    setGenerateButtonState(true, 'pdf');
    currentImageData = null;
    
    switchInputMode('text');
}


async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/`);
        const data = await response.json();
        console.log('API Status:', data.message);
    } catch (error) {
        console.warn('Backend API is not running. Please start the server at', API_URL);
    }
}

document.addEventListener('DOMContentLoaded', checkAPIHealth);