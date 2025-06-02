import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import mysql.connector
import smtplib
from email.message import EmailMessage

def connect_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="758110", database="CampusRecruitmentDB"
    )

def log_activity(activity):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO logs (activity) VALUES (%s)", (activity,))
    db.commit()
    db.close()

def send_email(sender, receiver, subject, body):
    app_password = "dtll fqxz nxit sopp"
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender, app_password)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Email Error", "Authentication failed. Check your email and app password.")
    except Exception as e:
        messagebox.showerror("Email Error", str(e))

admin_email = None

def open_login_window():
    login_win = tk.Toplevel(root)
    login_win.title("Login")
    login_win.geometry("400x320")
    login_win.grab_set()

    notebook = ttk.Notebook(login_win)
    notebook.pack(expand=True, fill='both', padx=10, pady=10)

    admin_frame = tk.Frame(notebook)
    notebook.add(admin_frame, text="Admin Login")

    tk.Label(admin_frame, text="Admin Email", font=("Helvetica", 12)).pack(pady=(15,5))
    admin_email_entry = tk.Entry(admin_frame, width=30)
    admin_email_entry.pack()

    tk.Label(admin_frame, text="Admin Password", font=("Helvetica", 12)).pack(pady=(15,5))
    admin_password_entry = tk.Entry(admin_frame, show="*", width=30)
    admin_password_entry.pack()

    def admin_attempt_login():
        global admin_email
        email = admin_email_entry.get()
        password = admin_password_entry.get()

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email, password))
        admin = cursor.fetchone()
        db.close()

        if admin:
            admin_email = email
            messagebox.showinfo("Login Success", "Welcome, Admin!")
            login_win.destroy()
            open_admin_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid admin credentials")

    tk.Button(admin_frame, text="Login", command=admin_attempt_login, bg="#ff6666", fg="white").pack(pady=20)

    student_frame = tk.Frame(notebook)
    notebook.add(student_frame, text="Student Login")

    tk.Label(student_frame, text="Student Email", font=("Helvetica", 12)).pack(pady=(15,5))
    student_email_entry = tk.Entry(student_frame, width=30)
    student_email_entry.pack()

    tk.Label(student_frame, text="Student Password", font=("Helvetica", 12)).pack(pady=(15,5))
    student_password_entry = tk.Entry(student_frame, show="*", width=30)
    student_password_entry.pack()

    def student_attempt_login():
        email = student_email_entry.get()
        password = student_password_entry.get()

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
        student = cursor.fetchone()
        db.close()
        if student:
            log_activity(f"Student {email} logged in")
            messagebox.showinfo("Login Success", f"Welcome, {email}")
            login_win.destroy()
            student_dashboard(email)
        else:
            messagebox.showerror("Login Failed", "Invalid student credentials")

    tk.Button(student_frame, text="Login", command=student_attempt_login, bg="#99e699", fg="white").pack(pady=20)

def open_admin_dashboard():
    win = tk.Toplevel(root)
    win.title("Admin Dashboard")
    win.geometry("850x600")

    notebook = ttk.Notebook(win)
    notebook.pack(expand=True, fill='both')

    post_frame = tk.Frame(notebook)
    notebook.add(post_frame, text="Post Job")

    tk.Label(post_frame, text="Post a Job", font=("Helvetica", 16)).pack(pady=10)

    tk.Label(post_frame, text="Job Title").pack(pady=5)
    title_entry = tk.Entry(post_frame)
    title_entry.pack()

    tk.Label(post_frame, text="Description").pack(pady=5)
    desc_entry = tk.Text(post_frame, height=5)
    desc_entry.pack()

    tk.Label(post_frame, text="Salary").pack(pady=5)
    salary_entry = tk.Entry(post_frame)
    salary_entry.pack()

    tk.Label(post_frame, text="Location").pack(pady=5)
    location_entry = tk.Entry(post_frame)
    location_entry.pack()

    def post():
        title = title_entry.get()
        description = desc_entry.get("1.0", tk.END).strip()
        salary = salary_entry.get()
        location = location_entry.get()

        if not title or not description or not salary or not location:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO posts (title, description, salary, location, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, description, salary, location, admin_email))
            db.commit()
            db.close()

            messagebox.showinfo("Success", "Job posted successfully!")
            title_entry.delete(0, tk.END)
            desc_entry.delete("1.0", tk.END)
            salary_entry.delete(0, tk.END)
            location_entry.delete(0, tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    tk.Button(post_frame, text="Post Job", command=post, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=15)

    app_frame = tk.Frame(notebook)
    notebook.add(app_frame, text="View Applications")

    tk.Label(app_frame, text="Applications", font=("Helvetica", 16)).pack(pady=10)

    app_columns = ("Application ID", "Student Email", "Job Title", "Status/Reply")
    app_tree = ttk.Treeview(app_frame, columns=app_columns, show='headings')
    for col in app_columns:
        app_tree.heading(col, text=col)
        app_tree.column(col, anchor=tk.W, width=180)
    app_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def refresh_applications():
        for row in app_tree.get_children():
            app_tree.delete(row)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT a.id, a.student_email, p.title, a.reply
            FROM applications a
            JOIN posts p ON a.job_id = p.id
            ORDER BY a.id DESC
        """)
        applications = cursor.fetchall()
        db.close()
        for app_row in applications:
            app_tree.insert('', 'end', values=app_row)

    refresh_applications()

    def update_status():
        selected = app_tree.focus()
        if not selected:
            messagebox.showerror("Error", "No application selected")
            return
        app_id, student_email, job_title, status = app_tree.item(selected)['values']
        new_status = simpledialog.askstring("Update Status", "Enter new status (e.g. Pending, Accepted, Rejected):", initialvalue=status)
        if new_status:
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("UPDATE applications SET reply=%s WHERE id=%s", (new_status, app_id))
                db.commit()
                db.close()
                log_activity(f"Application {app_id} status updated to {new_status}")
                refresh_applications()
                messagebox.showinfo("Success", "Application status updated")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

    def send_reply_email():
        selected = app_tree.focus()
        if not selected:
            messagebox.showerror("Error", "No application selected")
            return
        app_id, student_email, job_title, status = app_tree.item(selected)['values']

        subject = f"Application Update for {job_title}"
        body = simpledialog.askstring("Email Reply", "Enter your message to the applicant:")
        if not body:
            messagebox.showinfo("Cancelled", "Email sending cancelled.")
            return

        if not admin_email:
            messagebox.showerror("Error", "Admin email is required to send email.")
            return

        send_email(admin_email, student_email, subject, body)
        messagebox.showinfo("Email Sent", f"Reply sent to {student_email} successfully.")

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("UPDATE applications SET reply=%s WHERE id=%s", (body, app_id))
            db.commit()
            db.close()
            log_activity(f"Sent email reply to {student_email} for application {app_id} with reply: {body}")
            refresh_applications()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

    btn_frame = tk.Frame(app_frame)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Update Selected Status", command=update_status, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Send Email Reply", command=send_reply_email, bg="#FFA500", fg="black", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)

    student_frame = tk.Frame(notebook)
    notebook.add(student_frame, text="Manage Students")

    tk.Label(student_frame, text="Registered Students", font=("Helvetica", 16)).pack(pady=10)

    student_columns = ("Student ID", "Name", "Email")
    student_tree = ttk.Treeview(student_frame, columns=student_columns, show='headings')
    for col in student_columns:
        student_tree.heading(col, text=col)
        student_tree.column(col, anchor=tk.W, width=200)
    student_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def refresh_students():
        for row in student_tree.get_children():
            student_tree.delete(row)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM students ORDER BY id DESC")
        students = cursor.fetchall()
        db.close()
        for student in students:
            student_tree.insert('', 'end', values=student)

    refresh_students()

    def delete_student():
        selected = student_tree.focus()
        if not selected:
            messagebox.showerror("Error", "No student selected")
            return
        student_id, name, email = student_tree.item(selected)['values']
        confirm = messagebox.askyesno("Confirm Delete", f"Delete student {name} ({email})?")
        if confirm:
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
                db.commit()
                db.close()
                log_activity(f"Deleted student {email}")
                refresh_students()
                messagebox.showinfo("Success", "Student deleted")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

    tk.Button(student_frame, text="Delete Selected Student", command=delete_student, bg="#f44336", fg="white", font=("Helvetica", 12)).pack(pady=10)

def student_register():
    name = simpledialog.askstring("Register", "Enter Name")
    email = simpledialog.askstring("Register", "Enter Email")
    password = simpledialog.askstring("Register", "Enter Password", show='*')
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        db.commit()
        log_activity(f"Student {email} registered")
        messagebox.showinfo("Success", "Registration Successful")
    except mysql.connector.errors.IntegrityError:
        messagebox.showerror("Error", "Email already registered")
    db.close()

def student_dashboard(email):
    win = tk.Toplevel(root)
    win.title("Available Jobs & Your Applications")
    win.geometry("800x600")

    jobs_frame = tk.LabelFrame(win, text="Available Jobs")
    jobs_frame.pack(fill='both', expand=True, padx=10, pady=10)

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, email FROM posts")
    jobs = cursor.fetchall()
    db.close()

    tree = ttk.Treeview(jobs_frame, columns=("ID", "Title", "Posted By"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Job Title")
    tree.heading("Posted By", text="Posted By")
    tree.pack(expand=True, fill='both', side=tk.LEFT, padx=5, pady=5)

    for job in jobs:
        tree.insert('', 'end', values=job)

    def apply():
        selected = tree.focus()
        if not selected:
            return
        job_id = tree.item(selected)['values'][0]
        db2 = connect_db()
        cursor2 = db2.cursor()
        cursor2.execute("INSERT INTO applications (student_email, job_id, reply) VALUES (%s, %s, %s)",
                        (email, job_id, 'Pending'))
        db2.commit()
        db2.close()

        subject = f"Application Submitted for Job ID {job_id}"
        body = f"Dear Student,\n\nYou have successfully applied for the job with ID {job_id}. Your application status is currently 'Pending'.\n\nBest regards,\nCampus Recruitment Team"

        if admin_email:
            send_email(admin_email, email, subject, body)
        else:
            messagebox.showwarning("Warning", "Admin email not set, email not sent.")

        log_activity(f"{email} applied for job {job_id}")
        messagebox.showinfo("Applied", "Application Sent")
        refresh_applications()

    tk.Button(jobs_frame, text="Apply for Selected Job", command=apply).pack(side=tk.RIGHT, padx=10, pady=10)

    apps_frame = tk.LabelFrame(win, text="Your Applications & Status")
    apps_frame.pack(fill='both', expand=True, padx=10, pady=10)

    app_columns = ("Application ID", "Job Title", "Status/Reply")
    app_tree = ttk.Treeview(apps_frame, columns=app_columns, show='headings')
    for col in app_columns:
        app_tree.heading(col, text=col)
        app_tree.column(col, anchor=tk.W, width=200)
    app_tree.pack(expand=True, fill='both', padx=5, pady=5)

    def refresh_applications():
        for row in app_tree.get_children():
            app_tree.delete(row)
        db3 = connect_db()
        cursor3 = db3.cursor()
        cursor3.execute("""
            SELECT a.id, p.title, a.reply
            FROM applications a
            JOIN posts p ON a.job_id = p.id
            WHERE a.student_email = %s
            ORDER BY a.id DESC
        """, (email,))
        applications = cursor3.fetchall()
        db3.close()
        for app in applications:
            app_tree.insert('', 'end', values=app)

    refresh_applications()

root = tk.Tk()
root.title("Campus Recruitment System")
root.geometry("800x600")

bg_img = Image.open(r"D:\Nothing\COLLEGE\4 SEM\DBMS\project\background.png")
bg_img = bg_img.resize((800, 600))
bg = ImageTk.PhotoImage(bg_img)
bg_label = tk.Label(root, image=bg)
bg_label.place(relwidth=1, relheight=1)

tk.Label(root, text="Campus Recruitment System", font=("Helvetica", 20), bg="#ffffff").pack(pady=30)

tk.Button(root, text="Login", command=open_login_window, bg="#5a9bd4", fg="white", font=("Helvetica", 14)).pack(pady=15)
tk.Button(root, text="Student Register", command=student_register, bg="#66b3ff", fg="white", font=("Helvetica", 14)).pack(pady=10)

root.mainloop()
