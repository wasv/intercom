import os
import platform
import shlex
import subprocess
import uuid

__author__ = 'ahanes'
import time


class Command(object):
    def __init__(self):
        self.uid = uuid.uuid4()
        print(self.uid)
        pass

    def act(self):
        """
        Act on a command

        Throw exception on error
        :return: None
        """
        raise NotImplementedError("No act method")


class SayCommand(Command):
    def __init__(self, text):
        super().__init__()
        self.text = shlex.quote(text.decode('utf-8','ignore'))

    def act(self):
        if platform.system() == 'Darwin':
            os.system("say -v 'Bad News' " + self.text)
        elif platform.system() == 'Linux':
            subprocess.call(["echo", self.text])
        else:
            os.system("echo " + self.text)