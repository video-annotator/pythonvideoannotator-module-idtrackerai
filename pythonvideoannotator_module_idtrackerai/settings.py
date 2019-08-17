# !/usr/bin/python3
# -*- coding: utf-8 -*-
SETTINGS_PRIORITY = 0

import os

def path(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

ANNOTATOR_ICON_IDTRACKERAI = path('idtrackerai.png')

IDTRACKERAI_SHORT_KEYS= {
    'Jumps 1 frame backward.':                  'X',
    'Jumps 1 frame forward.':                   'Z',
    'Go to next crossing.':                     'Ctrl+X',
    'Go to previous crossing.':                 'Ctrl+Z',
    'Check/Uncheck add centroid.':              'Ctrl+C',
    'Check/Uncheck add blob.':                  'Ctrl+A',
    'Delete centroid.':                         'Ctrl+D'
}
