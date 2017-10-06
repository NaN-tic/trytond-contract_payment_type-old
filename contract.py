# This file is part of the contract_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, Bool

__all__ = ['Contract', 'ContractConsumption']


class Contract:
    __metaclass__ = PoolMeta
    __name__ = 'contract'
    company_party = fields.Function(fields.Many2One('party.party',
        'Company Party'), 'get_company_party')
    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', domain=[
            ('kind', '=', 'receivable'),
        ])
    receivable_bank_account = fields.Many2One('bank.account',
        'Receivable Bank Account', domain=[
            ('owners', '=', Eval('party')),
        ], states={
            'invisible': ~Bool(Eval('payment_type')),
        }, depends=['payment_type', 'party'],
        help='Party bank account')
    company_bank_account = fields.Many2One('bank.account',
        'Company Bank Account',
        domain=[
            ('owners', '=', Eval('company_party')),
        ], states={
            'invisible': ~Bool(Eval('payment_type')),
        }, depends=['company_party', 'payment_type'],
        help='Default party payable bank account')

    @staticmethod
    def default_payment_type():
        Config = Pool().get('contract.configuration')
        config = Config(1)
        return config.payment_type.id if config.payment_type else None

    def get_company_party(self, name=None):
        return self.company.party.id if self.company else None


class ContractConsumption:
    __metaclass__ = PoolMeta
    __name__ = 'contract.consumption'

    @classmethod
    def _group_invoice_key(cls, line):
        grouping = super(ContractConsumption, cls)._group_invoice_key(line)

        consumption_id, _ = line
        consumption = cls(consumption_id)
        grouping.append(
            ('payment_type', consumption.contract_line.contract.payment_type))
        return grouping

    @classmethod
    def _invoice(cls, consumptions):
        Invoice = Pool().get('account.invoice')

        invoices = super(ContractConsumption, cls)._invoice(consumptions)

        to_write = []
        for invoice in invoices:
            contract = None
            for line in invoice.lines:
                if line.origin and line.origin.__name__ == 'contract.consumption':
                    contract = line.origin.contract_line.contract
                    break
            if contract:
                payment_type = (contract.payment_type or
                    contract.party.customer_payment_type)
                if payment_type:
                    to_write.extend(([invoice], {'payment_type': payment_type}))

        if to_write:
            Invoice.write(*to_write)

        return invoices
