class Listener:
    '''
    Class for monitoring state in Physics, Graphics, PObject,
    etc. To be used by Scene (or whatevs floats the boat) for making
    binary decisions (e.g. if object state < epsilon).
    '''
    def __init__(self, object, epsilon=1):
        '''
        :param object: The object whose state is to be tracked
        '''
        self.object = object
        self.epsilon = 1

    def listen(self):
        '''
        Read the state of the object.
        '''
        return self.object.velocity.length < self.epsilon

    def tick_listen(self):
        '''
        Read how many ticks
        '''
        return self.object.tick
