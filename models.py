#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from peewee import (DateTimeField, CharField, IntegerField, FloatField,
                    BooleanField, ForeignKeyField, TextField)
from Common.models import (BaseModel, SettingsAdmin, Version, FileJoin,
                           Organization, Owner)

FDATE = u"%c"
NOW = datetime.now()


class ProviderOrClient(BaseModel):

    """ Represents the company emmiting the invoices
    """
    # class Meta:
    #     order_by = ('name',)

    CLT = 'Client'
    FSEUR = 'Fournisseur'
    TYPES = [CLT, FSEUR]

    name = CharField(unique=True, verbose_name=("Nom de votre entreprise"))
    address = TextField(
        null=True, verbose_name=("Adresse principale de votre société"))
    phone = CharField(
        verbose_name=("Numero de téléphone de votre entreprise"), default="")
    email = CharField(
        null=True, verbose_name=("Adresse électronique de votre entreprise"))
    legal_infos = TextField(
        null=True, verbose_name=("Informations légales"))
    type_ = CharField(max_length=30, choices=TYPES, default=CLT)
    picture = ForeignKeyField(
        FileJoin, null=True, related_name='file_joins_pictures',
        verbose_name=("image de la societe"))

    def invoices(self):
        return Invoice.select().where(Invoice.client == self)

    def buys(self):
        return Buy.select().where(Buy.provd_or_clt == self)

    def invoices_items(self):
        return Report.select().where(Report.type_ == Report.S,
                                     Report.invoice.client == self)

    def is_indebted(self):
        flag = False
        if self.last_remaining() > 0:
            flag = True
        return flag

    def last_refund(self):
        try:
            return Refund.select().where(Refund.provider_client == self).order_by(
                Refund.date.desc()).get()
        except Exception as e:
            return None

    def last_remaining(self):
        last_r = self.last_refund()
        return last_r.remaining if last_r else 0

    def __str__(self):
        return u"{}, {}".format(self.name, self.phone)

    def __unicode__(self):
        return self.__str__()

    @classmethod
    def get_or_create(cls, name, phone, typ):
        try:
            ctct = cls.get(name=name, phone=phone, type_=typ)
        except cls.DoesNotExist:
            ctct = cls.create(name=name, phone=phone, type_=typ)
        return ctct


class Collect(BaseModel):

    created_date = DateTimeField(verbose_name=("Date"), default=NOW)
    end_collect_date = DateTimeField(verbose_name=(
        "Date de Modification"), null=True)
    name = CharField(max_length=100, unique=True)
    deleted = BooleanField(default=False)
    is_end = BooleanField(default=False)
    totals_weight = FloatField(verbose_name=("Poids (g)"), default=0)
    totals_base = FloatField(verbose_name=("prix d'achat"), default=0)
    totals_cost = FloatField(verbose_name=("Solde"), default=0)

    def __unicode__(self):
        return "Collect {}".format(self.name)

    def end_collect(self):
        if is_end:
            self.end_collect_date = NOW

    def display_name(self):
        return self.__unicode__()


class Payment(BaseModel):

    """ docstring for Payment """

    class Meta:
        order_by = ('date',)

    collect = ForeignKeyField(Collect, verbose_name=("Utilisateur"))
    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    provider_clt = ForeignKeyField(ProviderOrClient)
    date = DateTimeField(verbose_name=("Date"))
    created_date = DateTimeField(verbose_name=("Date"), default=NOW)
    weight = FloatField(verbose_name=("Poids (g)"))  # en gramme
    base = FloatField(verbose_name=("prix d'achat"))
    carat = FloatField(verbose_name=("Carat"))
    libelle = CharField(verbose_name=("note"), null=True)
    cost = FloatField(verbose_name=("Solde"))
    deleted = BooleanField(default=False)

    def __unicode__(self):
        return "{date} / {lib}/ {weight}/ {base} / {cost} Fcfa".format(
            date=self.date.strftime(FDATE), weight=self.weight, cost=self.cost,
            base=self.base, lib=self.libelle)

    def __str__(self):
        return self.__unicode__()

    def display_name(self):
        return self.__unicode__()

    def save(self):
        """
        Calcul du cost en stock après une operation."""
        self.owner = Owner.get(Owner.islog == True)
        self.cost = float(self.weight) * float(self.base)

        super(Payment, self).save()

    def carat24(self):
        return (self.carat * self.weight) / 24

    def totals_amout(self):
        return self.base * self.carat24()

    def deletes_data(self):
        self.delete_instance()

    def restore(self):
        pass
