from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.format import nice_date, nice_date_time
from mycroft.util.parse import extract_datetime
from datetime import datetime, date
import caldav
import os


class SiCalendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        filename = "/etc/si-calendar/cal-config.txt"
        listOfLines=[]
        with open(filename,"r",encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                listOfLines.append(line)
        self.mail = listOfLines[0]
        self.client = caldav.DAVClient("https://nextcloud.humanoidlab.hdm-stuttgart.de/remote.php/dav", username=listOfLines[0], password=listOfLines[1])


    @intent_file_handler('specific.si.intent')
    def handle_specific_si(self, message):
        date, text_remainder = extract_datetime(message.data["utterance"], lang=self.lang)
        appointments = self.fetch_events()

        sorted_appointments = sorted((d for d in appointments if d.get("date").date() == date.date()), key=lambda d: d['date'])

        if(len(sorted_appointments) == 0):
            self.speak_dialog('no_appointment.si')
        else:
            for ap in sorted_appointments:
                if ap.get("type"):
                    self.speak_dialog('calendar.si', data = {"name": ap.get("name"), "date": nice_date(ap.get("date"))})
                else:
                    self.speak_dialog('calendar.si', data = {"name": ap.get("name"), "date": nice_date_time(ap.get("date"))})

    @intent_file_handler('multiple.si.intent')
    def handle_multiple_si(self, message):
        appointments = self.fetch_events()
        #Filters for appointments that are sooner than the present date and orders them by occurence
        sorted_appointments = sorted((d for d in appointments if d.get("date") >= datetime.now()), key=lambda d: d['date'])

        if(len(sorted_appointments) == 0):
            self.speak_dialog('no_appointment.si')
        else:
            for ap in sorted_appointments:
                if ap.get("type"):
                    self.speak_dialog('calendar.si', data = {"name": ap.get("name"), "date": nice_date(ap.get("date"))})
                else:
                    self.speak_dialog('calendar.si', data = {"name": ap.get("name"), "date": nice_date_time(ap.get("date"))})      
    
    @intent_file_handler('next.si.intent')
    def handle_next_si(self, message):
        appointments = self.fetch_events()
        #Filters for appointments that happen today and orders them by occurence
        sorted_appointments = sorted((d for d in appointments if d.get("date").date() == datetime.today().date()), key=lambda d: d['date'])

        #Next event prioritizes events that are scheduled at an exact time, instead of full day events
        if(len(sorted_appointments) == 0):
            self.speak_dialog('no_appointment.si')
        else:
            firstAppointment = sorted_appointments[0]
            #Check if next event is full day
            if firstAppointment.get("type"):
                #Check if there is another event in the future
                if len(sorted_appointments) > 1:
                    #If next event is also a full day event it will be also chosen 
                    firstAppointment = sorted_appointments[1]
                    if firstAppointment.get("type"):
                        self.speak_dialog('calendar.si', data = {"name": firstAppointment.get("name"), "date": nice_date(firstAppointment.get("date"))})
                    else:
                        self.speak_dialog('calendar.si', data = {"name": firstAppointment.get("name"), "date": nice_date_time(firstAppointment.get("date"))})
                else:
                    self.speak_dialog('calendar.si', data = {"name": firstAppointment.get("name"), "date": "today"})
            else:
                self.speak_dialog('calendar.si', data = {"name": firstAppointment.get("name"), "date": "today"})

    def fetch_events(self):
        appointments = []
        principal = self.client.principal()
        for calendar in principal.calendars():
            for event in calendar.events():
                ical_text = event.data
                summaryIndex = ical_text.find("SUMMARY:") + 8
                endIndex = ical_text.find("END:")
                #Titel des Events
                summary = ical_text[summaryIndex:endIndex]
        
                #Formatierung der Zeit des Events für `nice_date()`
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
                    date_time_str = day + "/" + month + "/" + year
                    date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y')
                    appointments.append({"name": summary, "date": date_time_obj, "type": is_full_day})
                else:
                    year = string_cut[doublepoint_index + 1:dtendindex][:4]
                    month = string_cut[doublepoint_index + 1:dtendindex][4:6]
                    day = string_cut[doublepoint_index + 1:dtendindex][6:8]
                    hour = string_cut[doublepoint_index + 1:dtendindex][9:11]
                    minute = string_cut[doublepoint_index + 1:dtendindex][11:13]
                    date_time_str = day + "/" + month + "/" + year + " " + hour + ":" + minute
                    date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M')
                    appointments.append({"name": summary, "date": date_time_obj, "type": is_full_day})

        return appointments
       
def create_skill():
    return SiCalendar()

