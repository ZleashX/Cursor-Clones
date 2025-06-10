from screeninfo import get_monitors
from utils import CursorMode

class Monitor:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.center = (x + width // 2, y + height // 2)
        #default last position is the center of the monitor
        self.last_position = self.center


class MonitorManager:
    def __init__(self, cursor_mode = CursorMode.LASTLOC_ClONE):
        monitors = get_monitors()
        self.total_monitors = len(monitors)
        self.monitor_list = [Monitor(m.width, m.height, m.x, m.y) for m in monitors]
        # Sort monitors by x coordinate to ensure left-to-right order
        self.monitor_list.sort(key=lambda monitor: monitor.x)
        self.active_monitor_index = 0
        self.look_monitor_index = 0
        self.cursor_mode = cursor_mode
        self.iswitching = False

    def print_info(self):
        for i, monitor in enumerate(self.monitor_list):
            print(f"Monitor {i}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y}), last position: {monitor.last_position}")

    def getMonitorIndexAtPoint(self, x, y):
        for i, monitor in enumerate(self.monitor_list):
            if monitor.x <= x < monitor.x + monitor.width and monitor.y <= y < monitor.y + monitor.height:
                return i
        return None
    
    def isPointInMonitor(self, x, y, monitor_index):
        monitor = self.monitor_list[monitor_index]
        return monitor.x <= x < monitor.x + monitor.width and monitor.y <= y < monitor.y + monitor.height
    
    def switchMonitor(self, mouse):
        if 0 <= self.look_monitor_index < self.total_monitors and self.look_monitor_index != self.active_monitor_index:
            self.iswitching = True
            if self.cursor_mode in [CursorMode.LASTLOC_ClONE, CursorMode.LASTLOC_NOCLONE]:
                self.monitor_list[self.active_monitor_index].last_position = mouse.position
                mouse.position = self.monitor_list[self.look_monitor_index].last_position
            else:
                x, y = mouse.position
                active_monitor = self.monitor_list[self.active_monitor_index]
                active_x = x - active_monitor.x
                active_y = y - active_monitor.y
                ratio_x = active_x / active_monitor.width
                ratio_y = active_y / active_monitor.height
                x_new = int(self.monitor_list[self.look_monitor_index].width * ratio_x) + self.monitor_list[self.look_monitor_index].x
                y_new = int(self.monitor_list[self.look_monitor_index].height * ratio_y) + self.monitor_list[self.look_monitor_index].y
                mouse.position = (x_new, y_new)
            self.active_monitor_index = self.look_monitor_index
            self.iswitching = False


    def isCursorCrossMonitor(self, mouse):
        #called when the mouse is moved to check if the cursor is crossing monitors manually
        #if the cursor is in the current monitor, do nothing
        #if the cursor is in another monitor, switch to that monitor, and set the last position of the last monitor to the center
        current_monitor_index = self.getMonitorIndexAtPoint(mouse.position[0], mouse.position[1])
        if current_monitor_index is not None and current_monitor_index != self.active_monitor_index and not self.iswitching:
            self.monitor_list[self.active_monitor_index].last_position = self.monitor_list[self.active_monitor_index].center
            self.active_monitor_index = current_monitor_index
        
    def resetMonitors(self):
        # Reset all monitors to their last position
        for monitor in self.monitor_list:
            monitor.last_position = monitor.center
        
if __name__ == "__main__":
    monitor_manager = MonitorManager()
    monitor_manager.print_info()