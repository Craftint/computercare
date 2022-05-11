// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales"] = {
	"filters": [
	
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		//~ {
			//~ "fieldname":"mode_of_payment",
			//~ "label": __("Mode of Payment"),
			//~ "fieldtype": "Link",
			//~ "options": "Mode of Payment"
		//~ },
		//~ {
			//~ "fieldname":"sales_person",
			//~ "label": __("Sales Person"),
			//~ "fieldtype": "Link",
			//~ "options": "Sales Person"
		//~ },
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center"
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		//~ {
			//~ "fieldname":"brand",
			//~ "label": __("Brand"),
			//~ "fieldtype": "Link",
			//~ "options": "Brand"
		//~ },
		//~ {
			//~ "fieldname":"item_group",
			//~ "label": __("Item Group"),
			//~ "fieldtype": "Link",
			//~ "options": "Item Group"
		//~ }

	]
}
