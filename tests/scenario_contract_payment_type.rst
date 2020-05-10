==============================
Contract Payment Type Scenario
==============================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Install contract_payment_type::

    >>> config = activate_modules('contract_payment_type')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create payment type::

    >>> PaymentType = Model.get('account.payment.type')
    >>> payment_type = PaymentType()
    >>> payment_type.name = 'Payment Type'
    >>> payment_type.kind = 'receivable'
    >>> payment_type.save()

Create parties::

    >>> Party = Model.get('party.party')
    >>> customer1 = Party(name='Customer 1')
    >>> customer1.customer_payment_term = payment_term
    >>> customer1.save()
    >>> customer2 = Party(name='Customer 2')
    >>> customer2.customer_payment_term = payment_term
    >>> customer2.contract_grouping_method = 'contract'
    >>> customer2.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create account category::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = accounts['expense']
    >>> account_category.account_revenue = accounts['revenue']
    >>> account_category.customer_taxes.append(tax)
    >>> account_category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')

    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'service'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('30')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_category = account_category
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Contract configuration::

    >>> Journal = Model.get('account.journal')
    >>> journal_revenue, = Journal.find([('type', '=', 'revenue')])

    >>> Config = Model.get('contract.configuration')
    >>> config = Config(1)
    >>> config.journal = journal_revenue
    >>> config.save()

Contract service::

    >>> ContractService = Model.get('contract.service')
    >>> contract_service = ContractService()
    >>> contract_service.name = 'service'
    >>> contract_service.product = product
    >>> contract_service.save()

Contracts monthly::

    >>> Contract = Model.get('contract')
    >>> ContractLine = Model.get('contract.line')
    >>> for customer in [customer1, customer2]:
    ...     contract = Contract()
    ...     contract.party = customer
    ...     contract.freq = 'monthly'
    ...     contract.interval = 1
    ...     contract.start_period_date = today
    ...     contract.first_invoice_date = today
    ...     contract.payment_type = payment_type
    ...     contract_line = ContractLine()
    ...     contract.lines.append(contract_line)
    ...     contract_line.service = contract_service
    ...     contract_line.start_date = today
    ...     contract.save()
    >>> contract1, contract2 = Contract.find([])
    >>> contract1.click('confirm')
    >>> contract1.state
    'confirmed'
    >>> contract2.click('confirm')
    >>> contract1.state
    'confirmed'

Create consumptions::

    >>> ContractConsumption = Model.get('contract.consumption')
    >>> Wizard('contract.create_consumptions').execute('create_consumptions')
    >>> consumptions = ContractConsumption.find([])
    >>> len(consumptions)
    2

Create Invoices::

    >>> Invoice = Model.get('account.invoice')
    >>> Wizard('contract.create_invoices').execute('create_invoices')
    >>> invoice1, invoice2 = Invoice.find([])
    >>> invoice1.party.id
    3
    >>> invoice1.payment_type.name
    'Payment Type'
    >>> invoice2.party.id
    2
    >>> invoice2.payment_type.name
    'Payment Type'
