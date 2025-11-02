import random
import threading
import keyboard
from paho.mqtt import client as mqtt_client
from connections.connect import connect_mqtt
from schemas import topics

#global variables
selected_topic = None
current_mode = None
messages = []

def publish(client):
    global selected_topic                             
    message = input("Enter message to send: ")                
    result = client.publish(selected_topic, message)             #Publish method to send data to selected topic
    status = result[0]
    if status == 0:
        handleheader(selected_topic)                            #print message, topic, and topic header 
        print(f"Sent: '{message}' to topic: {selected_topic}\n\r")
    else:
        print(f"Failed to send message to topic {selected_topic}")
    
    reset_mode()                                                #reset mode to recieve as it takes user back to main prompt where they can select mode.
        

def on_message(client, userdata, msg):
    global messages
    received_message = msg.payload.decode()
    messages.append(f"Received '{received_message}'\n\r from topic: {msg.topic}\n\r")  #appending messages but only printing when mode is 'receive'
    if current_mode == 'publish':
        pass          
    elif current_mode == 'receive':                                            #Checking if current mode is 'receive' to determine if output should be display to screen
        handleheader(msg.topic)                                              #Prints the header, prints the message
        print(messages[-1])                                                                                  
        print("IF BLANK PRESS 'ENTER' FOR PROMPT")                           #Because of in receive mode, constant display messages/headers or data received will flood the screen
    else: pass
                                                      #Print statement will show after each printed message/header for usability. 
def subscribe(client):
    global selected_topic
    client.subscribe(selected_topic)                                         #subscribing to selected topic.
    client.on_message = on_message

def handleheader(topic):
    header_width = 41
    header = (f"\n=============================================\n"
          f"| {topic.ljust(header_width)} |\n"                         #Formatting a nice header that is dependent on sending or receiving topic
          f"=============================================")
    print(header)
    
def reset_mode():
    global current_mode
    current_mode = None

def choice(mode_choice, client):
    match mode_choice:
        case 'send': return publish_mode(client)
        case 'recv': return recv_mode(client)
        case 'subscribe': return subscribe_mode(client)

def publish_mode(client): 
        global selected_topic,current_mode 
        current_mode = 'publish'                                                                    
        print("Switched to publish mode.")
        print('Topics: ')
        for key in topics:                                                     
            print(f'- {key}')
        topic_choice = input("Select a topic to publish to ('back'=return): ").strip().lower()
        if topic_choice in topics:
            selected_topic = topics[topic_choice]                              
            threading.Thread(target=publish, args=(client,)).start()          
        elif topic_choice == 'back':
            current_mode = None
        else:
            print("Invalid topic. Please choose a valid topic.")
            current_mode = None

def recv_mode(client):
        global selected_topic, current_mode
        current_mode = 'receive'
        print('Receive Mode - Now Receiving Messages From Subscribed Topcis')                                          
        back = input('Enter "any key" to return\n').strip().lower()    
        keyboard.read_key()
        current_mode = None
        


def subscribe_mode(client):
        global selected_topic,current_mode
        print('Topics: ')
        for key in topics:                                                    
            print(f'- {key}')
        topic_choice = input("Select a topic to subscribe to ('back'=return): ").strip().lower()
        if topic_choice in topics:
            selected_topic = topics[topic_choice]                              
            threading.Thread(target=subscribe, args=(client,)).start()        
            print(f"Now subscribed to topic: {selected_topic}")
        elif topic_choice == 'back':
            current_mode = None
        else:
            print("Invalid topic. Please choose a valid topic.")
            current_mode = None



def run():
    global current_mode, selected_topic
    client = connect_mqtt()
    client.loop_start()

    while True:                                                        
        mode_choice = input("MODE (recv|send|subscribe|exit): ").strip().lower()   #Prompting for mode, depending on mode, will determine what is 
                                                                        
        if mode_choice == "exit":
            break

        choice(mode_choice, client)

        if mode_choice == '':                                             
            pass
        

    client.loop_stop()  
    client.disconnect()  

if __name__ == '__main__':
    run()

