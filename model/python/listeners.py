class Listener:
    def __init__(self, measure):
        self.measure = measure
        self.state = None

    def listen(self, object):
        self.state = self.measure(self.state, object)

def is_stopped(last_pos, curr_pos):
    pass