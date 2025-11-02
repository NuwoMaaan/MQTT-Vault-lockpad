
from schemas.topics import TOPICS

def console_out(result_status, result_metric, padlock_status_data, padlock_metric_data):
    publish_status_status = result_status[0]
    publish_metrics_status = result_metric[0]

    if publish_status_status == 0:
        print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_status_data}, topic: {TOPICS.status}\n\r")
    else:
        print(f"Failed to send message to topic {TOPICS.status}")
    if publish_metrics_status == 0:
        print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_metric_data}, topic: {TOPICS.metrics}\n\r")
    else:
        print(f"Failed to send message to topic {TOPICS.metrics}")