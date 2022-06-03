# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
from computercare.utils import get_user_permissions_for

def execute(filters=None):
	return _execute(filters)

def _execute(filters, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = frappe._dict({})

	invoice_list = get_invoices(filters, additional_query_columns)
	columns, income_accounts, tax_accounts = get_columns(invoice_list, additional_table_columns)

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	invoice_income_map = get_invoice_income_map(invoice_list)
	invoice_income_map, invoice_tax_map = get_invoice_tax_map(invoice_list,
		invoice_income_map, income_accounts)
	#Cost Center & Warehouse Map
	invoice_cc_wh_map = get_invoice_cc_wh_map(invoice_list)
	invoice_so_dn_map = get_invoice_so_dn_map(invoice_list)
	mode_of_payments = get_mode_of_payments([inv.name for inv in invoice_list])

	data = []
	for inv in invoice_list:
		# invoice details
		sales_order = list(set(invoice_so_dn_map.get(inv.name, {}).get("sales_order", [])))
		delivery_note = list(set(invoice_so_dn_map.get(inv.name, {}).get("delivery_note", [])))
		cost_center = list(set(invoice_cc_wh_map.get(inv.name, {}).get("cost_center", [])))
		warehouse = list(set(invoice_cc_wh_map.get(inv.name, {}).get("warehouse", [])))

		row = [
			inv.name, inv.posting_date, inv.customer,
		]
		credit= None
		if inv.mode_of_payment == "Credit":
			credit=inv.base_grand_total
		
		if additional_query_columns:
			for col in additional_query_columns:
				row.append(inv.get(col))

		row +=[	credit,
				inv.cash,
				inv.credit_card,
				inv.cheque,
				inv.payfort,
				inv.amex,			
				inv.bank_transfer,
				inv.base_grand_total,
				", ".join(cost_center),
				inv.sales_person,
			]
		data.append(row)

	return columns, data

def get_columns(invoice_list, additional_table_columns):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Sales Invoice:120", _("Posting Date") + ":Date:80",
		_("Customer") + ":Link/Customer:120",
	]

	if additional_table_columns:
		columns += additional_table_columns

	columns +=[
		_("CREDIT") + ":Currency/currency:120",
		_("Cash") + ":Currency/currency:120",
		_("Credit Card") + ":Currency/currency:120",
		_("Cheque") + ":Currency/currency:120",
		_("Payfort") + ":Currency/currency:120",
		_("Amex") + ":Currency/currency:120",
		_("Bank Transfer") + ":Currency/currency:120",
		_("Grand Total") + ":Currency/currency:120",
		_("Cost Center") + ":Link/Cost Center:100",
		_("Sales Person") + ":Link/Cost Center:100",
	]

	income_accounts = tax_accounts = income_columns = tax_columns = []

	if invoice_list:
		income_accounts = frappe.db.sql_list("""select distinct income_account
			from `tabSales Invoice Item` where docstatus = 1 and parent in (%s)
			order by income_account""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

		tax_accounts = 	frappe.db.sql_list("""select distinct account_head
			from `tabSales Taxes and Charges` where parenttype = 'Sales Invoice'
			and docstatus = 1 and base_tax_amount_after_discount_amount != 0
			and parent in (%s) order by account_head""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list])) 

	return columns, income_accounts, tax_accounts

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company='%s'"%(filters.company)
	if filters.get("customer"): conditions += " and customer = '%s'"%(filters.company)

	if filters.get("from_date"): conditions += " and posting_date >= '%s'"%(filters.from_date)
	if filters.get("to_date"): conditions += " and posting_date <= '%s'"%(filters.to_date)

	if filters.get("owner"): conditions += " and st.sales_person = '%s'"%(filters.sales_person)

	if filters.get("mode_of_payment"):
		conditions += """ and exists(select name from `tabSales Invoice Payment`
			 where parent=`tabSales Invoice`.name
			 	and ifnull(`tabSales Invoice Payment`.mode_of_payment, '') = '%s')"""%(filters.mode_of_payment)

	if filters.get("cost_center"):
		conditions +=  " and s.cost_center = '%s'"%(filters.cost_center)
		
	else:
		costcenter_list = get_costcenter_list(filters)
		cost_center = []
		for i in costcenter_list:
			cost_center.append(i.get("name"))
		cost_center = tuple(cost_center)
		if len(costcenter_list) == 1:
			for i in costcenter_list:
				conditions +=  " and s.cost_center = '%s'"%(str(i.get("name")))
		else:
			conditions +=  " and s.cost_center in "+ str(cost_center)

	if filters.get("warehouse"):
		conditions +=  " and s.warehouse = %s"%(filters.warehouse)

	if filters.get("brand"):
		conditions +=  " and s.brand = '%s'"%(filters.brand)
	
	if filters.get("item_group"):
		conditions +=  " and s.item_group = '%s'"%(filters.item_group)

	return conditions

def get_invoices(filters, additional_query_columns):
	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	conditions = get_conditions(filters)
	return frappe.db.sql("""
		select s.name, s.posting_date, s.debit_to, s.project, s.customer, 
		s.customer_name, s.owner, s.remarks, s.territory, s.cost_center,
        s.tax_id, s.customer_group,s.mode_of_payment,
        
        (select p.base_amount from `tabSales Invoice Payment` p
        where p.mode_of_payment = 'Cheque' and p.parent = s.name ) as cheque,
        (select p.base_amount from `tabSales Invoice Payment` p
        where p.mode_of_payment = 'Payfort' and p.parent = s.name ) as payfort,
        (select p.base_amount from `tabSales Invoice Payment` p
        where p.mode_of_payment = 'Amex' and p.parent = s.name ) as amex,
        (select p.base_amount from `tabSales Invoice Payment` p
        where p.mode_of_payment = 'Cash' and p.parent = s.name ) as cash,
        (select p.base_amount from `tabSales Invoice Payment` p
        where p.mode_of_payment = 'Credit Card' and p.parent = s.name ) as credit_card,
        (select p.base_amount from `tabSales Invoice Payment` p
        where p.mode_of_payment = 'Bank Transfer' and p.parent = s.name ) as bank_transfer,
        
		s.base_net_total, s.base_grand_total, s.outstanding_amount, st.sales_person as sales_person
		from `tabSales Invoice` s
        LEFT OUTER join `tabSales Team` as st on (st.parent = s.name)
		where s.docstatus = 1 %s order by posting_date asc, name asc""".format(additional_query_columns or '') %
		conditions, filters, as_dict=1)
		
def get_invoice_income_map(invoice_list):
	income_details = frappe.db.sql("""select parent, income_account, sum(base_net_amount) as amount
		from `tabSales Invoice Item` where parent in (%s) group by parent, income_account""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_income_map = {}
	for d in income_details:
		invoice_income_map.setdefault(d.parent, frappe._dict()).setdefault(d.income_account, [])
		invoice_income_map[d.parent][d.income_account] = flt(d.amount)

	return invoice_income_map

def get_invoice_tax_map(invoice_list, invoice_income_map, income_accounts):
	tax_details = frappe.db.sql("""select parent, account_head,
		sum(base_tax_amount_after_discount_amount) as tax_amount
		from `tabSales Taxes and Charges` where parent in (%s) group by parent, account_head""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_tax_map = {}
	for d in tax_details:
		if d.account_head in income_accounts:
			if d.account_head in invoice_income_map[d.parent]:
				invoice_income_map[d.parent][d.account_head] += flt(d.tax_amount)
			else:
				invoice_income_map[d.parent][d.account_head] = flt(d.tax_amount)
		else:
			invoice_tax_map.setdefault(d.parent, frappe._dict()).setdefault(d.account_head, [])
			invoice_tax_map[d.parent][d.account_head] = flt(d.tax_amount)

	return invoice_income_map, invoice_tax_map

def get_invoice_so_dn_map(invoice_list):
	si_items = frappe.db.sql("""select parent, sales_order, delivery_note, so_detail
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(sales_order, '') != '' or ifnull(delivery_note, '') != '')""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_so_dn_map = {}
	for d in si_items:
		if d.sales_order:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault(
				"sales_order", []).append(d.sales_order)

		delivery_note_list = None
		if d.delivery_note:
			delivery_note_list = [d.delivery_note]
		elif d.sales_order:
			delivery_note_list = frappe.db.sql_list("""select distinct parent from `tabDelivery Note Item`
				where docstatus=1 and so_detail=%s""", d.so_detail)

		if delivery_note_list:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault("delivery_note", delivery_note_list)

	return invoice_so_dn_map

def get_invoice_cc_wh_map(invoice_list):
	si_items = frappe.db.sql("""select parent, cost_center, warehouse
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(cost_center, '') != '' or ifnull(warehouse, '') != '')""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_cc_wh_map = {}
	for d in si_items:
		if d.cost_center:
			invoice_cc_wh_map.setdefault(d.parent, frappe._dict()).setdefault(
				"cost_center", []).append(d.cost_center)

		if d.warehouse:
			invoice_cc_wh_map.setdefault(d.parent, frappe._dict()).setdefault(
				"warehouse", []).append(d.warehouse)

	return invoice_cc_wh_map

def get_mode_of_payments(invoice_list):
	mode_of_payments = {}
	if invoice_list:
		inv_mop = frappe.db.sql("""select parent, mode_of_payment
			from `tabSales Invoice Payment` where parent in (%s) group by parent, mode_of_payment""" %
			', '.join(['%s']*len(invoice_list)), tuple(invoice_list), as_dict=1)

		for d in inv_mop:
			mode_of_payments.setdefault(d.parent, []).append(d.mode_of_payment)

	return mode_of_payments
	
def get_costcenter_list(filters):
	condition = ''
	user_permitted_costcenter = get_user_permissions_for("Cost Center")
	value = ()
	val = []
	if user_permitted_costcenter:
		for i in user_permitted_costcenter:
			if i.get("applicable_for") == "Cost Center":	
				condition = "and name in %s"
				name = i.get("doc").encode("utf-8")
				return frappe.db.sql("""select name, ifnull(abbr, name) as abbr 
		from `tabCost Center` where is_group = 0 and name = '{0}'""".format(name), as_dict=1)
				
	elif not user_permitted_costcenter and filters.get("costcenter"):
		condition = "and name = %s"
		value = filters.get("costcenter")

	return frappe.db.sql("""select name, ifnull(abbr, name) as abbr 
		from `tabCost Center` where is_group = 0
		{condition}""".format(condition=condition), value, as_dict=1)





