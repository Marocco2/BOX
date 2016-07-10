#
#
#    BBBBBBBBBBBBBBBBB        OOOOOOOOO     XXXXXXX       XXXXXXX
#    B::::::::::::::::B     OO:::::::::OO   X:::::X       X:::::X
#    B::::::BBBBBB:::::B  OO:::::::::::::OO X:::::X       X:::::X
#    BB:::::B     B:::::BO:::::::OOO:::::::OX::::::X     X::::::X
#      B::::B     B:::::BO::::::O   O::::::OXXX:::::X   X:::::XXX
#      B::::B     B:::::BO:::::O     O:::::O   X:::::X X:::::X
#      B::::BBBBBB:::::B O:::::O     O:::::O    X:::::X:::::X
#      B:::::::::::::BB  O:::::O     O:::::O     X:::::::::X
#      B::::BBBBBB:::::B O:::::O     O:::::O     X:::::::::X
#      B::::B     B:::::BO:::::O     O:::::O    X:::::X:::::X
#      B::::B     B:::::BO:::::O     O:::::O   X:::::X X:::::X
#      B::::B     B:::::BO::::::O   O::::::OXXX:::::X   X:::::XXX
#    BB:::::BBBBBB::::::BO:::::::OOO:::::::OX::::::X     X::::::X
#    B:::::::::::::::::B  OO:::::::::::::OO X:::::X       X:::::X
#    B::::::::::::::::B     OO:::::::::OO   X:::::X       X:::::X
#    BBBBBBBBBBBBBBBBB        OOOOOOOOO     XXXXXXX       XXXXXXX
#
#
# Assetto Corsa framework created by Marco 'Marocco2' Mollace
#
# version 0.1.2
#
# Usage of this library is under LGPLv3. Be careful :)
#
#

import ac
import traceback
import os


try:
    import ctypes.wintypes
except:
    ac.log('BOX: error loading ctypes.wintypes: ' + traceback.format_exc())
    raise

from ctypes.wintypes import MAX_PATH

# TODO: read from config file for filters | IMPORTS
from os.path import dirname, realpath
# import configparser

import functools
import threading
import zipfile
import time


def async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        return t

    return wrapper


try:
    from box_lib import pyfmodex
except Exception as e:
    ac.log('BOX: error loading pyfmodex: ' + traceback.format_exc())
    raise

try:
    import requests
except Exception as e:
    ac.log('BOX: error loading requests: ' + traceback.format_exc())
    raise


# A useful push notification via Telegram if I need send some news
def NotifyFrom(self, telegram_bot_oauth):
    try:
        telegram_api_url = "http://api.telegram.org/bot" + telegram_bot_oauth + "/getUpdates"
        r = requests.get(telegram_api_url)
        message = r.json()
        var_notify = message["result"][-1]["message"]["text"]
        ac.log('BOX: Notification from Telegram: ' + var_notify)
        return var_notify
    except:
        ac.log('BOX: No Internet connection')
        var_notify = ""
        return var_notify


# It downloads a zip file and extract it in a folder
def get_zipfile(download_link, dir_path=''):
    try:
        local_filename = download_link.split('/')[-1]
        # NOTE the stream=True parameter
        r = requests.get(download_link, stream=True)
        log_getZipFile = "Download of " + local_filename + "completed"
        ac.log("BOX: " + log_getZipFile)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush() commented by recommendation from J.F.Sebastian
        try:
            with zipfile.ZipFile(local_filename, "r") as z:
                z.extractall(os.path.join(os.path.dirname(__file__), dir_path))  # Extracting files
            os.remove(local_filename)
            log_getZipFile = "Files extracted"
            return log_getZipFile
        except:
            log_getZipFile = "Error extracting files"
            return log_getZipFile
    except:
        log_getZipFile = "Error downloading zip file"
        ac.log('BOX: error downloading zip file: ' + traceback.format_exc())
        return log_getZipFile


# A new function to automatize app updates for AC
# WORK IN PROGRESS
# TODO: make reorder files logic
def newupdate(version, check_link, download_link):
    try:
        r = requests.get(check_link)
        if r.json() != version:  # Check if server version and client version is the same
            update_status = get_zipfile(download_link)
            return update_status
        else:
            update_status = "No new update"
            ac.log('BOX: ' + update_status)
            return update_status
    except:
        update_status = "Error checking new update"
        ac.log('BOX: error checking new update: ' + traceback.format_exc())
        return update_status


# Uses GitHub to check updates
# WORK IN PROGRESS
# TODO: make reorder files logic
def github_newupdate(sha, git_repo, branch='master'):
    try:
        check_link = "https://api.github.com/repos/" + git_repo + "/commits/" + branch
        headers = {'Accept': 'application/vnd.github.VERSION.sha'}
        r = requests.get(check_link, headers=headers)
        if r.text != sha:  # Check if server version and client version is the same
            download_link = "https://github.com/" + git_repo + "/archive/" + branch + ".zip"
            update_status = get_zipfile(download_link)
            return update_status
        else:
            update_status = "No new update"
            ac.log('BOX: ' + update_status)
            return update_status
    except:
        update_status = "Error checking new update"
        ac.log('BOX: error checking new update: ' + traceback.format_exc())
        return update_status


from threading import Thread, Event


# WORK IN PROGRESS
class SoundPlayer(object):
    def __init__(self, filename, player):
        self.filename = filename
        self._play_event = Event()
        self.player = player
        self.playbackpos = [0.0, 0.0, 0.0]
        self.playbackvol = 1.0
        self.EQ = []
        self.initEq()
        self.sound_mode = pyfmodex.constants.FMOD_2D
        self.speaker_mix = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        for i in self.EQ:
            self.player.add_dsp(i)
        self.channel = self.player.get_channel(0)
        self.queue = []
        self.thread = Thread(target=self._worker)
        self.thread.daemon = True
        self.thread.start()

    def initEq(self):
        freq = [16.0, 31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
        for i in freq:
            dsp = self.player.create_dsp_by_type(pyfmodex.constants.FMOD_DSP_TYPE_PARAMEQ)
            dsp.set_param(pyfmodex.constants.FMOD_DSP_PARAMEQ_GAIN, 1.0)
            dsp.set_param(pyfmodex.constants.FMOD_DSP_PARAMEQ_BANDWIDTH, 1.0)
            dsp.set_param(pyfmodex.constants.FMOD_DSP_PARAMEQ_CENTER, i)
            self.EQ.append(dsp)

    def set_volume(self, volume):
        self.playbackvol = volume

    def set_sound_mode(self, sound_mode):
        self.sound_mode = sound_mode

    def set_position(self, position):
        self.playbackpos = position

    def set_gain(self, gain):
        if self.sound_mode == pyfmodex.constants.FMOD_3D:
            for i in self.EQ:
                i.set_param(pyfmodex.constants.FMOD_DSP_PARAMEQ_GAIN, gain)
        elif self.sound_mode == pyfmodex.constants.FMOD_2D:
            volume = gain
            self.speaker_mix = [volume, volume, volume, 1.0, volume, volume, volume, volume]

    def stop(self):
        while self.queue:
            self.queue.pop()

    def queueSong(self, filename=None):
        if filename is not None:
            if os.path.isfile(filename):
                sound = self.player.create_sound(bytes(filename, encoding='utf-8'), self.sound_mode)
                self.queue.append({'sound': sound, 'mode': self.sound_mode})
                state = self._play_event.is_set()
                if state == False:
                    self._play_event.set()
            else:
                ac.log('[Spotter]File not found : %s' % filename)

    def _worker(self):
        while True:
            self._play_event.wait()
            queue_len = len(self.queue)
            while queue_len > 0:
                self.player.play_sound(self.queue[0]['sound'], False, 0)
                if self.sound_mode == pyfmodex.constants.FMOD_3D and self.queue[0][
                    'mode'] == pyfmodex.constants.FMOD_3D:
                    self.channel.position = self.playbackpos
                elif self.sound_mode == pyfmodex.constants.FMOD_2D and self.queue[0][
                    'mode'] == pyfmodex.constants.FMOD_2D:
                    self.channel.spectrum_mix = self.speaker_mix
                self.channel.volume = self.playbackvol
                self.player.update()
                while self.channel.is_playing == 1:
                    time.sleep(0.1)
                self.queue[0]['sound'].release()
                self.queue.pop(0)
                queue_len = len(self.queue)
            self._play_event.clear()
