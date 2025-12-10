# dashboard/ai_service.py - SIMPLE TRAINED VERSION
import os
import tensorflow as tf
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class PestDetectionAI:
    def __init__(self):
        self.model = None
        self.class_names = ['sehat', 'hama']
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the trained CNN model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'ml_models/pepper_cnn_trained.h5')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                self.model_loaded = True
                logger.info("✅ Trained CNN model loaded successfully")
            else:
                logger.warning("⚠️ Trained model not found, using fallback mode")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model_loaded = False
    
    def predict(self, image_path, lahan_id=None):
        """Predict using trained model or fallback"""
        try:
            if self.model_loaded and self.model:
                # Load and preprocess image
                img = Image.open(image_path).convert('RGB')
                img = img.resize((150, 150))  # Match training size
                img_array = np.array(img) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                # Make prediction
                predictions = self.model.predict(img_array, verbose=0)
                confidence = float(np.max(predictions[0]))
                class_idx = int(np.argmax(predictions[0]))
                class_name = self.class_names[class_idx]
                
                # Determine severity
                if confidence >= 0.85:
                    severity = "Tinggi"
                elif confidence >= 0.70:
                    severity = "Sedang"
                else:
                    severity = "Rendah"
                
                return {
                    'success': True,
                    'prediction': {
                        'class_name': class_name,
                        'confidence': round(confidence * 100, 2),
                        'severity': severity
                    },
                    'mode': 'trained_cnn',
                    'note': 'Trained CNN Model (2 classes)'
                }
            else:
                # Fallback to development mode
                import time
                time.sleep(1)
                
                # Simple random prediction for development
                class_name = np.random.choice(self.class_names)
                confidence = np.random.uniform(0.75, 0.95)
                
                return {
                    'success': True,
                    'prediction': {
                        'class_name': class_name,
                        'confidence': round(confidence * 100, 2),
                        'severity': 'Tinggi' if confidence > 0.85 else 'Sedang'
                    },
                    'mode': 'development',
                    'note': 'Development mode (trained model not available)'
                }
                
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_status(self):
        """Get model status"""
        return {
            'model_loaded': self.model_loaded,
            'classes': self.class_names,
            'model_name': 'Pepper Disease CNN'
        }

# Create global instance
pest_ai = PestDetectionAI()
