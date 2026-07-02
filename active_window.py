import pygetwindow as gw

def get_active_window_title():
    """
    Get the title of the currently active window.

    Returns:
        str: The title of the active window, or None if no active window is found.
    """
    try:
        active_window = gw.getActiveWindowTitle()
        if active_window is not None:
            return active_window
        else:
            return None
    except Exception as e:
        print(f"Error getting active window title: {e}")
        return None
    
print("Active window title:", get_active_window_title())    



    