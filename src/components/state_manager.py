from enum import Enum

class BotState(Enum):
    IDLE = 'idle'
    LISTENING = 'listening'
    PROCESSING = 'processing'
    ERROR = 'error'

class StateManager:
    def __init__(self):
        self.current_state = BotState.IDLE
        self.observers = []
        
    def change_state(self, new_state):
        self.current_state = new_state
        self.notify_observers()
        
    def add_observer(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self):
        for observer in self.observers:
            observer.on_state_change(self.current_state) 