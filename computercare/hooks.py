# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "computercare"
app_title = "Computercare"
app_publisher = "Tristar"
app_description = "Custom App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@tristar-enterprises.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/computercare/css/computercare.css"
# app_include_js = "/assets/computercare/js/computercare.js"

# include js, css files in header of web template
# web_include_css = "/assets/computercare/css/computercare.css"
# web_include_js = "/assets/computercare/js/computercare.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "computercare.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "computercare.install.before_install"
# after_install = "computercare.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "computercare.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Sales Invoice": {
		"autoname": "computercare.utils.set_custom_auto_name",

		"before_save" : [
				"computercare.utils.validate_cost_center",
				"computercare.utils.validate_payment_entry",
				"computercare.utils.validate_itemprice",
		],
		
		"before_submit" : [
				"computercare.utils.validate_cash_payment_entry",
		],
	},
	"Quotation": {
		"autoname": "computercare.utils.set_custom_auto_name",

		 "before_save" : [
                                "computercare.utils.validate_cost_center",
                ],


		#"validate" : [
		#		"computercare.utils.validate_warehouse"
		#	],
	},
	"Sales Order": {
		"autoname": "computercare.utils.set_custom_auto_name",

		"before_save" : [
                                "computercare.utils.validate_cost_center",
                ],


		#"validate" : [
		#		"computercare.utils.validate_cost_center",
		#		"computercare.utils.validate_warehouse"
		#	],

	},
	"Delivery Note": {
		"autoname": "computercare.utils.set_custom_auto_name",

		 "before_save" : [
                                "computercare.utils.validate_cost_center",
                ],


		#"validate" : [
		#		"computercare.utils.validate_cost_center"
		#	
		#	],
	},
	"Purchase Order": {
		"autoname": "computercare.utils.set_custom_auto_name",
		#"validate" : [
		#		"computercare.utils.validate_cost_center",
		#		"computercare.utils.validate_warehouse"
		#	],
	},
	"Purchase Receipt": {
		"autoname": "computercare.utils.set_custom_auto_name",

		"before_save" : [
				"computercare.utils.validate_cost_center",
			],
	},
	"Purchase Invoice": {
		"autoname": "computercare.utils.set_custom_auto_name",

		"before_save" : [
				"computercare.utils.validate_cost_center",
			],
	},

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"computercare.tasks.all"
# 	],
# 	"daily": [
# 		"computercare.tasks.daily"
# 	],
# 	"hourly": [
# 		"computercare.tasks.hourly"
# 	],
# 	"weekly": [
# 		"computercare.tasks.weekly"
# 	]
# 	"monthly": [
# 		"computercare.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "computercare.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "computercare.event.get_events"
# }

