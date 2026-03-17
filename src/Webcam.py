import cv2 as cv
import numpy as np
from src.DrawBox import DrawBox
from src.States import StateController
from src.Time import TimeController

class webcam:
    def __init__(self, time_controller: TimeController, state_controller: StateController, draw_box_obj: DrawBox):
        self.time_controller = time_controller
        self.state_controller = state_controller
        self.draw_box_obj = draw_box_obj 
        
        # Initialize state as a single variable
        self.state_controller.state = self.state_controller.normal_STATE
            
        # Start baseline timers
        self.time_controller.hydration_time.threshold_time_start()
        self.time_controller.deepwork_time.threshold_time_start()

    def videocapture(self):
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FPS, 15)
        
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret or (cv.waitKey(1) & 0xFF == ord("q")): 
                break
            
            if self.time_controller.stream_time.should_process_frame():    
                detected_objects = self.draw_box_obj.box_on_frame(
                    frame=frame, 
                    time_obj=self.time_controller.stream_time, 
                    state_obj=self.state_controller
                )
                
                # --- BOOLEAN FLAGS ---
                is_person_present = 'person' in detected_objects
                is_using_phone    = 'cell phone' in detected_objects
                is_hydrating      = 'cup' in detected_objects or 'bottle' in detected_objects

                # --- 1. PERSON AT DESK LOGIC ---
                if is_person_present:
                    self.time_controller.emptydesk_time.threshold_time_end()
                    
                    # A. Initial check: If we were "Away", reset to "Normal" to begin
                    if self.state_controller.state == self.state_controller.emptydesk_STATE:
                        self.state_controller.state = self.state_controller.normal_STATE
                        self.time_controller.stream_time.stream_resume()

                    # B. Deep Work / Normal Logic (The baseline state)
                    dw_dur = self.time_controller.deepwork_time.get_threshold_time_seconds()
                    if dw_dur >= self.state_controller.deepwork_STATE.threshold:
                        self.state_controller.state = self.state_controller.deepwork_STATE
                    else:
                        self.state_controller.state = self.state_controller.normal_STATE
                        # Restart deep work timer if it was killed by a phone earlier
                        if self.time_controller.deepwork_time.treshold_start_time == 0:
                            self.time_controller.deepwork_time.threshold_time_start()

                    # C. Hydration Logic (Overwrites Baseline)
                    if is_hydrating:
                        self.time_controller.hydration_time.threshold_time_end()
                        self.time_controller.hydration_time.threshold_time_start()
                        # If we detect a bottle/cup, the state naturally stays DeepWork/Normal (per your request)
                    else:
                        h_dur = self.time_controller.hydration_time.get_threshold_time_seconds()
                        if h_dur >= self.state_controller.dehydrated_STATE.threshold:
                            self.state_controller.state = self.state_controller.dehydrated_STATE

                    # D. Phone Logic (Final Overwrite - Latest/Highest Priority)
                    if is_using_phone:
                        if self.time_controller.distruction_time.treshold_start_time == 0:
                            self.time_controller.distruction_time.threshold_time_start()
                        
                        dist_dur = self.time_controller.distruction_time.get_threshold_time_seconds()
                        if dist_dur >= self.state_controller.distracted_STATE.threshold:
                            self.state_controller.state = self.state_controller.distracted_STATE
                            self.time_controller.deepwork_time.threshold_time_end()
                    else:
                        self.time_controller.distruction_time.threshold_time_end()

                # --- 2. DESK IS EMPTY LOGIC ---
                else:
                    if self.time_controller.emptydesk_time.treshold_start_time == 0:
                        self.time_controller.emptydesk_time.threshold_time_start()
                    
                    e_dur = self.time_controller.emptydesk_time.get_threshold_time_seconds()
                    if e_dur >= self.state_controller.emptydesk_STATE.threshold:
                        self.state_controller.state = self.state_controller.emptydesk_STATE
                        self.time_controller.stream_time.stream_pause()
                        self.time_controller.deepwork_time.threshold_time_end()

        cap.release()
        cv.destroyAllWindows()