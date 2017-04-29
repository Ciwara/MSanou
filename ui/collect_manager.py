#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga


from PyQt4.QtGui import (QSplitter, QVBoxLayout,
                         QMenu, QIcon, QGridLayout, QTableWidgetItem)

from datetime import datetime
from PyQt4.QtCore import Qt

from models import Collect

from Common.ui.common import (BttExportXLS, FWidget, Button, LineEdit)
from Common.ui.table import FTableWidget

from configuration import Config

from ui.collect_edit_add import EditOrAddCollectDialog


try:
    unicode
except:
    unicode = str

ALL_CONTACTS = "TOUS"


class CollectViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(CollectViewWidget, self).__init__(parent=parent,
                                                *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(
            Config.NAME_ORGA + u"Gestion des Collectes")

        vbox = QVBoxLayout(self)
        self.now = datetime.now().strftime(Config.DATEFORMAT)

        self.table = RapportTableWidget(parent=self)
        self.button = Button(u"Ok")
        self.button.clicked.connect(self.refresh_period)

        self.btt_export = BttExportXLS(u"Exporter")
        # self.btt_export.clicked.connect(self.export_xls)
        # self.add_btt = Button("Ajout")
        # self.add_btt.setEnabled(False)
        # self.add_btt.clicked.connect(self.add_collect)
        # self.add_btt.setIcon(QIcon(u"{img_media}{img}".format(
        #     img_media=Config.img_media, img="in.png")))
        self.add_btt = Button("Collecte")
        # self.add_btt.setMaximumHeight(10)
        self.add_btt.setIcon(QIcon(u"{img_media}{img}".format(
            img_media=Config.img_media, img="in.png")))

        self.add_btt.setFixedWidth(200)
        self.add_btt.setFixedHeight(50)
        self.add_btt.clicked.connect(self.add_prov_or_clt)

        editbox = QGridLayout()
        editbox.addWidget(self.add_btt, 0, 1)
        # editbox.addWidget(self.btt_export, 1, 7)
        # editbox.setColumnStretch(1, 4)

        self.search_field = LineEdit()
        self.search_field.textChanged.connect(self.search)
        self.search_field.setPlaceholderText(u"Nom ou numéro tel")
        self.search_field.setMaximumHeight(40)
        splitter = QSplitter(Qt.Horizontal)

        self.splt_add = QSplitter(Qt.Horizontal)
        self.splt_add.setLayout(editbox)
        splitter.addWidget(self.table)

        vbox.addWidget(self.splt_add)
        vbox.addWidget(splitter)
        self.setLayout(vbox)

    def refresh_period(self):
        self.table.refresh_()

    def search(self):
        self.table.refresh_(self.search_field.text())

    def add_prov_or_clt(self):
        self.parent.open_dialog(EditOrAddCollectDialog,
                                modal=True, table_p=self.table)

    def add_collect(self):
        self.open_dialog(EditOrAddCollectDialog, modal=True,
                         collect=None, table_p=self.table)


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        # self.hheaders = ["", u"Nom de collecte", u"Date debut", "Date fin",
        # u"Total Poids(g)", u"Pirx du gramme", u"Coût", "Status", ""]
        self.hheaders = ["", u"Nom de collecte",
                         u"Date debut", "Date fin", "Status", ""]
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)
        self.parent = parent
        self.sorter = False
        self.stretch_columns = [0, 1, 2, 3, 4, 5]
        self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'r'}
        self.ecart = -15
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self, search=None):
        """ """

        self.totals_weight = 0
        self.totals_base = 0
        self.totals_cost = 0
        # self.on_date = date_to_datetime(self.parent.on_date_field.text())
        # self.end_date = date_to_datetime(self.parent.end_date_field.text())
        # l_date = [self.on_date, self.end_date]
        self._reset()
        self.set_data_for(search=search)
        self.refresh()
        self.hideColumn(len(self.hheaders) - 1)

    def set_data_for(self, search=None):
        qs = Collect.select().where(Collect.deleted == False).order_by(
            Collect.created_date.asc())
        # self.data = [("", collect.name, collect.created_date, collect.end_collect_date,
        #               collect.totals_weight, collect.totals_base, collect.totals_cost,
        # collect.is_end, collect.id) for collect in qs.iterator()]
        self.data = [("", collect.name, collect.created_date, collect.end_collect_date,
                      "en cours"if not collect.is_end else "finie", collect.id) for collect in qs.iterator()]

    def _item_for_data(self, row, column, data, context=None):

        if column == 0:
            return QTableWidgetItem(
                QIcon(u"{img_media}{img}".format(
                    img_media=Config.img_cmedia, img="find.png")), (u"voir"))
        return super(RapportTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        # last_column = self.hheaders.__len__() - 2
        if column != 0:
            return
        from ui.debt_manager import DebtsViewWidget
        try:
            self.parent.change_main_context(
                DebtsViewWidget, collect=Collect.get(id=self.data[row][-1]))
        except Exception as e:
            print("click_item", self.data[row], e)

    def popup(self, pos):

        # from ui.ligne_edit import EditLigneViewWidget
        from ui.deleteview import DeleteViewWidget

        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        editaction = menu.addAction("Modifier cette ligne")
        delaction = menu.addAction("Supprimer cette ligne")
        end_collect = menu.addAction("Finir la collect")
        action = menu.exec_(self.mapToGlobal(pos))
        row = self.selectionModel().selection().indexes()[0].row()
        collect = Collect.get(id=self.data[row][-1])
        if action == editaction:
            self.parent.open_dialog(EditOrAddCollectDialog, modal=True,
                                    collect=collect, table_p=self)
        if action == end_collect:
            self.parent.open_dialog(EditOrAddCollectDialog, modal=True,
                                    collect=collect, table_p=self, end=True)
        if action == delaction:
            self.parent.open_dialog(DeleteViewWidget, modal=True,
                                    table_p=self, obj=collect, trash=False)

    def extend_rows(self):
        pass
