// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consolidated Vat Ledger"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"voucher_no",
			"label": __("Voucher No"),
			"fieldtype": "Data",
		},
		{
			"fieldtype": "Break",
		},

	]
}
