from flask import Flask, redirect, url_for, render_template, request, session
import datetime, bcrypt, pprint, pdb, os
from flask_mysqldb import MySQL
app = Flask(__name__)
app.secret_key = "7777777"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'secret11'
app.config['MYSQL_DB'] = 'flask_blog'
app.config["IMAGE_UPLOADS"] = "/Library/WebServer/Documents/flask_blog/static/uploads"


mysql = MySQL(app)

@app.route('/')
def index():
   date = datetime.datetime.now()
   cur = mysql.connection.cursor()
   cur.execute("SELECT * FROM blogs")
   data = cur.fetchall()
   cur.close()	
   return render_template('index.html',year = date.year, items = data)

@app.route('/create-blog' , methods=['POST', 'GET'])
def createBlog():
	if 'auth' not in session:
		return redirect(url_for('login'))
	if request.method == 'POST': 
		title = request.form['title']  
		description = request.form['description']
		image = request.files["image"]
		image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
		image = 'uploads/'+image.filename
		body = request.form['body']
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO blogs(title, description, image, body) VALUES (%s, %s, %s, %s)", (title, description, image, body))
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('admin'))
	else:
		return render_template('create-blog.html')		

@app.route('/update-blog/<int:num>', methods = ['POST','GET'])
def updateBlog(num):
	if 'auth' not in session:
		return redirect(url_for('login'))

	if request.method == 'POST': 
		title = request.form['title']  
		description = request.form['description']
		image = request.files["image"]
		imageurl = request.form['imageurl']
		
		if image.filename == '':
			image = imageurl
		else:
			image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
			image = 'uploads/'+image.filename
		body = request.form['body']
		cur = mysql.connection.cursor()
		cur.execute("UPDATE blogs SET title = %s ,description = %s, image= %s , body = %s WHERE id = %s ", (title,description, image, body, num))
		mysql.connection.commit()
		cur.close()
		done = " Successfully Updated Data !"
		return redirect(url_for('updateBlog', num =num))
	else:
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM blogs WHERE id = %s ", ( num, ))
		response = cur.fetchone()
		cur.close()
		return render_template('update-blog.html', data = response)

@app.route('/delete-blog/<int:num>')	
def deleteBlog(num):
	if 'auth' not in session:
		return redirect(url_for('login'))
	data = num
	cur = mysql.connection.cursor()
	cur.execute("DELETE FROM blogs WHERE id = %s ", ( num, ))
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('admin'))	

@app.route('/blogspot/<int:num>')
def blogspot(num):
   data = num
   cur = mysql.connection.cursor()
   cur.execute("SELECT * FROM blogs WHERE id = %s ", ( num, ))
   response = cur.fetchone()
   cur.close()
   # print(response[5].year)
   # exit()

   if response is None:
    raise Exception('Invalid Blog ID ')

   return render_template('blogspot.html', data = response)


@app.route('/admin')
def admin():
	if 'auth' in session:
		email = session['email']
		password = session['password']
		username = session['username']
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM blogs")
		data = cur.fetchall()
		cur.close()
		return render_template('admin.html', email=email, password=password, username=username, data = data)
	else:
		return redirect(url_for('login'))	


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
      email = request.form['email']
      password = request.form['password'].encode('utf-8')
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM users WHERE email = %s ", ( email, ) )
      response = cur.fetchone()
      cur.close()
      # print(response) 
      # exit()
      if response is None:
      	return render_template('login.html' , error = 'Non-existent Email' )
      
      if bcrypt.checkpw(password, response[3].encode('utf-8')):
      	session['auth'] = request.form['password']
      	session['email'] = response[2]
      	session['password'] = response[3]
      	session['username'] = response[1]
      else:	
      	# raise Exception('Invalid Email or Password')
      	return render_template('login.html' , error = 'Invalid Username or Password' )
      return redirect(url_for('admin'))
    else:
   	  return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password'].encode('utf-8')
		username = request.form['username']
		password = bcrypt.hashpw(password, bcrypt.gensalt())
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM users WHERE email = %s ", ( email, ) )
		response = cur.fetchone()
		if response is not None:
			return render_template('register.html' , error = 'Email already exists!' )
		cur.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)", (username, email, password))
		mysql.connection.commit()
		cur.close()
		session['auth'] = request.form['password']
		session['email'] = request.form['email']
		session['password'] = request.form['password']
		session['username'] = request.form['username']
		return redirect(url_for('admin'))
	else:
		return render_template('register.html')	

@app.route('/logout')
def logout():
	session.pop('auth', None)
	session.clear()
	return redirect(url_for('index'))		


if __name__ == '__main__':
   app.run(debug=True)
