# -*- coding: utf-8 -*-
{
    'name': "Cheque rechazado",

    'summary': """ Cheque rechazado """,

    'description': """
        Cheque rechazado
    """,

    'author': "Aquih S.A.",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['account'],

    'data': [
        'views/cheque_rechazado_views.xml',
        'security/ir.model.access.csv',
    ],
}
