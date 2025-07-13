from enum import IntEnum

class WeekDay(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    @classmethod
    def choices(cls):
        """Возврат (значение, имя) кортежа вариантов для Django CharField / IntegerField."""
        return tuple((day.value, day.name.capitalize()) for day in cls)