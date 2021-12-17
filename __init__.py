from mycroft import MycroftSkill, intent_file_handler


class SiCalendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.si.intent')
    def handle_calendar_si(self, message):
        self.speak_dialog('calendar.si', data={'name': 'Lucas'})


def create_skill():
    return SiCalendar()

