from schemas.constants import TOPICS

def console_padlock_out(result_status, padlock_status_data,
                        result_metric, padlock_metric_data,
                        ):

    if result_status[0] == 0:
        print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_status_data}, topic: {TOPICS.status}\n\r")
    else:
        print(f"Failed to send message to topic: {TOPICS.status}")
    if result_metric[0] == 0:
        print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_metric_data}, topic: {TOPICS.metrics}\n\r")
    else:
        print(f"Failed to send message to topic: {TOPICS.metrics}")


def console_control_out(result_control, control_data):
    if result_control[0] == 0:
        print(f"Sent: CONTROL_SYS->PADLOCK: {control_data}, topic: {TOPICS.control}\n\r")
    else:
        print(f"Failed to send message to topic {TOPICS.control}")

def console_lock_out():
    print(f"LOCKOUT TRIGGERED: Vault Padlock is now: INDEFINITE_LOCKED\n\r")


def handleheader(topic):
        min_width = 20
        padding = 4  
        content_width = len(topic) + padding
        header_width = max(min_width, content_width)
        
        # Create the border line
        border = "=" * (header_width + 4)  # +4 for the | characters
        
        header = (f"\n{border}\n"
            f"| {topic.center(header_width)} |\n"                         
            f"{border}\n")
        print(header)

def ascii_art():
    art = r"""
  __  __  ___ _____ _____     _             
 |  \/  |/ _ \_   _|_   _|   /_\  _ __ _ __ 
 | |\/| | (_) || |   | |    / _ \| '_ \ '_ \
 |_|  |_|\__\_\|_|   |_|   /_/ \_\ .__/ .__/
                                 |_|  |_|   """
    print(art)