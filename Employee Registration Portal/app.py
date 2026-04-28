import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'change-this-to-a-secure-key'
app.config['DATABASE'] = os.path.join(app.root_path, 'employees.db')

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS employee(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL
            )
        ''')
        conn.commit()


init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_employee():
    name = request.form.get('name', '').strip()
    department = request.form.get('department', '').strip()
    salary_value = request.form.get('salary', '').strip()

    if not name or not department or not salary_value:
        flash('All fields are required.', 'error')
        return redirect(url_for('home'))

    try:
        salary = float(salary_value)
        if salary < 0:
            raise ValueError('Salary must be positive.')
    except ValueError:
        flash('Salary must be a valid number.', 'error')
        return redirect(url_for('home'))

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO employee(name, department, salary) VALUES (?, ?, ?)',
            (name, department, salary)
        )
        conn.commit()

    flash('Employee added successfully.', 'success')
    return redirect(url_for('view_employees'))


@app.route('/view')
def view_employees():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM employee ORDER BY id DESC')
        employees = cur.fetchall()

    return render_template('view.html', employees=employees)


@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM employee WHERE id = ?', (employee_id,))
        conn.commit()

    flash('Employee record removed.', 'success')
    return redirect(url_for('view_employees'))

if __name__ == '__main__':
    app.run(debug=True)