import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_payslip():
    try:
        employee_name = employ_entry.get()

        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()
        c.execute('SELECT * FROM payroll WHERE employee_name = ?', (employee_name,))
        record = c.fetchone()
        conn.close()

        if record:
            print("Record fetched from database:", record)
            payslip_filename = f"{employee_name}_payslip.pdf"
            c = canvas.Canvas(payslip_filename, pagesize=letter)
            c.drawString(100, 770, f"QRS 'EURO SPORT'")
            c.drawString(100, 750, f"Payslip for {employee_name}")
            c.drawString(100, 730, f"Hours Worked: {record[1] if record[1] is not None else 'N/A'}")
            c.drawString(100, 710, f"Hourly Rate: {record[2] if record[2] is not None else 'N/A'}")
            c.drawString(100, 690, f"Saturday Hours: {record[3] if record[3] is not None else 'N/A'}")
            c.drawString(100, 670, f"Saturday Rate: {record[4] if record[4] is not None else 'N/A'}")
            c.drawString(100, 650, f"Total Payment: {record[5] if record[5] is not None else 'N/A'}")
            c.drawString(100, 630, f"Bonus: {record[6] if record[6] is not None else 'N/A'}")
            # c.drawString(100, 610, f"Date: {record[7] if record[7] is not None else 'N/A'}")  # Uncomment if you have a date field
            c.showPage()
            c.save()

            messagebox.showinfo("Payslip Generated", f"Payslip for {employee_name} has been generated and saved as {payslip_filename}.")
        else:
            messagebox.showerror("Error", "Employee not found.")
    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", f"An error occurred: {e}")


def calculate_pay():
    try:
        employee_name = employ_entry.get()
        hours = float(hours_entry.get())
        rate = float(rate_entry.get())
        saturday_hours = float(saturday_entry.get())
        saturday_rate = float(saturday_rate_entry.get())

        regular_hours = min(hours,40)
        overtime_hours = max(0,hours-40)

        weekly_pay = (regular_hours * rate) + (overtime_hours * 3.50) + (saturday_hours * saturday_rate)

       
        if hours >= 80:
            bonus = hours * 1.70
            total_payment = weekly_pay + bonus
            bonus_label.config(text=f"Bonus: ${bonus:.2f}")
        else:
            bonus = 0
            total_payment = weekly_pay
            bonus_label.config(text="Pa bonus")

        total_label.config(text=f"Pagesa totale: ${total_payment:.2f}")

        # Connect to SQLite database
        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()

        # Create table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS payroll (
                        employee_name TEXT,
                        hours INTEGER,
                        rate REAL,
                        saturday_hours INTEGER,
                        saturday_rate REAL,
                        total_payment REAL,
                        bonus REAL
                    )''')

        # Insert data into the database
        c.execute('''INSERT INTO payroll (employee_name, hours, rate, saturday_hours, saturday_rate, total_payment, bonus)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', (employee_name, hours, rate, saturday_hours, saturday_rate, total_payment, bonus))

        # Commit changes and close connection
        conn.commit()
        conn.close()
    except ValueError:
        messagebox.showerror("Gabim në hyrje", "Ju lutem futni vlera numerike të vlefshme.")

def clear_fields():
    employ_entry.delete(0, tk.END)
    hours_entry.delete(0, tk.END)
    rate_entry.delete(0, tk.END)
    saturday_entry.delete(0, tk.END)
    saturday_rate_entry.delete(0, tk.END)
    bonus_label.config(text="")
    total_label.config(text="")

def view_records(order_by="employee_name"):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute(f'SELECT rowid, * FROM payroll ORDER BY {order_by}')
    records = c.fetchall()
    conn.close()

    records_window = tk.Toplevel(root)
    records_window.title("Regjistrimet e Pagesave")
    
    text = tk.Text(records_window)
    text.pack()

    for record in records:
        text.insert(tk.END, f"ID: {record[0]}, Emri: {record[1]}, Orët: {record[2]}, Tarifa: {record[3]}, Orët e Shtunës: {record[4]}, Tarifa e Shtunës: {record[5]}, Pagesa Totale: {record[6]}, Bonusi: {record[7]}\n")

def export_to_csv():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('SELECT * FROM payroll')
    records = c.fetchall()
    conn.close()

    with open('regjistrimet_e_pagesave.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Emri i Punonjësit', 'Orët', 'Tarifa', 'Orët e Shtunës', 'Tarifa e Shtunës', 'Pagesa Totale', 'Bonusi'])
        writer.writerows(records)

    messagebox.showinfo("Eksport", "Regjistrimet u eksportuan në regjistrimet_e_pagesave.csv")

def delete_record():
    try:
        record_id = int(record_id_entry.get())
        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()
        c.execute('DELETE FROM payroll WHERE rowid = ?', (record_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukses", "Regjistrimi u fshi me sukses.")
        record_id_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Gabim", "Ju lutem futni një ID të vlefshme.")

def delete_all_records():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('DELETE FROM payroll')
    conn.commit()
    conn.close()
    messagebox.showinfo("Sukses", "Të gjitha regjistrimet u fshinë me sukses.")


def update_record():
    try:
        record_id = int(record_id_entry.get())
        employee_name = employ_entry.get()
        hours = float(hours_entry.get())
        rate = float(rate_entry.get())
        saturday_hours = float(saturday_entry.get())
        saturday_rate = float(saturday_rate_entry.get())

        weekly_pay = (hours - saturday_hours) * rate + saturday_hours * saturday_rate

        if hours >= 41 and hours <= 60:
            bonus = hours * 0.30
            total_payment = weekly_pay + bonus
            bonus_label.config(text=f"Bonus: ${bonus:.2f}")
        elif hours >= 60 and hours <= 79:
            bonus = hours * 0.70
            total_payment = weekly_pay + bonus
            bonus_label.config(text=f"Bonus: ${bonus:.2f}")
        elif hours >= 80:
            bonus = hours * 1.70
            total_payment = weekly_pay + bonus
            bonus_label.config(text=f"Bonus: ${bonus:.2f}")
        else:
            bonus = 0
            total_payment = weekly_pay
            bonus_label.config(text="Pa bonus")

        total_label.config(text=f"Pagesa totale: ${total_payment:.2f}")

        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()
        c.execute('''UPDATE payroll SET employee_name = ?, hours = ?, rate = ?, saturday_hours = ?, saturday_rate = ?, total_payment = ?, bonus = ?
                     WHERE rowid = ?''', (employee_name, hours, rate, saturday_hours, saturday_rate, total_payment, bonus, record_id))

        conn.commit()
        conn.close()
        messagebox.showinfo("Sukses", "Regjistrimi u përditësua me sukses.")
    except ValueError:
        messagebox.showerror("Gabim", "Ju lutem futni të dhëna të vlefshme.")

def search_records():
    employee_name = search_entry.get()
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('SELECT rowid, * FROM payroll WHERE employee_name LIKE ?', ('%' + employee_name + '%',))
    records = c.fetchall()
    conn.close()

    search_window = tk.Toplevel(root)
    search_window.title("Rezultatet e Kërkimit")
    
    text = tk.Text(search_window)
    text.pack()

    for record in records:
        text.insert(tk.END, f"ID: {record[0]}, Emri: {record[1]}, Orët: {record[2]}, Tarifa: {record[3]}, Orët e Shtunës: {record[4]}, Tarifa e Shtunës: {record[5]}, Pagesa Totale: {record[6]}, Bonusi: {record[7]}\n")

def show_statistics():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('SELECT total_payment, bonus FROM payroll')
    records = c.fetchall()
    conn.close()

    total_payments = sum(record[0] for record in records)
    total_bonuses = sum(record[1] for record in records)
    average_payment = total_payments / len(records) if records else 0
    average_bonus = total_bonuses / len(records) if records else 0

    stats_window = tk.Toplevel(root)
    stats_window.title("Statistikat e Pagesave")
    
    text = tk.Text(stats_window)
    text.pack()

    text.insert(tk.END, f"Totali i Pagesave: ${total_payments:.2f}\n")
    text.insert(tk.END, f"Totali i Bonuseve: ${total_bonuses:.2f}\n")
    text.insert(tk.END, f"Pagesa Mesatare: ${average_payment:.2f}\n")
    text.insert(tk.END, f"Bonusi Mesatar: ${average_bonus:.2f}\n")

root = tk.Tk()
root.title("Kalkulatori i Pagesave")

# GUI elements
tk.Label(root, text="Shkruani Emrin e Punonjësit:").grid(row=0, column=0)
employ_entry = tk.Entry(root)
employ_entry.grid(row=0, column=1)

tk.Label(root, text="Shkruani Orët Regullare:").grid(row=1, column=0)
hours_entry = tk.Entry(root)
hours_entry.grid(row=1, column=1)

tk.Label(root, text="Shkruani Tarifën Regullare:").grid(row=2, column=0)
rate_entry = tk.Entry(root)
rate_entry.grid(row=2, column=1)

tk.Label(root, text="Shkruani Orët e Shtunës:").grid(row=3, column=0)
saturday_entry = tk.Entry(root)
saturday_entry.grid(row=3, column=1)

tk.Label(root, text="Shkruani Tarifën e Shtunës:").grid(row=4, column=0)
saturday_rate_entry = tk.Entry(root)
saturday_rate_entry.grid(row=4, column=1)

tk.Button(root, text="Llogarit Pagesën", command=calculate_pay).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="Pastro Fushat", command=clear_fields).grid(row=6, column=0, columnspan=2)

bonus_label = tk.Label(root, text="")
bonus_label.grid(row=7, column=0, columnspan=2)

total_label = tk.Label(root, text="Pagesa totale: $0.00")
total_label.grid(row=8, column=0, columnspan=2)

tk.Label(root, text="ID e Regjistrimit për Fshirje/Përditësim:").grid(row=9, column=0)
record_id_entry = tk.Entry(root)
record_id_entry.grid(row=9, column=1)

tk.Button(root, text="Fshi Regjistrimin", command=delete_record).grid(row=10, column=0, columnspan=2)
tk.Button(root, text="Përditëso Regjistrimin", command=update_record).grid(row=11, column=0, columnspan=2)

tk.Button(root, text="Shiko Regjistrimet", command=view_records).grid(row=12, column=0, columnspan=2)

delete_all_button = tk.Button(root, text="Fshij të gjitha regjistrimet", command=delete_all_records)
delete_all_button.grid(row=17, column=0, columnspan=2)

payslip_button = tk.Button(root, text="Generate Payslip", command=generate_payslip)
payslip_button.grid(row=18, column=0, columnspan=2)

tk.Button(root, text="Eksporto në CSV", command=export_to_csv).grid(row=13, column=0, columnspan=2)

tk.Label(root, text="Kërko sipas emrit:").grid(row=14, column=0)
search_entry = tk.Entry(root)
search_entry.grid(row=14, column=1)

tk.Button(root, text="Kërko", command=search_records).grid(row=15, column=0, columnspan=2)

tk.Button(root, text="Shfaq Statistikat", command=show_statistics).grid(row=16, column=0, columnspan=2)

root.mainloop()
