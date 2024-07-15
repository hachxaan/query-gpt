from redis import Redis


class RedisSingleton:
    class __RedisSingleton:
        def __init__(self, port, dns, database):
            self.redis = Redis(port=port, host=dns, db=database)

    instance = None

    def __init__(self, port, dns, database):
        if not RedisSingleton.instance:
            RedisSingleton.instance = RedisSingleton.__RedisSingleton(
                port=port,
                dns=dns,
                database=database).redis
        else:
            RedisSingleton.instance.port = port
            RedisSingleton.instance.dns = dns
            RedisSingleton.instance.database = database

    def __getattr__(self, name):
        return getattr(self.instance, name)
