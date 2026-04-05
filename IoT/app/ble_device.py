
class BLEDevice():
    def __init__(self):
        self.UUID = None
        self.token = None
        self.local_name = None

    def __repr__(self):
        return f"<BLEDevice(localname='{self.local_name}', UUID='{self.UUID}', token='{self.token}')>"
    

