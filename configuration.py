# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields

__all__ = ['Configuration']


class Configuration:
    __metaclass__ = PoolMeta
    __name__ = 'contract.configuration'
    payment_type = fields.Property(fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            ('kind', '=', 'receivable'),
        ]))
