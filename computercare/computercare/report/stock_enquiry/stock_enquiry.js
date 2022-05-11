// Copyright (c) 2016, Tristar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Enquiry"] = {
	"filters": [
	
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		{
			"fieldname": "item_name",
			"label": __("Item Name"),
			"fieldtype": "Data",
			"width": "80"
		},
		/*
		{
			"fieldname": "category",
			"label": __("Category"),
			"fieldtype": "Select",
			"options":" \n3D GLASSES\nADAPTER\nAIO\nBATTERY\nBARCODE SCANNER\nCABINET\nCABLE\nCAMERA\nCARDS\nCARTRIDGE\nCASE\nCASH DRAWER\nCHAIR\nCLEANER\nCONNECTOR\nCONVERTOR\nDESKTOP\nDIGI CAM\nDOCKINGSTATION\nDVDWRITER\nDVR\nEARPHONE\nEXTENSION WARANTY\nPOWER EXTESION\nFINGERTEC\nGAME PAD\nGENERAL\nGLASSES\nHARD DRIVE\nHEADSET\nHUBS\nIPOD CASE\nJOYSTIC\nKEYBOARD\nKIT\nLAMP\nLAPTOP\nMONITOR\nLENS\nLOCK\nMIC\nMOBILE\nMOTHERBOARD\nMOUSE\nMOUNTING\nMOUSE PAD\nPOWER BANK\nPEN\nPHONE\nPLAYSTATION\nPRESENTER\nPRINTER\nPROJECTOR\nPROJECTOR SCREEN\nRAM\nRECHARGE\nRING HOLDER\nROUTER\nSCANNER\nSCREEN PROTECTOR\nSERVE\nSERVER\nSKIN\nSOFTWARE\nSPEAKER\nSOLID STATE DRIVE\nSTICKERS\nSTORAGE\nSWITCH\nTABLET\nTAPE\nTONER\nTRIPOD\nUPS\nUSBFLASH\nVGA\nWATCH\nWEBCAM\nWORKSTATION\nTABKEYBOARD\nEARPHONE\nMOBILECASE\nTABCASE\nHEADPHONE\nFLASH LIGHT",
			"width": "80"
		},*/
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "80",
			"reqd": 1,
			"options": "Item Group"
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse"
		},
		{
			"fieldname": "show_variant_attributes",
			"label": __("Show Variant Attributes"),
			"fieldtype": "Check",
			//"default" : 1
		},

	]
}
