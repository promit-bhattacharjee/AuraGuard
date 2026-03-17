import supervision as sv


class Colors:
    # Static Variables (Class Attributes)
    # Supervision expects RGB format: sv.Color(R, G, B)
    ANNOTATION_GREEN = sv.Color(0, 150, 0)
    ANNOTATION_RED = sv.Color(150, 0, 0)
    ANNOTATION_BLUE = sv.Color(0, 0, 255)
    ANNOTATION_WHITE = sv.Color(255, 255, 255)
    ANNOTATION_YELLOW = sv.Color(255, 255, 0)


# Format: (Blue, Green, Red)
    TEXT_GREEN = (0, 255, 0)  # Pure Green
    TEXT_RED = (0, 0, 255)  # Pure Red (Your 150,0,0 was dark and in the wrong slot)
    TEXT_BLUE = (255, 0, 0)  # Pure Blue
    TEXT_WHITE = (255, 255, 255)
    TEXT_YELLOW = (0, 255, 255)  # Green + Red = Yellow in BGR
    TEXT_BLACK=(0,0,0)
