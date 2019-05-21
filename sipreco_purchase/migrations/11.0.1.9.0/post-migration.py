from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        'Update action_aeroo_purchase_requisition_report to noupdate=True')
    imd = env['ir.model.data'].search([
        ('module', '=', 'sipreco_purchase'),
        ('name', '=', 'action_aeroo_purchase_requisition_report'),
    ], limit=1)
    imd.write({'noupdate': True})
