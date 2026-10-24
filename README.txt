MediTrack Billing Update

Files:
- meditrack.py: redesigned billing page and patient submit flow
- database.py: MySQL connection configuration from your uploaded file

Run:
1. Install: pip install mysql-connector-python
2. Ensure MySQL is running and the medical_store database/tables exist.
3. Run: python meditrack.py

Billing sections: patient details, medicine details, bill items, payment method, discount, GST rate, CGST/SGST breakdown, total GST, amount to pay, and submit/confirm bill.
CGST and SGST are displayed as equal halves of the entered GST amount. Confirm applicable tax treatment for your business before using invoices commercially.
