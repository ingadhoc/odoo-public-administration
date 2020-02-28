from odoo import models, fields, api


class PublicBudgetTransferAssetWizard(models.TransientModel):
    _name = "public_budget.transfer.asset.wizard"

    location_id = fields.Many2one(
        'public_budget.location',
        required=True,
        string='Location Destiny',
        domain="[('asset_management', '=', True)]",
    )

    def confirm(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        if active_id:
            asset = self.env['account.asset.asset'].browse(
                active_id)
            asset.location_id = self.location_id
            asset.transit = True
        return True
