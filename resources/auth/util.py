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
    try:
        response = sg.send(message)
        logger.debug(response.status_code)
        logger.debug(response.body)
        logger.debug(response.headers)
        logger.info('Message sent...')
    except Exception as e:
        logger.error(e.message)
