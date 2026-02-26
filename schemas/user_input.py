from pydantic import BaseModel
    
class UserInput(BaseModel):
    back: str = "back"
    exit: str = "exit"
    receive: str = "recv"
    publish: str = "pub"
    subscribe: str = "sub"
    unsubscribe: str = "del-sub"
    empty: str = ""

U_INPUT = UserInput()
    
