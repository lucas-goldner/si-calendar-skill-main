from mycroft import MycroftSkill, intent_file_handler
import caldav

class SiCalendar(MycroftSkill):
    def __init__(self):
        self.client = caldav.DAVClient("https://nextcloud.humanoidlab.hdm-stuttgart.de/remote.php/dav", username="nichts@gmail",
                          password="nichts")
        self.events = []
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.si.intent')
    def return_appointment_for_Date(self, message):
        #date = message.data('date')
        #events_fetched = my_new_calendar.date_search(
        #start=datetime(2021, 1, 1), end=datetime(2024, 1, 1), expand=True)
        self.speak_dialog('calendar.si')
    
    def handle_calendar_si(self, message):
        self.get_calendar_events()
        self.speak_dialog('calendar.si')

    def get_calendar_events(self):
        principal = self.client.principal()
        for calendar in principal.calendars():
            for event in calendar.events():
                ical_text = event.data
                summaryIndex = ical_text.find("SUMMARY:") + 8
                endIndex = ical_text.find("END:")
                summary = ical_text[summaryIndex:endIndex]
        
                #difference between full day and certain time 
                is_full_day = False
                dtstartindex = ical_text.find("DTSTART;") + 8
                dtendindex = ical_text.find("DTEND;")
                year = "0000"
                month = "00"
                day = "00"
        
                #variables for not full day
                string_cut = ical_text[dtstartindex:dtendindex]
                doublepoint_index = string_cut.find(":")
                hour = "00"
                minute = "00"
        
                if ical_text[dtstartindex:dtstartindex+5]  == "VALUE":
                    is_full_day = True
                if is_full_day:
                    year = ical_text[dtstartindex + 11:dtendindex][:4]
                    month = ical_text[dtstartindex + 11:dtendindex][4:6]
                    day = ical_text[dtstartindex + 11:dtendindex][6:8]
                    self.events.append({"name": summary, "date": day + "." + month + "." + year, "full-day": True})
                else:
                    year = string_cut[doublepoint_index + 1:dtendindex][:4]
                    month = string_cut[doublepoint_index + 1:dtendindex][4:6]
                    day = string_cut[doublepoint_index + 1:dtendindex][6:8]
                    hour = string_cut[doublepoint_index + 1:dtendindex][9:11]
                    minute = string_cut[doublepoint_index + 1:dtendindex][11:13]
                    self.events.append({"name": summary, "date":  hour + ":" + minute + "@" + day + "." + month + "." + year, "full-day": False})

    @intent_file_handler('calendar.nextAppointment.intent')
    def return_next_appointment(self, message):
        self.speak_dialog('calendar.si')
        
def create_skill():
    return SiCalendar()

