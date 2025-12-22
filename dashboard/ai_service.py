import os
import tensorflow as tf
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class PestDetectionAI:
    def __init__(self):
        self.model = None
        self.model_loaded = False

        # HARUS SESUAI URUTAN TRAINING
        self.class_names = [
            'Pepper__bell___Bacterial_spot',
            'Pepper__bell___healthy',
            'Tomato_Bacterial_spot',
            'Tomato_Early_blight',
            'Tomato_Late_blight',
            'Tomato_Leaf_Mold',
            'Tomato_Spider_mites_Two_spotted_spider_mite',
            'Tomato__Target_Spot',
            'Tomato_Septoria_leaf_spot',
            'Tomato__Tomato_YellowLeaf__Curl_Virus',
            'Tomato__Tomato_mosaic_virus',
            'Tomato_healthy'
        ]

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
        'prevention': 'Jaga kelembaban tinggi, semprotkan air ke daun, kontrol gulma.',
        'treatment': 'Semprot mitisida atau insektisida (abamectin), aplikasi predator alami, pangkas daun terinfeksi berat.'
    },

    'Tomato_Target_Spot': {
        'display_name': 'Bercak Target pada Tomat',
        'latin_name': 'Corynespora cassiicola',
        'description': 'Penyakit jamur yang menyebabkan bercak berbentuk target pada daun tomat.',
        'symptoms': 'Bercak coklat dengan lingkaran konsentris seperti target, daun menguning dan rontok.',
        'prevention': 'Rotasi tanaman, jaga jarak tanam, hindari kelembaban berlebih, gunakan mulsa.',
        'treatment': 'Aplikasi fungisida berbasis mancozeb atau chlorothalonil, buang daun terinfeksi.'
    },

    'Tomato_Tomato_YellowLeaf__Curl_Virus': {
        'display_name': 'Virus Keriting Kuning Tomat',
        'latin_name': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'description': 'Penyakit virus yang ditularkan kutu kebul.',
        'symptoms': 'Daun menguning, menggulung ke atas, ukuran daun mengecil, pertumbuhan kerdil.',
        'prevention': 'Gunakan varietas tahan, kontrol kutu kebul, gunakan perangkap kuning.',
        'treatment': 'Cabut tanaman terinfeksi, semprot insektisida untuk kutu kebul.'
    },

    'Tomato__Tomato_mosaic_virus': {
        'display_name': 'Virus Mosaik Tomat',
        'latin_name': 'Tomato Mosaic Virus (ToMV)',
        'description': 'Penyakit virus yang menyebabkan pola mosaik pada daun tomat.',
        'symptoms': 'Pola belang hijau terang dan gelap, daun keriting, pertumbuhan terhambat.',
        'prevention': 'Gunakan benih bersertifikat, sterilisasi alat, kontrol serangga.',
        'treatment': 'Tidak ada pengobatan. Cabut dan musnahkan tanaman terinfeksi.'
    },

    'Tomato_healthy': {
        'display_name': 'Tomat Sehat',
        'latin_name': '-',
        'description': 'Daun tomat sehat tanpa tanda penyakit atau hama.',
        'symptoms': 'Daun hijau segar, pertumbuhan normal.',
        'prevention': 'Pemupukan seimbang, penyiraman teratur, monitoring rutin.',
        'treatment': 'Tidak diperlukan treatment.'
    }
}  

        self.load_model()

    def load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'ml_models/pepper_cnn_trained.h5')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                self.model_loaded = True
                logger.info("✅ Model loaded")
        except Exception as e:
            logger.error(e)

    def predict(self, image_path, lahan_id=None):
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((150, 150))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = self.model.predict(img_array, verbose=0)
            confidence = float(np.max(predictions[0]))
            class_idx = int(np.argmax(predictions[0]))
            class_name = self.class_names[class_idx]

            is_healthy = class_name.endswith('healthy')

            # ====== LOGIKA NORMAL ======
            if is_healthy:
                condition = 'SEHAT'
                severity = 'Aman'
            else:
                condition = 'TERDETEKSI'
                if confidence >= 0.85:
                    severity = 'Tinggi'
                elif confidence >= 0.70:
                    severity = 'Sedang'
                else:
                    severity = 'Rendah'

            disease_info = self.disease_info.get(class_name, {})

            return {
                'success': True,
                'condition': condition,
                'prediction': {
                    'class_name': class_name,
                    'display_name': disease_info.get('display_name', class_name),
                    'confidence': round(confidence * 100, 2),
                    'severity': severity,
                    'disease_info': disease_info
                },
                'mode': 'trained_cnn'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

pest_ai = PestDetectionAI()
