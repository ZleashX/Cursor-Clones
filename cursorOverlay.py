import tkinter as tk
import threading
from utils import CursorMode

class CursorOverlay(threading.Thread):
    def __init__(self, monitor_manager, mouse):
        threading.Thread.__init__(self)
        self.mouse = mouse
        self.monitor_manager = monitor_manager
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
            window.attributes('-transparentcolor', 'white')
            window.overrideredirect(1)
                       
            window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
            canvas = tk.Canvas(window, bg='white', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            self.windows.append(window)
            self.canvases.append(canvas)
    
    def updateOverlays(self):
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
                    
                # Draw cursor
                cursor_size = 15
                canvas.create_oval(local_x-cursor_size, local_y-cursor_size,
                                local_x+cursor_size, local_y+cursor_size,
                                outline='red', width=2)
                canvas.create_line(local_x-cursor_size, local_y,
                                local_x+cursor_size, local_y,
                                fill='red', width=2)
                canvas.create_line(local_x, local_y-cursor_size,
                                local_x, local_y+cursor_size,
                                fill='red', width=2)
    
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
