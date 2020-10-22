import sys, os, time, datetime, math, re
import argparse

from pathlib import Path
from enum import Enum

import watchdog.events
import watchdog.observers
import logging.config

_VERSION_MAJ = 0
_VERSION_MIN = 1
_VERSION_BUILD = "1"


class Process(Enum):
    NOOP = 0
    RENAME_ONLY = 1
    CATEGORIZE_ONLY = 2
    RENAME_CATEGORIZE = 3

class Replay():
    def __init__(self, process=Process.NOOP, orig_path=None, parentdir_name=None, data={"category": 0, "parentdir_name": "", "newfilename": ""}):
        self.process = process
        self.orig_path = orig_path
        self.new_path = None
        self.new_filename = None
        self.category = 0
        self.parentdir_name = parentdir_name
        self.data = data
        self.status = "Null Status"
        self.ui_status = "YYYY-MM-DD@HHMM_SS [RENAMED]: [NAMEOFGAME~] NAME_OF_FILE"


class ReplayProcessor():
    def __init__(self, target_replay=None, process=Process.NOOP):
        self.target_replay = target_replay
        self.process = Process.NOOP


    @staticmethod
    def run_process(replay, process):
        logging.debug(f"ReplayProcessor(process={process}) entry")

        if process is Process.RENAME_ONLY:
            logging.debug(f"  Starting replay backup process")
            try:
                #winsound.PlaySound(os.path.join(os.getcwd(),_AUDIO_CUE_BANK["new"]), winsound.SND_FILENAME)
                suffix = ".AGE3YSAV"
                # GENERATE FILENAME
                replay_filename = "test1"
                replay_filename += suffix

                new_path = os.path.join(os.path.split(replay.orig_path)[0], f"{replay_filename}{os.path.splitext(replay.orig_path)[1]}")

                logging.debug(f"ReplayProcessor.run_process(Process.RENAME_ONLY) - new_path : {new_path}")
                os.rename(replay.orig_path, new_path)
                replay.new_filename = os.path.basename(new_path)
                logging.debug(f"ReplayProcessor.run_process(Process.RENAME_ONLY) - SUCCESS")
                replay.status = "RENAME Successful"

                logging.debug(f"  successful replay result is {replay}")
                return (True,
                        {
                         "exception": None
                         },
                        replay)

            except Exception as e:
                #winsound.PlaySound(os.path.join(os.getcwd(), _AUDIO_CUE_BANK["error"]), winsound.SND_FILENAME)
                logging.debug(f"  RENAME FAILED : {e}")
                return (False,
                        {
                         "exception": e
                         },
                        replay)

        elif replay.process is Process.CATEGORIZE_ONLY:
            pass
        elif replay.process is Process.RENAME_CATEGORIZE:
            pass
        elif process is Process.CATEGORIZE_ONLY:
            pass
        else:
            pass


class ReplayFinder(watchdog.events.FileSystemEventHandler):

    def __init__(self,  *args, **kwargs):
        self.app = None
    """A handler for new replay files which triggered watchdog events"""
    def on_created(self, event):
        #logging.debug("ReplayFinder() entry")
        if self.is_replay(event.src_path):
            logging.debug(f"*CREATED REPLAY*: {event.src_path}")
        else:
            logging.debug(f"CREATED FILE: {event.src_path}")

        return

    def on_modified(self, event):
        if self.is_replay(event.src_path):
            logging.debug(f"MODIFIED REPLAY: {event.src_path}")
        else:
            logging.debug(f"MODIFIED FILE: {event.src_path}")

    def is_replay(self, path):
        name, ext = os.path.splitext(path)
        return ext in ['.age3Yrec']


def watchdog_event_handler(self, event):
    logging.debug("app.watchdog_event_handler() entry")

    watchdog_event = event.payload
    replay_origpath = watchdog_event.src_path

    if (os.path.exists(replay_origpath)):
        replay_origpath = watchdog_event.src_path
        replay_parentdir_name = Path(replay_origpath).parent.name
        logging.debug("  new replay found @ " + replay_origpath)

        replay = self.build_replay(process=Process.RENAME_ONLY, timeout_s=15, orig_path=replay_origpath)

        result = ReplayProcessor().run_process(replay, Process.RENAME_ONLY)
        logging.debug(f"app.form.watchdog_event_handler() - ReplayProcessor result is {result}")

def main(path):
    observer = watchdog.observers.Observer()
    event_handler = ReplayFinder()
    observer.schedule(event_handler, path=path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # dir = getReplayPath()

    logging.basicConfig(filename="replayBoss.log", level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    # = os.path.join(os.getcwd())
    #! Modify this static path until auto-detect
    dir = "C:\\Users\\root\\Games\\Age of Empires 3 DE\\76561197960427286\\Savegame"

    logging.debug(f"ReplayBoss is now monitoring {dir} for new replays to backup.")
    main(dir)
