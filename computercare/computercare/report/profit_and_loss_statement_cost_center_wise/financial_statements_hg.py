# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (flt, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)

def get_cost_center_list(filters):
	cost_center_list = []
	for d in get_cost_center(filters):
		cost_center = frappe._dict({
				"key": d.name, 
				"label": d.cost_center_code
			})
		cost_center_list.append(cost_center)

	return cost_center_list

def get_cost_center(filters):
	cc = tuple(filters.cost_center)
	condition = " and company='%s'"%(filters.company)
	if filters.division:
		condition += " and division='%s'"%(filters.division)
	if filters.cost_center:
		condition += " and name in {}".format(cc)

	return frappe.db.sql("""SELECT name, cost_center_name FROM `tabCost Center` WHERE is_group=0 {condition} ORDER BY cost_center_name""".format(condition=condition), as_dict=1)


def get_division_list(filters):
	division_list = []
	for d in get_divison(filters):
		division = frappe._dict({
				"key": d.name, 
				"label": d.division_code
			})
		division_list.append(division)
	return division_list


def get_divison(filters):
	condition = " company='%s'"%(filters.company)
	if filters.division:
		condition += " and name='%s'"%(filters.division)
	
	return frappe.db.sql("""SELECT name, division_code, division_name FROM `tabDivision` WHERE {condition}""".format(condition=condition), as_dict=1)


def get_period_list(filters):
	if filters.option == "Cost-Center-Wise":
		return get_cost_center_list(filters)
	elif filters.option == "Division-Wise":
		return get_division_list(filters)
	else:
		return get_periodicity_list(filters.fiscal_year, filters.periodicity)

def get_periodicity_list(fiscal_year, periodicity):
	"""Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
		Periodicity can be (Yearly, Quarterly, Monthly)"""

	fy_start_end_date = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"])
	if not fy_start_end_date:
		frappe.throw(_("Fiscal Year {0} not found.").format(fiscal_year))

	# start with first day, so as to avoid year to_dates like 2-April if ever they occur]
	year_start_date = get_first_day(getdate(fy_start_end_date[0]))
	year_end_date = getdate(fy_start_end_date[1])
	
	if periodicity == "Yearly":
		period_list = [frappe._dict({"from_date": year_start_date, "to_date": year_end_date, 
			"key": fiscal_year, "label": fiscal_year})]
	else:
		months_to_add = {
			"Half-Yearly": 6,
			"Quarterly": 3,
			"Monthly": 1
		}[periodicity]

		period_list = []

		start_date = year_start_date
		for i in xrange(12 / months_to_add):
			period = frappe._dict({
				"from_date": start_date
			})
			to_date = add_months(start_date, months_to_add)
			start_date = to_date
			
			if to_date == get_first_day(to_date):
				# if to_date is the first day, get the last day of previous month
				to_date = add_days(to_date, -1)
			else:
				# to_date should be the last day of the new to_date's month
				to_date = get_last_day(to_date)

			if to_date <= year_end_date:
				# the normal case
				period.to_date = to_date
			else:
				# if a fiscal year ends before a 12 month period
				period.to_date = year_end_date
			
			period_list.append(period)
			
			if period.to_date == year_end_date:
				break
				
	# common processing
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly":
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			label = get_label(periodicity, opts["from_date"], opts["to_date"])
			
		opts.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list

def get_label(periodicity, from_date, to_date):
	if periodicity=="Yearly":
		if formatdate(from_date, "YYYY") == formatdate(to_date, "YYYY"):
			label = formatdate(from_date, "YYYY")
		else:
			label = formatdate(from_date, "YYYY") + "-" + formatdate(to_date, "YYYY")
	else:
		label = formatdate(from_date, "MMM YY") + "-" + formatdate(to_date, "MMM YY")

	return label


def get_accounts(company, root_type, parent_account=None):
	if parent_account:
		parent = frappe.db.sql("""select lft, rgt from `tabAccount`
		where company=%s and root_type=%s and account_name=%s""", (company, root_type, parent_account), as_dict=1)
		if parent:
			return frappe.db.sql("""select name, case when (parent_account is not null and lft={0} and rgt={1}) then null else parent_account end as parent_account, lft, rgt, root_type, report_type, account_name from
								`tabAccount` where (lft >= {0} and rgt <= {1})
								order by lft""".format(parent[0].lft, parent[0].rgt), as_dict=True)
	else:
		return frappe.db.sql("""select name, parent_account, lft, rgt, root_type, report_type, account_name from `tabAccount`
		where company=%s and root_type=%s order by lft""", (company, root_type), as_dict=True)


def get_data(filters, period_list, root_type, balance_must_be, parent_account=None, add_total=False):
	accounts = get_accounts(filters.company, root_type, parent_account)
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")

	gl_entries_by_account = {}
	if parent_account:
		for root in frappe.db.sql("""select lft, rgt from tabAccount
				where root_type='%s' and company='%s' and account_name='%s' """ % (root_type, filters.company, parent_account), as_dict=1):
			#and ifnull(parent_account, '') = ''
			set_gl_entries_by_account(filters, period_list, root, gl_entries_by_account,
				ignore_closing_entries=True)
	else:
		for root in frappe.db.sql("""select lft, rgt from tabAccount
				where root_type='%s' and ifnull(parent_account, '') = ''""", root_type, as_dict=1):
			set_gl_entries_by_account(filters, period_list, root, gl_entries_by_account,
				ignore_closing_entries=True)

	calculate_values(accounts_by_name, gl_entries_by_account, period_list)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list)
	out = prepare_data(accounts, balance_must_be, period_list, company_currency, filters)
	out = filter_out_zero_value_rows(out, parent_children_map)

	if out and add_total:
		add_total_row(out, balance_must_be, period_list, company_currency)


	return out

	

def calculate_values(accounts_by_name, gl_entries_by_account, period_list, accumulated_values=1):
	for entries in gl_entries_by_account.values():
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			for period in period_list:
				# check if posting date is within the period
				if entry.posting_date <= period.to_date:
					if period.option == "Consolidated" and (accumulated_values or entry.posting_date >= period.from_date):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

					elif (period.option == "Division-Wise" and period.key == entry.division):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

					elif (period.option == "Cost-Center-Wise" and period.key == entry.cost_center):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

					elif not period.option and (accumulated_values or entry.posting_date >= period.from_date):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)


def accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values=1):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = accounts_by_name[d.parent_account].get(period.key, 0.0) + \
					d.get(period.key, 0.0)

def prepare_data(accounts, balance_must_be, period_list, company_currency, filters=None):
	data = []
	
	for d in accounts:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict({
			"account_name": d.account_name,
			"account": d.name,
			"parent_account": d.parent_account,
			"indent": flt(d.indent),
			"year_start_date": filters.from_date,
			"year_end_date": filters.to_date,
			"currency": company_currency
		})
		for period in period_list:
			if d.get(period.key):
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= (1 if balance_must_be=="Debit" else -1)

			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if abs(row[period.key]) >= 0.005:
				# ignore zero values
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)
		
	return data
	
def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value"):
			data_with_value.append(d)
		else:
			# show group with zero balance, if there are balances against child
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						break

	return data_with_value

def add_total_row(out, balance_must_be, period_list, company_currency):
	total_row = {
		"account_name": "'" + _("Total ({0})").format(balance_must_be) + "'",
		"account": None,
		"currency": company_currency
	}

	for row in out:
		if not row.get("parent_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
				row[period.key] = ""
			
			total_row.setdefault("total", 0.0)
			total_row["total"] += flt(row["total"])
			row["total"] = ""
	
	if total_row.has_key("total"):
		out.append(total_row)

		# blank row after Total
		out.append({})


def filter_accounts(accounts, depth=10):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []
	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			if parent == None:
				sort_root_accounts(children)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map

def sort_root_accounts(roots):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_roots(a, b):
		if a.report_type != b.report_type and a.report_type == "Balance Sheet":
			return -1
		if a.root_type != b.root_type and a.root_type == "Asset":
			return -1
		if a.root_type == "Liability" and b.root_type == "Equity":
			return -1
		if a.root_type == "Income" and b.root_type == "Expense":
			return -1
		return 1

	roots.sort()


def set_gl_entries_by_account(filters, period_list, root, gl_entries_by_account, ignore_closing_entries=False):
	"""Returns a dict like { "account": [gl entries], ... }"""
	additional_conditions = []

	if ignore_closing_entries:
		additional_conditions.append("and ifnull(voucher_type, '')!='Period Closing Voucher'")

	if filters.cost_center:
		cc = tuple(filters.cost_center)
		additional_conditions.append("and cost_center in {}".format(cc))
	# else:
	# 	additional_conditions.append("and cost_center = cost_center")

	query = """select posting_date, account, debit, credit, is_opening, cost_center from `tabGL Entry`
		where company='{company}'
		{additional_conditions}
		and posting_date <= '{to_date}'
		and account in (select name from `tabAccount`
			where lft >= {lft} and rgt <= {rgt})
		order by account, posting_date""".format(
			additional_conditions="\n".join(additional_conditions).format(cost_center=filters.cost_center),
			company=filters.company,
			to_date=period_list[0]["to_date"],
			from_date = period_list[0]["from_date"],
			lft = root.lft,
			rgt = root.rgt
		)


	gl_entries = frappe.db.sql(query, as_dict=True)

	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.account, []).append(entry)


	return gl_entries_by_account


def get_columns(period_list, company=None):
	columns = [{
		"fieldname": "account",
		"label": _("Account"),
		"fieldtype": "Link",
		"options": "Account",
		"width": 300
	}]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	columns.append({
			"fieldname": "total",
			"label": _("Total"),
			"fieldtype": "Currency",
			"width": 150
			})
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})

	return columns
