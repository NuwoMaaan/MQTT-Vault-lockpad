
class Modes():
    receive: str = "receive"
    publish: str = "publish"
    subscribe: str = "subscribe"
    unsubscribe: str = "unsubscribe"

MODE = Modes()


class Topics():
    event: str = "vault/padlock/event" 
    status: str = "vault/padlock/status"
    metrics: str = "vault/padlock/metrics"
    control: str = "vault/padlock/control" 

TOPICS = Topics()

    
class UserInput():
    back: str = "back"
    exit: str = "exit"
    receive: str = "recv"
    publish: str = "pub"
    subscribe: str = "sub"
    unsubscribe: str = "del-sub"
    empty: str = ""

U_INPUT = UserInput()
    
