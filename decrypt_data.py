import base64
import os

# مسار البيانات
data_dir = 'data/abc'

# المرور على جميع الملفات في المجلد
for filename in os.listdir(data_dir):
    filepath = os.path.join(data_dir, filename)
    
    # التأكد أنه ملف وليس مجلد
    if os.path.isfile(filepath):
        try:
            with open(filepath, 'r') as f:
                encoded_data = f.read()
                # فك التشفير
                decoded_data = base64.b64decode(encoded_data)
                print(f"--- File: {filename} ---")
                print(decoded_data.decode('utf-8'))
                print("-" * 30)
        except Exception as e:
            print(f"Error reading {filename}: {e}")