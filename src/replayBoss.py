import sys, os, time, datetime, math, re
import argparse

from pathlib import Path
from enum import Enum
from collections import deque

import watchdog.events
import watchdog.observers
import logging.config


_VERSION_MAJ = 0
_VERSION_MIN = 1
_VERSION_BUILD = "1"


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
        self.ui_status = "YYYY-MM-DD@HHMM_SS [RENAMED]: [NAMEOFGAME~] NAME_OF_FILE"


class ReplayProcessor(watchdog.events.FileSystemEventHandler):
    def __init__(self, target_replay=None, process=Process.NOOP):
        #self.target_replay = target_replay
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

    """A handler for new replay files which triggered watchdog events"""
    def on_created(self, event):
        logging.debug(f"CREATED FILE: {event.src_path}")

    def on_modified(self, event):

        if self.is_civ(event.src_path):
            logging.debug(f"MODIFIED CIV: {event.src_path}")
            if self.last_event is ModEvent.REPLAY:  # Triggered
                logging.debug("<< Triggered")
                self.triggered = True

            self.trigger_buf.append(ModEvent.CIV)
            self.event_buf.append(ModEvent.CIV)
            self.last_event = ModEvent.CIV

        elif self.is_replay(event.src_path):
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
                logging.debug("GAMEOVER DETECTED, SAVING REPLAY")
                # self.runprocess(Process.CATEGORIZE_RENAME)


    def is_civ(self, path):
        name, ext = os.path.splitext(path)
        return ext in ['.xml']

    def is_replay(self, path):
        #name, ext = os.path.splitext(path)
        #return ext in ['.age3Yrec']
        return str(path).endswith("Record Game.age3Yrec")

    """ <SCRATCHPAD>
    replay = self.build_replay(process=Process.RENAME_ONLY, timeout_s=15, orig_path=replay_origpath)
    result = ReplayProcessor().run_process(replay, Process.RENAME_ONLY)
   </SCRATCHPAD> """

def main(path):
    observer = watchdog.observers.Observer()
    event_handler = ReplayProcessor()
    observer.schedule(event_handler, path=path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def footprint():
    # TODO: make ReplayBoss Archive subdir
    # TODO: write log under ReplayBoss Archive
    pass

def get_replay_path():
    # TODO: Dynamically locate game replay path
    pass


if __name__ == "__main__":
    # get_replay_path()
    footprint()
    logging.basicConfig(filename="ReplayBoss.log", level=logging.DEBUG, format='%(asctime)s,%(msecs)03d %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    #! Modify this static path until auto-detect
    dir = "C:\\Users\\root\\Games\\Age of Empires 3 DE\\76561197960427286\\Savegame"
    logging.debug(f"ReplayBoss is now monitoring {dir} for new replays to backup.")
    main(dir)
