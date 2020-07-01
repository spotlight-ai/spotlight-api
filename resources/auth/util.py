from threading import Thread

from loguru import logger

from db import sg


def send_email(message):
    """
    Sends email asynchronously via SendGrid.
    :param message: Message content
    :return: None
    """
    logger.info('Sending e-mail message....')
    Thread(target=send, args=(message,)).start()


def send(message):
    sg.send(message)
    logger.info('Message sent...')
