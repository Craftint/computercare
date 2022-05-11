from __future__ import unicode_literals
import frappe, erpnext 
#vouchers=[]

#with open('/home/hercules/Desktop/difference_account.csv','r') as csvfile:
#	data = csv.reader(csvfile, delimiter=',')
#	for row in data:
#		v = {
#			"voucher_type":		row[1],
#			"voucher_number":	row[2]
#		}
#		vouchers.append(v)
#
#for voucher in vouchers:
#	print("{0},".format(voucher))

def execute():
	vouchers = [
		{'voucher_number': 'CC-ACC-PINV-2019-00002', 'voucher_type': 'Purchase Invoice'},
		{'voucher_number': 'CC-ACC-PINV-2019-00006', 'voucher_type': 'Purchase Invoice'}
		]

	for v in vouchers:
		print'voucher_type',v
		doc = frappe.get_doc(v["voucher_type"], v["voucher_number"])

		doc.docstatus = 2
		doc.make_gl_entries_on_cancel(repost_future_gle=False)

		# update gl entries for submit state of vouchers
		#doc.docstatus = 1
		#doc.make_gl_entries(repost_future_gle=False)
