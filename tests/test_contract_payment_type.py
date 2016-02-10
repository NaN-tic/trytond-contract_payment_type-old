# This file is part of the contract_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite
import unittest


class ContractPaymentTypeTestCase(ModuleTestCase):
    'Test Contract Payment Type module'
    module = 'contract_payment_type'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            ContractPaymentTypeTestCase))
    return suite
