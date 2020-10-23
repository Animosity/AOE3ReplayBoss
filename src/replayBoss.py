import os, time
import argparse
import shutil
import watchdog.events
import watchdog.observers
import logging.config

from datetime import datetime
from enum import Enum
from collections import deque

_VERSION_MAJ = 0
_VERSION_MIN = 1
_VERSION_BUILD = "MinimumViableProduct"

_SUBDIR = "ReplayBoss Archive\\"
_PATH_ARCHIVE = os.path.join(os.getcwd(), _SUBDIR)

class ModEvent(Enum):
    NULL = -1
    REPLAY = 0
    CIV = 1

class Process(Enum):
    NOOP = -1
    RENAME_ONLY = 0
    CATEGORIZE_ONLY = 1
    RENAME_CATEGORIZE = 2


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


class ReplayProcessor(watchdog.events.FileSystemEventHandler):
    def __init__(self, path, target_replay=None, process=Process.NOOP):
        #self.target_replay = target_replay
        self.path_replays = path
        self.process = process
        self.triggered = False
        self.last_event = ModEvent.NULL
        self.trigger_buf = deque([ModEvent.NULL]*2, 2)  # FIFO-2
        self.event_buf = deque([ModEvent.NULL]*7, 7)    # FIFO-7
        self.new_replay= ""


    @staticmethod
    def run_process(replay, process):
        logging.debug(f"ReplayProcessor(process={process}) entry")

        if process is Process.RENAME_ONLY:
            try:
                pass
            except Exception as e:
                #winsound.PlaySound(os.path.join(os.getcwd(), _AUDIO_CUE_BANK["error"]), winsound.SND_FILENAME)
                logging.debug(f"RENAME FAILED : {e}")
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

    """A handler for new replay files which triggered watchdog events"""
    def on_created(self, event):
        logging.debug(f"CREATED FILE: {event.src_path}")

    def on_modified(self, event):
        def is_civ(path):
            name, ext = os.path.splitext(path)
            return ext in ['.xml']

        def is_replay(path):
            # name, ext = os.path.splitext(path)
            # return ext in ['.age3Yrec']
            return str(path).endswith("Record Game.age3Yrec")

        if is_civ(event.src_path):
            logging.debug(f"MODIFIED CIV: {event.src_path}")
            if self.last_event is ModEvent.REPLAY:  # Triggered
                logging.debug("<< Triggered")
                self.triggered = True

            self.trigger_buf.append(ModEvent.CIV)
            self.event_buf.append(ModEvent.CIV)
            self.last_event = ModEvent.CIV

        elif is_replay(event.src_path):
            logging.debug(f"MODIFIED REPLAY: {event.src_path}")
            self.last_event = ModEvent.REPLAY
            self.trigger_buf.append(ModEvent.REPLAY)
            self.event_buf.append(ModEvent.REPLAY)
            self.new_replay = event.src_path

        else: pass

        if self.triggered:
            pattern = [ModEvent.REPLAY, ModEvent.CIV, ModEvent.CIV, ModEvent.CIV, ModEvent.CIV, ModEvent.CIV, ModEvent.CIV]
            buf_list = list(self.event_buf)[:7]
            if buf_list == pattern:
                logging.info("GAMEOVER DETECTED, ARCHIVING UNSAVED REPLAY")
                self.triggered = False
                self.archive_replay()
                # self.runprocess(Process.CATEGORIZE_RENAME)

    def archive_replay(self):
        try:
            timestamp = datetime.now()
            timestamp = timestamp.replace(microsecond=0)
            timestamp = timestamp.strftime("%Y-%m-%d %H-%M-%S")

            replay_filename = "Record Game.age3Yrec"
            archived_replay = f"Record Game {str(timestamp)}.age3Yrec"
            new_replay_file = os.path.join(_PATH_ARCHIVE, replay_filename)
            archived_replay_file = os.path.join(_PATH_ARCHIVE, archived_replay)
            shutil.copy(self.new_replay, _PATH_ARCHIVE)
            os.rename(new_replay_file, archived_replay_file)
            print(f"REPLAY ARCHIVED @ : {archived_replay_file}")
            logging.info(f"REPLAY ARCHIVED @ : {archived_replay_file}")
            # winsound.PlaySound(os.path.join(os.getcwd(), _AUDIO_CUE_BANK["success"]), winsound.SND_FILENAME)

            """ <SCRATCHPAD>
                replay = self.build_replay(process=Process.RENAME_ONLY, timeout_s=15, orig_path=replay_origpath)
                result = ReplayProcessor().run_process(replay, Process.RENAME_ONLY)
               </SCRATCHPAD> """

        except FileNotFoundError as e:
            logging.info(f"REPLAY was already properly saved by AOE3DE.")


def main(path):
    observer = watchdog.observers.Observer()
    event_handler = ReplayProcessor(path=path)
    observer.schedule(event_handler, path=path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def footprint():
    if not os.path.isdir(_PATH_ARCHIVE):
        os.mkdir(_PATH_ARCHIVE)

    path_logfile = os.path.join(_PATH_ARCHIVE, "ReplayBoss.log")
    logging.basicConfig(filename=path_logfile, level=logging.DEBUG, format='%(asctime)s,%(msecs)03d %(message)s',
    datefmt = '%d/%m/%Y %H:%M:%S')


def get_replay_path():
    # TODO: Dynamically locate game replay path
    path_replays = os.getcwd()
    return path_replays


if __name__ == "__main__":
    dir = get_replay_path()
    footprint()

    #! Modify this static path until auto-detect. Overwrites get_replay_path() result
    #path_replays = "C:\\Users\\root\\Games\\Age of Empires 3 DE\\76561197960427286\\Savegame"
    print(f"Started ReplayBoss v{_VERSION_MAJ}.{_VERSION_MIN}-{_VERSION_BUILD}")
    logging.info(f"ReplayBoss is now monitoring {dir} for new replays to backup.")
    print(f"ReplayBoss is now monitoring {dir} for new replays to backup.")
    logging.info(f"ReplayBoss is now monitoring {dir} for new replays to backup.")
    main(dir)
