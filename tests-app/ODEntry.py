import canopen
import ast


class ODEntry:
    def __init__(self, index, subindex=None):
        self.index = index
        self.subindex = subindex

    @staticmethod
    def createEntries(sdo, od_entrie):
        if isinstance(sdo[od_entrie], canopen.sdo.base.Record):
            return [str(ODEntry(od_entrie, sub)) for sub in sdo[od_entrie].keys()]
        else:
            return [str(ODEntry(od_entrie))]

    def __str__(self):
        return '{:X}sub{:X}'.format(self.index, self.subindex) if self.subindex is not None \
            else '{:X}'.format(self.index)

    @staticmethod
    def parce(s):
        v = s.split('sub')
        return ODEntry(int(v[0], 16), int(v[1], 16) if len(v) == 2 else None)

    def getvalue(self, sdo):
        if self.subindex is None:
            return sdo[self.index].raw
        else:
            return sdo[self.index][self.subindex].raw

    def setvalue(self, sdo, val):
        def int_parser(x, _t):
            return ast.literal_eval(str(x)) if _t is int else x

        if self.subindex is None:
            t = type(sdo[self.index].raw)
            sdo[self.index].raw = t(int_parser(val, t))
        else:
            t = type(sdo[self.index][self.subindex].raw)
            sdo[self.index][self.subindex].raw = t(int_parser(val, t))
