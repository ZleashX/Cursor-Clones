import tkinter as tk
import threading
import time
import colorsys
from utils import CursorMode
from PIL import Image, ImageTk

class CursorOverlay(threading.Thread):
    def __init__(self, monitor_manager, mouse):
        threading.Thread.__init__(self)
        self.mouse = mouse
        self.monitor_manager = monitor_manager
        self.hue = 0.0
        self.last_glow_time = [0.0] * monitor_manager.total_monitors
        self.last_look_monitor_index = -1
        self.stop_event = threading.Event()
        self.daemon = True  # Thread will exit when main program exits
        
    def run(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.windows = []
        self.canvases = []
        self.createOverlays()
        
        try:
            while not self.stop_event.is_set():
                self.updateOverlays()
                self.root.update()  # Process Tkinter events
        finally:
            self.cleanup()
    
    def createOverlays(self):
        for i, monitor in enumerate(self.monitor_manager.monitor_list):
            window = tk.Toplevel()
            window.attributes('-alpha', 0.7)
            window.attributes('-topmost', True)
            window.attributes('-transparentcolor', 'green')
            window.overrideredirect(1)
                       
            window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
            canvas = tk.Canvas(window, bg='green', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            self.windows.append(window)
            self.canvases.append(canvas)
        
        image = Image.open("cursor.png")
        image = image.resize((16,24))
        self.photo = ImageTk.PhotoImage(image)

    
    def updateOverlays(self):
        current_time = time.time()
        if self.last_look_monitor_index != self.monitor_manager.look_monitor_index:
            self.last_look_monitor_index = self.monitor_manager.look_monitor_index
            self.last_glow_time[self.last_look_monitor_index] = current_time

        for i, (monitor, canvas) in enumerate(zip(self.monitor_manager.monitor_list, self.canvases)):
            if not canvas.winfo_exists():  # Check if the canvas still exists
                continue
            canvas.delete("all")
            local_x = 0
            local_y = 0

            if i != self.monitor_manager.active_monitor_index and self.monitor_manager.cursor_mode not in [CursorMode.LASTLOC_NOCLONE, CursorMode.FOLLOW_NOCLONE]:
                if self.monitor_manager.cursor_mode == CursorMode.LASTLOC_ClONE:
                    x, y = monitor.last_position
                    local_x = x - monitor.x
                    local_y = y - monitor.y
                elif self.monitor_manager.cursor_mode == CursorMode.FOLLOW_CLONE:
                    x, y = self.mouse.position
                    active_monitor = self.monitor_manager.monitor_list[self.monitor_manager.active_monitor_index]
                    active_x = x - active_monitor.x
                    active_y = y - active_monitor.y
                    ratio_x = active_x / active_monitor.width
                    ratio_y = active_y / active_monitor.height
                    local_x = int(monitor.width * ratio_x)
                    local_y = int(monitor.height * ratio_y)

                if self.monitor_manager.look_monitor_index == i and (current_time - self.last_glow_time[i]) < 2.0:
                    
                    # Calculate center point
                    cx = local_x + 6
                    cy = local_y + 12

                    num_rings = 10
                    for i in range(num_rings):
                        # Cycle through hue with offset for each ring
                        hue = (self.hue + i * 0.01) % 1.0
                        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                        hex_color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
                        
                        radius = 40 - i * 2  # Decreasing radii
                        canvas.create_oval(
                            cx - radius,
                            cy - radius,
                            cx + radius,
                            cy + radius,
                            fill=hex_color,
                            outline='',
                            stipple='gray75',
                            width=0
                        )
                    # control the hue cycle speed
                    self.hue = (self.hue + 0.0001) % 1.0

                # Draw cursor
                canvas.create_image(local_x, local_y, image=self.photo, anchor="nw")
                

    def stop(self):
        self.stop_event.set()
    
    def cleanup(self):
        for window in self.windows:
            try:
                window.destroy()
            except:
                pass
        try:
            self.root.destroy()
        except:
            pass
