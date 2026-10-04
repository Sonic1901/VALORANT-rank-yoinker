import threading

menu_check_requested = threading.Event()


def request_menu_check():
    """Wake the backend so it checks the current VALORANT state."""
    menu_check_requested.set()
