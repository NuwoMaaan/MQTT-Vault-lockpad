from typing import List
from paho.mqtt import client as mqtt_client
from utils.mqtt_app import MQTTApp
from utils.signal_utils import shutdown_flag
from services.MonitorAppService import MonitorService
from utils.console import handleheader

class MonitorApp(MQTTApp):
    def __init__(self):
        super().__init__()
        self.selected_topic = None
        self.current_mode = None
        self.messages: List[str] = []

    def publish(self, client: mqtt_client):                           
        message = input("Enter message to send: ")                
        result = client.publish(self.selected_topic, message)            
        status = result[0]
        if status == 0:
            handleheader(self.selected_topic)                           
            print(f"Sent: '{message}' to topic: {self.selected_topic}\n\r")
        else:
            print(f"Failed to send message to topic {self.selected_topic}")
    
        self.current_mode = None

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            received_message = msg.payload.decode()
            self.messages.append(f"Received '{received_message}'\n\r from topic: {msg.topic}\n\r")          
            if self.current_mode == 'receive':                                           
                handleheader(msg.topic)
                print(self.messages[-1])                                             
                print("PRESS 'ENTER' TO EXIT RECEIVE MODE\n\r")                          
  
        client.subscribe(self.selected_topic)
        client.on_message = on_message

    def main_loop(self):
        self.client.loop_start()
        try:
            while True:                                                        
                mode_choice = input("MODE (recv|send|subscribe|exit): ").strip().lower()   #Prompting for mode, depending on mode, will determine what is                                                      
                if mode_choice == "exit":
                    break
                MonitorService.choice(self, mode_choice)
                if mode_choice == '':                                             
                    pass
        except KeyboardInterrupt:
            print("KeyboardInterrupt, shutting down...")
            shutdown_flag.set()
            self.client.loop_stop()  
            self.client.disconnect()

if __name__ == '__main__':

    app = MonitorApp()
    app.main_loop()
    

