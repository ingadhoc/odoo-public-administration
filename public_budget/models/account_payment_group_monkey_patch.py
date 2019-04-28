# forma horrible que encontramos para que el default nativo de este campo
# no se setee al hacer upgra del modulo account_payment_group. Probamos
# haciendo funcion y heredando funcion pero tampoco funcionó
from odoo import fields
from odoo.addons.account_payment_group.models.account_payment_group import \
    AccountPaymentGroup


new_payment_date = fields.Date(
    string='Payment Date',
    required=True,
    copy=False,
    readonly=True,
    states={'draft': [('readonly', False)]},
    index=True,
)


AccountPaymentGroup.payment_date = new_payment_date
