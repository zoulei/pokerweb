
class AllinWithExtraChips(Exception):
    def __str__(self):
        return "all in with extra chips"

class LastActionAllinError(AllinWithExtraChips):
    def __str__(self):
        return str(AllinWithExtraChips) + " : but this is the last action"

class CheckWhenRaiseMade(Exception):
    def __str__(self):
        return "check when raise made"

class ExtraAction(Exception):
    def __str__(self):
        return "extra action"

class RaiseValueDecrease(Exception):
    def __str__(self):
        return "raise value smaller than bet value"

class NotEnoughAction(Exception):
    def __str__(self):
        return "not enough action"