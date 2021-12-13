# -*- coding: utf-8 -*-

{
    'name': "Approvals Statement",
    'version': '1.0',
    'depends': ['base', 'hr_contract', 'account_accountant'],
    
    'author': "Sebastien Buhl",
    'website': "http://www.buhl.be",
    'license': 'LGPL-3',

    'application': True,
    'category': 'Category',
    'summary': 'Statements Approvals',
    'description': """
        Add an approval step on the bank statement
    """,
    
    'data': [
        'data/activity.xml',
        'security/account_approval_security.xml',
        'security/ir.model.access.csv',
        'views/account_menuitem_inherited.xml',
        'views/account_approval_request_inherited_tree.xml',
    ],

}
