from ultralytics import YOLO
import supervision as sv
import numpy as np
import cv2 as cv
from src.Colors import Colors
from src.HeadsUpDisplay import HeadsUpDisplay

class DrawBox:
    """
    Handles the YOLO inference pipeline. Filters detections for relevant
    COCO classes and renders bounding boxes with state-dependent colors.
    """
    def __init__(self, hud_obj: HeadsUpDisplay):
        """
        Handles object detection and visual rendering.
        """
        self.hud = hud_obj
        # Standardize internal dimensions to match your HUD
        self.width = self.hud.width
        self.height = self.hud.height
        
        # 0=Person, 39=Bottle, 41=Cup, 67=Cell Phone
        self.selected_classes = [0, 39, 41, 67] 
        self.model = YOLO('yolo26n.pt') 
        
        # Initialize your 3 Annotators
        self.box_annotator = sv.BoxAnnotator()
        self.person_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        
    def box_on_frame(self, frame, time_obj, state_obj):
        """
        Processes frame and renders UI based on the single active state.
        """
        # 1. Standardize Input Frame Size
        frame = cv.resize(frame, (self.width, self.height))

        # 2. Run Inference
        result = self.model(frame, classes=self.selected_classes, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(result)
        
        # Map class IDs to names for the webcam logic return
        labels = [result.names[class_id] for class_id in detections.class_id]

        # 3. Filter Detections for Annotation
        person_detections = detections[detections.class_id == 0]
        other_detections = detections[detections.class_id != 0]

        # --- HUD RELATED PART: UPDATE STATE LOGIC ---
        # Since state_obj.state is now a single object:
        current_status_text = state_obj.state.text
        border_color = state_obj.state.annotation_color
        text_color = state_obj.state.text_color
        is_flashing = state_obj.state.flashing_text

        # Apply the color to the person annotator specifically
        self.person_annotator.color = border_color

        # 4. Annotate the Frame (Layered)
        # First: Other objects
        annotated_frame = self.box_annotator.annotate(
            scene=frame,
            detections=other_detections
        )
        # Second: Person (State-colored)
        annotated_frame = self.person_annotator.annotate(
            scene=annotated_frame,
            detections=person_detections
        )
        # Third: Labels
        annotated_frame = self.label_annotator.annotate(
            scene=annotated_frame,
            detections=detections,
            labels=labels
        )

        # 5. Draw HUD Elements
        # Draw Stream Time (Top Left)
        self.hud.draw_text(
            image=annotated_frame, 
            text=f"Stream: {time_obj.get_time_string()}", 
            org=(15, 25), 
            fontScale=0.45,
            color=Colors.TEXT_BLACK,
            thickness=1
        )

        # Draw Current State (Bottom Center)
        (tw, th), _ = cv.getTextSize(current_status_text, self.hud.font, 0.5, 2)
        center_x = (self.width - tw) // 2
        
        self.hud.draw_text(
            image=annotated_frame, 
            text=current_status_text,
            org=(center_x, self.height - 25), 
            fontScale=0.5,
            color=text_color,
            thickness=2,
            flashing=is_flashing
        )

        # 6. Final Display
        self.hud.draw_imshow(frame=annotated_frame)

        # Return combined labels for the webcam logic
        return labels