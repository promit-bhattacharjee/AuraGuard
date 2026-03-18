import cv2 as cv
import numpy as np
from src.DrawBox import DrawBox
from src.States import StateController
from src.Time import TimeController

class Webcam:
    """
    Main capture engine for AuraGuard. Handles the video stream loop
    and evaluates behavioral rules based on detection data.
    """
    def __init__(self, time_controller: TimeController, state_controller: StateController, draw_box_obj: DrawBox):
        self.time_controller = time_controller
        self.state_controller = state_controller
        self.draw_box_obj = draw_box_obj 
        
        # Start in Normal state (User is at desk, no phone, no dehydration)
        self.state_controller.state = self.state_controller.normal_STATE
            
        # Initial threshold starts for hydration and deep work
        self.time_controller.hydration_time.threshold_time_start()
        self.time_controller.deepwork_time.threshold_time_start()

    def videocapture(self):
        """
        Primary application loop. Captures frames, triggers inference,
        and manages state transitions.
        """
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FPS, 15) # Match our processing target
        
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret or (cv.waitKey(1) & 0xFF == ord("q")): 
                break
            
            # Resource optimization: Only process at the target FPS (default 15)
            if self.time_controller.stream_time.should_process_frame():    
                detected_objects = self.draw_box_obj.box_on_frame(
                    frame=frame, 
                    time_obj=self.time_controller.stream_time, 
                    state_obj=self.state_controller
                )
                
                # --- DETECTION FLAGS ---
                is_person_present = 'person' in detected_objects
                is_using_phone    = 'cell phone' in detected_objects
                is_hydrating      = 'cup' in detected_objects or 'bottle' in detected_objects

                # --- 1. USER AT DESK LOGIC ---
                if is_person_present:
                    self.time_controller.emptydesk_time.threshold_time_end()
                    
                    # A. Recovery Case: User was previously 'Away'
                    if self.state_controller.state == self.state_controller.emptydesk_STATE:
                        self.state_controller.state = self.state_controller.normal_STATE
                        self.time_controller.stream_time.stream_resume()

                    # B. Deep Work Logic (Baseline presence state)
                    dw_dur = self.time_controller.deepwork_time.get_threshold_time_seconds()
                    if dw_dur >= self.state_controller.deepwork_STATE.threshold:
                        self.state_controller.state = self.state_controller.deepwork_STATE
                    else:
                        self.state_controller.state = self.state_controller.normal_STATE
                        # Restart deep work clock if phone was recently put away
                        if self.time_controller.deepwork_time.threshold_start_time == 0:
                            self.time_controller.deepwork_time.threshold_time_start()

                    # C. Hydration Logic
                    if is_hydrating:
                        # Seen bottle/cup? Reset the gap timer to zero
                        self.time_controller.hydration_time.threshold_time_end()
                        self.time_controller.hydration_time.threshold_time_start()
                    else:
                        # Not seen? Check if the gap exceeds the 30-min (demo: 30s) limit
                        h_dur = self.time_controller.hydration_time.get_threshold_time_seconds()
                        if h_dur >= self.state_controller.dehydrated_STATE.threshold:
                            self.state_controller.state = self.state_controller.dehydrated_STATE

                    # D. Phone Logic (Highest priority override)
                    if is_using_phone:
                        # 2-second continuous threshold to avoid flicker alerts
                        if self.time_controller.distraction_time.threshold_start_time == 0:
                            self.time_controller.distraction_time.threshold_time_start()
                        
                        dist_dur = self.time_controller.distraction_time.get_threshold_time_seconds()
                        if dist_dur >= self.state_controller.distracted_STATE.threshold:
                            self.state_controller.state = self.state_controller.distracted_STATE
                            self.time_controller.deepwork_time.threshold_time_end() # Kill focus session
                    else:
                        self.time_controller.distraction_time.threshold_time_end()

                # --- 2. DESK IS EMPTY LOGIC ---
                else:
                    if self.time_controller.emptydesk_time.threshold_start_time == 0:
                        self.time_controller.emptydesk_time.threshold_time_start()
                    
                    e_dur = self.time_controller.emptydesk_time.get_threshold_time_seconds()
                    if e_dur >= self.state_controller.emptydesk_STATE.threshold:
                        self.state_controller.state = self.state_controller.emptydesk_STATE
                        self.time_controller.stream_time.stream_pause()
                        self.time_controller.deepwork_time.threshold_time_end()

        cap.release()
        cv.destroyAllWindows()