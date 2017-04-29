#!/usr/bin/env python
# -*- encoding: utf-8
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from models import Payment
from configuration import Config


def check_befor_update_payment(pay):
    cost = pay.cost
    lt = []
    for rpt in pay.next_rpts():
        previous_cost = int(rpt.last_cost_payment())
        if rpt.type_ == Payment.CREDIT:
            cost = previous_cost + int(rpt.credit)
            lt.append(
                "{} = last {} + {}".format(cost, previous_cost, rpt.credit))
        if rpt.type_ == Payment.DEBIT:
            cost = previous_cost - int(rpt.debit)
            lt.append(
                "{} = last {} - {}".format(cost, previous_cost, rpt.debit))
        # if cost < 0:
        #     return False
    return True


def str_to_float(value):

    return float(value.replace(",", ".").replace(
        " ", "").replace('\xa0', ''))
