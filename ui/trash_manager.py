#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga


from PyQt4.QtCore import Qt, SIGNAL, SLOT, QSize, QDate
from PyQt4.QtGui import (QSplitter, QHBoxLayout, QMenu)
from Common.ui.common import FWidget
from Common.ui.table import FTableWidget, TotalsWidget
from configuration import Config
from peewee import fn
from models import Payment


class TrashViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, collect="", parent=0, *args, **kwargs):
        super(TrashViewWidget, self).__init__(parent=parent,
                                              *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(
            Config.NAME_ORGA + u"Gestion des dettes")

        self.title = u"corbeille"

        self.collect = collect
        self.table = RapportTableWidget(parent=self)
        self.splitter = QSplitter(Qt.Horizontal)

        self.splitter.addWidget(self.table)
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = ["Fornisseur", "Collecte", u"Date", u"Libelle opération", u"Poids(g)",
                         u"Base", u"Carat", "24 Carat", "Montant", ""]

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.parent = parent

        self.sorter = False
        self.stretch_columns = [0, 1, 2, 3, 4, 5, 6]
        self.align_map = {0: 'l', 1: 'l', 2: 'r',
                          3: 'r', 4: 'r', 5: 'r', 6: 'r'}
        self.ecart = -15
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self, search=None):
        """ """

        self.totals_weight = 0
        self.totals_base = 0
        self.totals_amout = 0
        self.mtt_carat24 = 0
        self.mtt_carat = 0
        self._reset()
        self.set_data_for()
        self.refresh()
        # self.parent.label_cost.setText(
        # self.parent.display_remaining(self.totals_amout, self.totals_weight,
        # self.totals_base, self.mtt_carat, self.mtt_carat24,))
        self.hideColumn(len(self.hheaders) - 1)

    def set_data_for(self):
        qs = Payment.select().where(
            Payment.deleted == True).order_by(Payment.date.asc())
        self.data = [(pay.provider_clt, pay.collect.name, pay.date, pay.libelle,
                      pay.weight, pay.base, pay.carat,
                      pay.carat24(), pay.totals_amout(), pay.id) for pay in qs]

    def popup(self, pos):

        # from ui.ligne_edit import EditLigneViewWidget
        from ui.deleteview import DeleteViewWidget
        from ui.restoreview import RestoreViewWidget
        # from data_helper import check_befor_update_payment

        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        restor = menu.addAction("Restorer")
        delaction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        row = self.selectionModel().selection().indexes()[0].row()
        payment = Payment.get(id=self.data[row][-1])
        if action == restor:
            self.parent.open_dialog(RestoreViewWidget, modal=True,
                                    table_p=self, obj=payment)
        if action == delaction:
            self.parent.open_dialog(DeleteViewWidget, modal=True,
                                    table_p=self, obj=payment, trash=False)
