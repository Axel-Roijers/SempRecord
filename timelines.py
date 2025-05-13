from math import e

from flask.cli import F
from settings import HOME_DIR


# EXAMPLE EDL FILE:

# TITLE: Timeline 1
# FCM: NON-DROP FRAME

# 001 AX V C 00:00:30:13 00:00:45:18 01:00:00:00 01:00:15:05
# * FROM CLIP NAME: Brambience.mkv

# 002 AX V C 00:01:01:16 00:01:23:11 01:00:15:05 01:00:37:00
# * FROM CLIP NAME: Brambience.mkv


# TEMPLATE STRING:
header_template = """TITLE: {title}
FCM: NON-DROP FRAME
* SOURCE DIRECTORY: {source_directory}"""

entry_template = """
{entry_number} AX V C {start_source} {end_source} {start_timeline} {end_timeline}
* FROM CLIP NAME: {clip_name}"""

EDL_FPS: int = 30 # only 30 and 24 fps are supported in EDL files
EDL_WRITERS = {}

def register_take(appname: str, start_frame: int, end_frame: int, clip_name: str):
    """Register an app switch in the EDL file."""
    # Find the writer for the appname, or create a new one if it doesn't exist
    edl_writer = EDL_WRITERS.get(appname)
    if edl_writer is None:
        edl_writer = EdlDataWriter(appname)
        EDL_WRITERS[appname] = edl_writer
    # add the entry to the writer
    edl_writer.add_entry(start_frame, end_frame, clip_name)


def frame_to_timecode(frame: int,industry_offset=False) -> str:
    """Convert a frame number to a timecode string.
    Industry offset is a 1 hour offset in the film industry which has found its way into EDL files.
    This means that the timecode starts at 01:00:00:00 instead of 00:00:00:00.

    """
    hours = industry_offset + frame // (EDL_FPS * 3600)  # 1 hour offset is a tradition in the film industry
    minutes = (frame // (EDL_FPS * 60)) % 60
    seconds = (frame // EDL_FPS) % 60
    frames = frame % EDL_FPS
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"


def timecode_to_frame(timecode: str) -> int:
    """Convert a timecode string to a frame number."""
    hours, minutes, seconds, frames = map(int, timecode.split(":"))
    return (hours * 3600 + minutes * 60 + seconds) * EDL_FPS + frames


class EdlDataWriter:
    def __init__(self, appname: str, entry_limit_lapped = 1):
        self.appname = appname
        self.entry_limit_lapped = entry_limit_lapped # every 999 entries, a new file is created 
        self.entry_number = 1  # there is no entry 0 in EDL files
        self.timeline_frame = 0

        self.source_dir = HOME_DIR / "Records" 
        self.edl_path = HOME_DIR / "Timelines" / f"{self.appname} {self.entry_limit_lapped}.edl"
        self.edl_path.parent.mkdir(parents=True, exist_ok=True)

        valid = self._validate_and_extract_entry()
        if not valid:
            self.new_file = True
            # remove the file if it is invalid if it exists
            self.edl_path.unlink(missing_ok=True)           
            self.edl_path.touch()
            self._write_header()
            print(f"Created new EDL file: {self.edl_path}")

    def _write_header(self):
        """Write the header to the EDL file."""
        with open(self.edl_path, "w") as f:
            output = header_template.format(
                title=self.appname,
                source_directory=str(self.source_dir),
            )
            f.write(output)

    def _validate_and_extract_entry(self) -> int:
        """Read and validate the existing EDL file
         return true if valid.
         return false if invalid.
         sets the entry number and timeline frame to the last entry in the file.        
        """

        if  not self.edl_path.exists():    
            return False    
        try:
            with open(self.edl_path, "r") as f:
                lines = f.readlines()
                if len(lines) < 4:
                    print("EDL file is empty or malformed.")
                    

                last_timecode_line = lines[-2] # -2 because the last line is a reference to the clip name
                last_entry_line = lines[-3]
                # find the start timecode
                start_timecode = last_timecode_line.split()[3]

                # find the entry number
                entry_number = last_entry_line.split()[0]

                self.timeline_frame = timecode_to_frame(start_timecode)
                self.entry_number = int(entry_number) + 1
                return True
        except:
            return False

    def add_entry(self, start_frame: int, end_frame: int, clip_name: str):
        print(f"Adding entry: {start_frame} - {end_frame} {clip_name}")
        # Convert frames to timecodes
        start_source = frame_to_timecode(start_frame)
        end_source = frame_to_timecode(end_frame)
        start_timeline = frame_to_timecode(self.timeline_frame + start_frame,True)
        end_timeline = frame_to_timecode(self.timeline_frame + end_frame,True)
        self.timeline_frame += end_frame - start_frame
        # Create the entry string
        entry = entry_template.format(
            entry_number=self.entry_number,
            start_source=start_source,
            end_source=end_source,
            start_timeline=start_timeline,
            end_timeline=end_timeline,
            clip_name=clip_name,
        )
        # Write the entry to the file
        with open(self.edl_path, "a") as f:
            f.write(entry)
            # Increment the entry number
            self.entry_number += 1
            # check if the entry number is greater than the limit
            assert self.entry_number <= 999, "Entry number is greater than 999, we are cooked for now."



def flush_all_edl_writers():
    """Flush all EDL writers to their files."""
    for appname, writer in EDL_WRITERS.items():
        writer.flush()    
