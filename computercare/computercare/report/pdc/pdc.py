# Copyright (c) 2013, Tristar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from frappe.utils import (flt, cstr, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate, nowdate, now)
from erpnext.accounts.utils import get_fiscal_year
import datetime


def execute(filters=None):
	columns = get_pdc_columns(filters)
	data = get_pdc_data(filters, columns)
	#~ data = add_total_row(data, columns)
	return columns, data

def get_condition(filters):
	#if filters.company:
	condition = " where pe.company = '%s'  "%(filters.company)
	if filters.enquiry_type == "PDC":
		condition += " AND pe.reference_date > pe.posting_date AND pe.docstatus = 0	"
	elif filters.enquiry_type == "Cleared":
		condition += " AND pe.docstatus = 1  "
	elif filters.enquiry_type == "All":
		condition += " AND ( pe.docstatus = 1 OR pe.docstatus = 0 ) "
	if filters.from_date<=filters.to_date:
		if filters.from_date:
			condition += " AND pe.posting_date >= '%s' "%(filters.from_date)
		if filters.to_date:
			condition += " AND pe.posting_date <= '%s' "%(filters.to_date)
	elif filters.from_date>filters.to_date:
		frappe.msgprint(" To Date Should be Greater than From Date")
	if filters.payment_type:
		condition += " AND pe.payment_type = '%s' "%(filters.payment_type)
	if filters.party_type:
		condition += " AND pe.party_type = '%s' "%(filters.party_type)
	if filters.party:
		condition += " AND pe.party = '%s' "%(filters.party)
	if filters.cost_center:
		condition += " AND pe.cost_center = '%s' "%(filters.cost_center)
	return condition

def get_pdc_data(filters, columns):
	condition = get_condition(filters)
	query = """ Select pe.name as voucher_number,
			pe.posting_date,
			pe.payment_type,
			pe.mode_of_payment,
			pe.party_type, pe.party, pe.party_name,
			pe.paid_from, pe.paid_from_account_currency,
			pe.paid_to, pe.paid_to_account_currency,
			pe.paid_amount,pe.source_exchange_rate,
			pe.received_amount, pe.target_exchange_rate,
			pe.reference_no,
			pe.reference_date,
			pe.clearance_date,
			pe.cost_center,
			pe.remarks
			from `tabPayment Entry` as pe			
  		{condition};""".format(condition=condition)
	return  frappe.db.sql(query, as_dict=1)

def get_pdc_columns(filters):
	columns = [
			{"fieldname":"posting_date","label": _("Posting Date"),"fieldtype": "Date",	"width": 100},
			{"fieldname":"voucher_number","label": _("Payment Entry"), "fieldtype": "Link", "options":"Payment Entry","width": 100},
			{"fieldname": "reference_no","label": _("Cheque/Reference No"),"fieldtype": "Data","width": 100},
			{"fieldname": "reference_date","label": _("Cheque/Reference Date"),"fieldtype": "Date","width": 100},
			{"fieldname": "party_type","label": _("Party Type"),"fieldtype": "Data","width": 100},
			{"fieldname": "payment_type","label": _("Payment Type"),"fieldtype": "Data","width": 100},
			{"fieldname": "party","label": _("Party"),"fieldtype": "Data","width": 100},
			{"fieldname": "paid_from","label": _("Paid From"),"fieldtype": "Data","width": 100},
			{"fieldname": "paid_amount","label": _("Paid Amount"),"fieldtype": "Currency","width": 100},			
			{"fieldname": "paid_to","label": _("Paid To"),"fieldtype": "Data","width": 100},
			{"fieldname": "received_amount","label": _("Received Amount"),"fieldtype": "Currency","width": 100},
			{"fieldname": "clearance_date","label": _("Clearance Date"),"fieldtype": "Date","width": 100},
			{"fieldname":"cost_center","label": _("Cost Center"), "fieldtype": "Link", "options":"Cost Center","width": 100},
			
	]

	return columns

def add_total_row(result, columns):
	total_row = [""]*len(columns)
	for row in result:
		i=0
		for col in range(0,len(columns)):
			fieldname = columns[i]["fieldname"]
			fieldvalue= row[fieldname]
			if columns[i]["fieldtype"] == "Currency" :
				
				total_row[i] = flt(total_row[i]) + flt(fieldvalue)
			
			i = i + 1

	

	first_col_fieldtype = None
	if isinstance(columns[0], basestring):
		first_col = columns[0].split(":")
		if len(first_col) > 1:
			first_col_fieldtype = first_col[1].split("/")[0]
	else:
		first_col_fieldtype = columns[0].get("fieldtype")

	if first_col_fieldtype not in ["Currency", "Int", "Float", "Percent"]:
		if first_col_fieldtype == "Link":
			total_row[0] = "'" + _("Total") + "'"
		else:
			total_row[5] = _("Total")

	result.append(total_row)
	return result
