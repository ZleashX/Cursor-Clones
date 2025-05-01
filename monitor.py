from screeninfo import get_monitors

class Monitor:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y


class MonitorManager:
    def __init__(self):
        monitors = get_monitors()
        self.total_monitors = len(monitors)
        self.monitor_list = [Monitor(m.width, m.height, m.x, m.y) for m in monitors]
        self.active_monitor_index = 0

    def print_info(self):
        for i, monitor in enumerate(self.monitor_list):
            print(f"Monitor {i}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")

    def getMonitorIndexAtPoint(self, x, y):
        for i, monitor in enumerate(self.monitor_list):
            if monitor.x <= x < monitor.x + monitor.width and monitor.y <= y < monitor.y + monitor.height:
                return i
        return None
    
    def switchMonitor(self, monitor_index, mouse):
        if 0 <= monitor_index < self.total_monitors and monitor_index != self.active_monitor_index:
            self.active_monitor_index = monitor_index
            active_monitor = self.monitor_list[monitor_index]
            mouse.position = (active_monitor.x + active_monitor.width // 2, active_monitor.y + active_monitor.height // 2)
        
        
if __name__ == "__main__":
    monitor_manager = MonitorManager()
    monitor_manager.print_info()