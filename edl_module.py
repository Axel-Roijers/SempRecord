import settings
import subprocess
import tempfile

# TITLE: Timeline 1
# FCM: NON-DROP FRAME

# 001  AX       V     C        00:00:30:13 00:00:45:18 01:00:00:00 01:00:15:05  
# * FROM CLIP NAME: Video1.mkv

# 002  AX       V     C        00:01:01:16 00:01:23:11 01:00:15:05 01:00:37:00  
# * FROM CLIP NAME: Video2.mkv

def convert_frame_to_timecode(frame: int) -> str:
    """Convert a frame number to a timecode string."""

    hours = 1 + frame // (settings.FRAME_RATE * 3600)
    minutes = (frame // (settings.FRAME_RATE * 60)) % 60
    seconds = (frame // settings.FRAME_RATE) % 60
    frames = frame % settings.FRAME_RATE
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"



class EdlDataWriter:
    def __init__(self):
        self.cutlist = []
        self.last_time = 0
    
    
def add_cut(self, frame: int, title: str):

       
    def __str__(self):
         return "".join(self.meta_data)
    

    def add_chapters_to_video(self,input_file):
        # Create a temporary file for the metadata
        pass
