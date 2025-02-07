from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, send_from_directory
import pymysql.cursors
import webbrowser
from selenium import webdriver
import json
import os
from datetime import datetime, date
from config import host, user, password, database


def connect_db():
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 database=database,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

app = Flask(__name__)
app.config['SECRET_KEY'] = '12304560'
app.config['UPLOAD_FOLDER'] = "static/pictures/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@app.route("/login", methods=["POST", "GET"])
def login():
    data = request.json
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select `login`, `psw` from `users`")
        info = cursor.fetchall()
    for i in info:
        if i['login'] == data['value'][0] and i['psw'] == data['value'][1]:
            return {1: True}
    # cursor.execute("insert into `users` ")
    return {1: False}

@app.route("/ask/<int:course>", methods=["POST", "GET"])
def ask(course):
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select question from `tests` where courses_id = %s", course)
        info = cursor.fetchall()
        print(info)
    return info

@app.route("/new/<int:course>", methods=["POST", "GET"])
def new(course):
    print(request.json)
    data = request.json

    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select `answer` from `tests` where courses_id = %s", course)
        info = cursor.fetchall()
    correct = 0
    for i in range(7):
        if data['value'][i].lower() == str(info[i]['answer']): 
            correct += 1
    return {1: round(correct / 7 * 100)}


# @app.route("/get/<int:course>", methods=["POST", "GET"])
# def get(course):
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select * from `courses` where id = %s", course)
        info = cursor.fetchall()
        print(info)
    return info

# Debug
@app.route("/test", methods=["POST", "GET"])
def test():
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select * from courses;")
        info = cursor.fetchall()
    return info


# @app.route("/get/<int:card>", methods=["POST", "GET"])
# def get(card):
#     connection = get_db()
#     with connection.cursor() as cursor:
#         cursor.execute("select * from `product` where id = %s", card)
#         info = cursor.fetchall()
#         print(info)
#     return info


# @app.route("/index", methods=['POST', 'GET'])
# @app.route("/", methods=['POST', 'GET'])
# def index():
#     # if 'login' not in session:
#     #     return redirect(url_for('login'))
#     if request.method == 'POST':
#         connection = get_db()
#         with connection.cursor() as cursor:
#             cursor.execute("select * from product where `name` like %s or `description` like %s ",
#                            ('%' + request.form['search'] + '%', '%' + request.form['search'] + '%'))
#             info = cursor.fetchall()
#             flash(info)

#     return render_template('index.html', title='Main', role=session['role'], login=session['login'])


# @app.route("/login", methods=['POST', 'GET'])
# def login():
#     if 'login' in session:
#         return redirect(url_for('index'))
#     elif request.method == 'POST':
#         connection = get_db()
#         with connection.cursor() as cursor:
#             cursor.execute("select login, psw from users;")
#             for row in cursor.fetchall():
#                 count = 0
#                 for key, value in row.items():
#                     if count == 0:
#                         login_enter = value
#                     elif count == 1:
#                         password_enter = value
#                         if request.form['login'] == login_enter and request.form['psw'] == password_enter:
#                             session['login'] = request.form['login']
#                             # return redirect('localhost:3000/catalog')
#                             # webbrowser.open('localhost:3000/catalog', new=0, autoraise=True)
#                             # webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser('C:\Program Files\Google\Chrome\Application\chrome.exe'))
#                             # webbrowser.get(using='Chrome').open_new_tab('localhost:3000/catalog')
#                             # webbrowser.get(using='chrome').open_new_tab('localhost:3000/catalog')
#                             driver = webdriver.Chrome()
#                             # driver.get("localhost:3000/catalog")
#                             # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
#                             # driver.switch_to.window(driver.window_handles[1])
#                             # driver.quit()
#                             driver.execute_script(f"window.open('localhost:3000/catalog')")
#                             print("GGGGGGGGGGGGGGG")
#                             return 0
#                         elif request.form['login'] == login_enter and request.form['psw'] != password_enter:
#                             flash('Incorrect password')

#                         count = -1
#                     count += 1
#         flash('Login is not registered')
#     return render_template('login.html', title='Login')


# @app.route("/registration", methods=['POST', 'GET'])
# def registration():
#     if 'login' in session:
#         return redirect(url_for('index'))

#     elif request.method == 'POST':
#         connection = get_db()
#         with connection.cursor() as cursor:
#             cursor.execute("select login from users;")

#             # Check for used login
#             for row in cursor.fetchall():
#                 if request.form['login'] in row.values():
#                     flash("Login is used")
#                     return redirect(url_for('registration'))

#             # Add information into database
#             cursor.execute("insert into `users`(`login`, `psw`)"
#                            "values(%s, %s) ON DUPLICATE KEY update `login` = `login`",
#                            (request.form['login'], request.form['psw']))
#             connection.commit()
#             return redirect(url_for('login'))
#     return render_template('registration.html', title='Registration')


@app.route("/store", methods=["POST", "GET"])
def store():
    if 'login' not in session:
        return redirect(url_for('login'))
    connection = get_db()

    with connection.cursor() as cursor:
        cursor.execute("select * from product;")
        info = cursor.fetchall()
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("insert into `cart`(`users_login`, `product_id`, `value`)"
                           "values(%s, %s, %s) ON DUPLICATE KEY update `value` = `value` + 1",
                           (session['login'], request.form['id'], 1))
            connection.commit()
            return redirect(url_for('profile', login=session['login']))
    return render_template('store.html', title='Store', cursor=info, role=session['role'],
                           login=session['login'])


@app.route("/products", methods=['POST', 'GET'])
def products():
    if session['role'] != 'admin':
        return redirect(url_for('index'))
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select * from product;")
        list_products = cursor.fetchall()
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['name'] + '.jpg'))
        with connection.cursor() as cursor:
            cursor.execute("insert into product(name, price, description, value, photo) "
                           "values(%s, %s, %s, %s, %s)",
                           (request.form['name'], request.form['price'],
                            request.form['description'], request.form['value'],
                            os.path.join(app.config['UPLOAD_FOLDER'], request.form['name'] + '.jpg')))
            connection.commit()

        return redirect(url_for('products'))
    return render_template('products.html', title='Products', list_products=list_products,
                           role=session['role'], login=session['login'])


@app.route("/reports", methods=['POST', 'GET'])
def reports():
    if session['role'] != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        connection = get_db()
        with connection.cursor() as cursor:
            if request.form['report'] == '1':
                cursor.execute("select `product_id`,count(`product_id`) as `count ordered`"
                               "from `orders`"
                               "group by `product_id`"
                               "order by count(*) DESC")
                msg = cursor.fetchall()
                flash(msg, '1')

            elif request.form['report'] == '2':
                cursor.execute("select * from users")
                msg = cursor.fetchall()
                flash(msg, '2')

            elif request.form['report'] == '3':
                cursor.execute("select `product_id`, max(`value`) as `count value`"
                               "from `orders`"
                               "group by `product_id`"
                               "order by max(value) DESC")
                msg = cursor.fetchall()
                flash(msg, '3')

            elif request.form['report'] == '4':
                cursor.execute("select *"
                               "from `orders`"
                               "where (`users_login`, `date`, `time`) in ("
                               "    select `users_login`, `date`, `time`"
                               "    from `orders`"
                               "    where `id` in ("
                               "        select max(id)"
                               "        from `orders`))")
                msg = cursor.fetchall()
                flash(msg, '4')
        return redirect(url_for('reports'))
    return render_template('reports.html', title='Reports',
                           role=session['role'], login=session['login'])


@app.route("/product/<int:id_product>")
def product(id_product):
    if 'login' not in session:
        return redirect(url_for('login'))
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(f"select * from product where id = {id_product}")
        info = cursor.fetchone()
    if info is None:
        abort(404)
    return render_template('product.html', title=f"Product {info['name']}",
                           row=info, role=session['role'], login=session['login'])


@app.route("/profile/<login>", methods=['POST', 'GET'])
def profile(login):
    if 'login' not in session:
        return redirect(url_for('login'))
    if session['login'] != login:
        abort(401)
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("select * from `product` "
                       "where `id` in "
                       "(select `product_id` from `cart` where `users_login` = %s)", login)
        cart = cursor.fetchall()

        # For ordered values products
        cursor.execute("select `product_id`, `value` from `cart`"
                       "where `users_login` = %s", login)
        value_product = cursor.fetchall()
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Out cart 1 product
            cursor.execute("update `cart` "
                           "set value = value - 1 "
                           "where product_id = %s and if(value<>0, 'yes', 'no') = 'yes'", request.form['id'])

            # if value product = 0 => delete product from cart
            cursor.execute("delete "
                           "from cart "
                           "where product_id = %s and if(value=0, 'yes', 'no') = 'yes'", request.form['id'])
            connection.commit()
            return redirect(url_for('profile', login=session['login']))
    return render_template('profile.html', title=f"Profile {login}", cart=cart,
                           role=session['role'], login=session['login'], value_product=value_product)


@app.route("/profile/<login>/purchase", methods=['POST', 'GET'])
def purchase(login):
    if 'login' not in session:
        return redirect(url_for('login'))
    now = datetime.now()
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("insert into `orders` (`users_login`, `product_id`, `value`, `date`, `time`)"
                       "select `users_login`, `product_id`, `value`, %s, %s from `cart` where users_login = %s",
                       (date.today(), f"{str(now.hour)}:{str(now.minute)}", session['login']))
        connection.commit()

        cursor.execute("delete from cart where `users_login` = %s", session['login'])
        connection.commit()

    return redirect(url_for('profile', login=session['login']))


@app.route("/products/delete", methods=['POST', 'GET'])
def delete_product():
    if session['role'] != 'admin':
        redirect(url_for('index'))
    if request.method == 'POST':
        connection = get_db()
        with connection.cursor() as cursor:
            cursor.execute("delete from product where id = %s", request.form['id'])
            connection.commit()
    return redirect(url_for('products'))


@app.errorhandler(404)
def page_not_found(error):
    # if 'login' not in session:
    #     return redirect(url_for('login'))
    return render_template('page404.html', title='Page not found', role=session['role'],
                           login=session['login']), 404


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
