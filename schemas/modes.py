from pydantic import BaseModel
    
class Modes(BaseModel):
    receive: str = "receive"
    publish: str = "publish"
    subscribe: str = "subscribe"

    

MODE = Modes()