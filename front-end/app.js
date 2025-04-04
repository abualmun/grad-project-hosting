document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const imageUpload = document.getElementById('imageUpload');
    const uploadBtn = document.getElementById('uploadBtn');
    const videoElement = document.getElementById('videoElement');
    const captureBtn = document.getElementById('captureBtn');
    const cameraTabs = document.getElementById('imageTabs');
    const loadingElement = document.getElementById('loading');
    const resultsElement = document.getElementById('results');
    const resultImage = document.getElementById('resultImage');
    const classTitle = document.getElementById('classTitle');
    const classDescription = document.getElementById('classDescription');
    const wrongClassBtn = document.getElementById('wrongClassBtn');
    const predictionsList = document.getElementById('predictionsList');
    
    // State variables
    let currentPredictions = [];
    let currentImageData = null;
    let currentPredictionIndex = 0;
    let stream = null;
    
    // API endpoints (change these to your actual deployed backend URLs)
    const API_BASE_URL = process.env.API_URL || 'https://your-backend-url.app';
    const CLASSIFY_ENDPOINT = `${API_BASE_URL}/api/classify`;
    const DESCRIPTION_ENDPOINT = `${API_BASE_URL}/api/description`;
    
    // Enable upload button only when an image is selected
    imageUpload.addEventListener('change', function() {
        uploadBtn.disabled = !imageUpload.files.length;
    });
    
    // Handle image upload classification
    uploadBtn.addEventListener('click', function() {
        if (imageUpload.files.length) {
            const file = imageUpload.files[0];
            processImageFile(file);
        }
    });
    
    // Initialize camera when camera tab is shown
    cameraTabs.addEventListener('shown.bs.tab', function(event) {
        if (event.target.id === 'camera-tab') {
            initCamera();
        } else if (stream) {
            // Stop camera when switching away from camera tab
            stopCamera();
        }
    });
    
    // Capture image from camera
    captureBtn.addEventListener('click', function() {
        captureImage();
    });
    
    // Handle "wrong classification" button
    wrongClassBtn.addEventListener('click', function() {
        currentPredictionIndex++;
        // Check if we have more predictions available
        if (currentPredictionIndex < currentPredictions.length) {
            updateResultDisplay(currentPredictions[currentPredictionIndex]);
        } else {
            // Reset to the first prediction if we've gone through all of them
            currentPredictionIndex = 0;
            updateResultDisplay(currentPredictions[currentPredictionIndex]);
            alert("We've shown all available classifications. Starting from the beginning.");
        }
    });
    
    // Initialize camera
    function initCamera() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(mediaStream) {
                    stream = mediaStream;
                    videoElement.srcObject = mediaStream;
                })
                .catch(function(error) {
                    console.error("Error accessing camera:", error);
                    alert("Unable to access camera. Please make sure you've granted permission.");
                });
        } else {
            alert("Your browser does not support camera access.");
        }
    }
    
    // Stop camera stream
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    }
    
    // Capture image from camera
    function captureImage() {
        if (!stream) return;
        
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(function(blob) {
            const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
            processImageFile(file);
        }, 'image/jpeg');
    }
    
    // Process the image file (either uploaded or captured)
    function processImageFile(file) {
        // Show loading indicator
        loadingElement.style.display = 'block';
        resultsElement.style.display = 'none';
        
        // Create a URL for the image preview
        currentImageData = URL.createObjectURL(file);
        resultImage.src = currentImageData;
        
        // Prepare file for upload
        const formData = new FormData();
        formData.append('image', file);
        
        // Send the image to the backend for classification
        fetch(CLASSIFY_ENDPOINT, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Process predictions
            currentPredictions = data.predictions;
            currentPredictionIndex = 0;
            
            // Display the top prediction
            if (currentPredictions.length > 0) {
                updateResultDisplay(currentPredictions[0]);
                displayAlternativePredictions(currentPredictions);
            } else {
                throw new Error('No predictions returned');
            }
            
            // Hide loading, show results
            loadingElement.style.display = 'none';
            resultsElement.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            loadingElement.style.display = 'none';
            alert("Error classifying image: " + error.message);
        });
    }
    
    // Update the result display with the given prediction
    function updateResultDisplay(prediction) {
        classTitle.textContent = prediction.className;
        classDescription.textContent = prediction.description || 'Loading description...';
        
        // If the description is not included in the prediction, fetch it from the database
        if (!prediction.description) {
            fetch(`${DESCRIPTION_ENDPOINT}/${prediction.classIndex}`)
                .then(response => response.json())
                .then(data => {
                    classDescription.textContent = data.description;
                })
                .catch(error => {
                    console.error('Error fetching description:', error);
                    classDescription.textContent = 'Description not available.';
                });
        }
        
        // Highlight the current prediction in the alternatives list
        const cards = document.querySelectorAll('.prediction-card');
        cards.forEach((card, index) => {
            if (index === currentPredictionIndex) {
                card.classList.add('border-primary', 'bg-light');
            } else {
                card.classList.remove('border-primary', 'bg-light');
            }
        });
    }
    
    // Display alternative predictions
    function displayAlternativePredictions(predictions) {
        // Clear previous predictions
        predictionsList.innerHTML = '';
        
        // Create a card for each prediction
        predictions.forEach((prediction, index) => {
            const predictionCard = document.createElement('div');
            predictionCard.className = `col prediction-card ${index === 0 ? 'border-primary bg-light' : ''}`;
            predictionCard.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${prediction.className}</h5>
                        <p class="card-text">Confidence: ${(prediction.score * 100).toFixed(2)}%</p>
                    </div>
                </div>
            `;
            
            // Add click event to select this prediction
            predictionCard.addEventListener('click', function() {
                currentPredictionIndex = index;
                updateResultDisplay(prediction);
            });
            
            predictionsList.appendChild(predictionCard);
        });
    }
    
    // Clean up when page is unloaded
    window.addEventListener('beforeunload', function() {
        stopCamera();
        if (currentImageData) {
            URL.revokeObjectURL(currentImageData);
        }
    });
});