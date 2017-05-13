# -*- coding: utf-8 -*-
from openerp import fields, models
# from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountCheck(models.Model):
    """
    Ellos debitan directamente del banco y querían un estado adicional para
    referirse a la entrega del cheque, entonces directamente renombramos
    estados:
    * Entregado --> A ser entregado
    * Debitado --> Entregado
    """

    _inherit = 'account.check'

    # cambiamos la descripción de handed y debited.
    state = fields.Selection([
        ('draft', 'Draft'),
        ('holding', 'Holding'),
        ('deposited', 'Deposited'),
        ('selled', 'Selled'),
        ('delivered', 'Delivered'),
        ('transfered', 'Transfered'),
        ('reclaimed', 'Reclaimed'),
        ('withdrawed', 'Withdrawed'),
        ('handed', 'A ser entregado'),
        ('rejected', 'Rejected'),
        ('debited', 'Entregado'),
        ('returned', 'Returned'),
        ('changed', 'Changed'),
        ('cancel', 'Cancel'),
    ],)


class AccountCheckOperation(models.Model):

    _inherit = 'account.check.operation'

    # cambiamos la descripción de handed y debited
    operation = fields.Selection([
        # from payments
        ('holding', 'Receive'),
        ('deposited', 'Deposit'),
        ('selled', 'Sell'),
        ('delivered', 'Deliver'),
        # usado para hacer transferencias internas, es lo mismo que delivered
        # (endosado) pero no queremos confundir con terminos, a la larga lo
        # volvemos a poner en holding
        ('transfered', 'Transfer'),
        ('handed', 'A ser entregado'),
        ('withdrawed', 'Withdrawal'),
        # from checks
        ('reclaimed', 'Claim'),
        ('rejected', 'Rejection'),
        ('debited', 'Entregado'),
        ('returned', 'Return'),
        ('changed', 'Change'),
        ('cancel', 'Cancel'),
    ],)
