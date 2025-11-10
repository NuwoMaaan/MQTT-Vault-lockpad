
from schemas.topics import TOPICS

def console_padlock_out(result_status, result_metric, padlock_status_data, padlock_metric_data):
    publish_status_status = result_status[0]
    publish_metrics_status = result_metric[0]

    if publish_status_status == 0:
        print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_status_data}, topic: {TOPICS.status}\n\r")
    else:
        print(f"Failed to send message to topic {TOPICS.status}")
    if publish_metrics_status == 0:
        print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_metric_data}, topic: {TOPICS.metrics}\n\r")
    else:
        print(f"Failed to send message")


def console_control_out(result_control, control_data):
    publish_control_status = result_control[0]

    if publish_control_status == 0:
        print(f"Sent: CONTROL_SYS->PADLOCK: {control_data}, topic: {TOPICS.control}\n\r")
    else:
        print(f"Failed to send message to topic {TOPICS.control}")

def console_lock_out(msg):
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