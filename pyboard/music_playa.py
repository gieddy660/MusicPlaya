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
    
    def __init__(self, timer, dac, vol=1, speed=1):
        self.buffer = bytearray(MusicPlaya.BUFFER_SIZE)
        
        self.timer = timer
        self.dac = dac
        self.vol = vol
        self.speed = speed
        
        self.flag = False
    
    def _callback(self, tim):
        self.flag = True
        tim.deinit()
        
    def play(self, file):
        try:
            assert file.readinto(self.buffer) > 1
        except AssertionError:
            raise EOSong(EOSong.NEXT)
        
        self.flag = False

        
        boost = lambda x: x
        if self.vol != 1:
            boost = lambda x: min(max(127 + int( (x - 127) * self.vol ), 0), 255)
        
        self.timer.init(prescaler=(int(MusicPlaya.PRESCALER / self.speed)), period=MusicPlaya.BUFFER_SIZE-1, callback=self._callback)
        while self.flag == False:
            self.dac.write(boost(self.buffer[self.timer.counter()]))  # this doesn't go out of range because the buffer is preallocated and always of the same size


class MusicPlayaStereo(MusicPlaya):
    def __init__(self, timer, dacR, dacL, vol=1, speed=1):
        self.timer = timer
        self.dacR = dacR
        self.dacL = dacL
        self.vol = vol
        self.speed = speed
        
        self.flag = False

    def play(self, fileR, fileL):
        bufferR = fileR.read(MusicPlaya.BUFFER_SIZE)
        bufferL = fileL.read(MusicPlaya.BUFFER_SIZE)
        self.flag = False
        self.timer.init(prescaler=(int(MusicPlaya.PRESCALER / self.speed)), period=MusicPlaya.BUFFER_SIZE-1, callback=self._callback)
        boost = lambda x: x
        if self.vol != 1:
            boost = lambda x: min(max(127 + int( (x - 127) * self.vol ), 0), 255)
        try:
            while self.flag == False:
                self.dacR.write(boost(bufferR[self.timer.counter()]))
                self.dacL.write(boost(bufferL[self.timer.counter()])) # this goes out of range when 'file.read'  has read less than 'file.BUFFER_SIZE' bytes (it raises 'IndexError')
        except IndexError:
            raise EOSong(EOSong.NEXT)


class MusicPlayaMulti(MusicPlaya):
    def __init__(self, timer, *dac_list, vol=1, speed=1):
        self.timer = timer
        self.dac_list = dac_list
        self.vol = vol
        self.speed = speed
        
        self.flag = False
    
    def play(self, *files):
        buffers = [file.read(MusicPlaya.BUFFER_SIZE) for file in files]
        self.flag = False
        self.timer.init(prescaler=(int(MusicPlaya.PRESCALER / self.speed)), period=MusicPlaya.BUFFER_SIZE-1, callback=self._callback)
        boost = lambda x: x
        if self.vol != 1:
            boost = lambda x: min(max(127 + int( (x - 127) * self.vol ), 0), 255)
        try:
            while self.flag == False:
                for index, dac in enumerate(self.dac_list):
                    dac.write(boost(buffers[index][self.timer.counter()]))  # this goes out of range when 'file.read'  has read less than 'file.BUFFER_SIZE' bytes (it raises 'IndexError')
        except IndexError:
            raise EOSong(EOSong.NEXT)


def _test():
    from pyb import DAC, Timer
    tim = Timer(8)
    dac1 = DAC(2) #'X6'
    player = MusicPlaya(tim, dac1)
    with open('musica_test.raw', 'rb') as f:
        while 1:
            player.play(f)


if __name__ == '__main__':
    _test()
