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

  const API_URL = 'https://sattam-back-end.onrender.com/api/predict';

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
      setPrediction(null);
      setError(null);
    }
  };

  const handleCameraCapture = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
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
      setError("يرجى اختيار صورة أولاً");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Image = reader.result;
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
          setError(data.error || "فشل في التعرف على الصورة");
        }
        setLoading(false);
      };
      reader.readAsDataURL(selectedImage);
    } catch (err) {
      setError("حدث خطأ في الاتصال بالخادم. حاول مرة أخرى.");
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
    <div className="app" dir="rtl">
      <header>
        <h1>استكشف السعودية</h1>
        <p className="subtitle">ارفع صورة لمعْلَم للتعرف عليه أكثر</p>
      </header>

      <main>
        {!previewImage && !prediction && (
          <div className="intro-section">
            <img 
              src={classificationImage} 
              alt="معالم سعودية" 
              className="intro-image" 
            />
            <div className="intro-text">
              <h2>مرحبًا بك في مستكشف معالم السعودية</h2>
              <p>
                هل تسافر في السعودية وتتساءل عن المعالم التي تراها؟ تطبيقنا المدعوم بالذكاء الاصطناعي يمكنه التعرف على المعالم الشهيرة في السعودية وتقديم معلومات عنها. فقط التقط صورة أو قم برفع صورة موجودة لبدء الاستخدام!
              </p>
              <p>
                نستطيع التعرف على 14 معلمًا شهيرًا بما في ذلك المسجد الحرام، العلا، المسجد النبوي، وغيرهم الكثير.
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
                <FaUpload /> رفع صورة
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
                <FaCamera /> التقاط صورة
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
                  alt="معاينة" 
                  className="preview-image" 
                />
                <button 
                  className="classify-button" 
                  onClick={handleClassify}
                  disabled={loading}
                >
                  {loading ? "جارٍ التعرف..." : "تعرّف على المعلم"}
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
                alt="تم الرفع" 
                className="result-image" 
              />
              
              <div className="result-details">
                <h2>تم التعرف على المعلم!</h2>
                <div className="result-name">
                  <span>{prediction.class}</span>
                  <div className="confidence">
                    نسبة الدقة: {prediction.confidence}%
                  </div>
                </div>
                <div className="result-description">
                  {prediction.description}
                </div>
              </div>
            </div>
            <button className="reset-button" onClick={handleReset}>
              <FaRedo /> إعادة تعرّف
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
