import cv2 as cv
import time
from src.Colors import Colors
from src.DrawBox import DrawBox
from src.States import States, StateController
from src.Time import TimeController

class webcam:
    def __init__(self, time_controller: TimeController, state_controller: StateController, draw_box_obj: DrawBox):
        self.time_controller = time_controller
        self.state_controller = state_controller
        self.draw_box_obj = draw_box_obj 
        
        # Ensure the state starts as a list to support multiple simultaneous alerts
        if not isinstance(self.state_controller.state, list):
            self.state_controller.state = [self.state_controller.normal_STATE]
            
        # Initialize the baseline timers
        self.time_controller.hydration_time.threshold_time_start()
        # Deep Work needs a start time to begin counting towards its 10s/10m threshold
        self.time_controller.deepwork_time.threshold_time_start()

    def videocapture(self):
        # CAP_DSHOW is faster on Windows; 0 is usually the integrated webcam
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FPS, 15)
        
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret: 
                break
            
            # 1. Listen for 'q' to quit
            if cv.waitKey(1) & 0xFF == ord("q"): 
                break
            
            # 2. Process frame based on your StreamTime frequency (e.g., every 5th frame)
            if self.time_controller.stream_time.should_process_frame():    
                detected_objects = self.draw_box_obj.box_on_frame(
                    frame=frame, 
                    time_obj=self.time_controller.stream_time, 
                    state_obj=self.state_controller
                )
                
                # --- CASE A: USER IS AT DESK ---
                if 'person' in detected_objects:
                    # Clear 'Away' status if they just returned
                    if self.state_controller.emptydesk_STATE in self.state_controller.state:
                        self.state_controller.state.remove(self.state_controller.emptydesk_STATE)
                        self.time_controller.stream_time.stream_resume()

                    # --- Distraction Logic (Phone) ---
                    if 'cell phone' in detected_objects:
                        if self.state_controller.distracted_STATE not in self.state_controller.state:
                            # Start timer if it's the first time seeing the phone
                            if self.time_controller.distruction_time.treshold_start_time == 0:
                                self.time_controller.distruction_time.threshold_time_start()
                            
                            duration = self.time_controller.distruction_time.get_threshold_time_seconds()
                            if duration >= self.state_controller.distracted_STATE.threshold:
                                # Remove Normal, add Distracted
                                if self.state_controller.normal_STATE in self.state_controller.state:
                                    self.state_controller.state.remove(self.state_controller.normal_STATE)
                                self.state_controller.state.append(self.state_controller.distracted_STATE)
                                # Phone resets the Deep Work progress
                                self.time_controller.deepwork_time.threshold_time_end()
                    else:
                        # Reset phone timer when phone is gone
                        self.time_controller.distruction_time.threshold_time_end()
                        if self.state_controller.distracted_STATE in self.state_controller.state:
                            self.state_controller.state.remove(self.state_controller.distracted_STATE)

                    # --- Hydration Logic ---
                    if 'cup' in detected_objects or 'bottle' in detected_objects:
                        # Reset Dehydrated status if it was active
                        if self.state_controller.dehydrated_STATE in self.state_controller.state:
                            self.state_controller.state.remove(self.state_controller.dehydrated_STATE)
                        # Refresh the 30-minute timer
                        self.time_controller.hydration_time.threshold_time_end()
                        self.time_controller.hydration_time.threshold_time_start()
                    else:
                        h_duration = self.time_controller.hydration_time.get_threshold_time_seconds()
                        if h_duration >= self.state_controller.dehydrated_STATE.threshold:
                            if self.state_controller.dehydrated_STATE not in self.state_controller.state:
                                if self.state_controller.normal_STATE in self.state_controller.state:
                                    self.state_controller.state.remove(self.state_controller.normal_STATE)
                                self.state_controller.state.append(self.state_controller.dehydrated_STATE)

                    # --- Deep Work Logic ---
                    dw_duration = self.time_controller.deepwork_time.get_threshold_time_seconds()
                    if dw_duration >= self.state_controller.deepwork_STATE.threshold:
                        if self.state_controller.deepwork_STATE not in self.state_controller.state:
                            if self.state_controller.normal_STATE in self.state_controller.state:
                                self.state_controller.state.remove(self.state_controller.normal_STATE)
                            self.state_controller.state.append(self.state_controller.deepwork_STATE)

                    # --- Fallback: Ensure 'Normal' is present if no alerts are active ---
                    if not self.state_controller.state:
                        self.state_controller.state.append(self.state_controller.normal_STATE)
                        # Restart deep work timer if it was killed by an alert
                        if self.time_controller.deepwork_time.treshold_start_time == 0:
                            self.time_controller.deepwork_time.threshold_time_start()

                # --- CASE B: DESK IS EMPTY ---
                else:
                    if self.state_controller.emptydesk_STATE not in self.state_controller.state:
                        if self.time_controller.emptydesk_time.treshold_start_time == 0:
                            self.time_controller.emptydesk_time.threshold_time_start()
                        
                        e_duration = self.time_controller.emptydesk_time.get_threshold_time_seconds()
                        if e_duration >= self.state_controller.emptydesk_STATE.threshold:
                            # User is officially away: Clear warnings and pause stream
                            self.state_controller.state.clear()
                            self.state_controller.state.append(self.state_controller.emptydesk_STATE)
                            self.time_controller.stream_time.stream_pause()
                            self.time_controller.deepwork_time.threshold_time_end()
                            self.time_controller.emptydesk_time.threshold_time_end()

        cap.release()
        cv.destroyAllWindows()