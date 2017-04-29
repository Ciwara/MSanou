#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QGridLayout, QDialog)

from Common.ui.common import FWidget, FPageTitle, Button, FLabel


class RestoreViewWidget(QDialog, FWidget):

    def __init__(self, table_p, obj, parent, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle(u"Confirmation de la restoration")
        self.title = FPageTitle(u"Voulez vous vraiment le restorer?")
        self.obj = obj
        self.table_p = table_p
        self.parent = parent
        # self.title.setAlignment(Qt.AlignHCenter)
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(self.title)
        report_hbox = QGridLayout()

        report_hbox.addWidget(FLabel(obj.display_name()), 0, 0)
        # delete and cancel hbox
        Button_hbox = QHBoxLayout()

        # Delete Button widget.
        delete_but = Button(u"Restorer")
        Button_hbox.addWidget(delete_but)
        delete_but.clicked.connect(self.untrash)

        # Cancel Button widget.
        cancel_but = Button(u"Annuler")
        Button_hbox.addWidget(cancel_but)
        cancel_but.clicked.connect(self.cancel)

        # Create the QVBoxLayout contenaire.
        vbox = QVBoxLayout()
        vbox.addLayout(title_hbox)
        vbox.addLayout(report_hbox)
        vbox.addLayout(Button_hbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()
        return False

    def untrash(self):
        self.obj.deleted = False
        self.obj.save()
        self.cancel()
        self.table_p.refresh_()
        self.parent.Notify("le rapport à été bien restoré", "info")
