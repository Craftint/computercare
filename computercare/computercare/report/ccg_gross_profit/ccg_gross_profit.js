// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CCG Gross Profit"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Sales Invoice\nItem Code\nItem Group\nBrand\nCustomer\nCustomer Group\nTerritory\nSales Person\nCost Center\nProject",
			"default": "Sales Invoice"
		},
		{
			"fieldname":"group_by1",
			"label": __("Group By1"),
			"fieldtype": "Select",
			"options": " \nSales Invoice\nItem Code\nItem Group\nBrand\nCustomer\nCustomer Group\nTerritory\nSales Person\nCost Center\nProject",
		},
		{
			"fieldname":"group_by2",
			"label": __("Group By2"),
			"fieldtype": "Select",
			"options": " \nSales Invoice\nItem Code\nItem Group\nBrand\nCustomer\nCustomer Group\nTerritory\nSales Person\nCost Center\nProject",
		},

	]
}
