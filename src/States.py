import time
from src.Colors import Colors
from src.HeadsUpDisplay import HeadsUpDisplay
class StateProperty:
    """
    Data class representing a specific system state (e.g., Deep Work).
    Holds UI metadata like colors, text, and flashing triggers.
    """
    def __init__(self, category, threshold, text_color, text, annotation_color=Colors.ANNOTATION_WHITE, flashing_text=False):
        self.category = category
        self.threshold = threshold      # Time in seconds to trigger this state
        self.text_color = text_color
        self.text = text
        self.annotation_color = annotation_color
        self.flashing_text = flashing_text
        self.last_detected_time = time.perf_counter()
        self.status = False

class States:
    def __init__(self):  # Fixed: Must be __init__ (with two 'i's), not __int__
        self.EMPTY_DESK = StateProperty(
            category='empty_desk', 
            threshold=5, 
            text_color=Colors.TEXT_YELLOW, 
            text='System Paused: User Away'
        )
        
        self.DEEP_WORK = StateProperty(
            category='deep_work', 
            threshold=10, 
            annotation_color=Colors.ANNOTATION_GREEN, 
            text_color=Colors.TEXT_WHITE, 
            text='Status: Focusing'
        )
        
        self.DISTRACTED = StateProperty(
            category='distracted', 
            threshold=2, 
            annotation_color=Colors.ANNOTATION_RED, 
            text_color=Colors.TEXT_WHITE, 
            text='WARNING: PUT PHONE AWAY', 
            flashing_text=True
        )

        self.NORMAL = StateProperty(
            category='normal', 
            threshold=0, 
            annotation_color=Colors.ANNOTATION_WHITE, 
            text_color=Colors.TEXT_WHITE, 
            text='Status: Active'
        )
        self.DEHYDRATED = StateProperty(
            category='dehydrated', 
            threshold=30, 
            annotation_color=Colors.ANNOTATION_BLUE, 
            text_color=Colors.TEXT_BLUE, 
            text='HEALTH ALERT: Drink Water'
        )

        # Initialize the current state to Normal
        self.state = self.NORMAL
class StateController:
    def __init__(self):
        config=States()
        self.emptydesk_STATE=config.EMPTY_DESK
        self.deepwork_STATE=config.DEEP_WORK
        self.distracted_STATE=config.DISTRACTED
        self.dehydrated_STATE=config.DEHYDRATED
        self.normal_STATE=config.NORMAL
        self.state=config.NORMAL