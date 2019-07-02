# !/usr/bin/python3
# -*- coding: utf-8 -*-
SETTINGS_PRIORITY = 0

import os

def path(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

ANNOTATOR_ICON_IDTRACKERAI = path('idtrackerai.png')

IDTRACKERAI_SHORT_KEYS= {
    'Go to next crossing.': 'Ctrl+M',
    'Go to previous crossing.': 'Ctrl+N',
}