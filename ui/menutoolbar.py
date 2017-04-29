# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QIcon, QToolBar, QFont, QCursor)
from PyQt4.QtCore import Qt, QSize


from Common.ui.common import FWidget

# from static import Constants
from configuration import Config

# from ui.debt_manager import DebtsViewWidget
from ui.collect_manager import CollectViewWidget


class MenuToolBar(QToolBar, FWidget):

    def __init__(self, parent=None, *args, **kwargs):
        QToolBar.__init__(self, parent, *args, **kwargs)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        menu = [
            {"name": u"Collecte", "icon": 'collect',
             "admin": False, "goto": CollectViewWidget},
            # {"name": u"Tableau de bord", "icon": 'example',
            #  "admin": False, "goto": DebtsViewWidget},
        ]

        self.addAction(
            QIcon(u"{}exit.png".format(Config.img_cmedia)), u"Quiter", self.goto_exit)
        for m in menu:
            self.addSeparator()
            self.addAction(QIcon("{}{}.png".format(Config.img_media, m.get(
                'icon'))), m.get('name'), lambda m=m: self.goto(m.get('goto')))

    def goto(self, goto):
        self.change_main_context(goto)

    def goto_exit(self):
        self.parent().exit()
