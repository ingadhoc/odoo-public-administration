##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Public Budget Subscription",
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': 'Contract Purchase, Invoicing',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'public_budget',
        'purchase_contract',
    ],
    'data': [
        'views/purchase_subscription_views.xml',
        'data/ir_actions_server_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
