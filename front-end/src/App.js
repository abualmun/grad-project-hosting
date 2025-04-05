// App.js
import React, { useState, useRef } from 'react';
import './App.css';
import classificationImage from './assets/saudi-landmarks.jpg';
import { FaCamera, FaUpload, FaRedo } from 'react-icons/fa';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  // API endpoint - change this to your deployed backend URL
  const API_URL = 'https://your-backend-url.onrender.com/api/predict';

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
      
      // Reset prediction
      setPrediction(null);
      setError(null);
    }
  };

  const handleCameraCapture = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
      
      // Reset prediction
      setPrediction(null);
      setError(null);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleCameraClick = () => {
    cameraInputRef.current.click();
  };

  const handleClassify = async () => {
    if (!selectedImage) {
      setError("Please select an image first");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Convert image to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Image = reader.result;
        
        // Call API
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image: base64Image }),
        });
        
        const data = await response.json();
        
        if (data.success) {
          setPrediction(data);
        } else {
          setError(data.error || "Failed to classify image");
        }
        
        setLoading(false);
      };
      reader.readAsDataURL(selectedImage);
    } catch (err) {
      setError("Error connecting to the server. Please try again.");
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setPreviewImage(null);
    setPrediction(null);
    setError(null);
  };

  return (
    <div className="app">
      <header>
        <h1>Discover Saudi Arabia</h1>
        <p className="subtitle">Upload a photo of a landmark to learn more about it</p>
      </header>

      <main>
        {!previewImage && !prediction && (
          <div className="intro-section">
            <img 
              src={classificationImage} 
              alt="Saudi Landmarks" 
              className="intro-image" 
            />
            <div className="intro-text">
              <h2>Welcome to Saudi Landmark Explorer</h2>
              <p>
                Traveling in Saudi Arabia and curious about the landmarks you see?
                Our AI-powered app can identify famous Saudi landmarks and provide 
                you with information about them. Simply take a photo or upload an 
                existing image to get started!
              </p>
              <p>
                We can identify 14 famous landmarks including Al-Haram Mosque, 
                AlUla, The Prophet's Mosque, and many more.
              </p>
            </div>
          </div>
        )}

        {!prediction ? (
          <div className="upload-section">
            <div className="button-group">
              <button 
                className="upload-button" 
                onClick={handleUploadClick}
              >
                <FaUpload /> Upload Image
              </button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageChange}
                accept="image/*"
                className="hidden-input"
              />
              
              <button 
                className="camera-button" 
                onClick={handleCameraClick}
              >
                <FaCamera /> Take Photo
              </button>
              <input
                type="file"
                ref={cameraInputRef}
                onChange={handleCameraCapture}
                accept="image/*"
                capture="environment"
                className="hidden-input"
              />
            </div>

            {previewImage && (
              <div className="preview-container">
                <img 
                  src={previewImage} 
                  alt="Preview" 
                  className="preview-image" 
                />
                <button 
                  className="classify-button" 
                  onClick={handleClassify}
                  disabled={loading}
                >
                  {loading ? "Classifying..." : "Identify Landmark"}
                </button>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
          </div>
        ) : (
          <div className="result-section">
            <div className="result-container">
              <img 
                src={previewImage} 
                alt="Uploaded" 
                className="result-image" 
              />
              
              <div className="result-details">
                <h2>Landmark Identified!</h2>
                <div className="result-name">
                  <span>{prediction.class}</span>
                  <div className="confidence">
                    Confidence: {prediction.confidence}%
                  </div>
                </div>
                
                <div className="result-description">
                  {prediction.description}
                </div>
                
                <button 
                  className="try-again-button" 
                  onClick={handleReset}
                >
                  <FaRedo /> Try Another Image
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer>
        <p>Explore the beauty and history of Saudi Arabia</p>
        <p>© 2025 Saudi Landmark Explorer</p>
      </footer>
    </div>
  );
}

export default App;