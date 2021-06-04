import librosa
import  pyaudio
from librosa import display
import click
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
import time

class AudioHandler:
    def __init__(self):
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 22050
        self.CHUNK = 1024 * 8
        self.p = None
        self.stream = None
        self.devices = {}
        self.device_index = -1
        self._get_input_device()
        self.wave = np.array([])
        self.tempo = None
        self.times = []
        self.beats = []


    def _get_input_device(self, name="pulse"):
        pa = pyaudio.PyAudio()
        chosen_device_index = -1
        for x in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(x)
            self.devices[info['name']] = info
            print(pa.get_device_info_by_index(x))
            if info["name"] == name:
                self.device_index = info["index"]
                print(f"pulse device index: {self.device_index}")



    def start(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  input_device_index=self.device_index,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.CHUNK)

    def stop(self):
        self.stream.close()
        self.p.terminate()

    def callback(self, in_data, frame_count, time_info, flag):
        wave = np.frombuffer(in_data, dtype=np.float32)
        if len(wave) < self.CHUNK:
            print("Skip chunk of size: ", len(wave))
            return
        self.wave = wave
        onset_env = librosa.onset.onset_strength(y=wave, sr=self.RATE)
        pulse = librosa.beat.plp(onset_envelope=onset_env, sr=self.RATE)
        # prior = st.lognorm(loc=np.log(120), scale=120, s=1)
        # pulse_lognorm = librosa.beat.plp(onset_envelope=onset_env, sr=sr,prior=prior)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env)
        self.tempo = tempo
        self.beats = beats
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
        times = librosa.times_like(onset_env, sr=self.RATE)
        self.times = times
        print(tempo, beats, times[beats])
        return None, pyaudio.paContinue

    def mainloop(self):
        while (self.stream.is_active()): # if using button you can set self.stream to 0 (self.stream = 0), otherwise you can use a stop condition
            time.sleep(2.0)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    y, sr = librosa.load('../../Groove_Tantan Edit 1_Tantan_Take_5.ogg')
    print (sr)
    fig, ax = plt.subplots(nrows=5, sharex=True)
    display.waveshow(y, sr=sr, ax=ax[0])
    ax[0].set(title='Envelope view')
    ax[0].label_outer()
    y_harm, y_perc = librosa.effects.hpss(y)
    display.waveshow(y_harm, sr=sr, alpha=0.5, ax=ax[1], label='Harmonic')
    display.waveshow(y_perc, sr=sr, color='r', alpha=0.5, ax=ax[1], label='Percussive')
    ax[1].set(title='Multiple waveforms')
    ax[1].legend()
    # Beat detection
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
    prior = st.lognorm(loc=np.log(120), scale=120, s=1)
    pulse_lognorm = librosa.beat.plp(onset_envelope=onset_env, sr=sr,
                                     prior=prior)
    melspec = librosa.feature.melspectrogram(y=y, sr=sr)
    ax[2].plot(librosa.times_like(onset_env),
               librosa.util.normalize(onset_env),
               label='Onset strength')
    ax[2].plot(librosa.times_like(pulse_lognorm),
               librosa.util.normalize(pulse_lognorm),
               label='Predominant local pulse (PLP)')
    ax[2].set(title='Log-normal tempo prior, mean=120', xlim=[5, 20])
    ax[2].legend()
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env)
    beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
    times = librosa.times_like(onset_env, sr=sr)
    ax[3].plot(times, librosa.util.normalize(onset_env),
               label='Onset strength')
    ax[3].vlines(times[beats], 0, 1, alpha=0.5, color='r',
                 linestyle='--', label='Beats')
    ax[3].legend()
    ax[3].set(title='librosa.beat.beat_track')
    ax[3].label_outer()
    times_p = librosa.times_like(pulse, sr=sr)
    ax[4].plot(times_p, librosa.util.normalize(pulse),
               label='PLP')
    ax[4].vlines(times_p[beats_plp], 0, 1, alpha=0.5, color='r',
                 linestyle='--', label='PLP Beats')
    ax[4].legend()
    ax[4].set(title='librosa.beat.plp', xlim=[5, 20])
    ax[4].xaxis.set_major_formatter(librosa.display.TimeFormatter())
    plt.savefig('analysis.png', dpi=400)
    plt.show()
