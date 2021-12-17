from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.format import nice_time, nice_date
from datetime import datetime, date
import caldav


class SiCalendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.si.intent')
    def handle_calendar_si(self, message):
        filename = "/etc/si-calendar/cal-config.txt"
        listOfLines=[]
        with open(filename,"r",encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                listOfLines.append(line)
        self.client = caldav.DAVClient("https://nextcloud.humanoidlab.hdm-stuttgart.de/remote.php/dav", username=listOfLines[0], password=listOfLines[1])
        self.speak_dialog('calendar.si', data = {"mail": listOfLines[0], "password": listOfLines[1]})
        #self.speak_dialog('calendar.si', data = {"date": nice_date(datetime.now())})


def create_skill():
    return SiCalendar()

