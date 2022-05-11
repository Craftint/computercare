# Copyright (c) 2013, Tristar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re

def execute(filters=None):
	account_details = {}
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	filters = set_party_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	return columns, res

def validate_filters(filters, account_details):

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))


def set_party_currency(filters):
	filters["party_currency"] = frappe.db.get_value(filters.party_type, filters.party, "default_currency")

	return filters


def get_columns(filters):
	columns = [
		("Outputs") + "::500",
		("Amount (AED)") + ":Float:100", 
		("VAT Amount (AED)") + ":Float:120",
		("Adjustment (AED)") + ":Float:110",
		
	]

	return columns

def get_result(filters, account_details):
	entries = get_vat_entries(filters)

	return entries

def get_vat_entries(filters):

	vat_entries = [
	['Standard rated supplies in Abu Dhabi',0.0,0.0,0.0],
	['Standard rated supplies in Dubai',0.0,0.0,0.0],
	['Standard rated supplies in Sharjah',0.0,0.0,0.0],
	['Standard rated supplies in Ajman',0.0,0.0,0.0],
	['Standard rated supplies in Umm Al Quwain',0.0,0.0,0.0],
	['Standard rated supplies in Ras Al Khaimah',0.0,0.0,0.0],
	['Standard rated supplies in Fujairah',0.0,0.0,0.0],
	['Suppliies subject to the reverse charge provisions',0.0,0.0,0.0],
	['Zero rated supplies',0.0,0.0,0.0],
	['Supplies of goods and services to registered customer in other GCC implementing states',0.0,0.0,0.0],
	['Exempt supplies',0.0,0.0,0.0],
	['Import VAT accounted through UAE customs',0.0,0.0,0.0],
	['Amendments or corrections to Output figures',0.0,0.0,0.0],
	['Totals on Sales and all other Outputs',0.0,0.0,0.0],
	['Standard rated expenses',0.0,0.0,0.0],
	['Supplies subject to the reverse charge provisions',0.0,0.0,0.0],
	['Amendments or corrections to Input figures',0.0,0.0,0.0],
	['Totals on Expenses and all other Inputs',0.0,0.0,0.0],
	['Total value of due tax for the period',0.0,0.0,0.0],
	['Total value of recoverable tax for the period',0.0,0.0,0.0],
	['Net VAT due(or reclaimed) for the period',0.0,0.0,0.0],
	['Imported goods transferred to the Kingdom of Bahrain',0.0,0.0,0.0],
	['Imported goods transferred to the State of Kuwait',0.0,0.0,0.0],
	['Imported goods transferred to the Sultanate of Oman',0.0,0.0,0.0],
	['Imported goods transferred to the State of Qatar',0.0,0.0,0.0],
	['Imported goods transferred to the Kingdom of Saudi Arabia',0.0,0.0,0.0],
	['Goods transported to the Kingdom of Bahrain',0.0,0.0,0.0],
	['Goods transported to the State of Kuwait',0.0,0.0,0.0],
	['Goods transported to the Sultanate of Oman',0.0,0.0,0.0],
	['Goods transported to the State of Qatar',0.0,0.0,0.0],
	['Goods transported to the Kingdom of Saudi Arabia',0.0,0.0,0.0],
	['Recoverable VAT paid in the Kingdom of Bahrain',0.0,0.0,0.0],
	['Recoverable VAT paid in the State of Kuwait',0.0,0.0,0.0],
	['Recoverable VAT paid in the Sultanate of Oman',0.0,0.0,0.0],
	['Recoverable VAT paid in the State of Qatar',0.0,0.0,0.0],
	['Recoverable VAT paid in the Kingdom of Saudi Arabia',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Abu Dhabi',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Dubai',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Sharjah',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Ajman',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Umm Al Quwain',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Ras Al Khaimah',0.0,0.0,0.0],
	['Tax Refunds for Tourists Scheme paid in Fujairah',0.0,0.0,0.0],
	]

	frm_date = filters.get('from_date')
	to_date = filters.get('to_date')
	
	exchange_rate = frappe.db.sql(""" select exchange_rate from `tabCurrency Exchange` 
						where name = 'USD-AED'""")

	query = """select 	gl.posting_date as posting_date, 
						accn.account_name as account,
						comp.default_currency as company_ccy,
						gl.debit as debit, 
						gl.credit as credit,
						gl.debit as debit_aed, 
						gl.credit as credit_aed,
						gl.voucher_type,
						gl.voucher_no,
						gl.against, 
						comp.name as company,
						gl.remarks
						
						from `tabGL Entry` as gl
						inner join `tabCompany` as comp on (comp.name = gl.company)
						inner join `tabAccount` as accn on (accn.name = gl.account)
						left join `tabPurchase Invoice` as pinv on (gl.voucher_type = 'Purchase Invoice' and pinv.name = gl.voucher_no)
						left join `tabJournal Entry` as jrnl on (gl.voucher_type = 'Journal Entry' and jrnl.name = gl.voucher_no)
						where gl.docstatus=1 """

	if filters.get('company'):
		company = filters.get('company')
		query += """ and accn.name in (select name from `tabAccount` 
		where account_type = 'Tax' and company  = '"""+company+"""') """
	else:
		query += """ and accn.name in (SELECT name FROM `tabAccount` where name like '%VAT Output 5%' or name like '%VAT Input 5%') """

	query += """ and gl.posting_date >= '"""+frm_date+"""' and gl.posting_date <= '"""+to_date+"""' """

	if filters.get('voucher_no'):
		voucher_no = filters.get('voucher_no')
		query += """ and gl.voucher_no = '"""+voucher_no+"""'"""	
	gl_entries = frappe.db.sql(query)
	balances = 0
	finalbalance = 0
	entries = []
	glentries = []
	final_entries = ()
	for j in gl_entries:
		glentries.append(list(j))
	for j in glentries:		
		if j[2] != 'AED':
			j[5] = j[5] * exchange_rate[0][0]
			j[6] = j[6] * exchange_rate[0][0]
	
	for i in glentries:
		if balances != 0:
			finalbalance += float(i[5]-i[6])
			i = i[:7] + [round(finalbalance,6)] + i[7:] 
		else:
			balances += float(i[5]-i[6])
			finalbalance = balances
			i = i[:7] + [round(finalbalance,6)] + i[7:]
		entries.append(i)

	### Standard Rated Supplies	###

	#### Dubai ####
			
	std_supplies_dubai = 0.00
	debit = 0.00
	credit = 0.00
	pattern = re.compile(r'^Sales Invoice')

	for i in entries:
		if pattern.match(i[8]):
			net_total = frappe.db.get_value("Sales Invoice", i[9], "net_total")
			std_supplies_dubai += net_total
			debit += i[3]
			credit += i[4]
	
	sales_vat_total = credit - debit
	vat_entries[1][1] = (std_supplies_dubai)
	vat_entries[1][2] = (sales_vat_total)

	### Total Standard Rated Supplies	###
	vat_entries[13][1] = (std_supplies_dubai)
	vat_entries[13][2] = (sales_vat_total)

	### Standard Rated Expenses	###

	std_expenses_tax = 0.00
	
	pattern = re.compile(r'^Purchase Invoice')
	debit = 0.00
	credit = 0.00
	for i in entries:
		if pattern.match(i[8]):
			net_total = frappe.db.get_value("Purchase Invoice", i[9], "net_total")
			std_expenses_tax += net_total
			debit += i[3]
			credit += i[4]
			
	purchase_vat_total = debit - credit
	vat_entries[14][1] = (std_expenses_tax)
	vat_entries[14][2] = (purchase_vat_total)

	### Totals on Sales and all other Outputs ###
	vat_entries[17][1] = (std_expenses_tax)
	vat_entries[17][2] = (purchase_vat_total)

	### Total value of due tax for the period ###
	vat_entries[18][1] = (sales_vat_total)

	### Total value of recoverable tax for the period ###
	vat_entries[19][1] = (purchase_vat_total)

	### Net VAT due(or reclaimed) for the period ###
	
	vat_entries[20][1] = (sales_vat_total - purchase_vat_total)
	
	
	return vat_entries
