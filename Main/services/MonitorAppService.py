
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
            app.subscribe(app.client)
            print(f"Now subscribed to topic: {app.selected_topic}")
        else:
            print("Invalid topic.")

    @staticmethod
    def recv_mode(app):
        app.current_mode = MODE.receive
        print('Receive Mode - Listening for messages...')
        print('Press ENTER to exit receive mode.')

        def wait_for_exit():
            input()  # Wait for ENTER key
            app.current_mode = None
            print('Exited receive mode')

        threading.Thread(target=wait_for_exit, daemon=True).start()


    @staticmethod
    def choice(app, mode_choice):
        match mode_choice:
            case 'pub': return MonitorService.publish_mode(app)
            case 'recv': return MonitorService.recv_mode(app)
            case 'sub': return MonitorService.subscribe_mode(app)