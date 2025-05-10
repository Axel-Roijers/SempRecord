# flask api example
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import settings
import tray
import recorder
import csv

import logging
from logging.handlers import RotatingFileHandler



INDEX_PATH = r"frontend\public"

# this path contains index.html and all the other frontend files
app = Flask(__name__, static_folder = INDEX_PATH)
api = Api(app)

# allow Access-Control-Allow-Origin for all origins
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return response


# serve index.html at the root
@app.route("/")
def index():
    return app.send_static_file("index.html")

#serve build files too
@app.route("/<path:path>")
def static_proxy(path):
    return app.send_static_file(path)


@app.route("/api/status")
def status():
    if not recorder.is_recording():
        return jsonify({"status": "stopped"})
    else:
        return jsonify(recorder.ACTIVE_RECORDER.get_status())


@app.route("/api/controls/start", methods=["POST"])
def start():
    tray.start()
    return jsonify({"status": "started"})


@app.route("/api/controls/stop", methods=["POST"])
def stop():
    tray.stop()
    return jsonify({"status": "stopped"})


@app.route("/api/controls/pause", methods=["POST"])
def pause():
    tray.pause()
    return jsonify({"status": "paused"})


@app.route("/api/media/thumbnails")
def request_thumbnails():
    """get the list of thumbnails"""    
    # read the thumbnails from the directory
    path = settings.HOME_DIR / ".thumbnails"
    thumbnails = [str(p) for p in path.iterdir()]
    return jsonify(thumbnails)

# TODO settings route
#TODO delete recordings route

# TODO recordings route
@app.route("/api/recordings")
def request_recordings():
    """get the list of recordings"""
    recdir = settings.HOME_DIR / "Records"
    # read the recordings from the directory
    recordings = [str(p) for p in recdir.iterdir()]
    
    for record in recordings:
        # get the metadata tsv file for each recording-
        #remove the .mkv from the record
        record = record.replace(".mkv", "")
        metadata_path = recdir / ".metadata" / f"{record}.tsv"
        
        # read the metadata file
        with open(metadata_path, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            metadata = [row for row in reader]
        # add the metadata to the recording
        recording["metadata"] = metadata
        

app.run()
