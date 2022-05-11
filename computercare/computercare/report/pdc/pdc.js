// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PDC"] = {
	"filters": [
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
			"fieldname":"enquiry_type",
			"label":__("Enquiry Type"),
			"fieldtype":"Select",
			"default":"PDC",
			"options":"PDC\nCleared\nAll"
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"payment_type",
			"label":__("Payment Type"),
			"fieldtype":"Select",
			"default":"Receive",
			"options":"Receive\nPay\nInternal Transfer"
		},
		{
			"fieldname":"party_type",
			"label":__("Party Type"),
			"fieldtype":"Link",
			"options":"Party Type"
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report.get_filter_value('party_type');
				var party = frappe.query_report.get_filter_value('party');
				if(party && !party_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return party_type;
			}
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},

	]
}
