


import os
from cryptography.fernet import Fernet

class FernetSingleton:
    class __FernetSingleton:
        def __init__(self):
            key_str = os.getenv('DB_KEY')
            key_bytes = key_str.encode('utf-8')
            key_base64 = key_bytes.decode()
            self.fernet = Fernet(key_base64)
    instance = None

    def __init__(self):
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)        
