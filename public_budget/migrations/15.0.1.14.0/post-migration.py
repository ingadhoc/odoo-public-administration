from openupgradelib import openupgrade
import logging

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    logger.info('Corremos el método computado _compute_cover del modelo public_budget.expedient en aquellos registros con fecha de emisión y creados en el año 2024 y con fecha de última modificación el 16-02-2024 (fecha en la cual se introdujo el bug) que tengan registros en el campo "Proveedor/Empleado" (supplier_ids) y el campo "description" coincida con el campo "cover". Esto lo hacemos porque al momento de imprimir el Reporte de expediente en la carátula no sale concatenado el nombre de "Proveedor/Empleado".')
    env['public_budget.expedient'].search([('write_date', '>=', '2024-02-16'), ('issue_date', '>=', '2024-01-01'), ('create_date', '>=', '2024-01-01')]).filtered(lambda x: x.description and x.supplier_ids and x.description == x.cover)._compute_cover()
