"""Decides which application get recorded based on whitelist and blacklist.
An app is whitelisted if starts with or ends with a string in the whitelist.
An app is blacklisted if it contains a string in the blacklist.
Blacklist takes precedence over whitelist.
If no app is focused, no app is recorded.
"""


import tkinter as tk
from tkinter import messagebox
import threading
from time import sleep
from settings import HOME_DIR

WHITELIST = tuple()
BLACKLIST = tuple()


def isWhiteListed(app_name: str) -> str|bool:
    """Returns the whitlisted app name if it is whitelisted, otherwise False."""

    if not app_name:
        return False

    if not WHITELIST:
        return False

    for wl in WHITELIST:
        if app_name.endswith(wl) or app_name.startswith(wl):
            return wl

    return False


def isBlackListed(app_name: str) -> bool:
    """Returns True if the app is blacklisted or no focus is on an app."""

    if not app_name:# if no app is focused app_name ""
        return True

    if not BLACKLIST:
        return False

    for bl in BLACKLIST:
        if bl in app_name:
            return True

    return False


def update_lists():
    global WHITELIST, BLACKLIST
    wl = whitelist_listbox.get(0, tk.END)
    bl = blacklist_listbox.get(0, tk.END)
    # cleanse the lists of trailing newline characters
    WHITELIST = tuple([item.replace("\n", "") for item in wl])
    BLACKLIST = tuple([item.replace("\n", "") for item in bl])
    print(WHITELIST, BLACKLIST)


def save_lists():
    with open(HOME_DIR / ".settings" / "whitelist.txt", "w") as f:
        for item in WHITELIST:
            f.write(item + "\n")

    with open(HOME_DIR / ".settings" / "blacklist.txt", "w") as f:
        for item in BLACKLIST:
            f.write(item + "\n")


def load_lists():
    global WHITELIST, BLACKLIST
    try:
        with open(HOME_DIR / ".settings" / "whitelist.txt", "r") as f:
            WHITELIST = tuple(f.readlines())
            WHITELIST = tuple([item.strip() for item in WHITELIST])
    except FileNotFoundError:
        WHITELIST = tuple()

    try:
        with open(HOME_DIR / ".settings" / "blacklist.txt", "r") as f:
            BLACKLIST = tuple(f.readlines())
            BLACKLIST = tuple([item.strip() for item in BLACKLIST])
    except FileNotFoundError:
        BLACKLIST = tuple()


def add_to_list(listbox, entry):
    item = entry.get()
    if item:
        listbox.insert(tk.END, item)
        entry.delete(0, tk.END)
        update_lists()
    else:
        messagebox.showwarning("Input Error", "Please enter a valid item.")


def remove_from_list(listbox):
    selected_items = listbox.curselection()
    for item in selected_items[::-1]:
        listbox.delete(item)
    update_lists()


def wl_toggle(state_var):
    global WL_ENABLE
    if state_var.get():
        WL_ENABLE = True
    else:
        WL_ENABLE = False


def bl_toggle(listbox, state_var):
    global BL_ENABLE
    if state_var.get():
        BL_ENABLE = True
    else:
        BL_ENABLE = False


# Create main window
def create_window():
    global whitelist_listbox, blacklist_listbox
    global whitelist_state, blacklist_state
    global root
    root = tk.Tk()
    root.title("Whitelist and Blacklist Manager")

    # Create frames
    top_frame = tk.Frame(root)
    middle_frame = tk.Frame(root)
    bottom_frame = tk.Frame(root)

    top_frame.pack(side=tk.TOP, fill=tk.X)
    middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Create listboxes
    whitelist_listbox = tk.Listbox(middle_frame, selectmode=tk.MULTIPLE)
    blacklist_listbox = tk.Listbox(middle_frame, selectmode=tk.MULTIPLE)

    whitelist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    blacklist_listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create entry widgets
    whitelist_entry = tk.Entry(bottom_frame)
    blacklist_entry = tk.Entry(bottom_frame)

    whitelist_entry.pack(side=tk.LEFT, padx=10, pady=10)
    blacklist_entry.pack(side=tk.RIGHT, padx=10, pady=10)

    # Create buttons
    add_whitelist_button = tk.Button(
        bottom_frame,
        text="Add to Whitelist",
        command=lambda: add_to_list(whitelist_listbox, whitelist_entry),
    )
    remove_whitelist_button = tk.Button(
        bottom_frame,
        text="Remove from Whitelist",
        command=lambda: remove_from_list(whitelist_listbox),
    )

    add_blacklist_button = tk.Button(
        bottom_frame,
        text="Add to Blacklist",
        command=lambda: add_to_list(blacklist_listbox, blacklist_entry),
    )
    remove_blacklist_button = tk.Button(
        bottom_frame,
        text="Remove from Blacklist",
        command=lambda: remove_from_list(blacklist_listbox),
    )
    # Save button bottom center
    save_button = tk.Button(
        bottom_frame,
        text="Save",
        command=lambda: save_lists(),
    )

    add_whitelist_button.pack(side=tk.LEFT, padx=10, pady=10)
    remove_whitelist_button.pack(side=tk.LEFT, padx=10, pady=10)
    add_blacklist_button.pack(side=tk.RIGHT, padx=10, pady=10)
    remove_blacklist_button.pack(side=tk.RIGHT, padx=10, pady=10)
    save_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    for item in WHITELIST:
        whitelist_listbox.insert(tk.END, item)
    for item in BLACKLIST:
        blacklist_listbox.insert(tk.END, item)

    root.mainloop()


def open_window():
    gui_thread = threading.Thread(target=create_window, daemon=True)
    gui_thread.start()


def close_window():
    root.quit()
    root.destroy()
    root.update()


load_lists()

if __name__ == "__main__":
    from pprint import pprint

    open_window()

    while True:
        sleep(1)
        pprint((WHITELIST, BLACKLIST, WL_ENABLE, BL_ENABLE))
