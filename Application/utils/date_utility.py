from pytz import timezone
from datetime import datetime
timezone = timezone("Africa/Kampala")

class DateUtil:
    def __init__(self):
        self.timezone = timezone
        self.current_date_time = self.set_date_time()

    def set_date_time(self):
        current_date_time = datetime.now()
        return self.timezone.localize(current_date_time)

    @property
    def current_date(self):
        return self.current_date_time.date()

    @property
    def current_time(self):
        return self.current_date_time.time()
        