class EOSong(Exception):
    NEXT = True
    PREV = False
    
    def __init__(self, operation):
        if not isinstance(operation, bool):
            raise TypeError("Operation must be boolean; 'True'/'EOSong.NEXT' for next, 'False'/'EOSong.prev' for prev.")
        self.op = operation


class MusicPlaya:
    BUFFER_SIZE = 22060
    PRESCALER = 3808
    
    def __init__(self, timer, vol=1, speed=1):
        self.timer = timer
        self.vol = vol
        self.speed = speed
        self._flag = False
        
    def _callback(self, tim):
        self._flag = True
        tim.deinit()
    
    def play(self, condition, loop_part):
        if condition():
            raise EOSong(EOSong.NEXT)
        
        boost = lambda x: x
        if self.vol != 1:
            boost = lambda x: min(max(127 + int( (x - 127) * self.vol ), 0), 255)
        
        self._flag = False
        self.timer.init(prescaler=(int(MusicPlaya.PRESCALER / self.speed)), period=MusicPlaya.BUFFER_SIZE-1, callback=self._callback)
        
        while self._flag == False:
            loop_part()


class MusicPlayaMono(MusicPlaya):
    def __init__(self, timer, dac, vol=1, speed=1):
        self.buffer = bytearray(MusicPlaya.BUFFER_SIZE)
        self.dac = dac
        super().__init__(timer, vol, speed)
        
    def play(self, file):
        super().play(lambda: file.readinto(self.buffer) > 1,
                     lambda: self.dac.write(boost(self.buffer[self.timer.counter()])))


class MusicPlayaStereo(MusicPlaya):
    def __init__(self, timer, dacR, dacL, vol=1, speed=1):
        self.bufferR = bytearray(MusicPlaya.BUFFER_SIZE)
        self.bufferL = bytearray(MusicPlaya.BUFFER_SIZE)
        self.dacR = dacR
        self.dacL = dacL
        super().__init__(timer, vol, speed)

    def play(self, fileR, fileL):
        super().play(lambda: fileR.readinto(self.bufferR) > 1 and fileL.readinto(self.bufferL) > 1,
                     lambda: self.dacR.write(boost(self.bufferR[self.timer.counter()])) and self.dacL.write(boost(self.bufferL[self.timer.counter()])))


class MusicPlayaMulti(MusicPlaya):
    def __init__(self, timer, *dac_list, vol=1, speed=1):
        self.buffer_list = [bytearray(MusicPlaya.BUFFER_SIZE) for _ in len(dac_list)]
        self.dac_list = dac_list
        super().__init__(timer, vol, speed)
    
    def play(self, *files):
        def condition():
            sum([file.readinto(self.buffer_list[index]) > 1 for index, file in enumerate(files)]) == len(files)
        def loop_part():
            for index, dac in enumerate(self.dac_list):
                dac.write(boost(buffer_list[index][self.timer.counter()]))
        super().play(condition, loop_part)


def _test():
    from pyb import DAC, Timer
    tim = Timer(8)
    dac1 = DAC(2) #'X6'
    player = MusicPlayaMono(tim, dac1)
    with open('musica_test.raw', 'rb') as f:
        while 1:
            player.play(f)


if __name__ == '__main__':
    _test()
