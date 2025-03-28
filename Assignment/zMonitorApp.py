import random
import threading
from paho.mqtt import client as mqtt_client
#BEFORE
#MQTT broker configuration
broker = 'rule28.i4t.swin.edu.au'
port = 1883

#predefined topics
topics = {
    "control": "<103996982>/padlock/control",
    "status": "<103996982>/padlock/status",
    "metrics": "<103996982>/padlock/metrics",
    "lockout": "<103996982>/padlock/control/lockout"
}


client_id = f'client-{random.randint(0, 100)}'
username = '<103996982>'
password = '<103996982>'

#global variables
selected_topic = None
current_mode = None
messages = []

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")
                                                                        #Base code from: https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
def connect_mqtt() -> mqtt_client:                                      #Majority use of mqtt is based from here - then added with my functionality for all programs
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

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

def run():
    global current_mode, selected_topic
    client = connect_mqtt()
    client.loop_start()

    while True:                                                        
        mode_choice = input("MODE (recv|send|exit): ").strip().lower()   #Prompting for mode, depending on mode, will determine what is 
                                                                         #printed the screen. 
        if mode_choice == "exit":
            break
###################################### - publish mode
        if mode_choice == "send":                                        
            current_mode = "publish"                                               
            print("Switched to publish mode.")
            print('Topics: ')
            for key in topics:                                                     #Prints available topics
                print(f'- {key}')
            topic_choice = input("Select a topic to publish to ('back'=return): ").strip().lower()
            if topic_choice in topics:
                selected_topic = topics[topic_choice]                             #Verfiy input is valid, If valid; create and start thread to publish(send) 
                threading.Thread(target=publish, args=(client,)).start()          #(Threading to allow for ability to send and receive data)
            elif topic_choice == 'back':
                current_mode = 'receive'
            else:
                print("Invalid topic. Please choose a valid topic.")
###################################### - receive mode
        if mode_choice == "recv":   
            current_mode = "receive_menu"                                            #When entering receive mode initially messages will stop being printed so you can select with interference
            recv_mode = input('Enter "back" to view messages\n\r"recv" to select topic: ').strip().lower()
            if recv_mode == 'back':
                current_mode = 'receive'
            elif recv_mode == 'recv':
                current_mode = "receive_menu"                                   #if, elif, else Definitely could be arranged better lol
            else:
                print('Invalid input')
                current_mode = 'receive'
            if current_mode == 'receive_menu':
                print('Topics: ')
                for key in topics:                                                     #Prints available topics from dictionary
                    print(f'- {key}')
                topic_choice = input("Select a topic to subscribe to ('back'=return): ").strip().lower()
                if topic_choice in topics:
                    selected_topic = topics[topic_choice]                              #Verfiy input is valid, If valid; create and start thread to subscribe(recv)
                    threading.Thread(target=subscribe, args=(client,)).start()         #(Threading to allow for ability to send and receive data)
                    print(f"Now subscribed to topic: {selected_topic}")
                    current_mode = 'receive'
                elif topic_choice == 'back':                                           #usability options, goes return to main prompt and receive mode
                    current_mode = 'receive'
                else:
                    print("Invalid topic. Please choose a valid topic.")
                    current_mode = 'receive'
        if mode_choice == '':                                               #if 'enter' key is pressed prompt is reprinted to screen awaiting input
            pass
        

    client.loop_stop()  
    client.disconnect()  

if __name__ == '__main__':
    run()

####### ----IGNORE ---- #######
 #received message = {"CPU_Usage": "3.80%", "Temp": "19.00", "Network": {"Packets_recv": "84724", "Packets_sent": "46577", "Network_Errors": "0"}}
        #split 1 = "19.00", "Network": {"Packets_recv": "84724", "Packets_sent": "46577", "Network_Errors": "0"}}
        #split 2 = "19.00"
        # if '"Temp":' in received_message:
        #     split1 = received_message.split('"Temp":', 1)[1]
        #     print(split1)
        #     split2 = split1.split(',', 1)[0]
        #     print(split2)
        #     temp = split2.replace('"', '').strip()
        #     print(temp)
        #     if float(temp) > 15:
        #         return True
        # else:
        #     print('NO TEMP IN MESSAGE: ERROR')
                