# jangan dihapus Diagnostic untuk cek model
import os
import json

print("=" * 70)
print("🔍 AGROGUARD MODEL DIAGNOSTIC")
print("=" * 70)

# 1. Check class_names.json
print("\n📄 Checking class_names.json...")
try:
    if os.path.exists('dashboard/class_names.json'):
        with open('dashboard/class_names.json') as f:
            json_data = json.load(f)
        print(f"✅ File exists")
        print(f"   Total classes: {json_data.get('num_classes', 'N/A')}")
        print(f"   Trained date: {json_data.get('trained_date', 'N/A')}")
        
        if 'classes' in json_data:
            print(f"\n   First 3 classes:")
            for i, cls in enumerate(json_data['classes'][:3]):
                print(f"     {i}: {cls}")
            print(f"     ...")
    else:
        print("❌ class_names.json NOT FOUND!")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Check ai_service.py
print("\n🤖 Checking ai_service.py...")
try:
    from dashboard.ai_service import pest_ai
    
    status = pest_ai.get_status()
    print(f"✅ Module imported")
    print(f"   Model loaded: {status['model_loaded']}")
    print(f"   Total classes: {status['total_classes']}")
    print(f"   Model name: {status['model_name']}")
    
    print(f"\n   First 3 classes:")
    for i, cls in enumerate(pest_ai.class_names[:3]):
        print(f"     {i}: {cls}")
    print(f"     ...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 3. Check model file
print("\n🧠 Checking model file...")
model_path = 'dashboard/ml_models/pepper_cnn_trained.h5'
if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"✅ Model file exists")
    print(f"   Path: {model_path}")
    print(f"   Size: {size_mb:.2f} MB")
    
    # Try to load and check output
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)
        output_shape = model.output_shape
        num_classes = output_shape[-1]
        
        print(f"\n   Model architecture:")
        print(f"     Input shape: {model.input_shape}")
        print(f"     Output shape: {output_shape}")
        print(f"     Predicts: {num_classes} classes")
        
        # Compare with ai_service
        from dashboard.ai_service import pest_ai
        expected_classes = len(pest_ai.class_names)
        
        print(f"\n   Comparison:")
        print(f"     Model outputs: {num_classes} classes")
        print(f"     ai_service expects: {expected_classes} classes")
        
        if num_classes == expected_classes:
            print(f"     ✅ MATCH!")
        else:
            print(f"     ❌ MISMATCH!")
            print(f"\n   🔧 SOLUTION:")
            if num_classes == 2 and expected_classes == 12:
                print(f"     - Model is OLD (2 classes)")
                print(f"     - Need to retrain with 12 classes")
                print(f"     - Run: python train_cnn_12_classes.py")
            else:
                print(f"     - Retrain model or fix class_names order")
        
        # Check class order match with JSON
        try:
            with open('dashboard/class_names.json') as f:
                json_data = json.load(f)
            
            if 'classes' in json_data:
                if json_data['classes'] == pest_ai.class_names:
                    print(f"\n   ✅ Class order matches JSON")
                else:
                    print(f"\n   ⚠️ Class order differs from JSON!")
                    print(f"     Check if class_names in ai_service.py matches training order")
        except:
            pass
            
    except Exception as e:
        print(f"   ❌ Error loading model: {e}")
else:
    print(f"❌ Model file NOT FOUND!")
    print(f"   Expected at: {model_path}")
    print(f"\n   🔧 SOLUTION:")
    print(f"     - Train model: python train_cnn_12_classes.py")

# 4. Check dataset
print("\n📂 Checking dataset...")
dataset_path = 'Training/Dataset'
if os.path.exists(dataset_path):
    folders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]
    print(f"✅ Dataset folder exists")
    print(f"   Total folders: {len(folders)}")
    
    if len(folders) == 12:
        print(f"   ✅ Has 12 class folders (correct)")
    else:
        print(f"   ⚠️ Expected 12 folders, found {len(folders)}")
    
    print(f"\n   Folders:")
    for folder in sorted(folders):
        count = len([f for f in os.listdir(os.path.join(dataset_path, folder)) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"     {folder}: {count} images")
else:
    print(f"❌ Dataset folder NOT FOUND!")
    print(f"   Expected at: {dataset_path}")

# 5. Final summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

issues = []
solutions = []

# Check model status
try:
    from dashboard.ai_service import pest_ai
    if not pest_ai.model_loaded:
        issues.append("❌ Model not loaded")
        solutions.append("   → Train model: python train_cnn_12_classes.py")
    else:
        # Check mismatch
        import tensorflow as tf
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            if model.output_shape[-1] != len(pest_ai.class_names):
                issues.append("❌ Model class mismatch")
                solutions.append("   → Retrain model: python train_cnn_12_classes.py")
except:
    issues.append("❌ Cannot import ai_service")
    solutions.append("   → Check ai_service.py syntax")

if not issues:
    print("✅ ALL CHECKS PASSED!")
    print("\n🎉 System ready for detection!")
    print("   Run: python manage.py runserver")
else:
    print("Issues found:")
    for issue in issues:
        print(issue)
    
    print("\nSolutions:")
    for solution in solutions:
        print(solution)

print("=" * 70)