# dashboard/ai_service.py - IMPROVED VERSION
import os
import tensorflow as tf
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class PestDetectionAI:
    def __init__(self):
        self.model = None
        # Class names yang lebih deskriptif
        self.class_names = [
            "Daun Cabai Sehat",
            "Penyakit Bercak Bakteri (Bacterial Spot)"
        ]
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the trained CNN model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'ml_models/pepper_cnn_trained.h5')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                self.model_loaded = True
                logger.info("✅ Model CNN terlatih berhasil dimuat")
            else:
                logger.warning("⚠️ Model terlatih tidak ditemukan")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model_loaded = False
    
    def get_disease_info(self, class_name, confidence):
        """Get detailed disease information based on prediction"""
        
        disease_database = {
            "Daun Cabai Sehat": {
                "status": "SEHAT",
                "pest_name": "Tidak Ada Hama Dan Penyakit",
                "description": "Tanaman dalam kondisi sehat",
                "symptoms": "Daun berwarna hijau segar, tidak ada bercak atau kerusakan",
                "recommendation": "Pertahankan perawatan rutin. Monitor kondisi tanaman setiap minggu."
            },
            "Penyakit Bercak Bakteri (Bacterial Spot)": {
                "status": "",
                "pest_name": "Penyakit Bercak Bakteri (Bacterial Spot)",
                "description": "Penyakit bercak bakteri pada daun cabai",
                "symptoms": "Bercak kecil berair pada daun, berubah menjadi coklat dengan pinggiran kuning",
                "causes": "Bakteri Xanthomonas campestris pv. vesicatoria",
                "recommendation": "1. Gunakan fungisida tembaga\n2. Buang daun terinfeksi parah\n3. Hindari penyiraman di atas daun\n4. Rotasi tanaman"
            }
        }
        
        # Default jika tidak ditemukan
        default_info = {
            "status": "TERDETEKSI" if class_name != "Daun Cabai Sehat" else "SEHAT",
            "pest_name": class_name,
            "description": class_name,
            "recommendation": "Konsultasikan dengan penyuluh pertanian"
        }
        
        return disease_database.get(class_name, default_info)
    
    def determine_severity_level(self, confidence, class_name):
        """Tentukan tingkat keparahan: Aman, Rendah, Sedang, Tinggi"""
        
        if class_name == "Daun Cabai Sehat":
            return "Aman"
        
        # Logika untuk penyakit
        if confidence >= 0.90:
            return "Tinggi"
        elif confidence >= 0.75:
            return "Sedang"
        elif confidence >= 0.60:
            return "Rendah"
        else:
            return "Aman"
    
    def predict(self, image_path, lahan_id=None):
        """Predict dengan output yang lebih informatif"""
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
                
                # Get disease info
                disease_info = self.get_disease_info(class_name, confidence)
                
                # Determine severity
                severity = self.determine_severity_level(confidence, class_name)
                
                # Determine overall condition
                condition = "SEHAT" if class_name == "Daun Cabai Sehat" else "TERKENA PENYAKIT"
                
                # Prepare detailed response
                result = {
                    'success': True,
                    'condition': condition,
                    'prediction': {
                        'pest_name': disease_info['pest_name'],
                        'class_name': class_name,
                        'confidence': round(confidence * 100, 2),
                        'severity': severity,
                        'status': disease_info['status'],
                        'description': disease_info['description'],
                        'symptoms': disease_info.get('symptoms', ''),
                        'causes': disease_info.get('causes', ''),
                        'recommendation': disease_info['recommendation']
                    },
                    'mode': 'trained_cnn',
                    'note': 'Hasil dari model CNN terlatih'
                }
                
                logger.info(f"Prediction: {class_name} ({confidence*100:.1f}%) - {condition}")
                return result
                
            else:
                # Fallback mode dengan output yang lebih baik
                import time
                time.sleep(1)
                
                # Simulasi prediksi untuk development
                simulated_diseases = [
                    {
                        "class_name": "Daun Cabai Sehat",
                        "pest_name": "Tidak Ada Hama dan Penyakit",
                        "condition": "SEHAT"
                    },
                    {
                        "class_name": "Penyakit Bercak Bakteri (Bacterial Spot)",
                        "pest_name": "Penyakit Bercak Bakteri (Bacterial Spot)",
                        "condition": "TERKENA PENYAKIT"
                    },
                    {
                        "class_name": "Penyakit Daun Keriting (Leaf Curl)",
                        "pest_name": "Hama Kutu Daun (Aphids)",
                        "condition": "TERKENA PENYAKIT"
                    },
                    {
                        "class_name": "Penyakit Layu Fusarium",
                        "pest_name": "Jamur Fusarium oxysporum",
                        "condition": "TERKENA PENYAKIT"
                    }
                ]
                
                import random
                selected = random.choice(simulated_diseases)
                confidence = random.uniform(0.75, 0.95)
                
                # Tentukan severity
                severity = self.determine_severity_level(confidence, selected['class_name'])
                
                # Simulasi info penyakit
                if selected['condition'] == "SEHAT":
                    recommendation = "Tanaman dalam kondisi baik. Lanjutkan perawatan rutin."
                else:
                    recommendation = "Disarankan konsultasi dengan penyuluh pertanian dan lakukan treatment sesuai jenis penyakit."
                
                return {
                    'success': True,
                    'condition': selected['condition'],
                    'prediction': {
                        'pest_name': selected['pest_name'],
                        'class_name': selected['class_name'],
                        'confidence': round(confidence * 100, 2),
                        'severity': severity,
                        'status': selected['condition'],
                        'description': selected['class_name'],
                        'recommendation': recommendation
                    },
                    'mode': 'development',
                    'note': 'Mode pengembangan - hasil simulasi'
                }
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'note': 'Terjadi kesalahan saat analisis gambar'
            }
    
    def get_status(self):
        """Get model status"""
        return {
            'model_loaded': self.model_loaded,
            'classes': self.class_names,
            'total_classes': len(self.class_names),
            'model_name': 'CNN Deteksi Penyakit Daun Cabai'
        }

# Create global instance
pest_ai = PestDetectionAI()