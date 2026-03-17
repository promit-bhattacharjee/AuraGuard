import time

class Time:
    def __init__(self):
        """Initialize a new timer instance with its own independent state."""
        self.stream_start_time = time.perf_counter()
        self.stream_pause_start_time = 0.0
        self.prev_frame_time = 0.0
        self.pause = False
        self.treshold_start_time = 0.0

    def get_time_string(self):
        if self.pause:
            seconds_elapsed = self.stream_pause_start_time - self.stream_start_time
        else:
            seconds_elapsed = time.perf_counter() - self.stream_start_time
        
        hours = int(seconds_elapsed // 3600)
        mins  = int((seconds_elapsed % 3600) // 60)
        secs  = int(seconds_elapsed % 60)
        
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    
    def threshold_time_start(self):
        self.treshold_start_time = time.perf_counter()

    def get_threshold_time_seconds(self):
        if self.treshold_start_time == 0:
            return 0
        
        # Calculate current 'active' time based on pause state
        if self.pause:
            current_active_time = self.stream_pause_start_time
        else:
            current_active_time = time.perf_counter()
            
        return int(current_active_time - self.treshold_start_time)

    def threshold_time_end(self):
        self.treshold_start_time = 0.0
    
    def stream_pause(self):
        if not self.pause:
            self.stream_pause_start_time = time.perf_counter()
            self.pause = True

    def stream_resume(self):
        if self.pause:
            pause_duration = time.perf_counter() - self.stream_pause_start_time
            # Shift the start time forward by the duration of the pause
            self.stream_start_time += pause_duration
            self.stream_pause_start_time = 0.0
            self.pause = False

    def should_process_frame(self, target_fps=15):
        current_time = time.perf_counter()
        if current_time - self.prev_frame_time > (1.0 / target_fps):
            self.prev_frame_time = current_time
            return True
        return False

class TimeController:
    def __init__(self):
        self.stream_time=Time()
        self.emptydesk_time=Time()
        self.distruction_time=Time()
        self.hydration_time=Time()
        self.deepwork_time=Time()