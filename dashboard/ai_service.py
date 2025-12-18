# dashboard/ai_service.py - UPDATED WITH VALIDATION & DISEASE INFO
import os
import tensorflow as tf
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class PestDetectionAI:
    def __init__(self):
        self.model = None
        self.class_names = [
            'Pepper__bell___Bacterial_spot',
            'Pepper__bell___healthy',
            'Tomato__Target_Spot',
            'Tomato__Tomato_mosaic_virus',
            'Tomato__Tomato_YellowLeaf__Curl_Virus',
            'Tomato_Bacterial_spot',
            'Tomato_Early_blight',
            'Tomato_healthy',
            'Tomato_Late_blight',
            'Tomato_Leaf_Mold',
            'Tomato_Septoria_leaf_spot',
            'Tomato_Spider_mites_Two_spotted_spider_mite'
        ]
        
        # Database penyakit dengan deskripsi lengkap
        self.disease_info = {
            'Pepper__bell___Bacterial_spot': {
                'display_name': 'Bercak Bakteri pada Cabai',
                'latin_name': 'Xanthomonas campestris',
                'description': 'Penyakit bakteri yang menyebabkan bercak coklat pada daun, batang, dan buah cabai.',
                'symptoms': 'Bercak kecil berwarna coklat kehitaman pada daun, tepi daun menguning, dan luka pada buah.',
                'prevention': 'Gunakan benih bebas penyakit, rotasi tanaman, hindari penyiraman dari atas, dan jaga jarak tanam yang cukup.',
                'treatment': 'Aplikasi bakterisida berbasis tembaga, buang tanaman yang terinfeksi berat, dan tingkatkan sirkulasi udara.'
            },
            'Pepper__bell___healthy': {
                'display_name': 'Cabai Sehat',
                'latin_name': '-',
                'description': 'Daun cabai dalam kondisi sehat tanpa tanda-tanda penyakit atau serangan hama.',
                'symptoms': 'Daun berwarna hijau cerah, tidak ada bercak atau kerusakan, pertumbuhan normal.',
                'prevention': 'Pertahankan dengan pemupukan teratur, penyiraman yang cukup, dan monitoring rutin.',
                'treatment': 'Tidak diperlukan treatment. Lanjutkan perawatan standar dan monitoring berkala.'
            },
            'Tomato__Target_Spot': {
                'display_name': 'Bercak Target pada Tomat',
                'latin_name': 'Corynespora cassiicola',
                'description': 'Penyakit jamur yang menyebabkan bercak berbentuk target pada daun tomat.',
                'symptoms': 'Bercak coklat dengan lingkaran konsentris seperti target, daun menguning dan rontok.',
                'prevention': 'Rotasi tanaman, jaga jarak tanam, hindari kelembaban berlebih, gunakan mulsa.',
                'treatment': 'Aplikasi fungisida berbasis mancozeb atau chlorothalonil, buang daun terinfeksi, perbaiki drainase.'
            },
            'Tomato__Tomato_mosaic_virus': {
                'display_name': 'Virus Mosaik Tomat',
                'latin_name': 'Tomato Mosaic Virus (ToMV)',
                'description': 'Penyakit virus yang menyebabkan pola mosaik pada daun tomat.',
                'symptoms': 'Pola belang hijau terang dan gelap pada daun, daun keriting, pertumbuhan terhambat, buah berbintik.',
                'prevention': 'Gunakan benih bersertifikat, cuci tangan dan alat, hindari merokok di dekat tanaman, kontrol serangga vektor.',
                'treatment': 'Tidak ada pengobatan untuk virus. Cabut dan musnahkan tanaman terinfeksi, sterilisasi alat, tanam varietas tahan virus.'
            },
            'Tomato__Tomato_YellowLeaf__Curl_Virus': {
                'display_name': 'Virus Keriting Kuning Tomat',
                'latin_name': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
                'description': 'Penyakit virus yang ditularkan kutu kebul, menyebabkan daun menguning dan keriting.',
                'symptoms': 'Daun menguning, menggulung ke atas, ukuran daun mengecil, pertumbuhan kerdil, produksi buah menurun drastis.',
                'prevention': 'Gunakan kain kasa untuk mencegah kutu kebul, tanam varietas tahan virus, aplikasi insektisida sistemik, kontrol gulma.',
                'treatment': 'Cabut tanaman terinfeksi segera, semprot insektisida untuk kutu kebul, gunakan perangkap kuning lengket.'
            },
            'Tomato_Bacterial_spot': {
                'display_name': 'Bercak Bakteri pada Tomat',
                'latin_name': 'Xanthomonas spp.',
                'description': 'Penyakit bakteri yang menyerang daun, batang, dan buah tomat.',
                'symptoms': 'Bercak kecil berwarna gelap dengan halo kuning, luka pada buah, daun berlubang saat bercak gugur.',
                'prevention': 'Gunakan benih sehat, hindari penyiraman dari atas, rotasi tanaman minimal 2 tahun, jaga kebersihan kebun.',
                'treatment': 'Aplikasi bakterisida tembaga, tingkatkan drainase, buang bagian tanaman terinfeksi, kurangi kelembaban.'
            },
            'Tomato_Early_blight': {
                'display_name': 'Hawar Awal pada Tomat',
                'latin_name': 'Alternaria solani',
                'description': 'Penyakit jamur yang menyerang daun bagian bawah terlebih dahulu.',
                'symptoms': 'Bercak coklat gelap dengan lingkaran konsentris pada daun tua, daun menguning dan rontok dari bawah.',
                'prevention': 'Rotasi tanaman, jaga jarak tanam, mulsa untuk mencegah percikan tanah, sirkulasi udara baik.',
                'treatment': 'Aplikasi fungisida berbasis mancozeb atau copper, buang daun terinfeksi, kurangi kelembaban, perbaiki nutrisi tanaman.'
            },
            'Tomato_healthy': {
                'display_name': 'Tomat Sehat',
                'latin_name': '-',
                'description': 'Daun tomat dalam kondisi sehat tanpa tanda-tanda penyakit atau serangan hama.',
                'symptoms': 'Daun berwarna hijau segar, pertumbuhan normal, tidak ada bercak atau kerusakan fisik.',
                'prevention': 'Pertahankan dengan pemupukan NPK seimbang, penyiraman teratur pagi/sore, pruning berkala.',
                'treatment': 'Tidak diperlukan treatment. Lanjutkan monitoring rutin dan perawatan preventif standar.'
            },
            'Tomato_Late_blight': {
                'display_name': 'Hawar Akhir pada Tomat',
                'latin_name': 'Phytophthora infestans',
                'description': 'Penyakit jamur berbahaya yang dapat menghancurkan seluruh tanaman dalam hitungan hari.',
                'symptoms': 'Bercak coklat kehijauan basah pada daun, jamur putih di bawah daun saat lembab, batang dan buah membusuk cepat.',
                'prevention': 'Tanam varietas tahan, hindari kelembaban tinggi, jarak tanam lebar, aplikasi fungisida preventif saat musim hujan.',
                'treatment': 'SEGERA aplikasi fungisida sistemik (metalaxyl, mancozeb), cabut tanaman terinfeksi berat, tingkatkan drainase, kurangi penyiraman.'
            },
            'Tomato_Leaf_Mold': {
                'display_name': 'Jamur Daun Tomat',
                'latin_name': 'Passalora fulva (Fulvia fulva)',
                'description': 'Penyakit jamur yang sering muncul pada kondisi lembab dan sirkulasi udara buruk.',
                'symptoms': 'Bercak kuning di permukaan atas daun, lapisan jamur abu-abu/coklat di bawah daun, daun mengering dan rontok.',
                'prevention': 'Jaga sirkulasi udara baik, kurangi kelembaban, hindari penyiraman daun, tanam di rumah kaca dengan ventilasi.',
                'treatment': 'Aplikasi fungisida berbasis chlorothalonil atau mancozeb, buang daun terinfeksi, tingkatkan ventilasi, kurangi kelembaban.'
            },
            'Tomato_Septoria_leaf_spot': {
                'display_name': 'Bercak Daun Septoria',
                'latin_name': 'Septoria lycopersici',
                'description': 'Penyakit jamur yang menyerang daun dengan bercak kecil khas.',
                'symptoms': 'Bercak kecil bulat abu-abu dengan tepi gelap, titik hitam di tengah bercak (spora jamur), daun menguning dan rontok.',
                'prevention': 'Rotasi tanaman 3 tahun, mulsa untuk hindari percikan tanah, buang daun bawah, hindari penyiraman dari atas.',
                'treatment': 'Aplikasi fungisida berbasis copper atau chlorothalonil setiap 7-10 hari, buang daun terinfeksi, perbaiki drainase.'
            },
            'Tomato_Spider_mites_Two_spotted_spider_mite': {
                'display_name': 'Tungau Laba-laba Dua Titik',
                'latin_name': 'Tetranychus urticae',
                'description': 'Hama tungau kecil yang mengisap cairan daun, menyebabkan kerusakan serius.',
                'symptoms': 'Bintik kuning/putih kecil pada daun, jaring halus di bawah daun, daun keriting dan kering, pertumbuhan terhambat.',
                'prevention': 'Jaga kelembaban tinggi (tungau tidak suka lembab), semprotkan air ke daun, tanam tanaman pengusir (bawang), kontrol gulma.',
                'treatment': 'Semprot mitisida atau insektisida (abamectin), semprotkan air keras untuk mengusir tungau, aplikasi predator alami (tungau predator), pangkas daun terinfeksi berat.'
            }
        }
        
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
    
    def validate_image(self, image_path):
        """
        Validasi apakah gambar adalah daun (bukan objek lain)
        Menggunakan deteksi warna hijau dan tekstur daun
        """
        try:
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Hitung persentase piksel hijau
            hsv = tf.image.rgb_to_hsv(img_array / 255.0).numpy()
            h = hsv[:, :, 0]  # Hue
            s = hsv[:, :, 1]  # Saturation
            v = hsv[:, :, 2]  # Value
            
            # Rentang warna hijau dalam HSV (untuk daun)
            # Hue: 0.2-0.5 (hijau), Saturation: >0.2, Value: >0.2
            green_mask = (
                (h >= 0.15) & (h <= 0.55) &  # Rentang hijau lebih lebar
                (s >= 0.15) &                 # Saturasi cukup
                (v >= 0.15)                   # Brightness cukup
            )
            
            green_percentage = np.sum(green_mask) / green_mask.size
            
            logger.info(f"🍃 Green pixel percentage: {green_percentage * 100:.2f}%")
            
            # Threshold: minimal 15% piksel hijau untuk dianggap daun
            if green_percentage < 0.15:
                return {
                    'valid': False,
                    'reason': 'Foto tidak terdeteksi sebagai daun. Pastikan foto menampilkan daun cabai atau tomat dengan jelas.',
                    'green_percentage': round(green_percentage * 100, 2)
                }
            
            # Validasi ukuran gambar (minimal 100x100)
            if img.width < 100 or img.height < 100:
                return {
                    'valid': False,
                    'reason': 'Resolusi gambar terlalu kecil. Gunakan gambar minimal 100x100 piksel.',
                    'resolution': f"{img.width}x{img.height}"
                }
            
            # Validasi blur (deteksi gambar kabur)
            # Konversi ke grayscale dan hitung variance of Laplacian
            gray = np.array(img.convert('L'))
            laplacian_var = self._calculate_blur_score(gray)
            
            logger.info(f"📷 Blur score: {laplacian_var:.2f}")
            
            if laplacian_var < 50:  # Threshold untuk gambar blur
                return {
                    'valid': False,
                    'reason': 'Foto terlalu buram atau kurang fokus. Ambil foto yang lebih jelas.',
                    'blur_score': round(laplacian_var, 2)
                }
            
            return {
                'valid': True,
                'green_percentage': round(green_percentage * 100, 2),
                'blur_score': round(laplacian_var, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return {
                'valid': False,
                'reason': f'Error saat memvalidasi gambar: {str(e)}'
            }
    
    def _calculate_blur_score(self, gray_image):
        """Hitung blur score menggunakan Laplacian variance"""
        # Simple Laplacian kernel
        kernel = np.array([[0, 1, 0],
                          [1, -4, 1],
                          [0, 1, 0]])
        
        # Apply convolution
        from scipy import ndimage
        laplacian = ndimage.convolve(gray_image, kernel)
        variance = np.var(laplacian)
        
        return variance
    
    def get_disease_info(self, class_name):
        """Dapatkan informasi lengkap penyakit"""
        return self.disease_info.get(class_name, {
            'display_name': class_name,
            'latin_name': '-',
            'description': 'Informasi detail belum tersedia.',
            'symptoms': 'Belum tersedia.',
            'prevention': 'Konsultasikan dengan ahli pertanian.',
            'treatment': 'Konsultasikan dengan ahli pertanian.'
        })
    
    def predict(self, image_path, lahan_id=None):
        """Predict using trained model with validation"""
        try:
            # STEP 1: Validasi gambar terlebih dahulu
            validation = self.validate_image(image_path)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['reason'],
                    'error_type': 'VALIDATION_FAILED',
                    'details': validation
                }
            
            logger.info(f"✅ Image validation passed: {validation}")
            
            # STEP 2: Lanjut prediksi jika valid
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
                
                # Validasi confidence threshold
                if confidence < 0.50:  # Jika confidence terlalu rendah
                    return {
                        'success': False,
                        'error': 'Maaf, foto yang Anda unggah kurang jelas atau di luar konteks sistem. Pastikan foto menampilkan daun cabai atau tomat dengan jelas.',
                        'error_type': 'LOW_CONFIDENCE',
                        'details': {
                            'confidence': round(confidence * 100, 2),
                            'predicted_class': class_name
                        }
                    }
                
                # Determine severity
                if confidence >= 0.85:
                    severity = "Tinggi"
                elif confidence >= 0.70:
                    severity = "Sedang"
                else:
                    severity = "Rendah"
                
                # Get disease info
                disease_info = self.get_disease_info(class_name)
                
                return {
                    'success': True,
                    'validation': validation,
                    'prediction': {
                        'class_name': class_name,
                        'display_name': disease_info['display_name'],
                        'confidence': round(confidence * 100, 2),
                        'severity': severity,
                        'disease_info': disease_info
                    },
                    'mode': 'trained_cnn',
                    'note': f'Model CNN terlatih dengan {len(self.class_names)} kelas'
                }
            else:
                # Fallback mode (untuk development)
                import time
                time.sleep(1)
                
                # Random prediction for testing
                class_name = np.random.choice(self.class_names)
                confidence = np.random.uniform(0.60, 0.95)
                
                disease_info = self.get_disease_info(class_name)
                
                return {
                    'success': True,
                    'validation': validation,
                    'prediction': {
                        'class_name': class_name,
                        'display_name': disease_info['display_name'],
                        'confidence': round(confidence * 100, 2),
                        'severity': 'Tinggi' if confidence > 0.85 else 'Sedang',
                        'disease_info': disease_info
                    },
                    'mode': 'development',
                    'note': 'Mode development (model belum dilatih)'
                }
                
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': f'Terjadi kesalahan saat memproses gambar: {str(e)}',
                'error_type': 'SYSTEM_ERROR'
            }
    
    def get_status(self):
        """Get model status"""
        return {
            'model_loaded': self.model_loaded,
            'classes': self.class_names,
            'total_classes': len(self.class_names),
            'model_name': 'AgroGuard Plant Disease Detection',
            'supported_plants': ['Cabai (Pepper)', 'Tomat (Tomato)']
        }

# Create global instance
pest_ai = PestDetectionAI()