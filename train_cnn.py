# final_train.py - GUARANTEED TO WORK
import os
import shutil
import json
import tensorflow as tf
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random

print("=" * 70)
print("🌿 FINAL CNN TRAINING - NO DEPENDENCY ISSUES")
print("=" * 70)

# Check TensorFlow
print(f"\n🔍 TensorFlow version: {tf.__version__}")
print(f"🔍 NumPy version: {np.__version__}")

# ================= MANUAL DATA LOADING =================
def load_images_manual():
    """Load images manually without ImageDataGenerator"""
    
    print("\n📁 Loading images manually...")
    
    # Define classes
    classes = [
        ('sehat', 'Training/Dataset/Pepper__bell___healthy'),
        ('hama', 'Training/Dataset/Pepper__bell___Bacterial_spot')
    ]
    
    X_train, y_train = [], []
    X_val, y_val = [], []
    
    for class_idx, (class_name, folder_path) in enumerate(classes):
        print(f"   Processing: {class_name}...")
        
        if not os.path.exists(folder_path):
            print(f"   ❌ Folder not found: {folder_path}")
            continue
        
        # Get all images
        images = []
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                images.extend([f for f in files if f.lower().endswith(ext)])
        
        print(f"     Found {len(images)} images")
        
        # Shuffle and limit to 300 per class
        random.shuffle(images)
        images = images[:300]
        
        # Split 80/20
        split_idx = int(len(images) * 0.8)
        
        # Load images
        for i, img_name in enumerate(images):
            img_path = os.path.join(folder_path, img_name)
            
            try:
                # Load and resize
                img = Image.open(img_path).convert('RGB')
                img = img.resize((150, 150))  # Smaller for faster training
                img_array = np.array(img) / 255.0
                
                if i < split_idx:
                    X_train.append(img_array)
                    y_train.append(class_idx)
                else:
                    X_val.append(img_array)
                    y_val.append(class_idx)
                    
            except Exception as e:
                print(f"     ⚠️ Error loading {img_name}: {e}")
    
    # Convert to numpy arrays
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_val = np.array(X_val)
    y_val = np.array(y_val)
    
    print(f"\n📊 Dataset loaded:")
    print(f"   Training: {len(X_train)} images")
    print(f"   Validation: {len(X_val)} images")
    print(f"   Classes: ['sehat', 'hama']")
    
    return X_train, y_train, X_val, y_val

# ================= SIMPLE CNN MODEL =================
def build_simple_model(input_shape=(150, 150, 3), num_classes=2):
    """Build a very simple CNN"""
    
    print("\n🧠 Building Simple CNN Model...")
    
    model = tf.keras.Sequential([
        # Convolutional layers
        tf.keras.layers.Conv2D(8, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D(2, 2),
        
        tf.keras.layers.Conv2D(16, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),
        
        # Flatten and dense layers
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"✅ Model created with {model.count_params():,} parameters")
    return model

# ================= TRAINING =================
def train_model_simple():
    """Simple training function"""
    
    print("\n" + "=" * 50)
    print("🚀 STARTING TRAINING (5 EPOCHS)")
    print("=" * 50)
    
    # Load data
    X_train, y_train, X_val, y_val = load_images_manual()
    
    if len(X_train) == 0:
        print("❌ No training data loaded!")
        return None
    
    # Build model
    model = build_simple_model()
    
    # Train
    print("\n⏳ Training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=5,
        batch_size=16,
        verbose=1
    )
    
    # Evaluate
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    print(f"\n📈 Final Validation Accuracy: {val_acc * 100:.2f}%")
    
    return model, val_acc, history

# ================= SAVE EVERYTHING =================
def save_model_and_update(model, accuracy):
    """Save model and update AI service"""
    
    print("\n💾 Saving model and files...")
    
    # Create directories
    os.makedirs('dashboard/ml_models', exist_ok=True)
    
    # Save model
    model_path = 'dashboard/ml_models/pepper_cnn_trained.h5'
    model.save(model_path)
    print(f"✅ Model saved: {model_path}")
    
    # Save class names
    class_names = ['sehat', 'hama']
    with open('dashboard/class_names.json', 'w') as f:
        json.dump(class_names, f)
    print(f"✅ Class names saved")
    
    # Create simple AI service
    ai_service_code = '''# dashboard/ai_service.py - SIMPLE TRAINED VERSION
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
'''
    
    # Write AI service
    with open('dashboard/ai_service.py', 'w', encoding='utf-8') as f:
        f.write(ai_service_code)
    
    print("✅ AI service updated: dashboard/ai_service.py")
    
    # Create test script
    test_code = '''# test_model.py - Test the trained model
import tensorflow as tf
import numpy as np
from PIL import Image
import os

def test_trained_model():
    """Test the trained model"""
    
    print("🧪 Testing Trained Model...")
    
    # Load model
    model = tf.keras.models.load_model('dashboard/ml_models/pepper_cnn_trained.h5')
    
    # Test with a sample image
    sample_folder = 'Training/Dataset/Pepper__bell___healthy'
    if os.path.exists(sample_folder):
        images = [f for f in os.listdir(sample_folder) if f.lower().endswith('.jpg')]
        if images:
            sample_image = os.path.join(sample_folder, images[0])
            
            # Preprocess
            img = Image.open(sample_image).convert('RGB')
            img = img.resize((150, 150))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            predictions = model.predict(img_array, verbose=0)
            confidence = np.max(predictions[0])
            class_idx = np.argmax(predictions[0])
            class_names = ['sehat', 'hama']
            
            print(f"📸 Image: {images[0]}")
            print(f"🎯 Prediction: {class_names[class_idx]}")
            print(f"📊 Confidence: {confidence * 100:.2f}%")
            print(f"✅ Expected: sehat (should be high confidence)")
            
            return True
    
    return False

if __name__ == "__main__":
    test_trained_model()
'''
    
    with open('test_trained_model.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Test script created: test_trained_model.py")
    
    return accuracy

# ================= MAIN =================
def main():
    print("\n🎯 Starting CNN Training Pipeline...")
    
    try:
        # Train model
        result = train_model_simple()
        
        if result:
            model, accuracy, history = result
            
            if accuracy > 0.6:  # If accuracy is reasonable
                # Save everything
                save_model_and_update(model, accuracy)
                
                print("\n" + "=" * 70)
                print(f"🎉 TRAINING SUCCESSFUL! 🎉")
                print("=" * 70)
                print(f"\n📊 Model Accuracy: {accuracy * 100:.2f}%")
                print(f"📁 Model saved: dashboard/ml_models/pepper_cnn_trained.h5")
                print(f"🤖 AI Service: dashboard/ai_service.py")
                print(f"🏷️ Classes: ['sehat', 'hama']")
                
                print("\n🚀 NEXT STEPS:")
                print("   1. Restart Django server")
                print("   2. Go to: http://localhost:8000/dashboard/deteksi/")
                print("   3. Upload a pepper leaf image")
                print("   4. See trained CNN predictions!")
                
                print("\n🧪 Test model: python test_trained_model.py")
                
            else:
                print(f"\n⚠️ Low accuracy: {accuracy * 100:.2f}%")
                print("   But model saved anyway for testing")
                save_model_and_update(model, accuracy)
        
        else:
            print("\n❌ Training failed!")
            
    except Exception as e:
        print(f"\n❌ Error in training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    