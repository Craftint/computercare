# Copyright (c) 2013, Tristar and contributors
# For license information, please see license.txt



#~ from __future__ import unicode_literals
#~ import frappe
#~ from frappe import _

#~ def execute(filters=None):
	#~ include_uom = filters.get("include_uom")
	#~ columns = get_columns()
	#~ items = get_items(filters)
	#~ sl_entries = get_stock_ledger_entries(filters, items)
	#~ item_details = get_item_details(items, sl_entries, include_uom)
	#~ opening_row = get_opening_balance(filters, columns)

	#~ data = []
	#~ conversion_factors = []
	#~ if opening_row:
		#~ data.append(opening_row)
	#~ for sle in sl_entries:
		
		#~ if sle.voucher_type == 'Sales Invoice' and sle.in_qty > 0:
			#~ data.append([sle.item_code, 
			#~ 0, sle.in_qty or 0, 
			#~ sle.qty_after_transaction or 0,
			#~ ])
		#~ else:
			#~ item_detail = item_details[sle.item_code]
			
			#~ data.append([sle.item_code, 
			#~ sle.in_qty or 0, sle.out_qty or 0, 
			#~ sle.qty_after_transaction or 0,
			#~ ])

			#~ if include_uom:
				#~ conversion_factors.append(item_detail.conversion_factor)
			
	#Stock Summary
		
	#~ dict = {}
	#~ for elem in data:
	  #~ if elem[0] not in dict:
		#~ dict[elem[0]] = []
	  #~ dict[elem[0]].append(elem[1:])
	#~ for key in dict:
		#~ dict[key] = [sum(i) for i in zip(*dict[key])]
	  	
	#~ data = []
	#~ for i in dict:
		#~ description = frappe.get_value("Item", i, ["description"])
		#~ item_group = frappe.get_value("Item", i, ["item_group"])
		#~ brand = frappe.get_value("Item", i, ["brand"])
		
		#~ report_data = [i,
				#~ description,
				#~ item_group,
				#~ brand,
				#~ dict.get(i)[0],
				#~ dict.get(i)[1],
				#~ dict.get(i)[2]
			#~ ]
		#~ data.append(report_data)

	#~ return columns, data

#~ def get_columns():
	#~ columns = [
		#~ {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
		#~ {"label": _("Description"), "fieldname": "description", "width": 200},
		#~ {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		#~ {"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 100},
		#~ {"label": _("In Qty"), "fieldname": "in_qty", "fieldtype": "Int", "width": 50, "convertible": "qty"},
		#~ {"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Int", "width": 50, "convertible": "qty"},
		#~ {"label": _("Balance Qty"), "fieldname": "qty_after_transaction", "fieldtype": "Int", "width": 100, "convertible": "qty"},
	#~ ]

	#~ return columns

#~ def get_stock_ledger_entries(filters, items):
	#~ item_conditions_sql = ''
	#~ if items:
		#~ item_conditions_sql = 'and sle.item_code in ({})'\
			#~ .format(', '.join(['"' + frappe.db.escape(i) + '"' for i in items]))

	#~ return frappe.db.sql("""select concat_ws(" ", posting_date, posting_time) as date,
			#~ item_code, warehouse, 
			#~ case when actual_qty >= 1 then actual_qty end as in_qty,
			#~ case when actual_qty < 1 then actual_qty end as out_qty,
			#~ actual_qty, qty_after_transaction, incoming_rate, valuation_rate,
			#~ stock_value, voucher_type, voucher_no, batch_no, serial_no, company, project
		#~ from `tabStock Ledger Entry` sle
		#~ where company = %(company)s and voucher_type != 'Stock Entry' and
			#~ posting_date between %(from_date)s and %(to_date)s
			#~ {sle_conditions}
			#~ {item_conditions_sql}
			#~ order by posting_date asc, posting_time asc, name asc"""\
		#~ .format(
			#~ sle_conditions=get_sle_conditions(filters),
			#~ item_conditions_sql = item_conditions_sql
		#~ ), filters, as_dict=1)

#~ def get_items(filters):
	#~ conditions = []
	#~ if filters.get("item_code"):
		#~ conditions.append("item.name=%(item_code)s")
	#~ else:
		#~ if filters.get("brand"):
			#~ conditions.append("item.brand=%(brand)s")
		#~ if filters.get("item_group"):
			#~ conditions.append(get_item_group_condition(filters.get("item_group")))

	#~ items = []
	#~ if conditions:
		#~ items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			#~ .format(" and ".join(conditions)), filters)
	#~ return items

#~ def get_item_details(items, sl_entries, include_uom):
	#~ item_details = {}
	#~ if not items:
		#~ items = list(set([d.item_code for d in sl_entries]))

	#~ if not items:
		#~ return item_details

	#~ cf_field = cf_join = ""
	#~ if include_uom:
		#~ cf_field = ", ucd.conversion_factor"
		#~ cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%(include_uom)s"

	#~ for item in frappe.db.sql("""
		#~ select item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom{cf_field}
		#~ from `tabItem` item
		#~ {cf_join}
		#~ where item.name in ({names})
		#~ """.format(cf_field=cf_field, cf_join=cf_join, names=', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])),
		#~ {"include_uom": include_uom}, as_dict=1):
			#~ item_details.setdefault(item.name, item)

	#~ return item_details

#~ def get_sle_conditions(filters):
	#~ conditions = []
	#~ if filters.get("warehouse"):
		#~ warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
		#~ if warehouse_condition:
			#~ conditions.append(warehouse_condition)
	#~ if filters.get("voucher_no"):
		#~ conditions.append("voucher_no=%(voucher_no)s")
	#~ if filters.get("batch_no"):
		#~ conditions.append("batch_no=%(batch_no)s")
	#~ if filters.get("project"):
		#~ conditions.append("project=%(project)s")

	#~ return "and {}".format(" and ".join(conditions)) if conditions else ""

#~ def get_opening_balance(filters, columns):
	#~ if not (filters.item_code and filters.warehouse and filters.from_date):
		#~ return

	#~ from erpnext.stock.stock_ledger import get_previous_sle
	#~ last_entry = get_previous_sle({
		#~ "item_code": filters.item_code,
		#~ "warehouse_condition": get_warehouse_condition(filters.warehouse),
		#~ "posting_date": filters.from_date,
		#~ "posting_time": "00:00:00"
	#~ })
	#~ row = [""]*len(columns)
	#~ row[1] = _("'Opening'")
	#~ for i, v in ((9, 'qty_after_transaction'), (11, 'valuation_rate'), (12, 'stock_value')):
			#~ row[i] = last_entry.get(v, 0)

	#~ return row

#~ def get_warehouse_condition(warehouse):
	#~ warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	#~ if warehouse_details:
		#~ return " exists (select name from `tabWarehouse` wh \
			#~ where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"%(warehouse_details.lft,
			#~ warehouse_details.rgt)

	#~ return ''

#~ def get_item_group_condition(item_group):
	#~ item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	#~ if item_group_details:
		#~ return "item.item_group in (select ig.name from `tabItem Group` ig \
			#~ where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"%(item_group_details.lft,
			#~ item_group_details.rgt)

	#~ return ''


########################################################################


from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now
from erpnext.stock.utils import update_included_uom_in_report
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition

from six import iteritems

def execute(filters=None):
	if not filters: filters = {}

	validate_filters(filters)

	include_uom = filters.get("include_uom")
	columns = get_columns()
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)

	# if no stock ledger entry found return
	if not sle:
		return columns, []

	iwb_map = get_item_warehouse_map(filters, sle)
	item_map = get_item_details(items, sle, filters)
	item_reorder_detail_map = get_item_reorder_details(item_map.keys())

	data = []
	conversion_factors = []
	for (company, item, warehouse) in sorted(iwb_map):
		if item_map.get(item):
			qty_dict = iwb_map[(company, item, warehouse)]
			item_reorder_level = 0
			item_reorder_qty = 0
			if item + warehouse in item_reorder_detail_map:
				item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
				item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

			report_data = [item,
				#~ #item_map[item]["description"], 
				qty_dict.opening_qty,
				qty_dict.in_qty,
				qty_dict.out_qty, 
				qty_dict.bal_qty, 
				qty_dict.val_rate
			]

			if filters.get('show_variant_attributes', 0) == 1:
				variants_attributes = get_variants_attributes()
				report_data += [item_map[item].get(i) for i in variants_attributes]

			if include_uom:
				conversion_factors.append(item_map[item].conversion_factor)

			data.append(report_data)

	if filters.get('show_variant_attributes', 0) == 1:
		columns += ["{}:Data:100".format(i) for i in get_variants_attributes()]

	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
	
	#~ #Stock Summary
		
	dict = {}
	for elem in data:
		if elem[0] not in dict:
			dict[elem[0]] = []
		dict[elem[0]].append(elem[1:])
	  
	for key in dict:
		dict[key] = [sum(i) for i in zip(*dict[key])]
	  	
	data = []
	for i in dict:
		#case when actual_qty >= 1 then actual_qty end as in_qty,
		#case when actual_qty < 1 then actual_qty end as out_qty,
		sql_script  = """ select actual_qty,voucher_type
			from `tabStock Ledger Entry` sle
			where voucher_type != 'Stock Entry' and
				posting_date between '""" +filters.from_date+ """' and '"""+filters.to_date+"""' 
				and item_code = '"""+i+"""' 
				"""
		vals = frappe.db.sql(sql_script)
		
		in_qty = 0
		out_qty = 0
		for a in vals:
			#frappe.msgprint(_("items: {0}".format(a)))	
			#if a[2] == 'Sales Invoice' and a[0] > 0:
			#	in_qty += 0
			#	out_qty += a[0] or 0
			#~ elif a[2] == 'Purchase Invoice' and a[1] < 0:
				#~ in_qty += a[1] or 0	
				#~ out_qty += 0
			#else:
			#	in_qty += a[0] or 0
			#	out_qty += a[1] or 0

			if a[1] == 'Sales Invoice':
				out_qty += a[0]
			elif a[1] == 'Purchase Invoice':
				in_qty += a[0]

		report_data = [i,
				item_map[i]["description"],
				item_map[i]["item_group"],
				item_map[i]["brand"], 
				#~ dict.get(i)[0],
				in_qty,
				out_qty, 
				dict.get(i)[3],
				item_map[i]["last_purchase_rate"]
				#~ #dict.get(i)[4]
			]
		
		if report_data[4] == 0 and report_data[5] == 0:
			pass
		else:
			data.append(report_data)
		
	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
		{"label": _("Description"), "fieldname": "description", "width": 200},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		{"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 100},
		#~ {"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("In Qty"), "fieldname": "in_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},	
		{"label": _("Last Purchase Rate"), "fieldname": "last_purchase_rate", "fieldtype": "Currency", "width": 150, "convertible": "rate"},
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters.get("to_date"))
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("warehouse"):
		warehouse_details = frappe.db.get_value("Warehouse",
			filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
		if warehouse_details:
			conditions += " and exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)"%(warehouse_details.lft,
				warehouse_details.rgt)

	return conditions

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = ' and sle.item_code in ({})'\
			.format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items]))

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index)
		where sle.docstatus < 2 %s %s
		order by sle.posting_date, sle.posting_time, sle.name""" %
		(item_conditions_sql, conditions), as_dict=1)

def get_item_warehouse_map(filters, sle):
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0
			})

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date:
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if qty_diff > 0:
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff
		
	iwb_map = filter_items_with_no_transactions(iwb_map)

	return iwb_map
	
def filter_items_with_no_transactions(iwb_map):
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]
		
		no_transactions = True
		float_precision = cint(frappe.db.get_default("float_precision")) or 3
		for key, val in iteritems(qty_dict):
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False
		
		if no_transactions:
			iwb_map.pop((company, item, warehouse))

	return iwb_map

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sle]))

	if items:
		cf_field = cf_join = ""
		if filters.get("include_uom"):
			cf_field = ", ucd.conversion_factor"
			cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%(include_uom)s"

		for item in frappe.db.sql("""
			select item.name, item.item_name, item.description, item.item_group, item.brand, item.last_purchase_rate, item.stock_uom{cf_field}
			from `tabItem` item
			{cf_join}
			where item.name in ({names}) and ifnull(item.disabled, 0) = 0
			""".format(cf_field=cf_field, cf_join=cf_join, names=', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])),
			{"include_uom": filters.get("include_uom")}, as_dict=1):
				item_details.setdefault(item.name, item)

	if filters.get('show_variant_attributes', 0) == 1:
		variant_values = get_variant_values_for(list(item_details))
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in iteritems(item_details)}

	return item_details

def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.db.sql("""
			select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
			from `tabItem Reorder`
			where parent in ({0})
		""".format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])), as_dict=1)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

def get_variants_attributes():
	'''Return all item variant attributes.'''
	return [i.name for i in frappe.get_all('Item Attribute')]

def get_variant_values_for(items):
	'''Returns variant values for items.'''
	attribute_map = {}
	for attr in frappe.db.sql('''select parent, attribute, attribute_value
		from `tabItem Variant Attribute` where parent in (%s)
		''' % ", ".join(["%s"] * len(items)), tuple(items), as_dict=1):
			attribute_map.setdefault(attr['parent'], {})
			attribute_map[attr['parent']].update({attr['attribute']: attr['attribute_value']})

	return attribute_map
