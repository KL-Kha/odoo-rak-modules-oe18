# -*- coding: utf-8 -*-
{
	'name': 'Import Chart of Accounts from CSV or Excel File',	
	'version': '18.0.0.0',
	'category': 'Accounting',
	'summary': 'This apps helps to import chart of accounts using CSV or Excel file',
	'description': '''Using this module Charts os accounts is imported using excel sheets
	import accounts using csv 
	import accounts using xls
	import accounts using excel
	import Chart of account using csv 
	import Chart of account using xls
	import chart of accounts using excel
	import COA using csv 
	import COA using xls
	import COA using excel
	''',
	'author': 'BROWSEINFO',
	'website': 'https://www.browseinfo.com/demo-request?app=bi_import_chart_of_accounts&version=18&edition=Community',
	'depends': ['base','account'],
	'license': 'OPL-1',
	'data': [
		'security/ir.model.access.csv',
		'wizard/view_import_chart.xml',
		],
	'auto_install': False,
	'installable': True,
	'live_test_url'	:'https://www.browseinfo.com/demo-request?app=bi_import_chart_of_accounts&version=18&edition=Community',
    	'application': True,
    	'qweb': [
    		],
   	"images":['static/description/Banner.gif']
}

