from ultralytics import YOLO
import supervision as sv
import numpy as np
import cv2 as cv
from src.Colors import Colors
from src.HeadsUpDisplay import HeadsUpDisplay

class DrawBox:
    def __init__(self, hud_obj: HeadsUpDisplay):
        """
        Handles object detection and visual rendering.
        """
        self.hud = hud_obj
        self.model = YOLO('yolo26n.pt')
        self.width = self.hud.width
        self.height = self.hud.height
        
        # Class IDs: 0=Person, 39=Bottle, 41=Cup, 67=Dining Table
        self.selected_classes = [39, 41, 67] 
        
        # Initialize Supervision Annotators
        self.box_annotator = sv.BoxAnnotator()
        self.person_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        
    def box_on_frame(self, frame, time_obj, state_obj):
        """
        Processes frame and renders UI based on active states.
        """
        # 1. Standardize Input Frame Size
        # This ensures the HUD coordinates (480x360) match the pixel data
        frame = cv.resize(frame, (self.width, self.height))

        # 2. Run Inference
        result = self.model(frame, show=False, verbose=False, save=False)[0]
        detections = sv.Detections.from_ultralytics(result)
        
        # 3. Filter Detections
        person_detections = detections[detections.class_id == 0]
        mask = np.isin(detections.class_id, self.selected_classes)
        other_detections = detections[mask]

        # Update Person Annotator Color from State
        self.person_annotator.color = state_obj.state.annotation_color

        # 4. Annotate the Frame
        annotated_frame = self.person_annotator.annotate(scene=frame, detections=person_detections)
        annotated_frame = self.box_annotator.annotate(scene=annotated_frame, detections=other_detections)
        
        # 5. Draw HUD Elements
        # --- Stream Time (Top Left) ---
        self.hud.draw_text(
            image=annotated_frame, 
            text=f"Stream: {time_obj.get_time_string()}", 
            org=(15, 25), 
            fontScale=0.45,
            color=Colors.TEXT_BLACK,
            thickness=1
        )

        # --- System State (Bottom Center) ---
        status_text = state_obj.state.text
        f_scale = 0.5
        thick = 2
        
        # Calculate horizontal center
        (tw, th), _ = cv.getTextSize(status_text, self.hud.font, f_scale, thick)
        center_x = (self.width - tw) // 2
        # Place 30 pixels above the bottom edge
        bottom_y = self.height - 30 

        self.hud.draw_text(
            image=annotated_frame, 
            text=status_text,
            org=(center_x, bottom_y), 
            fontScale=f_scale,
            color=state_obj.state.text_color,
            thickness=thick,
            flashing=state_obj.state.flashing_text
        )

        # 6. Final Display via HUD
        self.hud.draw_imshow(frame=annotated_frame)

        # Return combined labels for webcam logic
        return other_detections['class_name'].tolist() + person_detections['class_name'].tolist()