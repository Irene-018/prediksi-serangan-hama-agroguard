# train_cnn_12_classes.py - Training untuk 12 kelas penyakit
import os
import json
import tensorflow as tf
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random
from datetime import datetime

print("=" * 70)
print("🌿 CNN TRAINING - 12 CLASSES (CABAI + TOMAT)")
print("=" * 70)

print(f"\n📊 TensorFlow version: {tf.__version__}")
print(f"📊 NumPy version: {np.__version__}")

# ================= KONFIGURASI =================
DATASET_PATH = 'Training/Dataset'
IMG_SIZE = (150, 150)
BATCH_SIZE = 32
EPOCHS = 15
VALIDATION_SPLIT = 0.2

# Class mapping folder dataset
CLASS_FOLDERS = [
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

# ================= LOAD DATA =================
def load_dataset_manual():
    """Load semua gambar dari 12 folder"""
    
    print("\n📂 Loading dataset...")
    
    X_train, y_train = [], []
    X_val, y_val = [], []
    
    class_distribution = {}
    
    for class_idx, folder_name in enumerate(CLASS_FOLDERS):
        folder_path = os.path.join(DATASET_PATH, folder_name)
        
        print(f"\n[{class_idx + 1}/12] Processing: {folder_name}")
        
        if not os.path.exists(folder_path):
            print(f"   ⚠️ Folder not found: {folder_path}")
            continue
        
        # Get all images
        all_files = os.listdir(folder_path)
        images = [f for f in all_files 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"   Found {len(images)} images")
        
        # Shuffle
        random.shuffle(images)
        
        # Limit per class untuk balance (optional)
        max_per_class = 500  # Sesuaikan dengan RAM Anda
        images = images[:max_per_class]
        
        # Split train/validation
        split_idx = int(len(images) * (1 - VALIDATION_SPLIT))
        
        train_count = 0
        val_count = 0
        
        # Load images
        for i, img_name in enumerate(images):
            img_path = os.path.join(folder_path, img_name)
            
            try:
                # Load and resize
                img = Image.open(img_path).convert('RGB')
                img = img.resize(IMG_SIZE)
                img_array = np.array(img) / 255.0
                
                if i < split_idx:
                    X_train.append(img_array)
                    y_train.append(class_idx)
                    train_count += 1
                else:
                    X_val.append(img_array)
                    y_val.append(class_idx)
                    val_count += 1
                    
            except Exception as e:
                print(f"   ⚠️ Error loading {img_name}: {e}")
        
        class_distribution[folder_name] = {
            'train': train_count,
            'val': val_count,
            'total': train_count + val_count
        }
        
        print(f"   ✅ Loaded: {train_count} train, {val_count} val")
    
    # Convert to numpy
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_val = np.array(X_val)
    y_val = np.array(y_val)
    
    print("\n" + "="*50)
    print("📊 DATASET SUMMARY")
    print("="*50)
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Total classes: {len(CLASS_FOLDERS)}")
    print(f"Image shape: {IMG_SIZE + (3,)}")
    
    print("\n📈 Class Distribution:")
    for cls_name, counts in class_distribution.items():
        print(f"   {cls_name}: {counts['total']} images")
    
    return X_train, y_train, X_val, y_val, class_distribution

# ================= BUILD MODEL =================
def build_cnn_model(num_classes=12):
    """Build CNN model untuk 12 kelas"""
    
    print("\n🏗️ Building CNN Model...")
    
    model = tf.keras.Sequential([
        # Block 1
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', 
                              input_shape=IMG_SIZE + (3,)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Dropout(0.2),
        
        # Block 2
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Dropout(0.2),
        
        # Block 3
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Dropout(0.3),
        
        # Dense layers
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"✅ Model created with {model.count_params():,} parameters")
    model.summary()
    
    return model

# ================= TRAINING =================
def train_model():
    """Main training function"""
    
    print("\n" + "="*50)
    print("🚀 STARTING TRAINING")
    print("="*50)
    
    # Load data
    X_train, y_train, X_val, y_val, class_dist = load_dataset_manual()
    
    if len(X_train) == 0:
        print("❌ No training data!")
        return None
    
    # Build model
    model = build_cnn_model(num_classes=len(CLASS_FOLDERS))
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=0.00001,
            verbose=1
        )
    ]
    
    # Train
    print(f"\n⏳ Training for {EPOCHS} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    print(f"\n📈 Final Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"📈 Final Validation Loss: {val_loss:.4f}")
    
    return model, val_acc, history, class_dist

# ================= SAVE MODEL =================
def save_everything(model, accuracy, history, class_dist):
    """Save model dan semua file pendukung"""
    
    print("\n💾 Saving model and files...")
    
    # Create directories
    os.makedirs('dashboard/ml_models', exist_ok=True)
    
    # Save model
    model_path = 'dashboard/ml_models/pepper_cnn_trained.h5'
    model.save(model_path)
    print(f"✅ Model saved: {model_path}")
    
    # Save class names
    class_names_data = {
        'classes': CLASS_FOLDERS,
        'num_classes': len(CLASS_FOLDERS),
        'accuracy': float(accuracy),
        'trained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'image_size': IMG_SIZE,
        'distribution': class_dist
    }
    
    with open('dashboard/class_names.json', 'w') as f:
        json.dump(class_names_data, f, indent=2)
    print("✅ Class names saved: dashboard/class_names.json")
    
    # Plot training history
    try:
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Train Accuracy')
        plt.plot(history.history['val_accuracy'], label='Val Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Train Loss')
        plt.plot(history.history['val_loss'], label='Val Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('training_history_12classes.png', dpi=150)
        print("✅ Training history plot saved: training_history_12classes.png")
    except Exception as e:
        print(f"⚠️ Could not save plot: {e}")
    
    return accuracy

# ================= MAIN =================
def main():
    print("\n🎯 Starting 12-class CNN training pipeline...")
    
    try:
        result = train_model()
        
        if result:
            model, accuracy, history, class_dist = result
            
            if accuracy > 0.60:
                save_everything(model, accuracy, history, class_dist)
                
                print("\n" + "="*70)
                print("🎉 TRAINING COMPLETED SUCCESSFULLY! 🎉")
                print("="*70)
                print(f"\n📊 Validation Accuracy: {accuracy * 100:.2f}%")
                print(f"📁 Model: dashboard/ml_models/pepper_cnn_trained.h5")
                print(f"📄 Classes: dashboard/class_names.json")
                print(f"🏷️ Total Classes: {len(CLASS_FOLDERS)}")
                
                print("\n🚀 NEXT STEPS:")
                print("   1. Copy ai_service.py yang baru ke dashboard/")
                print("   2. Restart Django server")
                print("   3. Test di: http://localhost:8000/dashboard/deteksi/")
                
                print("\n📋 Supported Classes:")
                for i, cls in enumerate(CLASS_FOLDERS, 1):
                    print(f"   {i}. {cls}")
                
            else:
                print(f"\n⚠️ Low accuracy: {accuracy * 100:.2f}%")
                print("   Consider:")
                print("   - Adding more training data")
                print("   - Increasing epochs")
                print("   - Data augmentation")
                save_everything(model, accuracy, history, class_dist)
        
        else:
            print("\n❌ Training failed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()