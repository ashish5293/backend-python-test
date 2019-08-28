import json
from alayatodo import app, DATABASE
from flask import (
    g,
    redirect,
    render_template,
    request,
    session
    )
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)

from models_orm import Users, Todos


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

    # sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    # cur = g.db.execute(sql % (username, password))
    # user = cur.fetchone()

    # TASK-6 : SQL code replaced with SQLAlchemy code
    user = Users.query.filter_by(username=username, password=password).first()

    if user:
        session['user'] = {'username': user.username,
                           'password': user.password,
                           'id': user.id}
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
    # cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    # todo = cur.fetchone()

    # TASK-6 : SQL code replaced with SQLAlchemy code
    todo = Todos.query.filter_by(id=id).first()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    # cur = g.db.execute("SELECT * FROM todos")
    # todos = cur.fetchall()

    # TASK-6 : SQL code replaced with SQLAlchemy code
    # todos = Todos.query.all()

    todos = get_todo_pagination(per_page_todo=5, page_num=1)

    # TASK-1 : render_template function provided an additional parameter for a
    # variable "descBlankMsg" added in todos.html
    # "descBlankMsg" is False when blank description message needs to be hidden on todos.html
    return render_template('todos.html', todos=todos, descBlankMsg=False)


# TASK-4 : a new app route added which handles the confirmation messages whenever a to-do item is
# added, deleted, marked complete or marked incomplete


@app.route('/todos/<confirmation>/<curr_page>/c', methods=['GET'])
def todos_confirm(confirmation, curr_page):
    if not session.get('logged_in'):
        return redirect('/login')

    # cur = g.db.execute("SELECT * FROM todos")
    # todos = cur.fetchall()

    ''' TASK-6 : SQL code replaced with SQLAlchemy code'''
    # todos = Todos.query.all()
    todos = get_todo_pagination(per_page_todo=5, page_num=int(curr_page))

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
        '''
        g.db.execute(
            "INSERT INTO todos (user_id, description, complete) VALUES ('%s', '%s',0)"
            % (session['user']['id'], request.form.get('description', ''))
        )
        '''

        # TASK-6 : SQL code replaced with SQLAlchemy code
        new_todo = Todos(user_id=session['user']['id'], description=request.form.get('description', ''),complete=0)
        db.session.add(new_todo)
    else:
        # cur = g.db.execute("SELECT * FROM todos")
        # todos = cur.fetchall()

        # TASK-6 : SQL code replaced with SQLAlchemy code
        # todos = Todos.query.all()

        todos = get_todo_pagination(per_page_todo=5, page_num=1)

        # "descBlankMsg" is True when blank description message needs to be displayed on todos.html
        return render_template('todos.html', todos=todos, descBlankMsg=True)

    # g.db.commit()
    db.session.commit()

    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/3/1/c')


@app.route('/todo/<id>/<curr_page>/d', methods=['POST'])
def todo_delete(id, curr_page):
    if not session.get('logged_in'):
        return redirect('/login')
    # g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    # g.db.commit()

    # TASK-6 : SQL code replaced with SQLAlchemy code
    delete_todo = db.session.query(Todos).filter_by(id=id).first()
    db.session.delete(delete_todo)
    db.session.commit()

    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/2/'+curr_page+'/c')


# TASK-2 : function todo_mark_complete runs when user marks a to-do as COMPLETE
@app.route('/todos/<id>/<curr_page>/com', methods=['GET'])
def todo_mark_complete(id, curr_page):
    if not session.get('logged_in'):
        return redirect('/login')
    # g.db.execute("UPDATE todos SET complete = 1 WHERE id ='%s'" % id)
    # g.db.commit()

    # TASK-6 : SQL code replaced with SQLAlchemy code
    update_todo = db.session.query(Todos).filter_by(id=id).first()
    update_todo.complete = 1
    db.session.commit()

    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/0/'+curr_page+'/c')


# TASK-2 : function todo_mark_incomplete runs when user marks a to-do as INCOMPLETE
@app.route('/todos/<id>/<curr_page>/incom', methods=['POST'])
def todo_mark_incomplete(id,curr_page):
    if not session.get('logged_in'):
        return redirect('/login')
    # g.db.execute("UPDATE todos SET complete = 0 WHERE id ='%s'" % id)
    # g.db.commit()

    # TASK-6 : SQL code replaced with SQLAlchemy code
    update_todo = db.session.query(Todos).filter_by(id=id).first()
    update_todo.complete = 0
    db.session.commit()

    # TASK-4 : modification done to redirect function parameter
    return redirect('/todos/1/'+curr_page+'/c')


# TASK-5 : This function executes whenever a user clicks a page number
@app.route('/todo/page/', methods=['POST'])
def todos_page_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    todos = get_todo_pagination(per_page_todo=5, page_num=1)
    return render_template('todos.html', todos=todos)


# TASK-3 : this function executes whenever json format of a to-do needs to be viewed
@app.route('/todo/<id>/<curr_page>/', methods=['POST'])
def todo_json(id, curr_page):
    if not session.get('logged_in'):
        return redirect('/login')

    todo = Todos.query.filter_by(id=id).first()
    todos = get_todo_pagination(per_page_todo=5, page_num=int(curr_page))

    return render_template('todos.html', todos=todos, json_dump=json.dumps([todo.serialize])[1:-1], json_todo_id=int(id))


# TASK-3 : this function executes whenever json format of a to-do needs to be hidden
@app.route('/todos/<curr_page>/hide', methods=['POST'])
def todo_hide(curr_page):
    if not session.get('logged_in'):
        return redirect('/login')

    todos = get_todo_pagination(per_page_todo=5, page_num=int(curr_page))
    return render_template('todos.html', todos=todos)


# TASK-5 : Pagination added
def get_todo_pagination(per_page_todo, page_num):
    user_id = session['user']['id']
    page = request.args.get('page', page_num, type=int)
    todos = Todos.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page_todo)
    return todos


