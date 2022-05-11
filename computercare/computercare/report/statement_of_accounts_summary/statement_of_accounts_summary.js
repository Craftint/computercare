// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statement of Accounts Summary"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
 		{
 			"fieldname":"cost_center",
 			"label": __("Cost Center"),
 			"fieldtype": "Link",
 			"options": "Cost Center",
 			"default": frappe.defaults.get_user_default("cost_center")
 		},
 		{
 			"fieldname":"sales_person",
 			"label": __("Sales Person"),
 			"fieldtype": "Link",
 			"options": "Sales Person"
 		},

		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"credit_days_based_on",
			"label": __("Credit Days Based On"),
			"fieldtype": "Select",
			"options": "\nFixed Days\nLast Day of the Next Month"
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"report_date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": 'Posting Date\nDue Date',
			"default": "Posting Date"
		},
		{
			"fieldname":"range1",
			"label": __("Ageing Range 1"),
			"fieldtype": "Int",
			"default": "30",
			"reqd": 1
		},
		{
			"fieldname":"range2",
			"label": __("Ageing Range 2"),
			"fieldtype": "Int",
			"default": "60",
			"reqd": 1
		},
		{
			"fieldname":"range3",
			"label": __("Ageing Range 3"),
			"fieldtype": "Int",
			"default": "90",
			"reqd": 1
		},
		{
		
			"fieldname":"range4",
			"label": __("Ageing Range 4"),
			"fieldtype": "Int",
			"default": "120",
			"reqd": 1
		}

	],

	onload: function(report) {
		report.page.add_inner_button(__("Statement of Accounts"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Accounts', { company: filters.company,cost_center:filters.cost_center, sales_person:filters.sales_person});
		});
	}
}
