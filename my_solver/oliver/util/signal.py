#!/usr/bin/env python
# coding=utf-8
import logging
import os

import psutil


def handler(signum, frame):
    logging.error('signum %s' % signum)
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    for child in children:
        logging.error('Child pid is {}\n'.format(child.pid))
        logging.error('Killing child.')
        try:
            os.kill(child.pid, 15)
        except OSError as e:
            logging.warn('Process might already be gone. See error below.')
            logging.warn('%s' % str(e))

    logging.warn('SIGNAL received')
    if signum == 15:
        raise TimeoutError('signal')
    else:
        raise InterruptedError('signal')


def nothing(signum, frame):
    logging.warn('SIGNAL received\n')
    logging.warn('SIGNAL ignored...\n')
