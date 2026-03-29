from paho.mqtt import client as mqtt_client
from app.MqttApp import MQTTApp
from utils.signal_utils import shutdown_flag
from schemas.constants import MODE, U_INPUT, Topics
from services.MonitorAppService import MonitorService
from utils.console import handleheader, ascii_art


class MonitorApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.selected_topic: str = None
        self.current_mode: str = None
        self.current_message: str = None 
        self.sub_list: list[str] = []

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
            self.current_message = f"Received '{received_message}' from topic: {msg.topic}"          
            if self.current_mode == MODE.receive:                                           
                handleheader(msg.topic)
                print(self.current_message)
                print("PRESS 'ENTER' TO EXIT RECEIVE MODE\n\r")                          
  
        client.subscribe(self.selected_topic)
        client.on_message = on_message
    
    def unsubscribe(self, client: mqtt_client):
        client.unsubscribe(self.selected_topic)
        

    def main_loop(self):
        print(self.id)
        self.client.loop_start()
        try:
            while True:                                                        
                mode_choice = input("MODE (recv|pub|sub|del-sub|exit): ").strip().lower()                                                       
                if mode_choice == U_INPUT.exit:
                    break
                MonitorService.choice(self, mode_choice)
                if mode_choice == U_INPUT.empty:                                             
                    pass
        except KeyboardInterrupt:
            print("KeyboardInterrupt, shutting down...")
            shutdown_flag.set()
            self.client.loop_stop()  
            self.client.disconnect()

if __name__ == '__main__':

    app = MonitorApp(id="MQTT CLI Monitor Application")
    ascii_art()
    print(Topics.metrics)
    app.main_loop()
    

