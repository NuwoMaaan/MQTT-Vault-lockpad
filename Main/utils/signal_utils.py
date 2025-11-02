import signal
import sys
import threading

shutdown_flag = threading.Event()

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print('\nShutdown signal received. Stopping...')
    shutdown_flag.set()
    sys.exit(0)

def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):  # SIGTERM might not be available on Windows
        signal.signal(signal.SIGTERM, signal_handler)

def is_shutting_down():
    """Check if shutdown has been requested"""
    return shutdown_flag.is_set()