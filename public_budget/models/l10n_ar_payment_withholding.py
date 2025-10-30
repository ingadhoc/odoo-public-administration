from odoo import _, models
from odoo.exceptions import ValidationError

class l10nArPaymentWithholding(models.Model):
    _inherit = "l10n_ar.payment.withholding"

    def change_withholding(self):
        """ Arrojamos este error para recordarnos que este metodo se implementa
        en realidad en public_budget_tax_settlement porque necesitamos del
        liquidador para marcar liquidada la devolución
        """
        raise ValidationError(_('No implementado todavía'))
