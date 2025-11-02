from zControlComputer import run as run_control
from zVaultPadlock import run as run_padlock
from zMonitorApp import run as run_monitor
import threading

def main():
  
    # control_thread = threading.Thread(target=run_control)
    # padlock_thread = threading.Thread(target=run_padlock)
    # monitor_thread = threading.Thread(target=run_monitor)

    run_control()
    run_padlock()
    run_monitor()


if __name__ == "__main__":
    main()