import cv2
import tkinter as tk
import sys

def bgr2rgb(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def rgb2bgr(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image

def mirrorImage(image):
    image = cv2.flip(image, 1)
    return image


def createCallibrateWindow(monitor):
    window = tk.Tk()
    window_width = 400
    window_height = 400
    center_x = int(monitor.x + (monitor.width - window_width) / 2)
    center_y = int(monitor.y + (monitor.height - window_height) / 2)
    window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    window.title("Calibration")

    def on_close():
        window.destroy()
        sys.exit()

    window.protocol("WM_DELETE_WINDOW", on_close)

    label = tk.Label(window, text="1. Please look at the monitor. " \
    "\n 2. Press the 'Calibrate' button. " \
    "\n 3. Hold still for 2 seconds.", 
    font=("Arial", 24), wraplength=window_width, justify='left') 
    label.pack(expand=True, fill=tk.BOTH)
    button = tk.Button(window, text="Calibrate", command=window.destroy, bg="blue", font=("Arial", 24))
    button.pack(expand=True, fill=tk.BOTH)
    
    window.mainloop()