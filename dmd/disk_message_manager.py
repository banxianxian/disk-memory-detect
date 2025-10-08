
class DiskMessageManager:
    _instance = None
    _disk_name = None
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance