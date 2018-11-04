#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import signal
import time
import contextlib
import pianohat

# Surpress output where pygame introduces itself
with contextlib.redirect_stdout(None):
    import pygame

playing = False
paused = False
volume = 0.5
current_index = -1
songs = {
    0: 'chromeo_tiny_desk_concert.ogg',
    2: 'plantasia.ogg',
    4: 'the_astrud_gilberto_album.ogg',
    5: 'trans_europe_express.ogg',
    7: 'wanderflower.ogg',
    9: 'from_here_to_eternity_and_back.ogg',
    10: 'a_coin_for_the_well.ogg',
    11: 'teal.ogg',
    12: 'tower_of_heaven.ogg',
}


def leds_off():
    for i in range(16):
        pianohat.set_led(i, False)


def pause_music(i, pressed):
    global paused

    if playing and pressed:
        if paused:
            print("Unpausing music.")
            pygame.mixer.music.unpause()
        else:
            print("Pausing music.")
            pygame.mixer.music.pause()
        paused = not paused
        pianohat.set_led(i, paused)


def volume_up(i, pressed):
    global volume

    pianohat.set_led(i, pressed)
    if pressed:
        volume += 0.1
        if volume > 1:
            volume = 1
        print('Volume: %.2f' % volume)
        set_volume(volume)


def volume_down(i, pressed):
    global volume

    pianohat.set_led(i, pressed)
    if pressed:
        volume -= 0.1
        if volume < 0:
            volume = 0
        print('Volume: %.2f' % volume)
        set_volume(volume)


def set_volume(v):
    pygame.mixer.music.set_volume(v)


def play_song(i, pressed):
    global playing, current_index, paused

    if not pressed:
        return

    paused = False

    if playing and current_index is i:
        pygame.mixer.music.stop()
        playing = False
        leds_off()
        print("Music stopped.")
        return

    try:
        song = songs[i]
    except KeyError:
        print('No song in slot', i)
        return

    leds_off()
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()
    pianohat.set_led(i, True)
    playing = True
    current_index = i
    print('Playing', song)


pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(volume)

leds_off()

pianohat.auto_leds(enable=False)
pianohat.on_octave_down(volume_down)
pianohat.on_octave_up(volume_up)
pianohat.on_instrument(pause_music)
pianohat.on_note(play_song)


def shutdown():
    leds_off()
    sys.exit(0)


def handle_sigterm(signal, frame):
    shutdown()


def main_loop():
    while 1:
        time.sleep(0.1)


# Listen for signal
signal.signal(signal.SIGTERM, shutdown)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nCaught interrupt. Exiting.\n')
        shutdown()
