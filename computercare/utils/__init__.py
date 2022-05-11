# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# util __init__.py

from __future__ import unicode_literals
from frappe.utils import flt, get_datetime, getdate, date_diff, cint, nowdate
from frappe import _, msgprint, throw
import frappe
from frappe.utils.background_jobs import enqueue
from frappe.core.doctype.communication.email import make
from frappe.defaults import get_user_permissions
import re
import os


def validate_warehouse(doc, method):
	default_warehouse = None 
	if frappe.get_meta(doc.doctype).get_field("warehouse") and doc.get("warehouse"):
		default_warehouse = doc.warehouse
	if not default_warehouse:
		default_warehouse = frappe.get_value("Cost Center", doc.cost_center, ["warehouse"])
	if not default_warehouse:
		default_warehouse = frappe.db.get_single_value('Stock Settings','default_warehouse')
	if not default_warehouse:
		return

	if doc.doctype in ["Delivery Note", "Sales Invoice"]:
		for item in doc.get("items"):
			if not item.warehouse:
				item.warehouse = default_warehouse
	else:
		for item in doc.get("items"):
			if not item.warehouse or item.warehouse not in default_warehouse:
				item.warehouse = doc.warehouse

def validate_cost_center(doc, method):
	if frappe.get_meta(doc.doctype).get_field("write_off_cost_center") and doc.write_off_cost_center != doc.cost_center:
		doc.write_off_cost_center = doc.cost_center

	if frappe.get_meta(doc.doctype + ' Item').get_field("cost_center"):
		for item in doc.get("items"):
			if not item.cost_center or item.cost_center not in doc.cost_center:
				item.cost_center = doc.cost_center

	for tax in doc.get("taxes"):
		if not tax.cost_center or tax.cost_center not in doc.cost_center:
			tax.cost_center = doc.cost_center

def get_user_permissions_for(doctype):
	return filter(None, get_user_permissions().get(doctype, []))

def set_custom_auto_name(doc, method=None):
	from computercare.utils import get_custom_auto_name
	series_format = frappe.get_meta(doc.doctype).get_field("naming_series").options
	doc.name = get_custom_auto_name(doc.cost_center, doc.naming_series, series_format)
	#frappe.msgprint(_("series_format: {0}".format(series_format)))

def get_custom_auto_name(cost_center, naming_series, series_format=None):
	from frappe.model.naming import make_autoname
	return make_autoname(get_custom_naming_series(cost_center, naming_series, series_format))

def get_custom_naming_series(cost_center, naming_series, series_format=None):
	abbr = frappe.db.get_value("Cost Center", cost_center, ["abbr"])
	number_format = "#####"

	if series_format and series_format.find("abbr") > 0:
		return series_format.replace("abbr", abbr)

	return "{abbr}-{naming_series}.{number_format}".format(naming_series=naming_series, abbr=abbr, number_format=number_format)
	
def validate_payment_entry(doc, method):
	if doc.mode_of_payment == "Cash":
		if doc.get("payments") == []:
			frappe.msgprint(_("You must choose any one mode of payments"))
		for payment in doc.get("payments"):
			if payment.amount == 0:
				doc.get("payments").remove(payment)
		for payment in doc.get("payments"):
			if payment.amount == 0:
				doc.get("payments").remove(payment)
		for payment in doc.get("payments"):
			if payment.amount == 0:
				doc.get("payments").remove(payment)
				
def validate_cash_payment_entry(doc, method):
	if doc.mode_of_payment == "Cash":
		if doc.outstanding_amount != 0.00:
			frappe.throw(_("Outstanding Amount :{0} . For Cash Invoice Outstanding amount should be 0.00 . Please record the payment fully.").format(doc.outstanding_amount))
		for payment in doc.get("payments"):
			
			if payment.amount > doc.grand_total:
				frappe.throw(_("Payment Amount :{0} . For Cash Invoice amount should not be greater than Grand Total {1}. Please record the payment fully.").format(payment.amount, doc.grand_total))
				
def validate_itemprice(doc, method):
	for item in doc.get("items"):
		itemprice = frappe.db.sql("""SELECT price_list_rate from `tabItem Price` where item_code = %s and selling=1; """, (item.item_code))		
		if not itemprice:
			frappe.throw(_("Update Price List Rate for {0}").format(item.item_code))
		if item.net_rate < itemprice[0][0]:
			frappe.throw(_("{0} price should be greater than Price List Rate {1} ").format(item.item_code,itemprice[0][0]))
			frappe.throw(_("{0} price should be greater than Price List Rate").format(item.item_code))
			
def get_user_permissions_for(doctype):
	return filter(None, get_user_permissions().get(doctype, []))
				
