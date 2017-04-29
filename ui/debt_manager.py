#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga


from PyQt4.QtGui import (QSplitter, QHBoxLayout,
                         QPixmap, QFont, QListWidget, QMenu, QListWidgetItem,
                         QIcon, QGridLayout)

from datetime import datetime
from PyQt4.QtCore import Qt, QSize

from models import ProviderOrClient, Payment

from Common.ui.common import (FWidget, Button,
                              LineEdit, FLabel, FormatDate, FormLabel)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import device_amount, show_date, is_float

from ui.payment_edit_add import EditOrAddPaymentrDialog
from GCommon.ui.provider_client_edit_add import EditOrAddClientOrProviderDialog

from configuration import Config


try:
    unicode
except:
    unicode = str

ALL_CONTACTS = "TOUS"


class DebtsViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, collect="", parent=0, *args, **kwargs):
        super(DebtsViewWidget, self).__init__(parent=parent,
                                              *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(
            Config.NAME_ORGA + u"Gestion des dettes")

        self.title = u"Movements"
        self.collect = collect

        hbox = QHBoxLayout(self)
        self.now = datetime.now().strftime(Config.DATEFORMAT)

        self.label_cost = FormLabel(u"Poid au {} ".format(self.now))
        self.label_weight = FormLabel("")
        self.label_ = FormLabel("")

        self.table = RapportTableWidget(parent=self)
        self.btt_export = Button(u"Exporter")
        self.btt_export.setIcon(QIcon(u"{img_media}{img}".format(
            img_media=Config.img_cmedia, img="xls.png")))
        self.btt_export.clicked.connect(self.export_xls)
        self.add_btt = Button("Ajout")
        self.add_btt.setEnabled(False)
        self.add_btt.clicked.connect(self.add_payment)
        self.add_btt.setIcon(QIcon(u"{img_media}{img}".format(
            img_media=Config.img_media, img="in.png")))

        # self.add_btt.setFixedWidth(100)
        self.add_btt.setFixedHeight(60)
        self.add_prov_btt = Button("Compte")
        self.add_prov_btt.setFixedWidth(300)
        self.add_prov_btt.setFixedHeight(60)
        # self.add_prov_btt.setMaximumHeight(40)
        # self.add_prov_btt.setMaximumWidth(10)
        self.add_prov_btt.clicked.connect(self.add_prov_or_clt)

        editbox = QGridLayout()
        # editbox.addWidget(self.sub_btt, 1, 5)
        editbox.addWidget(self.add_btt, 0, 1)
        editbox.addWidget(self.btt_export, 0, 3)
        editbox.setColumnStretch(0, 2)

        self.table_provid_clt = ProviderOrClientTableWidget(parent=self)

        self.search_field = LineEdit()
        self.search_field.textChanged.connect(self.search)
        self.search_field.setPlaceholderText(u"Nom ou numéro tel")
        self.search_field.setMaximumHeight(40)
        splitter = QSplitter(Qt.Horizontal)

        self.splt_add = QSplitter(Qt.Horizontal)
        self.splt_add.setLayout(editbox)

        self.splitter_left = QSplitter(Qt.Vertical)
        self.splitter_left.addWidget(self.search_field)
        self.splitter_left.addWidget(self.table_provid_clt)
        self.splitter_left.addWidget(self.add_prov_btt)

        self.splt_clt = QSplitter(Qt.Vertical)
        self.splt_clt.addWidget(self.splt_add)
        self.splt_clt.addWidget(self.table)
        self.splt_clt.addWidget(self.label_cost)
        self.splt_clt.resize(1000, 1000)
        splitter.addWidget(self.splitter_left)
        splitter.addWidget(self.splt_clt)

        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def refresh_period(self):
        self.table.refresh_()

    def search(self):
        self.table_provid_clt.refresh_(self.search_field.text())

    def add_prov_or_clt(self):
        self.parent.open_dialog(EditOrAddClientOrProviderDialog, modal=True,
                                prov_clt=None, table_p=self.table_provid_clt)

    def export_xls(self):
        from Common.exports_xlsx import export_dynamic_data
        dict_data = {
            'file_name': "compte.xlsx",
            'headers': self.table.hheaders[:-1],
            'data': self.table.data,
            "extend_rows": [],
            'sheet': self.title,
            # 'title': self.title,
            'widths': self.table.stretch_columns,
            'format_money': ["C:C", "D:D", "E:E", ],
            'exclude_row': len(self.table.data) - 1,
            'others': [("A7", "C7", "Compte : {}".format(self.table.provider_clt)),
                       ("A8", "B8", "Collecte {}".format(1)), ],
            'footers': [
                ("C", "D", "Coût total : {}".format(
                    device_amount(self.table.totals_amout))),
                ("C", "D", "Poids total : {}".format(
                    device_amount(self.table.totals_weight, dvs="g"))),
                ("C", "D", "Prix du gramme d’or : {}".format(
                    device_amount(self.table.totals_amout /
                                  self.table.totals_weight))),
            ],
        }
        export_dynamic_data(dict_data)

    def add_payment(self):
        self.open_dialog(EditOrAddPaymentrDialog, modal=True,
                         payment=None, collect=self.collect, table_p=self.table)

    def display_remaining(self, totals_amout, totals_weight, totals_base, mtt_carat, mtt_carat24):
        try:
            cost_g = (totals_amout / totals_weight)
        except ZeroDivisionError:
            cost_g = 0
        return """<h2>Solde du {date}</h2><h1> {collect_name} {status}</h1>
                  <h2 style="color: green"><strong>______________ Coût total : </strong>{totals_amout}</h2">
                  <h2 style="color: green"><strong>______________ Total poids  : </strong>{totals_weight}</h2">
                  <h2 style="color: green"><strong>______________ Total 24 carat : </strong>{mtt_carat24}</h2">
                  <h2 style="color: green"><strong>______________ Prix du gramme : </strong>{cost_g}</h2">
                  """.format(date=self.now, totals_amout=device_amount(totals_amout),
                             totals_weight=device_amount(
                                 totals_weight, dvs="g"),
                             mtt_carat24=device_amount(mtt_carat24, dvs=" "),
                             totals_base=device_amount(totals_base, dvs=" "),
                             cost_g=device_amount(cost_g),
                             collect_name=self.collect.name,
                             status="<span style='color: green'>(En cours)</span>" if not self.collect.is_end else "finie le {}".format(show_date(self.collect.end_collect_date)))


class ProviderOrClientTableWidget(QListWidget):
    """
    Affiche tout le nom de tous les provid_cltes
    """

    def __init__(self, parent, *args, **kwargs):
        super(ProviderOrClientTableWidget, self).__init__(parent)

        self.parent = parent
        self.setAutoScroll(True)
        # self.setAutoFillBackground(True)
        self.itemSelectionChanged.connect(self.handleClicked)
        self.refresh_()
        # self.setStyleSheet("QListWidget::item { border-bottom: 1px; }")

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if row < 1:
            return
        menu = QMenu()
        editaction = menu.addAction("Modifier l'info.")
        action = menu.exec_(self.mapToGlobal(pos))

        provid_clt = ProviderOrClient.get(
            ProviderOrClient.phone == self.item(row).text().split(",")[1])
        if action == editaction:
            self.parent.open_dialog(EditOrAddClientOrProviderDialog, modal=True,
                                    prov_clt=provid_clt, table_p=self)

    def refresh_(self, provid_clt=None):
        """ Rafraichir la liste des provid_cltes"""
        self.clear()
        self.provid_clt = provid_clt
        self.addItem(ProviderOrClientQListWidgetItem(ALL_CONTACTS))
        qs = ProviderOrClient.select().where(
            ProviderOrClient.type_ == ProviderOrClient.CLT)
        if provid_clt:
            qs = qs.where(ProviderOrClient.name.contains(provid_clt))
        for provid_clt in qs:
            self.addItem(ProviderOrClientQListWidgetItem(provid_clt))

    def handleClicked(self):
        self.provid_clt = self.currentItem()
        self.provid_clt_id = self.provid_clt.provid_clt_id
        if isinstance(self.provid_clt_id, int):
            self.parent.add_btt.setEnabled(True)
        else:
            self.parent.add_btt.setEnabled(False)
        self.parent.table.refresh_(provid_clt_id=self.provid_clt_id)


class ProviderOrClientQListWidgetItem(QListWidgetItem):

    def __init__(self, provid_clt):
        super(ProviderOrClientQListWidgetItem, self).__init__()

        self.provid_clt = provid_clt
        self.setSizeHint(QSize(0, 30))
        icon = QIcon()

        if not isinstance(self.provid_clt, str):
            icon.addPixmap(QPixmap("{}.png".format(
                Config.img_media + "debt" if self.provid_clt.is_indebted() else Config.img_cmedia + "user_active")),
                QIcon.Normal, QIcon.Off)

        self.setIcon(icon)
        self.init_text()

    def init_text(self):
        try:
            self.setText(
                "{}, {}".format(self.provid_clt.name, self.provid_clt.phone))
        except AttributeError:
            font = QFont()
            font.setBold(True)
            self.setFont(font)
            self.setTextAlignment(Qt.AlignCenter)
            self.setText(u"Tous")

    @property
    def provid_clt_id(self):
        try:
            return self.provid_clt.id
        except AttributeError:
            return self.provid_clt


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            u"Date", u"Libelle opération", u"Poids(g)", u"Base",
            u"Carat", "24 Carat", "Montant", ""]

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

    def refresh_(self, provid_clt_id=None, search=None):
        """ """

        self.totals_weight = 0
        self.totals_base = 0
        self.totals_amout = 0
        self.mtt_carat24 = 0
        self.mtt_carat = 0
        self._reset()
        self.set_data_for(provid_clt_id=provid_clt_id, search=search)
        self.refresh()
        self.parent.label_cost.setText(
            self.parent.display_remaining(
                self.totals_amout, self.totals_weight, self.totals_base,
                self.mtt_carat, self.mtt_carat24,))
        self.hideColumn(len(self.hheaders) - 1)

    def set_data_for(self, provid_clt_id=None, search=None):
        self.provid_clt_id = provid_clt_id
        qs = Payment.select().where(Payment.deleted == False).where(
            Payment.collect == self.parent.collect).order_by(Payment.date.asc())

        self.remaining = 0
        if isinstance(provid_clt_id, int):
            self.provider_clt = ProviderOrClient.get(id=provid_clt_id)
            qs = qs.select().where(Payment.provider_clt == self.provider_clt)
        else:
            self.provider_clt = "Tous"
            for prov in ProviderOrClient.select().where(
                    ProviderOrClient.type_ == ProviderOrClient.CLT):
                self.remaining += prov.last_remaining()
        # self.parent.label_cost.setText(
        #     self.parent.display_remaining(device_amount(self.remaining)))

        self.data = [(pay.date, pay.libelle, pay.weight, pay.base, pay.carat,
                      pay.carat24(), pay.totals_amout(), pay.id) for pay in qs.iterator()]

    def popup(self, pos):

        # from ui.ligne_edit import EditLigneViewWidget
        from ui.deleteview import DeleteViewWidget
        # from data_helper import check_befor_update_payment

        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        editaction = menu.addAction("Modifier cette ligne")
        delaction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        row = self.selectionModel().selection().indexes()[0].row()
        payment = Payment.get(id=self.data[row][-1])
        print(payment)
        if action == editaction:
            self.parent.open_dialog(EditOrAddPaymentrDialog, modal=True,
                                    payment=payment, table_p=self)
        if action == delaction:
            self.parent.open_dialog(DeleteViewWidget, modal=True,
                                    table_p=self, obj=payment, trash=True)

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows + 2, 2, 2, 4)
        self.totals_weight = 0
        self.totals_base = 0
        self.totals_amout = 0
        self.mtt_carat24 = 0
        self.mtt_carat = 0
        cp = 0
        for row_num in range(0, self.data.__len__()):
            mtt_weight = is_float(str(self.item(row_num, 2).text()))
            totals_base = is_float(str(self.item(row_num, 3).text()))
            mtt_carat = is_float(str(self.item(row_num, 4).text()))
            mtt_carat24 = is_float(str(self.item(row_num, 5).text()))
            totals_amout = is_float(str(self.item(row_num, 6).text()))
            self.totals_weight += mtt_weight
            self.totals_base += totals_base
            self.mtt_carat += mtt_carat
            self.mtt_carat24 += mtt_carat24
            self.totals_amout += totals_amout
            cp += 1

        self.setItem(
            nb_rows, 2, TotalsWidget(device_amount(self.totals_weight, dvs="g")))
        # self.setItem(
        #     nb_rows, 3, TotalsWidget(device_amount(self.totals_base, dvs=" ")))
        # self.setItem(
        #     nb_rows, 4, TotalsWidget(device_amount(self.mtt_carat, dvs=" ")))
        self.setItem(
            nb_rows, 5, TotalsWidget(device_amount(self.mtt_carat24, dvs=" ")))
        self.setItem(
            nb_rows, 6, TotalsWidget(device_amount(self.totals_amout, dvs=" ")))
