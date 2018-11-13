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
current_led_index = -1
current_song_index = -1
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


def leds_off() -> None:
    """ Turn off all LEDs on the Piano Hat """
    for i in range(15):
        pianohat.set_led(i, False)


def pause_music(i: int, pressed: bool) -> None:
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


def volume_up(i: int, pressed: bool) -> None:
    global volume

    pianohat.set_led(i, pressed)
    if pressed:
        volume += 0.1
        volume = 1 if volume > 1 else volume
        print('Volume: %.2f' % volume)
        set_volume(volume)


def volume_down(i: int, pressed: bool) -> None:
    global volume

    pianohat.set_led(i, pressed)
    if pressed:
        volume -= 0.1
        volume = 0 if volume < 0 else volume
        print('Volume: %.2f' % volume)
        set_volume(volume)


def set_volume(v: float) -> None:
    """ Set volume. Pygame expects a float between 0 and 1.  """
    pygame.mixer.music.set_volume(v)


def play_song(i: int, pressed: bool) -> None:
    """
    Play a song, unless the song assigned to this key is already playing, in
    which case we stop the song. If a different song is playing, Pygame will
    automatically stop it and play this one.
    """
    global playing, current_song_index, paused

    if not pressed:
        return

    paused = False

    if playing and current_song_index is i:
        # This track is already playing, so let's stop it
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

    # Play the song assigned to this key
    leds_off()
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()
    pianohat.set_led(i, True)
    playing = True
    current_song_index = i
    print('Playing', song)


def step_led_sequence() -> None:
    """
    Play one step of the LED flashing sequence while the music is stopped.
    Call this function repeatedly to play and loop the sequence.
    """
    global current_led_index

    if playing:
        return

    current_led_index += 1
    current_led_index = 0 if current_led_index > 12 else current_led_index

    # Turn on the appropriate LED (and turn off the others)
    for i in range(13):
        onOrOff = True if i is current_led_index else False
        pianohat.set_led(i, onOrOff)


pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(volume)

leds_off()

pianohat.auto_leds(enable=False)
pianohat.on_octave_down(volume_down)
pianohat.on_octave_up(volume_up)
pianohat.on_instrument(pause_music)
pianohat.on_note(play_song)


def shutdown() -> None:
    """ Things we need to do to gracefully shut this program down. """
    leds_off()
    sys.exit(0)


def handle_sigterm(signal, frame) -> None:
    shutdown()


def main_loop() -> None:
    """ Block to keep this program running. """
    while True:
        step_led_sequence()
        time.sleep(0.15)


# Listen for signal
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nCaught interrupt. Exiting.\n')
        shutdown()
