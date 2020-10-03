from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail
import json
from datetime import datetime
now = datetime.now()
cdatetime = now.strftime('%Y-%m-%d %H:%M:%S')

with open('config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.secret_key = params['secret-key']

# mail config 
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
# db config 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'alm'

mysql = MySQL(app)

# ================== app route ======================
# fontend route 
@app.route("/")
def home():
    return render_template('index.html', params=params)

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/services")
def services():
    return render_template('services.html',params=params)

@app.route("/service_detail")
def service_detail():
    return render_template('service_detail.html',params=params)

@app.route("/blogs")
def blogs():
    return render_template('blogs.html',params=params)

@app.route("/blog-detail")
def blog_detail():
    return render_template('blog_detail.html',params=params)

@app.route("/contact", methods=['GET','POST'])
def contact():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts(name, email,message) VALUES (%s, %s, %s)", (name, email, message))
        mysql.connection.commit()
        cur.close()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message 
                          )
        flash('Thank you for contact us... ','success')
        return redirect(url_for('contact'))
    else:
        error='failed.'
    return render_template('contact.html',error=error,params=params)

# backend route 
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    msg=''

    if 'loggedin' in session:
          return render_template('dashboard.html',params=params,username=session['user'])

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT username, password FROM users WHERE username=%s AND password=%s AND status=%s",(username,password,1))
        data = cur.fetchone()
        if data:
            session['loggedin'] = True
            session['id'] = data[0]
            session['user'] = data[1]
            return render_template('dashboard.html',params=params,username=session['user'])
        else:
            msg = 'Incorrect Username/Passwrod!'


    return render_template('login.html',params=params,msg=msg)

@app.route('/dashboard/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('user', None)
   # Redirect to login page
   return redirect(url_for('dashboard'))

@app.route('/dashboard-about/<string:id>',methods=['GET','POST'])
def dashboard_about(id):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM about WHERE id=%s AND status=%s",(1,1))
        data = cur.fetchall()
        data = data.json_encoder()
        if data:
            return render_template('dashboard-about.html',params=params,username=session['user'],id=id,data=data)
    return render_template('login.html',params=params)

@app.route('/dashboard-services',methods=['GET','POST'])
def dashboard_services():
    if 'loggedin' in session:
        return render_template('dashboard-services.html',params=params,username=session['user'])
    return render_template('login.html',params=params)

@app.route('/dashboard-blogs',methods=['GET','POST'])
def dashboard_blogs():
    if 'loggedin' in session:
        return render_template('dashboard-blogs.html',params=params,username=session['user'])
    return render_template('login.html',params=params)

@app.route('/dashboard-contacts',methods=['GET','POST'])
def dashboard_contacts():
    if 'loggedin' in session:
        return render_template('dashboard-contacts.html',params=params,username=session['user'])
    return render_template('login.html',params=params)
app.run(debug=True)