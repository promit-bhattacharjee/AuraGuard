import cv2 as cv
import time

class HeadsUpDisplay:
    """
    OpenCV-based rendering engine. Manages the main application window
    and provides utility methods for drawing standardized text and frames.
    """
    def __init__(self, extension=""):
        """
        Initializes the HUD with a standardized resolution.
        """
        # Window identification
        self.window_name = f"AuraGuard {extension}".strip()
        
        # Standardized dimensions for consistency across all screens
        self.width = 480
        self.height = 360
        self.font = cv.FONT_HERSHEY_SIMPLEX
        
        # Initialize the window properties
        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, self.width, self.height)

    def draw_imshow(self, frame):
        """
        Resizes any incoming frame (Webcam or Warning image) to 480x360 
        before displaying it. This prevents the window from jumping in size.
        """
        if frame is not None:
            # Force standardization of the image dimensions
            standard_frame = cv.resize(frame, (self.width, self.height))
            cv.imshow(self.window_name, standard_frame)

    def draw_text(self, image, text, org=(50, 50), fontScale=0.6, color=(255, 255, 255), thickness=2, flashing=False):
        """
        Draws text on the provided image. Handles flashing logic internally.
        """
        if flashing:
            # Toggle visibility every 400ms based on system time
            if int(time.time() / 0.4) % 2 == 0:
                cv.putText(image, text, org, self.font, fontScale, color, thickness, cv.LINE_AA)
        else:
            cv.putText(image, text, org, self.font, fontScale, color, thickness, cv.LINE_AA)

    def is_window_open(self):
        """Checks if the window is currently visible to the user."""
        try:
            # Returns True if window is visible, False if closed via 'X'
            return cv.getWindowProperty(self.window_name, cv.WND_PROP_VISIBLE) >= 1
        except cv.error:
            return False

    def close(self):
        """Safely destroys the specific HUD window."""
        try:
            cv.destroyWindow(self.window_name)
        except cv.error:
            pass