import time
class ChessClock(object):
    def __init__(self, time_limit=10, addition=0):
        self.time_left = time_limit * 60
        self.start = None
        self.addition = addition

    def start_clock(self):
        self.start = time.time()
    
    def get_time_used(self):
        if self.start is None:
            return 0
        return time.time() - self.start

    def stop_clock(self):
        self.time_left -= self.get_time_used()
        self.start = None
        self.time_left += self.addition
    
    def get_time_left(self):
        return self.time_left - self.get_time_used()

    def is_time_over(self):
        return not self.get_time_left() > 0


clock = ChessClock(time_limit=0.1)
clock.start_clock()
while not clock.is_time_over():
    time.sleep(1)
print('game finished')
