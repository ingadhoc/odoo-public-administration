from openupgradelib import openupgrade
import logging

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    logger.info('Forzamos la actualizacion de la vista product_views del modulo stock para que no nos de conflicto con la vista product_template_kanban_stock_view')
    openupgrade.load_data(
        env.cr, 'stock', 'views/product_views.xml')
