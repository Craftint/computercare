// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Profit and Loss Statement Cost-Center-Wise"] = $.extend({},
		erpnext.financial_statements);

	frappe.query_reports["Profit and Loss Statement Cost-Center-Wise"]["filters"].push(
		
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},

		{
			"fieldname": "to_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname": "option",
			"label": __("Option"),
			"fieldtype": "Select",
			"options": ["Cost-Center-Wise"],
			"width": "150px",
			"default": "Cost-Center-Wise",
			"reqd": 1 
		},
		{
			"fieldname":"with_details",
			"label": __("With Details"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		}
	);
});


