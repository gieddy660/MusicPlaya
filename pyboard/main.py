from micropython import alloc_emergency_exception_buf, mem_info
alloc_emergency_exception_buf(400)


from math import ceil
from time import sleep
from pyb import Timer, DAC, UART
from machine import Pin, ADC
from musicplaya import MusicPlayaMono, EOSong
from songlister import lister

from gc import collect, mem_alloc, mem_free


tim = Timer(8)
dac_right = DAC(Pin('X6'))
adc_volume = ADC(Pin('X1'))
uart = UART(2, 115200)

next_song_pin = Pin('Y1', Pin.IN, Pin.PULL_UP)
play_pause_pin = Pin('Y2', Pin.IN, Pin.PULL_UP)
prev_song_pin = Pin('Y3', Pin.IN, Pin.PULL_UP)
volume_pin = Pin('X9', Pin.IN, Pin.PULL_UP)
volume_reset_pin = Pin('Y8', Pin.IN, Pin.PULL_UP)
speed_pin = Pin('X11', Pin.IN, Pin.PULL_UP)
speed_reset_pin = Pin('X10', Pin.IN, Pin.PULL_UP)


collect()
player = MusicPlayaMono(tim, dac_right, speed=1)
songs = lister()


def size_to_bytes(num):
  tot_bits = len(bin(num)) - 2
  if tot_bits == 0: return b'\x80'
  tot_bytes = ceil(tot_bits / 7)
  res = bytearray(tot_bytes)
  for i in range(tot_bytes):
      res[tot_bytes - i - 1] = (num & (0b1111111 << (7*i))) >> (7*i)
  res[tot_bytes - 1] |= 0b10000000
  return res

exceptions_list = []
def main():
    sleep(3)
    while True:
        # check if stereo or mono
        
        playing = True
        song, song_size = songs.current()
        try:
            uart.write(b'\x01')
            uart.write(song[:-4])
            uart.write(b'\x03')
            uart.write(size_to_bytes(song_size // MusicPlaya.BUFFER_SIZE))
            collect()
            with open(song, 'rb') as song:
                song.seek(0, 0)
                while True:
                    if playing:
                        player.play(song)
                        uart.write(b'\x06')
                    
                    if play_pause_pin() == 0:
                        playing = not playing
                        sleep(0.5)
                    if next_song_pin() == 0:
                        playing = False
                        sleep(0.5)
                        raise EOSong(EOSong.NEXT)
                    if prev_song_pin() == 0:
                        playing = False
                        sleep(0.5)
                        raise EOSong(EOSong.PREV)
                    
                    if volume_pin() == 0:
                        volume = adc_volume.read_u16() / 6554 + 1
                        player.vol = volume
                    if volume_reset_pin() == 0:
                        player.vol = 1
                    
                    if speed_pin() == 0:
                        speed = adc_volume.read_u16() / 655 + 1
                        player.speed = speed
                    if speed_reset_pin() == 0:
                        player.speed = 1
        except EOSong as command:
            if command.op == EOSong.PREV:
                songs.prev()
            else:
                songs.next()
        except Exception as exc:
            exceptions_list.append(exc)
            print(exceptions_list)
            sleep(25)
            songs.next()


if __name__ == '__main__':
    main()
