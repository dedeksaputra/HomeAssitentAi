import threading


class BaseService:

    def __init__(self, name):


        self.name = name
        self.running = False

    def start_service(self):

        if self.running:
            return

        self.running = True
        self.start()

    def stop_service(self):

        self.running = False

    def run(self):

        raise NotImplementedError