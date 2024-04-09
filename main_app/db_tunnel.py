from sshtunnel import SSHTunnelForwarder
import os

def open_ssh_tunnel():
    server = SSHTunnelForwarder(
        (os.getenv("SSH_TUNNEL_HOST"), int(os.getenv("SSH_TUNNEL_PORT"))),
        ssh_username=os.getenv("SSH_TUNNEL_USER"),
        ssh_password=os.getenv("SSH_TUNNEL_PASSWORD"),
        remote_bind_address=(os.getenv("POSTGRES_DNS"), int(os.getenv("POSTGRES_PORT")))
    )
    server.start()
    return server

def close_ssh_tunnel(server):
    if server:
        server.stop()

def  get_tunnel_db_config(server):
    if server:
        print(".................................. Get Tunnel DB Config .................................. ")

        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "ATOMIC_REQUESTS": True,
            "HOST": "127.0.0.1",
            "PORT": server.local_bind_port,
            "TIME_ZONE": 'UTC',
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 0,
            "OPTIONS": {},
            "TEST": {
                "CHARSET": None, 
                "COLLATION": None, 
                "MIGRATE": True, 
                "MIRROR": None, 
                "NAME": None
            },
            "AUTOCOMMIT": False,
        }
    return {}
