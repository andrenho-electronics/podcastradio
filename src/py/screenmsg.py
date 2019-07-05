import syncqueue

class ScreenMessage(syncqueue.Message):
    pass

class WelcomeMessage(ScreenMessage):

    def execute(self, scr):
        scr.print_welcome_message()
        logger.debug("Welcome message printed.")
