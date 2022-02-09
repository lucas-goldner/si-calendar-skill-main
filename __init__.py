from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.format import nice_time, nice_date, nice_date_time
from mycroft.util.parse import extract_datetime, normalize
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

    @intent_file_handler('add.si.intent')
    def add_event_si(self, message):
        summary = message.data.get('summary', None)
        if summary is None:
            self.speak_dialog('add_no_summary.si')
        else:
            date, text_remainder = extract_datetime(message.data["utterance"], lang=self.lang)
            self.speak_dialog('calendar.si', data = {"name": summary, "date": nice_date_time(date)})

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
        sorted_appointments = sorted((d for d in appointments if d.get("date") > datetime.now()), key=lambda d: d['date'])

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
    
    def create_ics(self, summary, startdate, enddate):
        #default ICS Layout
        ics = """
        BEGIN:VCALENDAR
        PRODID:-//IDN nextcloud.com//Calendar app 2.3.3//EN
        CALSCALE:GREGORIAN
        VERSION:2.0
        BEGIN:VEVENT
        CREATED:20220112T154856Z
        DTSTAMP:20220112T154904Z
        LAST-MODIFIED:20220112T154904Z
        SEQUENCE:4
        UID:693bae92-5a23-410d-8ae1-a589d77e0844
        DTSTART;VALUE=DATE:20220112
        DTEND;VALUE=DATE:20220113
        SUMMARY:Fix mycroft
        END:VEVENT
        END:VCALENDAR
        """
        createdtime = datetime.now().strftime('%Y%m%dT%H%M%SZ')
        uid = createdtime + "@" + self.mail
        #Means it is a full day event
        if enddate is None:
            ics = ics.replace(ics[ics.index("CREATED:")+8: ics.index("DTSTAMP")], createdtime+"\n")
            ics = ics.replace(ics[ics.index("DTSTAMP:")+8: ics.index("LAST-MODIFIED")], createdtime+"\n")
            ics = ics.replace(ics[ics.index("UID:")+4: ics.index("DTSTART;VALUE=DATE:")], uid +"\n")
            ics = ics.replace(ics[ics.index("DTSTART;VALUE=DATE:")+19: ics.index("DTEND;VALUE=DATE:")], self.formatDateTime(startdate)+"\n")
            ics = ics.replace(ics[ics.index("DTEND;VALUE=DATE:")+17: ics.index("SUMMARY:")], self.formatDateTime(startdate)+"\n")
            ics = ics.replace(ics[ics.index("SUMMARY:")+8: ics.index("END:")], summary+"\n")
            return ics
        else:    
            ics = """BEGIN:VCALENDAR
            PRODID:-//IDN nextcloud.com//Calendar app 2.3.3//EN
            CALSCALE:GREGORIAN
            VERSION:2.0
            BEGIN:VEVENT
            CREATED:20211223T182215Z
            DTSTAMP:20211223T182255Z
            LAST-MODIFIED:20211223T182255Z
            SEQUENCE:2
            UID:715edfc1-6ddb-40e8-beb9-a77643d6168d
            DTSTART;TZID=Europe/Berlin:20211228T005500
            DTEND;TZID=Europe/Berlin:20211228T015500
            SUMMARY:Booster Vaccine
            END:VEVENT
            BEGIN:VTIMEZONE
            TZID:Europe/Berlin
            BEGIN:DAYLIGHT
            TZOFFSETFROM:+0100
            TZOFFSETTO:+0200
            TZNAME:CEST
            DTSTART:19700329T020000
            RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
            END:DAYLIGHT
            BEGIN:STANDARD
            TZOFFSETFROM:+0200
            TZOFFSETTO:+0100
            TZNAME:CET
            DTSTART:19701025T030000
            RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
            END:STANDARD
            END:VTIMEZONE
            END:VCALENDAR
            """
            local_timezone = '/'.join(os.path.realpath('/etc/localtime').split('/')[-2:]) 
            starttime = startdate.strftime('%Y%m%dT%H%M%S')
            endtime = enddate.strftime('%Y%m%dT%H%M%S')

            ics = ics.replace(ics[ics.index("CREATED:")+8: ics.index("DTSTAMP")], createdtime+"\n")
            ics = ics.replace(ics[ics.index("DTSTAMP:")+8: ics.index("LAST-MODIFIED")], createdtime+"\n")
            ics = ics.replace(ics[ics.index("UID:")+4: ics.index("DTSTART;")], uid +"\n")
            ics = ics.replace(ics[ics.index("DTSTART;TZID="+ local_timezone+":")+14+len(local_timezone): ics.index("DTEND;TZID=")], starttime+"\n")
            ics = ics.replace(ics[ics.index("DTEND;TZID="+local_timezone+":")+12+len(local_timezone): ics.index("SUMMARY")], endtime+"\n")
            ics = ics.replace(ics[ics.index("SUMMARY:")+8: ics.index("END:")], summary+"\n")
            ics = ics.replace(ics[ics.index("TZID:")+5: ics.index("TZID:")+5+len(local_timezone)], local_timezone)
            return ics
    
    def formatDateTime(datetime):
        year = str(datetime.date().year)
        month = str(datetime.date().month) 
        day = str(datetime.date().day)
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        return year + month + day
       
      
def create_skill():
    return SiCalendar()

