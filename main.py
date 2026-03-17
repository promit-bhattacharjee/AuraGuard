import cv2 as cv
from src.Webcam import webcam
from src.WarningScreen import WarningScreen
from src.States import StateController
from src.Time import TimeController
from src.DrawBox import DrawBox
from src.HeadsUpDisplay import HeadsUpDisplay
def main():
    # cam=webcam()
    hud=HeadsUpDisplay()

    warning_obj=WarningScreen(hud_obj=hud)
    user_choice=warning_obj.start()
    if user_choice == 1:    
        time_obj=TimeController()
        state_obj=StateController()
        draw_box_obj=DrawBox(hud_obj=hud)
        cam=webcam(time_controller=time_obj,state_controller=state_obj,draw_box_obj=draw_box_obj)
        cam.videocapture()
    else:
        print("Exiting program. User declined recording.")

    
if __name__=="__main__":    main()