#!/usr/bin/env python3

import os
from flask import Flask, render_template, redirect, url_for, request, session, escape, send_file
import datetime
import random
import MySQLdb
from datetime import datetime
import bcrypt

from io import BytesIO
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib.dates import DateFormatter,MinuteLocator,HourLocator
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from jinja2 import escape

app = Flask(__name__)
db_user = "costyusuf"
db_password = "password"
db_address = "localhost"
db_database = "costDevices"
app.secret_key = "verysecret"

@app.route('/init')
def init():
    """
        Delete all information
    """
    try:
        db = MySQLdb.connect(db_address, db_user, db_password, db_database)
    except:
        return "MYSQL not running"
    connection = db.cursor()
    try:
        connection.execute("delete from patioShade")
        #connection.execute("select * from patioShade")
        db.commit()
    except:
        db.rollback()
    db.close()
    return redirect("/")
    
@app.route("/update/", methods=["GET", "PUT"])
@app.route("/update/<appliance>", methods=["GET", "PUT"])
def update(appliance=None):
    if appliance == "kuptonShade":
        # return "usage: update/sensorid?temperature=VALUE"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        try:
            status = request.args.get('status')
            covered = request.args.get('covered')
            editedBy = request.args.get('editedBy')
            timestamp=datetime.now()
            query="update costDevices.patioShade set status = %s, shadeCovered = %s , editedby = %s, timestamp = %s where num = 1;"
            patioTuple=(status,covered,editedBy,timestamp)
            print(query)
            cursor.execute(query,patioTuple)
            db.commit()
        except:
            db.rollback()
            return "FAIL"
        db.close()
        return "OK"
    elif appliance == "samsungTv":
        # return "usage: update/sensorid?temperature=VALUE"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        try:
            status = request.args.get('status')
            tvChannel = request.args.get('channel')
            editedBy = request.args.get('editedBy')
            timestamp = datetime.now()
            query="update costDevices.samsungTv set status = %s, tvChannel = %s, editedby = %s, timestamp = %s where num = 1;"
            tvTuple=(status,tvChannel,editedBy,timestamp)
            print(query)
            cursor.execute(query,tvTuple)
            db.commit()
        except:
            db.rollback()
            return "FAIL"
        db.close()
        return "OK"

#login page
@app.route("/login", methods=["GET","POST", "PUT"])
def login():
    error = None
    if request.method == 'POST':
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database) 
        except:
            return "MYSQL not running"
        username = request.form['username'] #get username from login form
        password = request.form['password'] #get password from login form
        cursor = db.cursor()
        try:
            query=('''select password from users where username=%s;''')
            tuple1 = ([username]) 
            cursor.execute(query,tuple1) #prepared query
            hashedPwInDB = cursor.fetchone() #fetch output returned 
            if bcrypt.checkpw(password.encode('utf8'),hashedPwInDB[0].encode('utf8')): #checking password returned against hashed password in db
                session['username'] = request.form['username'] #set session username
                return redirect('/') #redirect if login success
            else: #password doesn't match
                error = 'Invalid password' 
            db.close()
        except Exception as e:
            db.rollback()
            print(str(e))
            error = 'Account does not exists' #no user in db matching username of input
            db.close()

    return render_template('login.html', error=error)

#sign up page
@app.route("/signup", methods=["GET","POST", "PUT"])
def signup():
    error = None
    if request.method == 'POST':
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        username = request.form['username'] #get username from signup form
        password = request.form['password'] #get password from signup form
        salt = bcrypt.gensalt() #generate salt
        hashedpw = bcrypt.hashpw(password.encode('utf8'),salt) #hash password using bcrypt with salt
        checkquery=('''select * from users where username=%s;''') #query to check if account with same username exists.
        checktuple = ([username]) 
        cursor.execute(checkquery,checktuple) #prepared query
        info = cursor.fetchone() #fetch output returned 
        if info == None: 
            if request.form['password'] != request.form['confirmpassword']: #checking if password matches confirm password
                error = 'Passwords do not match'
            else:
                if request.form['authorisationpw'] == "MyHomeIOTSensorDBAccessC0de": #checking if authorisation code matches string MyHomeIOTSensorDBAccessC0de
                    try:
                        query="insert into users(username,password) values (%s,%s);" #query to add user to db
                        tuple1 = (escape(username),hashedpw) 
                        cursor.execute(query,tuple1) #prepared query
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        print(str(e))
                        return "FAIL"
                        db.close()
                    return redirect('/login') #redirect to login

                else:
                    error = 'Authorisation password is incorrect.'
        else:
            error = 'Account already exists.'
                
    return render_template('signup.html', error=error) #render signup.html page from templates folder

@app.route("/updateuser" , methods=["GET","POST"])
def updateUser():
    error = None
    if 'username' in session:
        if request.method == 'POST':
            try:
                    db = MySQLdb.connect(db_address, db_user, db_password, db_database)
            except:
                    return "MYSQL not running"
            cursor = db.cursor()
            username = session['username'] #get username from session
            password = request.form['password'] #get password from change password form
            salt = bcrypt.gensalt() #generate salt
            hashedpw = bcrypt.hashpw(password.encode('utf8'),salt) #hash password using bcrypt with salt
            oldpassword = request.form['oldpassword'] #get current password from change password form
            checkquery=('''select password from users where username=%s;''')
            checktuple = ([username]) 
            cursor.execute(checkquery,checktuple) #prepared query
            checkCurrentPw = cursor.fetchone() #fetch output returned 

            if password != request.form['confirmpassword']: #checking if password matches confirm password
                error = 'Passwords do not match'
            elif bcrypt.checkpw(oldpassword.encode('utf8'),checkCurrentPw[0].encode('utf8')): #check if current password specified matches the one stored in db
                try:
                    query="update users set password = %s where username = %s;" #query to update password to db
                    tuple1 = (hashedpw,username) 
                    cursor.execute(query,tuple1) #prepared query
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(str(e))
                    return "FAIL"
                    db.close()
                return redirect('/login') #redirect to login
            
            else:
                error = 'Current password is incorrect'
        return render_template('modifyuser.html', error=error) #render webpage
    return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"

@app.route("/deleteuser" , methods=["GET","POST"])
def deleteUser():
    if 'username' in session:
            username = session['username']
            if request.method == 'POST':
                try:
                    db = MySQLdb.connect(db_address, db_user, db_password, db_database)
                except:
                    return "MYSQL not running"
                cursor = db.cursor()
                try:
                    query="delete from users where username = %s;" #query to add user to db
                    tuple1 = ([username]) 
                    cursor.execute(query,tuple1) #prepared query
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(str(e))
                    return "FAIL"
                    db.close()
                session.pop('username', None)
                return redirect('/login') #redirect to login

            return render_template('deleteuser.html') #render webpage
    return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"

@app.route("/usersettings")
def userSettings():
    if 'username' in session:
            username = session['username']

            return '<h1>Account Settings</h1>' +'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>" + """
           
           <br><br>
           <a href="/updateuser" "="">
            <button>Change Password</button>
            </a>

            <br><br>

            <a href="/deleteuser" "="">
            <button>Delete Account</button>
            </a>
           """
    return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"
            





#index page
@app.route("/", methods=["GET", "PUT"])
def default():
    
    if 'username' in session:
        username = session['username']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>" + "<br><b><a href = '/usersettings'>click here to update account settings</a></b>" + """
                <!DOCTYPE html>
                <html>
                <body>
                <h1>Index Page</h1>
                <p1>Please select a DB to view</p1>
                <br>
                  <a href="/tvappliance" "="">TV Appliance DB</a>
                  <br>
                  <a href="/patioshade" "="">Patio Shade DB</a> 
                  <br>
                  <a href="/temp" "="">Temperature sensor DB</a> 
                </body>
                </html>
             """
    return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"
 


@app.route("/add/", methods=["GET", "PUT"])
@app.route("/add/<appliance>", methods=["GET", "PUT"])
def add(appliance=None):
    if appliance == "kuptonShade":
        # return "usage: update/sensorid?temperature=VALUE"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        try:
            status = request.args.get('status')
            covered = request.args.get('covered')
            editedBy = request.args.get('editedBy')
            timestamp = datetime.now()
            query="insert into costDevices.patioShade(appliance,status,shadeCovered,editedBy,timeStamp) values (%s,%s,%s,%s,%s);"
            print(query)
            shadeTuple = (appliance,status,covered,editedBy,timestamp) #prepared stmt
            cursor.execute(query,shadeTuple)
            db.commit()
        except:
            db.rollback()
            return "FAIL"
        db.close()
        return "OK"
    elif appliance == "samsungTv":
        # return "usage: update/sensorid?temperature=VALUE"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        try:
            status = request.args.get('status')
            channel = str(request.args.get('channel'))
            editedBy = request.args.get('editedBy')
            timestamp = datetime.now()
            query="insert into costDevices.samsungTv(appliance,status,tvChannel,editedBy,timeStamp) values (%s,%s,%s,%s,%s);"
            print(query)
            tvTuple = (appliance,status,channel,editedBy,timestamp)
            cursor.execute(query,tvTuple)
            db.commit()
        except:
            db.rollback()
            return "FAIL"
        db.close()
        return "OK"

    elif appliance == "tempSensor":
        # return "usage: update/sensorid?temperature=VALUE"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        try:
            temperature_reading = request.args.get('temp')
            sensorCategoryStr = request.args.get('category')
            query="insert into temperaturesensor(temperature,category) values (%s,%s);"
            tempsensorTuple = (temperature_reading,sensorCategoryStr)
            print(query)
            cursor.execute(query,tempsensorTuple)
            db.commit()
        except Exception as e:
            db.rollback()
            print(str(e))
            return "FAIL"
        db.close()
        return "OK"

    elif appliance == "airconRemote":
         # return "usage: update/sensorid?temperature=VALUE"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        try:
            increase_decrease=request.args.get('temp_action')
            query="insert into iotsensor(state) values (%s);"
            airconTuple=([increase_decrease])
            print(query)
            cursor.execute(query,airconTuple)
            db.commit()
        except Exception as e:
            db.rollback()
            print(str(e))
            return "FAIL"
        db.close()
        return "OK"

            

#Function to display the database
@app.route("/temp", methods=["GET", "PUT"])
def displayTemp():
    """
        Show list of comments with form to submit comments
    """
    if 'username' in session:
        username = session['username']
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from temperaturesensor''')
        comments = cursor.fetchall()
    
        completeTable="<tr >"
        completeTable += "<th> ID </th>"
        completeTable += "<th> Timestamp </th>"
        completeTable += "<th> Temperature </th>"
        completeTable += "<th> Category </th>"
        completeTable += "<th> Status </th>"
        completeTable+="</tr>"
        for c in comments:
            completeTable+="<tr >"
            completeTable += "<th>" + str(c[0]) + "</th>" #ID Column
            completeTable += "<th>" + str(c[1]) + "</th>" #Timestamp Column
            completeTable += "<th>" + str(c[2]) + "</th>" #Temperature Column
            completeTable += "<th>" + str(c[3]) + "</th>" #Category Column
            completeTable += "<th> ON </th>" #Status Column
            completeTable+="</tr>"

        cursor = db.cursor()
        cursor.execute('''select * from iotsensor''')
        comments2 = cursor.fetchall()
        db.close()
        completeTable2="<tr >"
        completeTable2 += "<th> ID </th>"
        completeTable2 += "<th> Timestamp </th>"
        completeTable2 += "<th> Increase/Decrease </th>"
        completeTable2+="</tr>"
        for c in comments2:
            completeTable2+="<tr >"
            completeTable2 += "<th>" + str(c[0]) + "</th>"
            completeTable2 += "<th>" + str(c[1]) + "</th>"
            completeTable2 += "<th>" + str(c[2]) + "</th>"

        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>" + """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Temperature Sensor Data</h1>
            <table border=\"1\">
            %s
            </table>
            <h1>Aircon Remote Data</h1>
            <table border=\"1\">
        %s
            </table>
            <br>
            <div>
            <a href="/" "="">
            <button>Return to Index</button>
            </div>
            <div>
            <br>
            </a>
            <a href="/temp/graphs" "="">
            <button>Analyse Data</button>
            </a>
            </div>
        </body>
        </html>
        """ %(completeTable, completeTable2)
    return "Please login to access database. <br><a href = '/login'>" + "click here to log in</a>"


#Function to display the graphs and charts created
@app.route("/temp/graphs")
def showGraphs():
    if 'username' in session:
        username = session['username']
        return """


        <!DOCTYPE html>
        <html>
        <body>
            <h1>Temperature Reading Graph</h1>
            <img src="image">
            <h1>Temperature Range Pie Chart</h1>
            <img src="image2">
        </body>
        </html>
        """
    return "Please login to access database. <br><a href = '/login'>" + "click here to log in</a>"

#Function to create graph
@app.route("/temp/image")
def showImage():
     if 'username' in session:
        username = session['username']
        """
            Show list of comments with form to submit comments
        """
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from temperaturesensor''')
        comments = cursor.fetchall()
        index = 0
        timestampList = []
        temperatureList = []
        for c in comments:
            index = index+1
            if index <= len(comments):
                dateTime = datetime.strptime(str(c[1]), "%Y-%m-%d %H:%M:%S")
                temperatureList.append(int(c[2]))
                timestampList.append(dateTime)

        figure = plt.figure()
        axes = figure.add_subplot(1,1,1)
        axes.plot(timestampList, temperatureList)
        axes.set_title('Temperature Sensor Reading')
        timeFormat = DateFormatter('%H:%M')
        axes.set_xlabel('Time (Every 10 minutes interval)')
        axes.set_ylabel('Temperature')
        axes.xaxis.set_major_formatter(timeFormat)
        axes.xaxis.set_major_locator(MinuteLocator(interval=10))
        stream = BytesIO()
        figure.savefig(stream)
        stream.seek(0)
        return send_file(stream, mimetype='image/png')
     return "Please login to access database. <br><a href = '/login'>" + "click here to log in</a>"
        

#Function to create piechart
@app.route("/temp/image2")
def showImage2():
    if 'username' in session:
        username = session['username']
        """
            Show list of comments with form to submit comments
        """
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from temperaturesensor''')
        comments = cursor.fetchall()
        index = 0
        hotCounter = 0
        averageCounter = 0
        gettingColdCounter = 0
        coldCounter = 0
        for c in comments:
            print(c)
            index = index+1
            if index <= len(comments):
                if int(c[2]) >= 30 and int(c[2]) <= 35:
                    hotCounter = hotCounter+1
                    print(hotCounter)
                elif int(c[2]) >= 26 and int(c[2]) <= 29:
                    averageCounter = averageCounter+1
                    print("I am working2")
                elif int(c[2]) >= 23 and int(c[2]) <= 25:
                    gettingColdCounter = gettingColdCounter+1
                elif int(c[2]) <= 22:
                    coldCounter = coldCounter+1
        temperatureRangeList = [(hotCounter), (averageCounter), (gettingColdCounter), (coldCounter)]
        category = ['HOT \n(30°C - 35°C)', 'AVERAGE \n(26°C - 29°C)', 'GETTING COLD \n(23°C - 25°C)', 'COLD \n(<22°C)']

        figure, ax = plt.subplots()
        ax.pie(temperatureRangeList, labels = category, autopct='%.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Temperature Range Chart')
        stream = BytesIO()
        figure.savefig(stream)
        stream.seek(0)
        return send_file(stream, mimetype='image/png')
    return "Please login to access database. <br><a href = '/login'>" + "click here to log in</a>"


@app.route("/patioshade", methods=["GET", "PUT"])
def displayPatioShade():
    """
        Show list of comments with form to submit comments
    """
    if 'username' in session:
        username = session['username']
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from patioShade where num = 1''')
        comments = cursor.fetchall()
        db.close()
        completeTable="<tr >"
        completeTable += "<th> No. </th>"
        completeTable += "<th> Appliance </th>"
        completeTable += "<th> Status </th>"
        completeTable += "<th> Shade Covered </th>"
        completeTable += "<th> Edited By </th>"
        completeTable += "<th> Timestamp </th>"
        completeTable+="</tr>"
        for c in comments:
            completeTable+="<tr >"
            completeTable += "<th>" + str(c[0]) + "</th>"
            completeTable += "<th>" + str(c[1]) + "</th>"
            completeTable += "<th>" + str(c[2]) + "</th>"
            completeTable += "<th>" + str(c[3]) + "</th>"
            completeTable += "<th>" + str(c[4]) + "</th>"
            completeTable += "<th>" + str(c[5]) + "</th>"
            completeTable+="</tr>"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from patioShade WHERE NOT num = 1''')
        comments = cursor.fetchall()
        db.close()
        completeTableLogs="<tr >"
        completeTableLogs += "<th> No. </th>"
        completeTableLogs += "<th> Appliance </th>"
        completeTableLogs += "<th> Status </th>"
        completeTableLogs += "<th> Shade Covered </th>"
        completeTableLogs += "<th> Edited By </th>"
        completeTableLogs += "<th> Timestamp </th>"
        completeTableLogs+="</tr>"
        for c in comments:
            completeTableLogs+="<tr >"
            completeTableLogs += "<th>" + str(c[0]) + "</th>"
            completeTableLogs += "<th>" + str(c[1]) + "</th>"
            completeTableLogs += "<th>" + str(c[2]) + "</th>"
            completeTableLogs += "<th>" + str(c[3]) + "</th>"
            completeTableLogs += "<th>" + str(c[4]) + "</th>"
            completeTableLogs += "<th>" + str(c[5]) + "</th>"
            completeTableLogs+="</tr>"


        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>" + """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Sensors data LIVE</h1>
            <table border=\"1\">
            %s
            </table>
            <br>
            <h1>Sensors data Logs</h1>
            <table border=\"1\">
            %s
            </table>
            <br>
             <div>
        <a href="/" "="">
        <button>Return to Index</button>
        </a>
        </div>
        </body>
        </html>
        """ %(completeTable, completeTableLogs)
    return "Please login to access database. <br><a href = '/login'>" + "click here to log in</a>"

@app.route("/users", methods=["GET", "PUT"])
def displayUser():
    """
        Show list of comments with form to submit comments
    """

    try:
        db = MySQLdb.connect(db_address, db_user, db_password, db_database)
    except:
        return "MYSQL not running"
    cursor = db.cursor()
    cursor.execute('''select * from users ''')
    comments = cursor.fetchall()
    db.close()
    completeTable="<tr >"
    completeTable += "<th> No. </th>"
    completeTable += "<th> Username </th>"
    completeTable += "<th> Password </th>"
    completeTable+="</tr>"
    for c in comments:
        completeTable+="<tr >"
        completeTable += "<th>" + str(c[0]) + "</th>"
        completeTable += "<th>" + str(c[1]) + "</th>"
        completeTable += "<th>" + str(c[2]) + "</th>"
        completeTable+="</tr>"
        
    return """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>User data</h1>
            <table border=\"1\">
            %s
            </table>
            <br>
            <br>
            <div>
            <a href="/" "="">
            <button>Return to Index</button>
            </a>
            </div>
        </body>
        </html>
        """ %(completeTable)


@app.route("/tvappliance", methods=["GET", "PUT"])
def displayTv():
    """
        Show list of comments with form to submit comments
    """
    if 'username' in session:
        username = session['username']
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from samsungTv where num = 1''')
        comments = cursor.fetchall()
        db.close()
        completeTable="<tr >"
        completeTable += "<th> No. </th>"
        completeTable += "<th> Appliance </th>"
        completeTable += "<th> Status </th>"
        completeTable += "<th> Tv Channel </th>"
        completeTable += "<th> Edited By </th>"
        completeTable += "<th> Timestamp </th>"
        completeTable+="</tr>"
        for c in comments:
            completeTable+="<tr >"
            completeTable += "<th>" + str(c[0]) + "</th>"
            completeTable += "<th>" + str(c[1]) + "</th>"
            completeTable += "<th>" + str(c[2]) + "</th>"
            completeTable += "<th>" + str(c[3]) + "</th>"
            completeTable += "<th>" + str(c[4]) + "</th>"
            completeTable += "<th>" + str(c[5]) + "</th>"
            completeTable+="</tr>"
        try:
            db = MySQLdb.connect(db_address, db_user, db_password, db_database)
        except:
            return "MYSQL not running"
        cursor = db.cursor()
        cursor.execute('''select * from samsungTv WHERE NOT num = 1''')
        comments = cursor.fetchall()
        db.close()
        completeTableLogs="<tr >"
        completeTableLogs += "<th> No. </th>"
        completeTableLogs += "<th> Appliance </th>"
        completeTableLogs += "<th> Status </th>"
        completeTableLogs += "<th> Tv Channel </th>"
        completeTableLogs += "<th> Edited By </th>"
        completeTableLogs += "<th> Timestamp </th>"
        completeTableLogs+="</tr>"
        for c in comments:
            completeTableLogs+="<tr >"
            completeTableLogs += "<th>" + str(c[0]) + "</th>"
            completeTableLogs += "<th>" + str(c[1]) + "</th>"
            completeTableLogs += "<th>" + str(c[2]) + "</th>"
            completeTableLogs += "<th>" + str(c[3]) + "</th>"
            completeTableLogs += "<th>" + str(c[4]) + "</th>"
            completeTableLogs += "<th>" + str(c[5]) + "</th>"
            completeTableLogs+="</tr>"


        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>" +  """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Smart TV data LIVE</h1>
            <table border=\"1\">
            %s
            </table>
            <br>
            <h1>Smart TV data Logs</h1>
            <table border=\"1\">
            %s
            </table>
            <br>
            <div>
            <a href="/" "="">
            <button>Return to Index</button>
            </a>
            </div>
        </body>
        </html>
        """ %(completeTable, completeTableLogs)
    return "Please login to access database. <br><a href = '/login'>" + "click here to log in</a>"



@app.route("/logout", methods=["GET","POST"])
def logout():
    session.pop('username', None)
    return redirect('/')



if __name__ == "__main__":
    host = os.getenv("IP", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    app.run(host=host, port=port, debug=False, use_reloader=True, use_evalex=False)