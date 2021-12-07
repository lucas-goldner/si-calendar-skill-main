from mycroft import MycroftSkill, intent_file_handler


class SiCalendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.si.intent')
    def return_appointment_for_Date(self, message):
        #date = message.data('date')
        #events_fetched = my_new_calendar.date_search(
        #start=datetime(2021, 1, 1), end=datetime(2024, 1, 1), expand=True)
        self.speak_dialog('calendar.si')
    
    
    @intent_file_handler('calendar.nextAppointment.intent')
    def return_next_appointment(self, message):
        self.speak_dialog('calendar.si')

def create_skill():
    return SiCalendar()

