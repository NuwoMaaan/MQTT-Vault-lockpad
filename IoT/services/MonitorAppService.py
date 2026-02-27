
import threading
from schemas.topics import TOPICS
from schemas.user_input import U_INPUT
from schemas.modes import MODE

class MonitorService:
    @staticmethod
    def publish_mode(app):
        app.current_mode = MODE.publish
        print("Switched to publish mode.")
        for key in TOPICS:
            print(f'- {key}')

        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == U_INPUT.back:
            app.current_mode = None
            return

        if hasattr(TOPICS, topic_choice):
            app.selected_topic = getattr(TOPICS, topic_choice)
            app.publish(app.client)
        else:
            print("Invalid topic.")
            app.current_mode = None

    @staticmethod
    def subscribe_mode(app):
        app.current_mode = MODE.subscribe
        print("Topics:")
        for key in TOPICS:
            print(f"- {key}")
        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == U_INPUT.back:
            return
        if hasattr(TOPICS, topic_choice):
            app.selected_topic = getattr(TOPICS, topic_choice)

            if app.selected_topic in app.sub_list:
                print(f"Error: Already subscribed to topic: {app.selected_topic}")
                return
            
            app.subscribe(app.client)
            app.sub_list.append(app.selected_topic)
            print(f"Now subscribed to topic: {app.selected_topic}")
        else:
            print("Invalid topic.")
    
    @staticmethod
    def unsubscribe_mode(app):
        app.current_mode = MODE.unsubscribe
        for key in TOPICS:
            print(f"- {key}")
        print("Subscribed Topics:")
        for topic in app.sub_list:
            print(f"- {topic}")
        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == U_INPUT.back:
            return
        if hasattr(TOPICS, topic_choice):
            app.selected_topic = getattr(TOPICS, topic_choice)

            if app.selected_topic not in app.sub_list:
                print(f"Error: Already unsubscribed to topic: {app.selected_topic}")
                return
            
            app.unsubscribe(app.client)
            app.sub_list.remove(app.selected_topic)
            print(f"Unsubscribed from topic: {app.selected_topic}")
        else:
            print("Invalid topic.")


    @staticmethod
    def recv_mode(app):
        app.current_mode = MODE.receive
        print('Receive Mode - Listening for messages on topics:')
        for topic in app.sub_list:
            print(f"- {topic}")
        print('Press ENTER to exit receive mode.')

        def wait_for_exit():
            input()  # Wait for ENTER key
            app.current_mode = None
            print('Exited receive mode')

        threading.Thread(target=wait_for_exit, daemon=True).start()


    @staticmethod
    def choice(app, mode_choice):
        match mode_choice:
            case U_INPUT.publish: return MonitorService.publish_mode(app)
            case U_INPUT.receive: return MonitorService.recv_mode(app)
            case U_INPUT.subscribe: return MonitorService.subscribe_mode(app)
            case U_INPUT.unsubscribe: return MonitorService.unsubscribe_mode(app)