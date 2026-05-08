from __future__ import annotations
from typing import TYPE_CHECKING
from schemas.constants import Topics, U_INPUT, MODE
if TYPE_CHECKING:
    from app.MonitorApp import MonitorApp



class MonitorService:
    @staticmethod
    def publish_mode(app: MonitorApp):
        app.current_mode = MODE.publish
        print("Switched to publish mode.")
        for topic in Topics:
            print(f'- {topic.name}')

        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == U_INPUT.back:
            app.current_mode = None
            return

        try:
            app.selected_topic = Topics[topic_choice].value
            app.publish(app.client)
            app.selected_topic = None
        except KeyError:
            print("Invalid topic.")
            app.current_mode = None
            return

    @staticmethod
    def subscribe_mode(app: MonitorApp):
        app.current_mode = MODE.subscribe
        print("Topics:")
        for topic in Topics:
            print(f"- {topic.name}")
        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == U_INPUT.back:
            return
        
        try:
            app.selected_topic = Topics[topic_choice].value
        except KeyError:
            print("Invalid topic.")
            app.current_mode = None
            return

        if app.selected_topic in app.sub_list:
            print(f"Error: Already subscribed to topic: {app.selected_topic}")
            return
        
        app.subscribe(app.client)
        app.sub_list.append(app.selected_topic)
        print(f"Now subscribed to topic: {app.selected_topic}")
        app.selected_topic = None

    
    @staticmethod
    def unsubscribe_mode(app: MonitorApp):
        app.current_mode = MODE.unsubscribe
        for topic in Topics:
            print(f"- {topic.name}")
        print("Subscribed Topics:")
        for topic in app.sub_list:
            print(f"- {topic}")
        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == U_INPUT.back:
            return
        
        try:
            app.selected_topic = Topics[topic_choice].value
        except KeyError:
            print("Invalid topic.")
            app.current_mode = None
            return

        if app.selected_topic not in app.sub_list:
            print(f"Error: Already unsubscribed to topic: {app.selected_topic}")
            return
        
        app.unsubscribe(app.client)
        app.sub_list.remove(app.selected_topic)
        print(f"Unsubscribed from topic: {app.selected_topic}")
        app.selected_topic = None
    


    @staticmethod
    def recv_mode(app: MonitorApp):
        app.current_mode = MODE.receive
        print('Receive Mode - Listening for messages on Topics:')
        for topic in app.sub_list:
            print(f"- {topic}")
        print('Press ENTER to exit receive mode.')

        input()
        app.current_mode = None
        print("Exited receive mode")


    @staticmethod
    def choice(app: MonitorApp, mode_choice: str):
        match mode_choice:
            case U_INPUT.publish: return MonitorService.publish_mode(app)
            case U_INPUT.receive: return MonitorService.recv_mode(app)
            case U_INPUT.subscribe: return MonitorService.subscribe_mode(app)
            case U_INPUT.unsubscribe: return MonitorService.unsubscribe_mode(app)