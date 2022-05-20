# Copyright (c) 2013, Tristar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate
from computercare.computercare.report.profit_and_loss_statement_cost_center_wise.financial_statements_hg import (get_period_list, get_columns, get_data)

profit_and_loss_statement = [ 
	{"op": "get_data", "parent_account": "Revenue", "root_type": "Income", "balance_must_be": "Credit"},
	{"op": "get_data", "parent_account": "Cost Of Sales", "root_type": "Expense", "balance_must_be": "Debit"},
	{"op": "gross_profit_loss", "parent_account": "Gross Profit"},
	{"op": "get_data", "parent_account": "Administrative, Selling and General Expenses", "root_type": "Expense", "balance_must_be": "Debit"},
	{"op": "get_data", "parent_account": "Finance Cost", "root_type": "Expense", "balance_must_be": "Debit"},
	{"op": "get_data", "parent_account": "Other Income", "root_type": "Income", "balance_must_be": "Credit"},
	{"op": "net_profit_loss", "parent_account": "Net Profit"},

]

def execute(filters=None):
	period_list = get_period_list(filters)
	for period in period_list:
		period.update({
				"from_date": getdate(filters.from_date),
				"to_date": getdate(filters.to_date),
				"option": filters.option

		})

	data = get_pnl_data(period_list, filters)

	if not filters.with_details:
		data = []
		for s in profit_and_loss_statement:
			summary_data = get_pnl_summary_data(s["parent_account"])
			if summary_data and summary_data[0]:
				data.extend(summary_data)
				add_blank_row(data)

	columns = get_columns(period_list, filters.company)
	print ('columns',columns ) 
	for i in columns:
		#~ if i['fieldname'] == 'COMPUTER CARE - CARE':
			#~ i['label'] = 'COMPUTER CARE - CARE'
		if i['fieldname'] == 'Computer Care Branch - CCG':
			i['label'] = 'Computer Care Branch - CCG'
		if i['fieldname'] == 'Mobimetix - CCG':
			i['label'] = 'Mobimetix - CCG'
		if i['fieldname'] == 'COMPUTER CARE GROUP - CCG':
			i['label'] = 'COMPUTER CARE GROUP - CCG'
		if i['fieldname'] == 'Computer Circles - CCG':
			i['label'] = 'Computer Circles - CCG'
		if i['fieldname'] == 'EBU - CC - CCG':
			i['label'] = 'EBU - CC - CCG'
		if i['fieldname'] == 'Esen - CCG':
			i['label'] = 'Esen - CCG'
		if i['fieldname'] == 'Network - CC - CCG':
			i['label'] = 'Network - CC - CCG'
		if i['fieldname'] == 'Computer Care Main - CCG':
			i['label'] = 'Computer Care Main - CCG'
		if i['fieldname'] == 'EBU - CC - CCG':
			i['label'] = 'EBU - CC - CCG'
		if i['fieldname'] == 'Service - CC - CCG':
			i['label'] = 'Service - CC - CCG'
	return columns, data

def get_pnl_data(period_list, filters):
	data = []
	for s in profit_and_loss_statement:
		parent_data = []
		s["data"] = []
		if s["op"] == "get_data":
			parent_data = get_data(filters=filters, period_list=period_list, root_type=s["root_type"], balance_must_be=s["balance_must_be"], parent_account=s["parent_account"])
			s["data"] = parent_data[0] if parent_data else []
			data.extend(parent_data or [])

		elif s["op"] == "gross_profit_loss":
			gross_profit_loss = get_gross_profit_loss(period_list, filters.Company)
			s["data"] = gross_profit_loss if gross_profit_loss else []
			data.append(gross_profit_loss or [])

		elif s["op"] == "net_profit_loss":
			net_profit_loss = get_net_profit_loss(period_list, filters.Company)
			s["data"] = net_profit_loss if net_profit_loss else []
			data.append(net_profit_loss or [])

		if parent_data:
			add_blank_row(data)


	return data

def add_blank_row(data):
	data.append([])

def get_pnl_statement_value(parent_account, period_key):
	data = [d.get("data") for d in profit_and_loss_statement if d.get("parent_account")==parent_account]
	return data[0].get(period_key) if data and data[0] else 0.00

def get_pnl_summary_data(parent_account):
	return [d.get("data") for d in profit_and_loss_statement if d.get("parent_account")==parent_account]


def get_net_profit_loss(period_list, company):
	if period_list:
		total = 0
		net_profit_loss = {
			"account_name": "'" + _("Profit / Loss for the period") + "'",
			"account": None,
			"warn_if_negative": True,
			"currency": frappe.db.get_value("Company", company, "default_currency")
		}

		has_value = False
		for period in period_list:
			gross_profit = get_pnl_statement_value("Gross Profit", period.key)
			gen_admin_expense = get_pnl_statement_value("Administrative, Selling and General Expenses", period.key)
			finance_cost = get_pnl_statement_value("Finance Cost", period.key)
			other_income = get_pnl_statement_value("Other Income", period.key)
			net_profit_loss[period.key] = flt((gross_profit - gen_admin_expense - finance_cost + other_income), 3)
			if net_profit_loss[period.key]:
				has_value=True
			
			total += flt(net_profit_loss[period.key])
			net_profit_loss["total"] = total
		
		
		if has_value:
			return net_profit_loss

def get_gross_profit_loss(period_list, company):
	if period_list:
		total = 0
		gross_profit_loss = {
			"account_name": "'" + _("Gross Profit / Loss") + "'",
			"account": None,
			"warn_if_negative": True,
			"currency": frappe.db.get_value("Company", company, "default_currency")
		}

		has_value = False
		for period in period_list:
			revenue = get_pnl_statement_value("Revenue", period.key)
			cost_of_sales = get_pnl_statement_value("Cost Of Sales", period.key)
			gross_profit_loss[period.key] = flt((revenue - cost_of_sales), 3)
			if gross_profit_loss[period.key]:
				has_value=True
			
			total += flt(gross_profit_loss[period.key])
			gross_profit_loss["total"] = total
		
		if has_value:
			return gross_profit_loss

def get_profit_loss_summary(filters):
	pass



