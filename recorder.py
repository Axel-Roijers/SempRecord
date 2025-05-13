import os
import tempfile
import threading as tr
from time import sleep

import dxcam
import ffmpeg

# from thumbnailer import ThumbnailProcessor
import numpy as np

import bouncer
import timelines
import settings
import util
from filename_generator import generate_filename

CODEC = "hevc_nvenc" if util.nvenc_available() else "libx265"
FFPATH = r".\ffmpeg.exe"
# MIN_FRAMES_PER_SWITCH = 15
DIFF_SUBSAMPLE = 4 
def frameDiff(A: np.ndarray, B: np.ndarray):
    """
    Calculate the difference between two frames by subsampling and comparing their elements.
    This function downsamples the input arrays `A` and `B` by a factor defined by the 
    global constant `DIFF_SUBSAMPLE`, then computes the total number of differing 
    elements between the two subsampled arrays.
    Args:
        A (np.ndarray): The first input frame as a 2D NumPy array.
        B (np.ndarray): The second input frame as a 2D NumPy array.
    Returns:
        int: The total count of differing elements between the subsampled frames.
    """
    
    A = A[::DIFF_SUBSAMPLE, ::DIFF_SUBSAMPLE]
    B = B[::DIFF_SUBSAMPLE, ::DIFF_SUBSAMPLE]
    # summ the whole frame into one value
    diff = np.sum(A != B)
    return diff


def mkv_encoder(width, height, path):
    return (
        ffmpeg.input(
            "pipe:",
            format="rawvideo",
            r=settings.FRAME_RATE,
            pix_fmt="rgb24",
            s=f"{width}x{height}",
        )
        .output(
            str(path),
            r=settings.FRAME_RATE,
            vcodec=CODEC,
            cq=settings.QUALITY,
            preset="p5",
            tune="hq",
            weighted_pred=1,
            pix_fmt="yuv420p",
            movflags="faststart",
            color_primaries="bt709",  # sRGB uses BT.709 primaries
            color_trc="iec61966-2-1",  # sRGB transfer characteristics
            colorspace="bt709",  # sRGB uses BT.709 colorspace
            color_range="pc",  # Set color range to full
        )
        .run_async(pipe_stdin=True, pipe_stderr=True)
    )


class Recorder:
    """Allows for continuous writing to a video file.
    Gets destroyed after the recording is done.
    It is replaced by a new recorder instance.
    """

    def __init__(self):
        """Starts the recording process"""
        self.file_name = generate_filename() + ".mkv"
        self.path = settings.HOME_DIR / "Records"  / self.file_name

        
        self.total_frames_recorded = 0
        self.paused = False
        self.cut = False
        # start ffmpeg
        w, h = util.get_desktop_resolution()
        self.ffprocess = mkv_encoder(w, h, self.path)

        # launch threads
        self.end_record_flag = tr.Event()
        self.record_thread = tr.Thread(
            target=self._record_thread, name="Recording Thread"
        )

        self.end_status_flag = tr.Event()
        self.status_thread = tr.Thread(
            target=self._status_thread, name="Status Thread", daemon=True
        )

        self.record_thread.start()
        self.status_thread.start()

    def _record_thread(self):
        capturecam = dxcam.create()
        capturecam.start(target_fps=settings.FRAME_RATE)

        previous_frame = capturecam.get_latest_frame()
        previous_switch_frame = 0
        previous_appname = ""

        while not self.end_record_flag.is_set():
            new_frame = capturecam.get_latest_frame()
            if self.paused:
                previous_frame = new_frame
                continue

            # PERFORM APP SWITCH CHECKS
            new_window_title = util.getForegroundWindowTitle()
            
            if not (new_appname:=bouncer.isWhiteListed(new_window_title)):
                continue

            if bouncer.isBlackListed(new_window_title):
                continue

            if frameDiff(new_frame, previous_frame) < settings.CHANGE_THRESHOLD:
                continue

            # AFTER THIS POINT, WE KNOW THAT THE FRAME IS VALID AND WE CAN PROCESS IT

            if (
                previous_appname != new_appname
                and previous_appname != ""
                and self.total_frames_recorded - previous_switch_frame >= 1
            ):
                # an app switch has occurred
                timelines.register_take(
                    appname=previous_appname,
                    start_frame=previous_switch_frame,
                    end_frame=self.total_frames_recorded,
                    clip_name=self.file_name,
                )
                previous_switch_frame = self.total_frames_recorded
                print(f"App switch detected: {new_appname}")


            previous_appname = new_appname
            # Flush the frame to FFmpeg
            try:
                self.ffprocess.stdin.write(previous_frame.tobytes())  # write to pipe
                previous_frame = new_frame
                self.total_frames_recorded += 1
            except os.error:
                break
        # the recording ends here
        # everything beyond this point is cleanup

        self.ffprocess.stdin.close()
        self.ffprocess.wait()
        capturecam.stop()
        print("Capture stopped 🎬")

    def _status_thread(self):
        self.status = ""
        buffer = b""

        while not self.end_status_flag.is_set():
            new_stat = self.ffprocess.stderr.read1()

            # split the status into lines
            # we'd like to use readline but using \r as the delimiter
            new_stat = new_stat.split(b"\r")
            buffer += new_stat[0]
            if len(new_stat) > 1:
                # if there is more than one line, the last line is the current status
                self.status = buffer.decode("utf-8").strip()
                buffer = new_stat[-1]

    def get_status(self):
        if self.cut:
            return {}

        raw_stat = self.status.split(sep="=")
        raw_stat = [x.strip() for x in raw_stat]
        listed = []
        for s in raw_stat:
            listed.extend(s.split())
        # pair up the values
        status = {}
        for i in range(0, len(listed) - 1, 2):
            status[listed[i]] = listed[i + 1]
        return status

    def end_recording(self):
        self.cut = True

        # stop the status thread
        self.end_status_flag.set()
        self.end_record_flag.set()


# ==========INTERFACE==========
ACTIVE_RECORDER: Recorder = None


def is_recording() -> bool:
    """Check if recording is currently active."""
    if ACTIVE_RECORDER is None:
        return False
    if ACTIVE_RECORDER.cut:
        return False
    return True


def start() -> str:
    """Start or resume recording."""
    global ACTIVE_RECORDER
    if not is_recording():
        # Make a new recorder
        ACTIVE_RECORDER = Recorder()
        print("Started recording")
        return ACTIVE_RECORDER.file_name

    if ACTIVE_RECORDER.paused:
        ACTIVE_RECORDER.paused = False
        print("Resumed recording")


def stop() -> str:
    """Stop the recording if it is active."""
    global ACTIVE_RECORDER
    if not is_recording():
        return
    ACTIVE_RECORDER.end_recording()
    filename = ACTIVE_RECORDER.file_name
    print("Stopped recording")
    ACTIVE_RECORDER = None
    return filename


def pause() -> None:
    """Pause the recording if it is active."""
    global ACTIVE_RECORDER
    if not is_recording():
        return
    ACTIVE_RECORDER.paused = True
    print("Paused recording")


if __name__ == "__main__":
    ACTIVE_RECORDER = Recorder()
    input("Press enter to stop recording")
    ACTIVE_RECORDER.end_recording()
