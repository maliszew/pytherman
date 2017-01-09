"""Bomber component"""


class Bomber(object):
    """Bomber component defines how often and how many bombs
       entity can plant"""

    def __init__(self, max=1, cooldown=5):
        """Cooldown is in seconds"""
        self.max = max
        self.used = 0
        self.cooldown = cooldown
        self.last_planted = 0
