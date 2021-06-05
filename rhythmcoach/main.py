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
        self.font = pygame.font.SysFont("monospace", 50)
        window = pygame.display.set_mode(size=(1600, 800), flags=DOUBLEBUF)
        pygame.display.set_caption('Rhythm Coach')
        self.background = pygame.image.load('../perc.jpeg').convert()
        self.screen = pygame.display.get_surface()
        self.graph_size = (800, 800)
        self.AH = AudioHandler()
        self.AH.GUI = self
        self.recording = False
        self.label = None
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
            self.record_button.set('text', 'Stop')
            self.recording = True
            self.AH.start()
        else:
            self.record_button.set('text', 'Record')
            self.AH.stop()
            self.recording = False
        self.record_button.draw()

    def write_tempo(self, tempo):
        self.label = self.font.render(f'Tempo: {tempo:.2f} BPM', 1, (255, 255, 0), (0, 0, 0))
        self.screen.blit(self.label, (800, 150))

    def cycle_plot(self, hits):
        N = len(hits)
        bottom = 8
        max_height = 4
        fig = plt.Figure()
        fig.patch.set_alpha(0.5)
        ax = fig.add_subplot(1, 1, 1, projection='polar')
        ax.set_rmax(10)
        beats = hits * 32
        radii = max_height * np.ones(N)
        width = 1 / 32
        bars = ax.bar(beats, radii, width=width, bottom=bottom)

        self._draw_plot(fig, pos=(50, 300))

    def _draw_plot(self, fig, pos):
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        # canvas.setStyleSheet("background-color:transparent;")
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.graph_size = canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, self.graph_size, "RGB")
        self.screen.blit(surf, pos)

    def wave_plot(self):
        fig = plt.Figure()
        fig.patch.set_alpha(0.5)
        ax = fig.add_subplot(1, 1, 1)
        display.waveshow(self.AH.wave, sr=self.AH.RATE, ax=ax)
        if len(self.AH.beats) > 0:
            ax.vlines(self.AH.times[self.AH.beats], -.5, .5, alpha=0.5, color='r',
                      linestyle='--', label='Beats')
        ax.legend()
        self._draw_plot(fig, pos=(800, 300))

    def update_screen(self):
        if len(self.AH.wave) > 0:
            self.cycle_plot(self.AH.times[self.AH.beats])
            self.wave_plot()
            self.write_tempo(self.AH.tempo)

    def loop(self):
        while self.run:
            event = pygame.event.poll()
            if event.type == QUIT:
                self.run = False
            if event.type == KEYUP:
                key = event.key
                if key == K_ESCAPE:
                    self.run = False
            # self.screen.blit(self.background, (0,0))
            self.record_button.listen(event)
            self.record_button.draw()
            pygame.display.flip()


if __name__ == "__main__":
    App = Application()
    App.loop()
