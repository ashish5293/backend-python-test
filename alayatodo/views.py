from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session
    )


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()
    # TASK-1 : render_template function provided an additional parameter for a
    # variable "descBlankMsg" added in todos.html
    # "descBlankMsg" is False when blank description message needs to be hidden on todos.html
    return render_template('todos.html', todos=todos, descBlankMsg=False)


# TASK-4 : a new app route added which handles the confirmation messages whenever a to-do item is
# added, deleted, marked complete or marked incomplete


@app.route('/todos/<confirmation>/c', methods=['GET'])
def todos_confirm(confirmation):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()
    # TASK-4 : confirmMsg is
    # 0 when a to-do is marked incomplete
    # 1 when a to-do is marked COMPLETE
    # 2 when a to-do is deleted
    # 3 when a to-do is added
    return render_template('todos.html', todos=todos, confirmMsg=confirmation)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    # TASK-1 : Server-side validation of the user to add description
    if request.form.get('description', '') != '':
        g.db.execute(
            "INSERT INTO todos (user_id, description, complete) VALUES ('%s', '%s',0)"
            % (session['user']['id'], request.form.get('description', ''))
        )
    else:
        cur = g.db.execute("SELECT * FROM todos")
        todos = cur.fetchall()
        # "descBlankMsg" is True when blank description message needs to be displayed on todos.html
        return render_template('todos.html', todos=todos, descBlankMsg=True)

    g.db.commit()
    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/3/c')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/2/c')


# TASK-2 : function todo_mark_complete runs when user marks a to-do as COMPLETE
@app.route('/todos/<id>', methods=['GET'])
def todo_mark_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET complete = 1 WHERE id ='%s'" % id)
    g.db.commit()
    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/0/c')


# TASK-2 : function todo_mark_complete runs when user marks a to-do as INCOMPLETE
@app.route('/todos/<id>', methods=['POST'])
def todo_mark_incomplete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET complete = 0 WHERE id ='%s'" % id)
    g.db.commit()
    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/1/c')


