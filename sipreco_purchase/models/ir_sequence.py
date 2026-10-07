##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def next_by_code(self, sequence_code, sequence_date=None):
        # Las solicitudes de compra de sipreco numeran con la secuencia
        # histórica (SC), no con la de plantillas que trae el core desde la 18
        if sequence_code == 'purchase.requisition.purchase.template':
            sequence_code = 'purchase.requisition.purchase.tender'
        return super().next_by_code(sequence_code, sequence_date=sequence_date)
