from app.ControlComputer import run as run_control
from app.VaultPadlock import run as run_padlock
from app.MonitorApp import run as run_monitor


def main():

    # control_thread = threading.Thread(target=run_control)
    # padlock_thread = threading.Thread(target=run_padlock)
    # monitor_thread = threading.Thread(target=run_monitor)

    run_control()
    # run_padlock()
    # run_monitor()

    


if __name__ == "__main__":
    main()