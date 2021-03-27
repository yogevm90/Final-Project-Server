from datetime import datetime
import datetime as dt

from server.interfaces.jsonable import Jsonable


class ClassroomConfig(Jsonable):
    def __init__(self, classroom_id, user_ids, working_dir, start, end, day):
        self._classroom_id = classroom_id
        self._user_ids = user_ids
        self._working_dir = working_dir
        self._start = start
        self._end = end
        self._day = day

    @property
    def ID(self):
        return self._classroom_id

    @property
    def UserIds(self):
        return self._user_ids

    @property
    def WorkingDir(self):
        return self._working_dir

    @property
    def Start(self):
        return self._start

    @property
    def End(self):
        return self._end

    @property
    def DateInCurrWeek(self) -> datetime:
        today = datetime.now()
        dates_in_week = [today + dt.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        return dates_in_week[self._day - 1]

    def json(self):
        curr_date = self.DateInCurrWeek
        return {
            "start": f"{curr_date.year}:{curr_date.month}:{curr_date.day}T{self._start}",
            "end": f"{curr_date.year}:{curr_date.month}:{curr_date.day}T{self._end}",
        }
