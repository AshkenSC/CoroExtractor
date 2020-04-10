from threading import Lock

class Set(set):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock = Lock()
        
    def add(self, value):
        if self.lock.acquire():
            super().add(value)
            self.lock.release()

    def remove(self, value):
        if self.lock.acquire():
            try:
                super().remove(value)
            except:
                pass
            self.lock.release()

class Dict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock = Lock()
        
    def __setitem__(self, key, value):
        if self.lock.acquire():
            super().__setitem__(key, value)
            self.lock.release()

    def pop(self, key):
        if self.lock.acquire():
            try:
                item = super().pop(key)
            except:
                item = None
            self.lock.release()
        return item


if __name__ == '__main__':
    s = Set()
    s.add(1)
    print(s)
    s.remove(1)
    print(s)

    d = Dict()
    d[1] = 1
    print(d)
    d.pop(1)
    print(d)
