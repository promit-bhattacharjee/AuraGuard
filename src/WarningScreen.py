import cv2 as cv
import numpy as np
from src.HeadsUpDisplay import HeadsUpDisplay

class WarningScreen:
    def __init__(self, hud_obj: HeadsUpDisplay):
        self.hud = hud_obj
        self.w, self.h = self.hud.width, self.hud.height 
        self.user_choice = None
        
        # Coordinates: [x1, y1, x2, y2]
        self.btn_accept = [int(self.w * 0.1), int(self.h * 0.65), int(self.w * 0.45), int(self.h * 0.85)]
        self.btn_decline = [int(self.w * 0.55), int(self.h * 0.65), int(self.w * 0.9), int(self.h * 0.85)]

    def draw_ui(self, img):
        # 1. Header Text
        header_text = 'WARNING'
        (tw, th), baseline = cv.getTextSize(header_text, self.hud.font, 1.2, 3)
        header_x = (self.w - tw) // 2
        header_y = int(self.h * 0.35)
        self.hud.draw_text(img, header_text, (header_x, header_y), 1.2, (0, 0, 255), 3)

        # 2. Sub-text
        sub_text = 'Grant Camera Access?'
        (sw, sh), _ = cv.getTextSize(sub_text, self.hud.font, 0.5, 1)
        sub_x = (self.w - sw) // 2
        sub_y = int(self.h * 0.50)
        self.hud.draw_text(img, sub_text, (sub_x, sub_y), 0.5, (0, 0, 0), 1)

        # 3. YES Button (Green)
        cv.rectangle(img, (self.btn_accept[0], self.btn_accept[1]), 
                     (self.btn_accept[2], self.btn_accept[3]), (0, 150, 0), -1)
        self._draw_centered_btn_text(img, "YES", self.btn_accept)

        # 4. NO Button (Red)
        cv.rectangle(img, (self.btn_decline[0], self.btn_decline[1]), 
                     (self.btn_decline[2], self.btn_decline[3]), (0, 0, 150), -1)
        self._draw_centered_btn_text(img, "NO", self.btn_decline)

        return img

    def _draw_centered_btn_text(self, img, text, btn_coords):
        x1, y1, x2, y2 = btn_coords
        bw, bh = x2 - x1, y2 - y1
        (tw, th), baseline = cv.getTextSize(text, self.hud.font, 0.7, 2)
        
        # Adding baseline to th ensures vertical centering accounts for letter descenders
        tx = x1 + (bw - tw) // 2
        ty = y1 + (bh + th) // 2 
        self.hud.draw_text(img, text, (tx, ty), 0.7, (255, 255, 255), 2)

    def on_mouse_click(self, event, x, y, flags, param):
        """The callback needs to handle events specifically."""
        if event == cv.EVENT_LBUTTONDOWN:
            # Check Accept
            if self.btn_accept[0] <= x <= self.btn_accept[2] and self.btn_accept[1] <= y <= self.btn_accept[3]:
                self.user_choice = 1
            # Check Decline
            elif self.btn_decline[0] <= x <= self.btn_decline[2] and self.btn_decline[1] <= y <= self.btn_decline[3]:
                self.user_choice = 0

    def start(self):
        # Crucial: Ensure the window exists before setting the callback
        cv.namedWindow(self.hud.window_name)
        cv.setMouseCallback(self.hud.window_name, self.on_mouse_click)

        # Load asset or create fallback
        base_img = cv.imread('./assets/warning.png')
        if base_img is None:
            base_img = np.full((self.h, self.w, 3), 240, dtype=np.uint8) # Light grey fallback
        else:
            base_img = cv.resize(base_img, (self.w, self.h))

        while self.user_choice is None:
            display_img = base_img.copy()
            display_img = self.draw_ui(display_img)
            
            self.hud.draw_imshow(display_img)
            
            # Use a slightly longer waitKey to reduce CPU usage in the loop
            if cv.waitKey(10) & 0xFF == ord('q'):
                break
        
        return self.user_choice