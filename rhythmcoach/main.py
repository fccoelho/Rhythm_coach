import numpy as np
import pygame
import pygame_widgets as pw
from pygame.locals import (DOUBLEBUF,
                           FULLSCREEN,
                           KEYDOWN,
                           KEYUP,
                           K_LEFT,
                           K_RIGHT,
                           QUIT,
                           K_ESCAPE, K_UP, K_DOWN, K_RCTRL, K_LCTRL
                           )
from librosa import display
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
from rhythmcoach.audio.audioproc import AudioHandler


class Application:
    def __init__(self):
        pygame.init()
        window = pygame.display.set_mode(size=(1600, 800), flags=DOUBLEBUF)
        self.screen = pygame.display.get_surface()
        self.graph_size = (800, 800)
        self.AH = AudioHandler()
        self.recording = False
        self.record_button = pw.Button(
            self.screen, 100, 100, 300, 150, text='Record',
            fontSize=50, margin=20,
            inactiveColour=(255, 0, 0),
            pressedColour=(0, 255, 0), radius=20,
            onClick=self.on_click
        )
        self.run = True

    def on_click(self):
        if not self.recording:
            self.record_button.set('text','Stop')
            self.recording = True
            self.AH.start()
        else:
            self.record_button.set('text','Record')
            self.AH.stop()
            self.recording = False

    def cycle_plot(self, hits):
        N = 32
        bottom = 8
        max_height = 4
        fig = plt.Figure()
        ax = fig.add_subplot(1, 1, 1, projection='polar')
        beats = np.linspace(0, 16, 32, endpoint=False)
        radii = max_height * np.random.rand(N)
        width = 16 / N
        bars = ax.bar(beats, radii, width=width, bottom=bottom)

        self._draw_plot(fig, pos=(0,400))

    def _draw_plot(self, fig, pos):
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.graph_size = canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, self.graph_size, "RGB")
        self.screen.blit(surf, pos)

    def wave_plot(self):
        fig = plt.Figure()
        ax = fig.add_subplot(1, 1, 1)
        display.waveshow(self.AH.wave, sr=self.AH.RATE, ax=ax)
        if self.AH.beats:
            ax.vlines(self.AH.times[self.AH.beats], min(self.AH.wave), min(self.AH.wave), alpha=0.5, color='r',
                         linestyle='--', label='Beats')
        ax.legend()
        self._draw_plot(fig, pos=(800, 400))

    def loop(self):
        while self.run:
            if len(self.AH.wave)>0:
                self.cycle_plot([11, 22])
                self.wave_plot()
            event = pygame.event.poll()
            if event.type == QUIT:
                self.run = False
            if event.type == KEYUP:
                key = event.key
                if key == K_ESCAPE:
                    self.run = False

            self.record_button.listen(event)
            self.record_button.draw()
            pygame.display.flip()


if __name__ == "__main__":
    App = Application()
    App.loop()
