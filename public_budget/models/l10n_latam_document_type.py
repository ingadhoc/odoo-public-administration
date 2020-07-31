from odoo import models


class L10nLatamDocumentType(models.Model):

    _inherit = 'l10n_latam.document.type'


    def _format_document_number(self, document_number):
        """ We consider that validation not apply to recipts
        """
        if self._context.get('is_recipt', False):
            return document_number
        return super()._format_document_number(document_number)
