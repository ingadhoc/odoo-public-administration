from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    locations = env['public_budget.location'].search([])
    locations.write({'expedient_management': True})
