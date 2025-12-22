# test_prediction.py
import os

print("="*70)
print("🔍 CLASS ORDER VERIFICATION")
print("="*70)

# 1. Check dataset folder order (alphabetical)
dataset_path = 'Training/Dataset'
folders = sorted([f for f in os.listdir(dataset_path) 
                 if os.path.isdir(os.path.join(dataset_path, f))])

print("\n📂 Dataset folders (ALPHABETICAL):")
for i, folder in enumerate(folders):
    print(f"   {i}: {folder}")

# 2. Check training script
print("\n📝 Training script CLASS_FOLDERS:")
with open('train_cnn_12_classes.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'Tomato_Bacterial_spot' in content:
        # Check position
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'CLASS_FOLDERS = [' in line:
                print(f"   Found at line {i}")
                for j in range(i+1, min(i+15, len(lines))):
                    if ']' in lines[j]:
                        break
                    if "'" in lines[j]:
                        print(f"   {lines[j].strip()}")

# 3. Check ai_service.py
print("\n🤖 ai_service.py class_names:")
import sys
sys.path.insert(0, os.getcwd())
from dashboard.ai_service import pest_ai

for i, cls in enumerate(pest_ai.class_names):
    print(f"   {i}: {cls}")

# 4. Compare
print("\n🔍 COMPARISON:")
if folders == pest_ai.class_names:
    print("✅ PERFECT MATCH! Order is correct.")
else:
    print("❌ MISMATCH DETECTED!")
    print("\nDifferences:")
    for i in range(len(folders)):
        if folders[i] != pest_ai.class_names[i]:
            print(f"   Index {i}:")
            print(f"      Dataset: {folders[i]}")
            print(f"      ai_service: {pest_ai.class_names[i]}")

print("="*70)