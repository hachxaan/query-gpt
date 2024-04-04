import base64
from cryptography.fernet import Fernet
import os
KEY_DATABASE=  '8ddW8P1oTmsbQa21rbv8tmzh_9MasCSwQm4_Sne3IKo='


def decrypt_data(data: bytes):
    fernet = FernetSingleton()
    if data:
        return fernet.decrypt(data).decode()
    else:
        return None

class FernetSingleton:
    class __FernetSingleton:
        def __init__(self):
            key_str = KEY_DATABASE
            if key_str is None:
                raise ValueError("La clave de base de datos no está definida.")

            # Decodificar la clave base64 a bytes
            key_bytes = key_str.encode('utf-8')
            key = base64.urlsafe_b64decode(key_bytes)
            self.fernet = Fernet(key)
            
           
            self.fernet = Fernet(key_bytes)
    instance = None

    def __init__(self):
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)

if __name__ == '__main__':
    datos = 'gAAAAABj5cBdH4LcYqtQCvYkgJFzBaMJdycvYGXwRrXOngyApuPZVVw3YeN0xd05nh4qpXzkh5KL2xo4ETigL28F5fHpjyvbmg=='
    data = decrypt_data(datos)
