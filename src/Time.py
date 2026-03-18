import time

class Time:
    """
    Precision timer for tracking durations (e.g., focus sessions, bottle presence).
    Supports pausing/resuming to handle desk-away periods.
    """
    def __init__(self):
        self.stream_start_time = time.perf_counter()
        self.stream_pause_start_time = 0.0
        self.prev_frame_time = 0.0
        self.pause = False
        self.threshold_start_time = 0.0

    def get_time_string(self):
        """Returns the formatted session time HH:MM:SS."""
        if self.pause:
            seconds_elapsed = self.stream_pause_start_time - self.stream_start_time
        else:
            seconds_elapsed = time.perf_counter() - self.stream_start_time
        
        hours = int(seconds_elapsed // 3600)
        mins  = int((seconds_elapsed % 3600) // 60)
        secs  = int(seconds_elapsed % 60)
        
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    
    def threshold_time_start(self):
        """Starts a high-precision threshold timer."""
        self.threshold_start_time = time.perf_counter()

    def get_threshold_time_seconds(self):
        """Calculates seconds elapsed on the threshold timer, respecting pauses."""
        if self.threshold_start_time == 0:
            return 0
        
        if self.pause:
            current_active_time = self.stream_pause_start_time
        else:
            current_active_time = time.perf_counter()
            
        return int(current_active_time - self.threshold_start_time)

    def threshold_time_end(self):
        """Resets the threshold timer."""
        self.threshold_start_time = 0.0
    
    def stream_pause(self):
        """Pauses the session clock when the user is away."""
        if not self.pause:
            self.stream_pause_start_time = time.perf_counter()
            self.pause = True

    def stream_resume(self):
        """Resumes the session clock, offsetting the pause duration."""
        if self.pause:
            pause_duration = time.perf_counter() - self.stream_pause_start_time
            self.stream_start_time += pause_duration
            self.stream_pause_start_time = 0.0
            self.pause = False

    def should_process_frame(self, target_fps=15):
        """Ensures consistent inference speed (FPS capping)."""
        current_time = time.perf_counter()
        if current_time - self.prev_frame_time > (1.0 / target_fps):
            self.prev_frame_time = current_time
            return True
        return False

class TimeController:
    """
    Orchestrates multiple Time instances for various system requirements.
    """
    def __init__(self):
        self.stream_time = Time()       # Overall session duration
        self.emptydesk_time = Time()    # Time since user left
        self.distraction_time = Time()  # Continuous phone usage duration
        self.hydration_time = Time()    # Time since bottle/cup last seen
        self.deepwork_time = Time()     # Continuous focus duration