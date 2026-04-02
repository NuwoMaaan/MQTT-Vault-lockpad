from enum import StrEnum

class Modes():
    receive: str = "receive"
    publish: str = "publish"
    subscribe: str = "subscribe"
    unsubscribe: str = "unsubscribe"

MODE = Modes()


class Topics(StrEnum):
    event = "vault/padlock/event"
    status = "vault/padlock/status"
    metrics = "vault/padlock/metrics"
    control = "vault/padlock/control"
    token = "vault/padlock/ble/token"

    
class UserInput():
    back: str = "back"
    exit: str = "exit"
    receive: str = "recv"
    publish: str = "pub"
    subscribe: str = "sub"
    unsubscribe: str = "del-sub"
    empty: str = ""

U_INPUT = UserInput()
    
