from threading import Thread

from db import sg


def send_email(message):
    """
    Sends email asynchronously via SendGrid.
    :param message: Message content
    :return: None
    """
    Thread(target=sg.send, args=(message,)).start()
