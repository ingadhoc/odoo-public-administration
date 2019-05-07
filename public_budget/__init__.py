from . import controllers
from . import models
from . import wizards
from . import reports
from odoo import fields
from odoo.addons.account_payment_group.models.account_payment_group import \
    AccountPaymentGroup



def payment_date_default():
    """ monkey patch: importante, si se entra a una base que tenga este modulo
    instalado, el patch ya se aplica y afecta otras bases de datos en misma
    instancia, es un problema en desarrollo local nada mas
    TODO ver que en v12 tal vez no haga falta el monkey patch o el hook
    """

    new_payment_date = fields.Date(
        string='Payment Date',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True,
    )

    AccountPaymentGroup.payment_date = new_payment_date
