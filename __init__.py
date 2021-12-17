from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.format import nice_time, nice_date
from datetime import datetime, date


class SiCalendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.si.intent')
    def handle_calendar_si(self, message):
        self.speak_dialog('calendar.si', data = {"date": date(2002, 12, 4)})


def create_skill():
    return SiCalendar()

