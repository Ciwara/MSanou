#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os

from PyQt4.QtCore import Qt, QDate
from PyQt4.QtGui import (QIcon, QVBoxLayout, QFileDialog, QDialog, QTextEdit,
                         QFormLayout, QPushButton, QCompleter, QCheckBox)

from configuration import Config

from Common.ui.util import check_is_empty, field_error, date_to_datetime
from Common.ui.common import (FWidget, FPageTitle, Button_save, FormLabel,
                              LineEdit, Warning_btt, FormatDate)
import peewee
from models import Collect


try:
    unicode
except:
    unicode = str


class EditOrAddCollectDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, end=False, collect=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.collect = collect
        self.parent = parent
        self.table_p = table_p
        self.end = end
        self.succes_msg = u"{} a été bien enregistré."
        # self.title = u"{}."

        vbox = QVBoxLayout()
        formbox = QFormLayout()
        self.checked = QCheckBox("Fin de collecte")

        name = ""
        if self.collect:
            self.name = self.collect.name
            self.collect_created_date_field = FormatDate(
                self.collect.created_date)
            self.collect_created_date_field.setEnabled(False)
            self.collect_namefield = LineEdit(unicode(self.name))
            if end:
                self.collect_end_date_field = FormatDate(QDate.currentDate())
                self.collect_namefield.setEnabled(False)
                self.title = "Fin de {} ?".format(self.name)
                self.succes_msg.format(self.name)
                if self.collect.is_end:
                    self.checked.setCheckState(Qt.Checked)
                formbox.addRow(FormLabel(u"Date Fin: *"),
                               self.collect_end_date_field)
                formbox.addRow(FormLabel(u"Collecte : *"), self.checked)
            else:
                self.title = u"Modification de {}".format(self.name)
                self.succes_msg = u"{} a été bien mise à jour".format(
                    self.name)
        else:
            self.collect_namefield = LineEdit()
            self.new = True
            self.succes_msg = u"Client a été bien enregistré"
            self.title = u"Création d'un nouvel client"
            self.collect = Collect()

            self.collect_created_date_field = FormatDate(QDate.currentDate())

        formbox.addRow(FormLabel(u"Nom collecte : *"),
                       self.collect_namefield)
        formbox.addRow(FormLabel(u"Date Debut: *"),
                       self.collect_created_date_field)

        butt = Button_save(u"Enregistrer")
        butt.clicked.connect(self.save)
        formbox.addRow("", butt)
        vbox.addLayout(formbox)
        self.setWindowTitle(self.title)
        self.setLayout(vbox)

    def save(self):
        ''' add operation '''
        collect = self.collect

        if check_is_empty(self.collect_namefield):
            print("jjjj")
            return

        if self.collect:
            if self.end:
                end_collect_date = unicode(
                    self.collect_end_date_field.text())
                is_end = False
                if self.checked.checkState() == Qt.Checked:
                    is_end = True
                    collect.end_collect_date = date_to_datetime(
                        end_collect_date)
                collect.is_end = is_end
        else:
            collect_created_date = unicode(
                self.collect_created_date_field.text())
            collect.created_date = date_to_datetime(collect_created_date)

        name = unicode(self.collect_namefield.text())
        collect.name = name
        try:
            collect.save()
            self.close()
            self.parent.Notify(u"le {lib} à été enregistré avec succès".format(
                lib=name), "success")
            self.table_p.refresh_()
        except Exception as e:
            print(e)
            self.parent.Notify(e, "error")
