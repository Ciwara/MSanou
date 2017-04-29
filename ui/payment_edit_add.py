#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os

from PyQt4.QtCore import Qt, QDate
from PyQt4.QtGui import (QIcon, QVBoxLayout, QFileDialog, QDialog, QTextEdit,
                         QFormLayout, QPushButton, QCompleter)

from configuration import Config

from Common.ui.util import check_is_empty, field_error, date_to_datetime
from Common.ui.common import (FWidget, FPageTitle, Button_save, FormLabel,
                              FLabel, LineEdit, FloatLineEdit, Warning_btt,
                              FormatDate)
import peewee
from models import Payment


try:
    unicode
except:
    unicode = str


class EditOrAddPaymentrDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, collect, payment=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.payment = payment
        self.collect = collect
        self.parent = parent
        self.table_p = table_p

        if self.payment:
            self.new = False
            self.payment_date_field = FormatDate(self.payment.date)
            self.payment_date_field.setEnabled(False)
            self.title = u"Modification de {} {}".format(self.payment.weight,
                                                         self.payment.libelle)
            self.succes_msg = u"{} a été bien mise à jour".format(
                self.payment.libelle)
            base = payment.base
            weight = payment.weight
            carat = payment.carat
        else:
            self.new = True
            base = ""
            weight = ""
            carat = ""
            self.payment_date_field = FormatDate(QDate.currentDate())
            self.succes_msg = u"Client a été bien enregistré"
            self.title = u"Création d'un nouvel client"
            self.payment = Payment()
        self.setWindowTitle(self.title)
        self.weight_field = FloatLineEdit(unicode(weight))
        self.base_field = FloatLineEdit(unicode(base).replace(".", ","))
        self.carat_field = FloatLineEdit(unicode(carat).replace(".", ","))
        self.libelle_field = QTextEdit(self.payment.libelle)

        vbox = QVBoxLayout()

        formbox = QFormLayout()
        formbox.addRow(FormLabel(u"Poids : *"), self.weight_field)
        formbox.addRow(FormLabel(u"base : *"), self.base_field)
        formbox.addRow(FormLabel(u"Carat : *"), self.carat_field)
        formbox.addRow(FormLabel(u"Date : *"), self.payment_date_field)
        formbox.addRow(FormLabel(u"Libelle :"), self.libelle_field)

        butt = Button_save(u"Enregistrer")
        butt.clicked.connect(self.save)
        formbox.addRow("", butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def save(self):
        ''' add operation '''
        if check_is_empty(self.base_field):
            return
        self.pro_clt_id = self.table_p.provid_clt_id
        payment_date = unicode(self.payment_date_field.text())
        libelle = unicode(self.libelle_field.toPlainText())
        weight = float(unicode(self.weight_field.text().replace(",", ".")))
        carat = float(unicode(self.carat_field.text().replace(",", ".")))
        base = float(unicode(self.base_field.text().replace(
            ",", ".").replace(" ", "").replace('\xa0', '')))
        payment = self.payment
        payment.libelle = libelle
        payment.weight = weight
        payment.collect = self.collect
        payment.base = base
        payment.carat = carat
        if self.new:
            payment.date = date_to_datetime(payment_date)
            payment.provider_clt = self.table_p.provider_clt
        try:
            payment.save()
            self.close()
            self.parent.Notify(u"le {lib} à été enregistré avec succès".format(
                lib=libelle), "success")
            self.table_p.refresh_(provid_clt_id=self.pro_clt_id)
        except Exception as e:
            self.parent.Notify(e, "error")
