import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # Keep the old database templates (not deleted) but hide them from the
    # print menu, now that the module ships the comparison report. Matched by
    # report_name because the translated name does not match in en_US.
    old_reports = env['ir.actions.report'].search([
        ('model', '=', 'purchase.requisition'),
        ('report_type', '=', 'aeroo'),
        ('tml_source', '=', 'database'),
        ('report_name', '=', 'purchase_requisition_comparative_report'),
    ])
    old_reports.unlink_action()
    _logger.info('Unbound old price comparison reports: %s', old_reports.ids)
