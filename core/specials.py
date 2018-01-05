from dominate.tags import p as _p


def _first_char(arg):
    if isinstance(arg, str):
        if len(arg) == 0:
            return None
        return arg[0]
    if isinstance(arg):
        pass


class p(_p):
    def add(self, *args):
        for arg in args:
            self._single_add(arg)
        if len(args) == 1:
            return args[0]
        return args

    def _single_add(self, arg):
        first_char = self._last_char()
        second_char = _first_char(arg)
        if first_char is None:
            _p.add(self, arg)
            return

