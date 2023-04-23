import tkinter as tk
from tkinter import Tk,PhotoImage
import pystray
from PIL import ImageTk, Image
import threading



def placeholder():
    pass

def deletehistory():
    global historylist
    historylist=[]

def seehistory():
    history_window = tk.Toplevel(window)
    history_window.title("History")
    history_window.geometry("300x300")

    history_text = tk.Text(history_window, font=("Arial",10))
    history_text.pack(fill=tk.BOTH, expand=True)
    for item in historylist:
        history_text.insert(tk.END, item + "\n\n")

def sethistorysize():
    global historysize
    history_size_window = tk.Toplevel(window)
    history_size_window.title("Set History Size")
    history_size_window.geometry("300x100")

    history_size_entry = tk.Entry(history_size_window, width=10)
    history_size_entry.pack(pady=10)

    set_size_button = tk.Button(history_size_window, text="Set Size", command=lambda: set_size(history_size_entry, history_size_window))
    set_size_button.pack()

def set_size(entry, window):
    global historysize
    global historylist
    userinput = entry.get()
    try:
        historysize = int(userinput)
    except ValueError:
        pass
    historyclear()
    window.destroy()

def historyclear():
    global historysize
    global historylist
    if historysize < len(historylist):
        templist = []
        for i in range(historysize):
            templist += [historylist[-(i+1)]]
        templist.reverse()
        historylist = templist
    else:
        pass

def on_tray_click(icon, item):
    window.deiconify()
    icon.stop()

import threading

def minimize_to_tray():
    global icon
    image = icon_pil
    menu = pystray.Menu(pystray.MenuItem('Restore', on_tray_click))
    icon = pystray.Icon("name", image, "title", menu)

    # Run the icon in a separate thread
    t = threading.Thread(target=icon.run)
    t.start()

    # Convert icon back to a PhotoImage object
    icon = ImageTk.PhotoImage(icon_pil)
    window.iconphoto(True, icon)
    window.withdraw()




historysize = 10
historylist = []

window = tk.Tk()
window.title("Grabby")
window.geometry("1000x640")
window.configure(bg='#AAAAAA')


# Load the icon and create a PIL.Image object
icon_pil = Image.open("hand.ico")
icon_pil = icon_pil.resize((16, 16), Image.LANCZOS)


# Create the PhotoImage object from the PIL.Image object
icon = ImageTk.PhotoImage(icon_pil)
window.wm_iconphoto(True, icon)


minimize_button = tk.Button(window, text="Minimize to tray", command=minimize_to_tray)
minimize_button.pack()


menubar = tk.Menu(window)

settings = tk.Menu(menubar, tearoff=0)
settings.add_command(label="a",command=placeholder)
settings.add_command(label="b",command=placeholder)
menubar.add_cascade(label="Settings", menu=settings)

history = tk.Menu(menubar, tearoff=0)
history.add_command(label="See history",command=seehistory)
history.add_command(label="Delete history",command=deletehistory)
history.add_command(label="History length",command=sethistorysize)
menubar.add_cascade(label="History", menu=history)

window.config(menu=menubar)

mainbutton = tk.Button(window, text="Grab", command=placeholder, width=25, height=3, font=("Arial",20))
mainbutton.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

minimize_button = tk.Button

window.mainloop()
