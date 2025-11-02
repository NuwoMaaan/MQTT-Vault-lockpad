import random
import json
import psutil
import time
from datetime import datetime

def generate_padlock_status_data():
    time.sleep(5)                                         
    state = random.choice(["locked", "unlocked"])
    error = random.choice([None, "Authorization_failure", "Mechanical_failure", "Malfunction"]) 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "state": state,
        "error": error,
        "timestamp": timestamp,
    }
    return json.dumps(data)                                                 
                                                                            
def generate_padlock_metric_data():
    time.sleep(5)
    cpu = psutil.cpu_percent(interval=None)
    cpu_formatted = f"{cpu:.2f}"
    login_attempts = random.randint(1,10)                                   
    network = psutil.net_io_counters()
    netstats = {
        "Packets_recv": str(network.packets_recv),
        "Packets_sent": str(network.packets_sent),
        "Network_Errors": str(network.errin)                               
        
    }
    
    data = {
        "CPU_Usage": f'{cpu_formatted}%',
        "Login_attempts": login_attempts,  #Value that triggers response code from zControlComputer.py
        "Network": netstats
    }
    return json.dumps(data)