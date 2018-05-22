# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields

__all__ = ['Configuration', 'ConfigurationAccount']


class Configuration:
    __metaclass__ = PoolMeta
    __name__ = 'contract.configuration'
    payment_type = fields.MultiValue(fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            ('kind', '=', 'receivable'),
        ]))

    @classmethod
    def multivalue_model(cls, field):
        if field == 'payment_type':
            return Pool().get('contract.configuration.account')
        return super(Configuration, cls).multivalue_model(field)


class ConfigurationAccount:
    __metaclass__ = PoolMeta
    __name__ = 'contract.configuration.account'
    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            ('kind', '=', 'receivable'),
        ])

    @classmethod
    def _migrate_property(cls, field_names, value_names, fields):
        super(ConfigurationAccount, cls)._migrate_property(field_names, value_names, fields)
        field_names += ['payment_type']
        value_names += ['payment_type']
        fields.append('company')
        migrate_property(
            'contract.configuration', field_names, cls, value_names,
            fields=fields)
