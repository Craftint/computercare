# Copyright (c) 2013, Tristar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


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

	if filters.get("voucher_no") and filters.get("group_by_voucher"):
		frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))


def set_party_currency(filters):
	filters["party_currency"] = frappe.db.get_value(filters.party_type, filters.party, "default_currency")

	return filters


def get_columns(filters):
	
	columns = [
		{"label": ("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 50},
		{"label": ("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 100},
		{"label": ("Debit"), "fieldname": "debit", "fieldtype": "Currency", "width": 90},
		{"label": ("Credit"), "fieldname": "credit", "fieldtype": "Currency", "width": 90},
		{"label": ("Balance"), "fieldname": "balance", "fieldtype": "Currency", "width": 90},
		{"label": ("Voucher Type"), "fieldname": "voucher_type", "width": 100},
		{"label": ("Voucher No"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 120},
		#~ {"label": ("Voucher No"), "fieldname": "Voucher_no", "width": 120},
		{"label": ("Against Account"), "fieldname": "against_account", "width": 120},
		{"label": ("Remarks"), "fieldname": "remarks", "width": 120},
		
	]

	return columns

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	return gl_entries

def get_gl_entries(filters):

	frm_date = filters.get('from_date')
	to_date = filters.get('to_date')
	
	exchange_rate = frappe.db.sql(""" select exchange_rate from `tabCurrency Exchange` 
						where name = 'USD-AED'""")

	query = """select 	gl.posting_date as posting_date, 
						accn.account_name as account,
						gl.debit as debit, 
						gl.credit as credit,
						gl.voucher_type,
						gl.voucher_no,
						gl.against, 
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
		query += """ and accn.name in (SELECT name FROM `tabAccount` where name like 'Output Tax%' or name like 'Input Tax%') """

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
	#~ for j in glentries:		
		#~ if j[2] != 'AED':
			#~ j[5] = j[5] * exchange_rate[0][0]
			#~ j[6] = j[6] * exchange_rate[0][0]
	
	for i in glentries:
		if balances != 0:
			finalbalance += float(i[2]-i[3])
			i = i[:4] + [round(finalbalance,3)] + i[4:] 
		else:
			balances += float(i[2]-i[3])
			finalbalance = balances
			i = i[:4] + [round(finalbalance,3)] + i[4:]
		entries.append(i)
	
	return entries
