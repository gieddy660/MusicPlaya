from os import ilistdir


class BiTuple(tuple):
    def __init__(self, *args, looping=False, **kwargs):  # vedere __new__ (????)
        self._current_position = 0
        self._looping = looping                          # forse meglio cambiare la funzione qui (???)
        super().__init__(*args, **kwargs)
    
    def current(self):
        return self[self._current_position]
    
    def next(self):
        self._current_position += 1
        if self._looping:
            self._current_position %= len(self)
    
    def prev(self):
        self._current_position -= 1
        if self._looping:
            self._current_position %= len(self)


def lister():
    b = [(file[0], file[3]) for file in ilistdir() if file[1] is 0x8000 and file[0].split('.')[-1] == 'raw']
    return BiTuple(b, looping=True)
