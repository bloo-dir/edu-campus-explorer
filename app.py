from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__, template_folder='C:\\Users\\gbnat\\Desktop\\projets\\Python\\Application_Web\\School_abroad_optz\\templates')
app.secret_key = 'your_secret_key'
app.config['SQALCHEMY_DATABASE_URI']='postgres://mxpenaloywdtep:4cb5b60c55012cff5dd4f428839dba2b074c58b6d3d45e5c79011dd761542d06@ec2-3-217-146-37.compute-1.amazonaws.com:5432/d7mpq9hl1oqkvk'

# Connect to the database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="",
    database="sql"
)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index_director')
def index_director():
    return render_template('index_director.html')
    
@app.route('/register')
def register():
    cur = db.cursor()
    
    # Retrieve all campuses
    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()  # Fetch all rows from the query result
    cur.close()
    
    return render_template('register.html', categories=categories)


@app.route('/registersave', methods=['POST'])
def registersave():
    email = request.form['email']
    password = request.form['password']
    category = request.form['choice']

    cur = db.cursor()
    sql = "INSERT INTO users(Mail, Password, categoryName) VALUES (%s, %s, %s)"
    val = (email, password, category)
    cur.execute(sql, val)
    db.commit()

    cur.close()
    
    message = "New account created."
    return render_template('index.html', message=message)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        category = request.form['choice']

        cur = db.cursor()

        sql_login = "SELECT * FROM users WHERE Mail = %s AND Password = %s AND categoryName = %s"
        val = (email, password, category)
        cur.execute(sql_login, val)

        user = cur.fetchone()

        cur.close()

        if user:
            session['email'] = email
            if category == "Student":
                return redirect('/wish_add')
            else:
                return redirect('/index_director')
        else:
            cur = db.cursor()
            cur.execute("SELECT * FROM category")
            categories = cur.fetchall()
            cur.close()
            return render_template('login.html', message='Email or password incorrect', categories=categories)
    else:
        cur = db.cursor()
        cur.execute("SELECT * FROM category")
        categories = cur.fetchall()
        cur.close()

        return render_template('login.html', categories=categories)

@app.route('/user_list')
def user_list():
    # Check if the user is logged in by checking the session key
    if 'email' in session:
        # Retrieve the user's campus choices from the database
        # and pass the data to the list.html page for display
        return render_template('list.html', choices=choices_from_database)
    else:
        return redirect(url_for('index'))

@app.route('/wish_list')
def wish_list():
    cur = db.cursor()
 
    # You must complete the below SQL select query
    cur.execute("SELECT idCampus, campusName, studentMail FROM Campus INNER JOIN mobilitywish ON campus.idCampus = mobilitywish.Campus_idCampus;")
    results = cur.fetchall()
    cur.close()
    
    return render_template('wish_list.html', results=results)

# Add a choice
@app.route('/wish_add')
def wish_add():
    cur = db.cursor()
    
    # Retrieve all campuses
    cur.execute("SELECT * FROM campus")
    categories = cur.fetchall()  # Fetch all rows from the query result
    cur.close()
    
    return render_template('wish_add.html', categories=categories)

@app.route('/wish_save', methods=['POST'])
def wish_save():
    email = session['email']  # Retrieve email from session
    city = request.form['choice']  # Retrieve campus choice from form

    cur = db.cursor()

    # Check if the campus name is valid
    sql_campus_id = "SELECT idCampus FROM campus WHERE campusName = %s"
    cur.execute(sql_campus_id, (city,))
    result = cur.fetchone()

    idCampus = result[0]
    # Insert the record into the mobilitywish table with the campus ID and email
    sql_save = "INSERT INTO mobilitywish(studentMail, Campus_idCampus) VALUES (%s, %s)"
    val = (email, idCampus)
    cur.execute(sql_save, val)
    db.commit()

    cur.close()

    message = "Record inserted."
    return render_template('index.html', message=message)
    
# Add a campus
@app.route('/addcamp', methods=['GET', 'POST'])
def addcamp():
    if request.method == 'POST':
        campus_name = request.form['campus']

        # Data validation
        if not campus_name:
            return "Please enter a campus name."

        cursor = db.cursor()
        query = "INSERT INTO campus (campusName) VALUES (%s)"
        values = (campus_name,)

        try:
            cursor.execute(query, values)
            db.commit()
            cursor.close()
            return render_template('index_director.html', message="The campus has been added successfully.")
        except Exception as e:
            cursor.close()
            return "An error occurred while adding the campus: " + str(e)

    return render_template('add_campus.html')

# Run the Flask application
if __name__ == '__main__':
    app.run()