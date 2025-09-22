# write a webapp to display accounting data
# functions include: adding transactions and sort them out, viewing charts
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3 as sqlite
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.utils
import json

app = Flask(__name__)
DATABASE = 'accounting.db'
DEFAULT_DESCRIPTION = 'No description provided'
# small secret key for flashing messages in this local app
app.secret_key = 'change-this-to-a-secure-random-value'

# Predefined category choices for initial seed
SEED_CATEGORIES = [
    'Food',
    'Transport',
    'Housing',
    'Utilities',
    'Entertainment',
    'Health',
    'Other'
]
def init_db():
    with sqlite.connect(DATABASE) as con:
        cur = con.cursor()
        # Ensure transactions table exists
        cur.execute('''CREATE TABLE IF NOT EXISTS transactions
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        description TEXT,
                        amount REAL,
                        category TEXT)''')
        # If transactions table exists but lacks book_id, add the column.
        cur.execute("PRAGMA table_info(transactions)")
        cols = [r[1] for r in cur.fetchall()]
        if 'book_id' not in cols:
            cur.execute('ALTER TABLE transactions ADD COLUMN book_id INTEGER')
        # categories table stores available category names
        cur.execute('''CREATE TABLE IF NOT EXISTS categories
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE)''')
        # seed categories if table empty
        cur.execute('SELECT COUNT(*) FROM categories')
        cnt = cur.fetchone()[0]
        if cnt == 0:
            cur.executemany('INSERT INTO categories (name) VALUES (?)', [(c,) for c in SEED_CATEGORIES])
        # books table stores account books; do NOT auto-seed a default book.
        # Users must create a book first before adding transactions.
        cur.execute('''CREATE TABLE IF NOT EXISTS books
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE)''')
        # If there are existing transactions but no books (legacy data), create an
        # 'Imported' book and assign orphaned transactions to it so data isn't lost.
        cur.execute('SELECT COUNT(*) FROM books')
        bcnt = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM transactions')
        tcnt = cur.fetchone()[0]
        if bcnt == 0 and tcnt > 0:
            cur.execute('INSERT INTO books (name) VALUES (?)', ('Imported',))
            imported_id = cur.lastrowid
            # Assign any transactions with NULL or invalid book_id to the imported book
            cur.execute('UPDATE transactions SET book_id = ? WHERE book_id IS NULL OR book_id NOT IN (SELECT id FROM books)', (imported_id,))
        con.commit()


def get_categories():
    with sqlite.connect(DATABASE) as con:
        df = pd.read_sql_query('SELECT id, name FROM categories ORDER BY name', con)
    # return list of names and a list of (id,name) for management pages
    return df['name'].tolist(), df.to_dict(orient='records')


def get_books():
    with sqlite.connect(DATABASE) as con:
        df = pd.read_sql_query('SELECT id, name FROM books ORDER BY name', con)
    return df['name'].tolist(), df.to_dict(orient='records')


@app.context_processor
def inject_books():
    # make books and current_book available to all templates
    names, rows = get_books()
    # determine current book id (only from session). Do NOT auto-select a book.
    current_book_id = session.get('book_id')
    current_book = None
    if current_book_id is not None:
        for r in rows:
            if r['id'] == current_book_id:
                current_book = r
                break
    return dict(books=rows, current_book=current_book)


def find_current_book():
    """Return the current book dict if selected and exists, else None."""
    names, rows = get_books()
    current_book_id = session.get('book_id')
    if current_book_id is None:
        return None
    for r in rows:
        if r['id'] == current_book_id:
            return r
    return None


def ensure_book_selected():
    """Helper to enforce that a book exists and one is selected.
    Returns None if OK; otherwise returns a redirect response to /books.
    """
    names, rows = get_books()
    if not rows:
        from flask import flash
        flash('Please create a book first to use the app.', 'error')
        return redirect(url_for('manage_books'))
    if session.get('book_id') is None:
        from flask import flash
        flash('Please select a book from the selector in the navbar.', 'error')
        return redirect(url_for('manage_books'))
    # also ensure the selected book exists
    cb = find_current_book()
    if cb is None:
        from flask import flash
        flash('Selected book not found. Please re-select a book.', 'error')
        session.pop('book_id', None)
        return redirect(url_for('manage_books'))
    return None


@app.route('/select_book', methods=['POST'])
def select_book():
    bid = request.form.get('book_id')
    try:
        session['book_id'] = int(bid)
    except Exception:
        pass
    return redirect(request.referrer or url_for('index'))


@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    from flask import flash
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Category name cannot be empty', 'error')
        else:
            try:
                with sqlite.connect(DATABASE) as con:
                    cur = con.cursor()
                    cur.execute('INSERT INTO categories (name) VALUES (?)', (name,))
                    con.commit()
                flash('Category added', 'success')
            except sqlite.IntegrityError:
                flash('Category already exists', 'error')
        return redirect(url_for('manage_categories'))

    _, rows = get_categories()
    return render_template('categories.html', rows=rows)


@app.route('/categories/delete/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    from flask import flash
    with sqlite.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('DELETE FROM categories WHERE id = ?', (cat_id,))
        con.commit()
    flash('Category deleted', 'success')
    return redirect(url_for('manage_categories'))


@app.route('/categories/edit/<int:cat_id>', methods=['GET', 'POST'])
def edit_category(cat_id):
    from flask import flash
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Category name cannot be empty', 'error')
            return redirect(url_for('edit_category', cat_id=cat_id))
        try:
            with sqlite.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute('UPDATE categories SET name = ? WHERE id = ?', (name, cat_id))
                con.commit()
            flash('Category updated', 'success')
        except sqlite.IntegrityError:
            flash('Another category with that name exists', 'error')
        return redirect(url_for('manage_categories'))

    # GET
    with sqlite.connect(DATABASE) as con:
        df = pd.read_sql_query('SELECT id, name FROM categories WHERE id = ?', con, params=(cat_id,))
    if df.empty:
        return redirect(url_for('manage_categories'))
    row = df.to_dict(orient='records')[0]
    return render_template('edit_category.html', row=row)


@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Book name cannot be empty', 'error')
        else:
            try:
                with sqlite.connect(DATABASE) as con:
                    cur = con.cursor()
                    cur.execute('INSERT INTO books (name) VALUES (?)', (name,))
                    con.commit()
                flash('Book added', 'success')
            except sqlite.IntegrityError:
                flash('Book already exists', 'error')
        return redirect(url_for('manage_books'))
    _, rows = get_books()
    return render_template('books.html', rows=rows)


@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    # Prevent deleting a book that still has transactions.
    with sqlite.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM transactions WHERE book_id = ?', (book_id,))
        cnt = cur.fetchone()[0]
        if cnt > 0:
            flash('Cannot delete a book that has transactions. Move or delete transactions first.', 'error')
            return redirect(url_for('manage_books'))
        cur.execute('DELETE FROM books WHERE id = ?', (book_id,))
        con.commit()
    flash('Book deleted', 'success')
    # if the deleted book was selected, clear selection
    if session.get('book_id') == book_id:
        session.pop('book_id', None)
    return redirect(url_for('manage_books'))


@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Book name cannot be empty', 'error')
            return redirect(url_for('edit_book', book_id=book_id))
        try:
            with sqlite.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute('UPDATE books SET name = ? WHERE id = ?', (name, book_id))
                con.commit()
            flash('Book updated', 'success')
        except sqlite.IntegrityError:
            flash('Another book with that name exists', 'error')
        return redirect(url_for('manage_books'))
    with sqlite.connect(DATABASE) as con:
        df = pd.read_sql_query('SELECT id, name FROM books WHERE id = ?', con, params=(book_id,))
    if df.empty:
        return redirect(url_for('manage_books'))
    row = df.to_dict(orient='records')[0]
    return render_template('edit_book.html', row=row)
@app.route('/', methods=['GET', 'POST'])
def index():
    """Show list of books. User must click a book to view its transactions.
    If no books exist, show empty list with inline creation form.
    Handle POST to create new books inline.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Book name cannot be empty', 'error')
        else:
            try:
                with sqlite.connect(DATABASE) as con:
                    cur = con.cursor()
                    cur.execute('INSERT INTO books (name) VALUES (?)', (name,))
                    con.commit()
                flash('Book created', 'success')
            except sqlite.IntegrityError:
                flash('Book already exists', 'error')
        return redirect(url_for('index'))
    
    names, books = get_books()
    # render a list of books the user can click into (empty list is fine)
    return render_template('book_list.html', rows=books)


@app.route('/book/<int:book_id>')
def view_book(book_id: int):
    """Select the given book and display its transactions."""
    # ensure the book exists
    names, books = get_books()
    found = None
    for b in books:
        if b['id'] == book_id:
            found = b
            break
    if not found:
        from flask import flash
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    # set the session selection so other pages know the current book
    session['book_id'] = book_id
    # query transactions for this book and show the transactions page
    with sqlite.connect(DATABASE) as con:
        df = pd.read_sql_query("SELECT id, description, amount, category FROM transactions WHERE book_id = ?", con, params=(book_id,))
    rows = df.to_dict(orient='records')
    return render_template('index.html', rows=rows)
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    # ensure a book is selected before allowing adds
    r = ensure_book_selected()
    if r:
        return r

    if request.method == 'POST':
        # date is no longer entered by the user; use local date (YYYY-MM-DD)
        date = datetime.now().date().isoformat()
        # description is optional; use a default if empty or whitespace
        description = request.form.get('description', '')
        if not description or not description.strip():
            description = DEFAULT_DESCRIPTION
        # validate amount
        amount_raw = request.form.get('amount', '')
        try:
            amount = float(amount_raw)
        except Exception:
            from flask import flash
            flash('Amount must be a number', 'error')
            categories, _ = get_categories()
            return render_template('add.html', categories=categories, description=request.form.get('description',''), amount=amount_raw, category=request.form.get('category',''), DEFAULT_DESCRIPTION=DEFAULT_DESCRIPTION)
        if amount == 0:
            from flask import flash
            flash('Amount cannot be zero', 'error')
            categories, _ = get_categories()
            return render_template('add.html', categories=categories, description=request.form.get('description',''), amount=amount_raw, category=request.form.get('category',''), DEFAULT_DESCRIPTION=DEFAULT_DESCRIPTION)

        category = request.form.get('category', '') or 'Other'
        with sqlite.connect(DATABASE) as con:
            cur = con.cursor()
            book_id = session.get('book_id')
            # book_id must exist because we checked earlier in ensure_book_selected
            cur.execute("INSERT INTO transactions (date, description, amount, category, book_id) VALUES (?, ?, ?, ?, ?)",
                        (date, description, amount, category, book_id))
            con.commit()
        from flask import flash
        flash('Transaction added successfully!', 'success')
        # For rapid entry, redirect back to add page instead of index
        return redirect(url_for('add_transaction'))
    
    categories, _ = get_categories()
    return render_template('add.html', categories=categories, DEFAULT_DESCRIPTION=DEFAULT_DESCRIPTION)


@app.route('/delete/<int:tx_id>', methods=['POST'])
def delete_transaction(tx_id):
    # ensure a book is selected before deleting (prevents accidental global deletes)
    r = ensure_book_selected()
    if r:
        return r
    with sqlite.connect(DATABASE) as con:
        cur = con.cursor()
        # only delete if the transaction belongs to the selected book
        cur.execute("DELETE FROM transactions WHERE id = ? AND book_id = ?", (tx_id, session.get('book_id')))
        con.commit()
    from flask import flash
    flash('Transaction deleted', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:tx_id>', methods=['GET', 'POST'])
def edit_transaction(tx_id):
    # ensure a book is selected before editing
    r = ensure_book_selected()
    if r:
        return r

    if request.method == 'POST':
        description = request.form.get('description', '')
        if not description or not description.strip():
            description = DEFAULT_DESCRIPTION
        amount = float(request.form['amount'])
        category = request.form.get('category', '')
        with sqlite.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE transactions SET description = ?, amount = ?, category = ? WHERE id = ?",
                (description, amount, category, tx_id),
            )
            con.commit()
        from flask import flash
        flash('Transaction updated', 'success')
        return redirect(url_for('index'))

    # GET: load the existing record
    with sqlite.connect(DATABASE) as con:
        df = pd.read_sql_query("SELECT id, description, amount, category FROM transactions WHERE id = ? AND book_id = ?", con, params=(tx_id, session.get('book_id')))
    if df.empty:
        return redirect(url_for('index'))
    row = df.to_dict(orient='records')[0]
    categories, _ = get_categories()
    return render_template('edit.html', row=row, categories=categories)
@app.route('/report')
def report():
    """Show comprehensive spending report with total and interactive pie chart by category."""
    # ensure a book is selected before showing reports
    r = ensure_book_selected()
    if r:
        return r
    book = find_current_book()
    with sqlite.connect(DATABASE) as con:
        # Get category totals with transaction counts
        df = pd.read_sql_query(
            """SELECT category, SUM(amount) as total, COUNT(*) as transaction_count, 
               AVG(amount) as avg_amount FROM transactions 
               WHERE book_id = ? GROUP BY category ORDER BY total DESC""",
            con, params=(book['id'],)
        )
        # Get overall totals and stats
        total_result = pd.read_sql_query(
            """SELECT SUM(amount) as grand_total, COUNT(*) as total_transactions,
               AVG(amount) as overall_avg, MIN(amount) as min_amount, MAX(amount) as max_amount
               FROM transactions WHERE book_id = ?""",
            con, params=(book['id'],)
        )
        # Get recent transactions for trend analysis
        recent_transactions = pd.read_sql_query(
            """SELECT category, amount, date FROM transactions WHERE book_id = ?
               ORDER BY date DESC LIMIT 10""",
            con, params=(book['id'],)
        )
    
    # Extract stats with safe defaults
    if total_result.empty or total_result['grand_total'].iloc[0] is None:
        grand_total = 0
        total_transactions = 0
        overall_avg = 0
        min_amount = 0
        max_amount = 0
    else:
        grand_total = total_result['grand_total'].iloc[0]
        total_transactions = total_result['total_transactions'].iloc[0]
        overall_avg = total_result['overall_avg'].iloc[0]
        min_amount = total_result['min_amount'].iloc[0]
        max_amount = total_result['max_amount'].iloc[0]
    
    # If there's no data, render without chart
    if df.empty:
        return render_template('report.html', chart_json=None, grand_total=grand_total, 
                             book_name=book['name'], insights={})
    
    # Calculate spending insights
    insights = {
        'top_category': {
            'name': df.iloc[0]['category'],
            'amount': df.iloc[0]['total'],
            'percentage': (df.iloc[0]['total'] / grand_total * 100) if grand_total > 0 else 0,
            'transaction_count': df.iloc[0]['transaction_count'],
            'avg_transaction': df.iloc[0]['avg_amount']
        },
        'category_stats': df.to_dict('records'),
        'spending_distribution': {
            'categories_count': len(df),
            'top_3_percentage': (df.head(3)['total'].sum() / grand_total * 100) if grand_total > 0 else 0,
            'most_frequent_category': df.loc[df['transaction_count'].idxmax()]['category'] if not df.empty else None,
            'highest_avg_category': df.loc[df['avg_amount'].idxmax()]['category'] if not df.empty else None
        },
        'overall_stats': {
            'total_transactions': total_transactions,
            'overall_avg': overall_avg,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'avg_per_category': grand_total / len(df) if len(df) > 0 else 0
        }
    }

    # Create interactive Plotly pie chart
    labels = df['category'].fillna('Uncategorized').tolist()
    values = df['total'].tolist()
    
    # Create custom hover text with amounts and percentages
    hover_text = []
    total_sum = sum(values)
    for i, (label, value) in enumerate(zip(labels, values)):
        percentage = (value / total_sum) * 100
        hover_text.append(f"{label}<br>${value:.2f}<br>{percentage:.1f}% of total")
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hovertemplate='<b>%{label}</b><br>' +
                      'Amount: $%{value:.2f}<br>' +
                      'Percentage: %{percent}<br>' +
                      '<extra></extra>',
        textinfo='label+percent',
        textposition='auto',
        marker=dict(
            line=dict(color='#FFFFFF', width=2)
        ),
        pull=[0.05 if i == 0 else 0 for i in range(len(values))]  # Pull out the largest slice
    )])
    
    fig.update_layout(
        title={
            'text': f'Spending by Category - {book["name"]}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        font=dict(size=12),
        margin=dict(t=60, b=40, l=40, r=40),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    # Convert to JSON for embedding in template
    chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('report.html', chart_json=chart_json, grand_total=grand_total, 
                         book_name=book['name'], insights=insights)


if __name__ == '__main__':
    init_db()
    # Disable the reloader to avoid spawning child processes that might interact poorly
    # with GUI backends; Agg backend avoids GUI windows, but disabling the reloader
    # also keeps the app in a single process during development here.
    app.run(debug=True, use_reloader=False)