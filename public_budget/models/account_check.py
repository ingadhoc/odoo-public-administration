# -*- coding: utf-8 -*-
from openerp import models
# from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountCheck(models.Model):
    """
    Ellos debitan directamente del banco y querían un estado adicional para
    referirse a la entrega del cheque, entonces directamente usamos esta logica
    * Entregado --> es cuando esta en mesa de entrada
    * Debitado --> es entregado, ya consideran que salió del banco
    """

    _inherit = 'account.check'
