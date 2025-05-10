import os
import threading as tr
from time import sleep

import dxcam
import ffmpeg

import bouncer
import util
from filename_generator import generate_filename
import settings
# from thumbnailer import ThumbnailProcessor
import numpy as np
# import edl_module
import tempfile
CODEC = "hevc_nvenc" if util.nvenc_available() else "libx265"
FFPATH = r".\ffmpeg.exe"

SUBSAMPLE = 4  # subsample


def frameDiff(A: np.ndarray, B: np.ndarray):
    
    A = A[::SUBSAMPLE, ::SUBSAMPLE]
    B = B[::SUBSAMPLE, ::SUBSAMPLE]
    # summ the whole frame into one value
    diff = np.sum(A != B)
    return diff


def mkv_encoder(width, height, path):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mkv")
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

        self.prev_window_title = util.getForegroundWindowTitle()
        self.nframes = 0
        # generate a file name that looks like this: Wednesday 18 January 2023 HH;MM.mkv
        self.file_name = generate_filename()

        # self.thumbnail_generator = ThumbnailProcessor(self.file_name)
        # self.metadata_writer = edl_module.EdlDataWriter()

        self.path = settings.HOME_DIR / f"{self.file_name}.mkv"
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
        old_frame = capturecam.get_latest_frame()

        while not self.end_record_flag.is_set():
            new_frame = capturecam.get_latest_frame()
            if self.paused:
                old_frame = new_frame
                continue

            new_window_title = util.getForegroundWindowTitle()

            if not bouncer.isWhiteListed(new_window_title):
                continue

            if bouncer.isBlackListed(new_window_title):
                continue

            if frameDiff(new_frame, old_frame) < settings.CHANGE_THRESHOLD:
                continue

            if new_window_title != self.prev_window_title:
                self.prev_window_title = new_window_title
                # self.metadata_writer.add_chapter(self.nframes, new_window_title)


            # Flush the frame to FFmpeg
            try:
                self.ffprocess.stdin.write(old_frame.tobytes())  # write to pipe
                old_frame = new_frame
                self.nframes += 1
            except os.error:
                break
        # the recording ends here
        # everything beyond this point is cleanup

        self.ffprocess.stdin.close()
        self.ffprocess.wait()
        capturecam.stop()
        print("Capture stopped 🎬")
        # self.metadata_writer.add_chapters_to_video(self.path)

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

        # process the thumbnail queue
        print("Processing thumbnail")
        self.thumbnail_generator.render_webp_thumbnail()


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
