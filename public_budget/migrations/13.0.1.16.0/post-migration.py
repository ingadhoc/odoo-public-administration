from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'public_budget', 'migrations/13.0.1.16.0/mig_data.xml')
