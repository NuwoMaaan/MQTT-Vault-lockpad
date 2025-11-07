
import threading
import keyboard
from schemas.topics import TOPICS

class MonitorService:
    @staticmethod
    def publish_mode(app):
        app.current_mode = 'publish'
        print("Switched to publish mode.")
        for key in TOPICS:
            print(f'- {key}')

        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == 'back':
            app.current_mode = None
            return

        if hasattr(TOPICS, topic_choice):
            app.selected_topic = getattr(TOPICS, topic_choice)
            threading.Thread(target=app.publish, args=(app.client,)).start()
        else:
            print("Invalid topic.")
            app.current_mode = None

    @staticmethod
    def subscribe_mode(app):
        app.current_mode = 'subscribe'
        print("Topics:")
        for key in TOPICS:
            print(f"- {key}")
        topic_choice = input("Select a topic ('back'=return): ").strip().lower()
        if topic_choice == 'back':
            return
        if hasattr(TOPICS, topic_choice):
            app.selected_topic = getattr(TOPICS, topic_choice)
            threading.Thread(target=app.subscribe, args=(app.client,)).start()
            print(f"Now subscribed to topic: {app.selected_topic}")
        else:
            print("Invalid topic.")

    @staticmethod
    def recv_mode(app):
        app.current_mode = 'receive'
        print('Receive Mode - Listening for messages...')
        print('Press ENTER to exit receive mode.')

        def wait_for_exit():
            input()  # Wait for ENTER key
            app.current_mode = None
            print('Exited receive mode.')
        
        exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
        exit_thread.start()

    @staticmethod
    def choice(app, mode_choice):
        match mode_choice:
            case 'send': return MonitorService.publish_mode(app)
            case 'recv': return MonitorService.recv_mode(app)
            case 'subscribe': return MonitorService.subscribe_mode(app)