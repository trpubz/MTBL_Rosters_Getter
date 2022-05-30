# Front Office
# by pubins.taylor
# v0.1
# created 24 MAY 2022
# lastUpdate 26 MAY 2022

import json


class Team:

    def __init__(self, name: str):
        self.name: str = name
        self.roster = dict()

    def addPlayer(self, pos: str, pid: str):
        """
        Certain positions have multiple occurrences.  The range iterator starts at 1 and ends at the appropriate number
        for that position.
        :param pos:  string of the rostered spot
        :param pid:  string of the player id
        """
        if pos == "OF":
            for i in range(1, 3 + 1):
                if "OF" + i.__str__() not in self.roster:
                    self.roster["OF" + i.__str__()] = pid
        elif pos == "P":
            for i in range(1, 2 + 1):
                if "P" + i.__str__() not in self.roster:
                    self.roster["P" + i.__str__()] = pid
                    break
        elif pos == "SP":
            for i in range(1, 3 + 1):
                if "SP" + i.__str__() not in self.roster:
                    self.roster["SP" + i.__str__()] = pid
                    break
        elif pos == "RP":
            for i in range(1, 2 + 1):
                if "RP" + i.__str__() not in self.roster:
                    self.roster["RP" + i.__str__()] = pid
                    break
        elif pos == "Bench":
            for i in range(1, 21 + 1):
                if "BN" + i.__str__() not in self.roster:
                    self.roster["BN" + i.__str__()] = pid
                    break
        elif pos == "IL":
            for i in range(1, 6 + 1):
                if "IL" + i.__str__() not in self.roster:
                    self.roster["IL" + i.__str__()] = pid
                    break
        else:
            self.roster[pos] = pid

    def default(self, o):
        """
        Used as alternate method to convert self(object) as JSON Object
        :param self:
        :param o:
        :return:
        """
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)