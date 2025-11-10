// ==================== CONFIGURATION ====================
const API_URL = 'http://localhost:8000';
let currentImageData = null;

// ==================== PAGE NAVIGATION ====================

/**
 * Show the generator page and hide home page
 */
function showGenerator() {
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('generatorPage').classList.add('active');
}

/**
 * Show the home page and hide generator page
 */
function showHome() {
    document.getElementById('homePage').style.display = 'flex';
    document.getElementById('generatorPage').classList.remove('active');
    resetForm();
}

// ==================== FORM HANDLING ====================

/**
 * Initialize form submission handler
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('generatorForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    await generateImage();
}

// ==================== IMAGE GENERATION ====================

/**
 * Generate image from user input
 */
async function generateImage() {
    const description = document.getElementById('imageDescription').value.trim();
    const negativePrompt = document.getElementById('negativePrompt') ? 
        document.getElementById('negativePrompt').value.trim() : 
        "blurry, low quality, distorted, ugly, deformed"; // Default fallback
    const size = document.getElementById('imageSize').value;
    
    // Validate input
    if (!description) {
        showStatus('Please enter an image description', 'error');
        return;
    }

    const [width, height] = size.split('x').map(Number);

    // Show loader and disable button
    showLoader(true);
    setGenerateButtonState(false);
    hideImageResult();
    hideStatus();

    // Get current user ID from session/login (for now use default 1)
    const currentUserId = parseInt(sessionStorage.getItem('userId') || '1');

    // Prepare request data - FIXED: Use actual user input
    const requestData = {
        prompt: description,  // ← Now uses actual input
        negative_prompt: negativePrompt || "",  // ← Now uses actual input or empty
        width: width,
        height: height,
        steps: 50,
        user_id: currentUserId  // ← Dynamic user ID
    };

    console.log('Sending request:', requestData); // Debug log

    try {
        // Call API
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

        // Display the generated image
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
        setGenerateButtonState(true);
    }
}

/**
 * Display the generated image
 */
function displayGeneratedImage(data) {
    const imageUrl = `${API_URL}${data.image_path}?t=${Date.now()}`; // Add timestamp to prevent caching
    const imageElement = document.getElementById('generatedImage');
    
    imageElement.src = imageUrl;
    imageElement.alt = data.prompt;
    
    showImageResult();
}

// ==================== ACTION BUTTONS ====================

/**
 * Regenerate the current image
 */
function regenerateImage() {
    const description = document.getElementById('imageDescription').value.trim();
    
    if (!description) {
        showStatus('Please enter an image description first', 'error');
        return;
    }

    if (confirm('Do you want to regenerate this image with the same description?')) {
        generateImage();
    }
}

/**
 * Delete the current image
 */
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

        // Clear the display
        hideImageResult();
        currentImageData = null;
        showStatus('Image deleted successfully', 'success');

    } catch (error) {
        console.error('Delete error:', error);
        showStatus('Error deleting image: ' + error.message, 'error');
    }
}

/**
 * Save the current image to desktop
 */
async function saveImage() {
    if (!currentImageData) {
        showStatus('No image to save', 'error');
        return;
    }

    try {
        const imageUrl = `${API_URL}${currentImageData.image_path}`;
        
        // Fetch the image as blob
        const response = await fetch(imageUrl);
        if (!response.ok) {
            throw new Error('Failed to fetch image');
        }
        
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-generated-image-${Date.now()}.png`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showStatus('Image saved to your Downloads folder! 💾', 'success');

    } catch (error) {
        console.error('Save error:', error);
        showStatus('Error saving image: ' + error.message, 'error');
    }
}

// ==================== UI HELPER FUNCTIONS ====================

/**
 * Show or hide the loader
 */
function showLoader(show) {
    const loader = document.getElementById('loader');
    if (show) {
        loader.classList.add('active');
    } else {
        loader.classList.remove('active');
    }
}

/**
 * Enable or disable the generate button
 */
function setGenerateButtonState(enabled) {
    const button = document.getElementById('generateBtn');
    button.disabled = !enabled;
}

/**
 * Show the image result section
 */
function showImageResult() {
    document.getElementById('imageResult').classList.add('active');
}

/**
 * Hide the image result section
 */
function hideImageResult() {
    document.getElementById('imageResult').classList.remove('active');
}

/**
 * Show a status message
 */
function showStatus(message, type) {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            hideStatus();
        }, 5000);
    }
}

/**
 * Hide the status message
 */
function hideStatus() {
    const statusEl = document.getElementById('statusMessage');
    statusEl.className = 'status-message hidden';
}

/**
 * Reset the form and clear all states
 */
function resetForm() {
    const form = document.getElementById('generatorForm');
    if (form) {
        form.reset();
    }
    
    hideImageResult();
    hideStatus();
    showLoader(false);
    setGenerateButtonState(true);
    currentImageData = null;
}

// ==================== API HEALTH CHECK ====================

/**
 * Check if backend API is running
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/`);
        const data = await response.json();
        console.log('API Status:', data.message);
    } catch (error) {
        console.warn('Backend API is not running. Please start the server at', API_URL);
    }
}

// Check API health on page load
document.addEventListener('DOMContentLoaded', checkAPIHealth);