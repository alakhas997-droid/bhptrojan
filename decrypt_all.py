import os
import base64
import zlib

# المجلد الذي يحتوي على البيانات المسروقة
TARGET_DIR = 'data'

def decrypt_all():
    print(f"[*] Starting decryption in '{TARGET_DIR}' directory...")
    
    # المرور على جميع المجلدات والملفات
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            # معالجة ملفات .data فقط
            if file.endswith('.data'):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    
                    # 1. فك تشفير Base64
                    decoded = base64.b64decode(content)
                    
                    # 2. فك ضغط Zlib
                    decompressed = zlib.decompress(decoded)
                    
                    # تحديد صيغة الملف (صورة أم نص)
                    # ملفات BMP تبدأ عادة بالحرفين BM
                    if decompressed.startswith(b'BM'):
                        output_path = full_path.replace('.data', '.bmp')
                        file_type = "Image (Screenshot)"
                    else:
                        output_path = full_path.replace('.data', '_decoded.txt')
                        file_type = "Text Data"
                    
                    # حفظ الملف المفكوك
                    with open(output_path, 'wb') as f_out:
                        f_out.write(decompressed)
                        
                    print(f"[+] Decrypted: {file} -> {os.path.basename(output_path)} [{file_type}]")
                    
                except Exception as e:
                    print(f"[-] Failed {file}: {e}")

if __name__ == '__main__':
    decrypt_all()
    input("\nPress Enter to exit...")
