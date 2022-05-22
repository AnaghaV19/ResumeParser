from flask import Flask,render_template,request,redirect,url_for,session
from flask import request
from werkzeug.utils import secure_filename
import pathlib
import numpy as np
import MySQLdb
import requests
from flask import send_file
import os
import flask
import test as sc
from flask_mysqldb import MySQL
import MySQLdb.cursors
import cli as resumeextraction
import csv
import Prediction as pre
import scorecalc as sc
import ms as mail
from itertools import chain

app = Flask(__name__)
UPLOAD_FOLDER = './resume'
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = 'localhost'
#MySQL username
app.config['MYSQL_USER'] = 'root'
#MySQL password here in my case password is null so i left empty
app.config['MYSQL_PASSWORD'] = 'root'
#Database name In my case database name is projectreporting
app.config['MYSQL_DB'] = 'rss'
basedir = os.path.abspath(os.path.dirname(__file__))
data_file = os.path.join(basedir, 'resume')

ALLOWED_EXTENSIONS = {'pdf'}
mydb = MySQLdb.connect(host='localhost',user='root',passwd='root',db='rss')
conn = mydb.cursor()
mysql = MySQL(app)
    
@app.route("/") #home
def hello():
        return render_template("index.html")
@app.route("/sendsms") 
def sendsms():
        ids=[]
        jobtitle=session.get('jobtitle')
        requiredskills=session.get('skills')
        tskills=session.get('tskills')
        requiredskills+=tskills
        novc=session.get('nov')
        
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from resu where score !=0 order by score desc limit 10")
        #fetching all records from database
        data=cursor.fetchall()
        for row in data:
           print("row=",row)
           
           mobile=row['mono']
           pname=row['pname']
           email=row['email']
           
           ids.append(row['id'])
           #fname.append(row['sys_fname'])
           url = "https://www.fast2sms.com/dev/bulk"
           print("Selected Mobile Number==",mobile)
           msg="Dear "+pname+"Your Resume is shortlisted for Interview"+jobtitle
           payload = "sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+mobile
           headers = {'authorization':"6fXPjBRsFTnAaHytmqxepiQ2ZIKulJYgS043voz5UWLNMwhrCO8oAim6ZkTD1nyBcNS4MugqH3Qa95Yx",'Content-Type': "application/x-www-form-urlencoded",'Cache-Control': "no-cache",}
           response = requests.request("POST", url, data=payload, headers=headers)
           print(response.text)
           mail.process(email,msg)
        #rfname=[]
        cursor1=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        #print("Rejected file name==",rname)
        cursor1.execute("SELECT * FROM resu")
        #fetching all records from database
        data1=cursor1.fetchall()
        
        for row1 in data1:
                ides=row1['id']
                if ides not in ids:
                        
                        mobile1=row1['mono']
                        pname1=row1['pname']
                        email1=row1['email']
                        url1 = "https://www.fast2sms.com/dev/bulk"
                        print("Reject Mobile number==",mobile1)
                        msg1="Dear "+pname1+"Your Resume is Rejected  for Interview "+jobtitle+"You need to improve in "+requiredskills
                        payload1 = "sender_id=FSTSMS&message="+msg1+"&language=english&route=p&numbers="+mobile1
                        headers1 = {'authorization':"6fXPjBRsFTnAaHytmqxepiQ2ZIKulJYgS043voz5UWLNMwhrCO8oAim6ZkTD1nyBcNS4MugqH3Qa95Yx",'Content-Type': "application/x-www-form-urlencoded",'Cache-Control': "no-cache",}
                        response1 = requests.request("POST", url1, data=payload1, headers=headers1)
                        print(response1.text)
                        mail.process(email1,msg1)
                else:
                        print("Id Not found")
   

        return render_template("rlogin.html")

@app.route("/rlogin") 
def rlogin():
        return render_template("rlogin.html")
@app.route("/ulogin") 
def ulogin():
        return render_template("ulogin.html")
@app.route("/ureg") 
def ureg():
        return render_template("ureg.html")
@app.route("/upresume") 
def upresume():
        return render_template("upload.html")
@app.route("/upbres") 
def upbresume():
        return render_template("uploadbulk.html")
@app.route("/addreq") 
def addreq():
        return render_template("addreq.html")
def get_value(listOfDicts, key):
        for subVal in listOfDicts:
                print("Subvalues===",subVal)
                if key in subVal:
                        print("Key====",key)
                        print("subVal[key]===",listOfDicts[key])
                        return listOfDicts[key]

def get_education(education):
    '''
    Helper function to display the education in human readable format
    '''
    education_string = ''
    for edu in education:
        education_string += edu[0] + ' (' + str(edu[1]) + '), '
    return education_string.rstrip(', ')
@app.route("/addextract",methods=['POST'])
def addextract():
        
        jobpost=request.form['job']
        skills=request.form['skills']
        tskills=request.form['tskills']
        noofvac=request.form['noofvac']
        resumes_data=[]
        fname=[]
        session['jobtitle']=jobpost
        session['skills']=skills
        session['tskills']=tskills
        session['nov']=noofvac
        onlyfiles = next(os.walk("./resume"))[2] #dir is your directory path as string
        print("length of files in resue=")
        print (len(onlyfiles))
        dir_path = os.path.dirname(os.path.realpath(__file__))
        for root, dirs, files in os.walk("./resume"):
                for file in files:
                        # change the extension from '.mp3' to the one of your choice.
                        if file.endswith('.pdf'):
                                print("File Name",str(file))
                                path=dir_path
                                print("Dir path==",dir_path)
                                data =resumeextraction.extract_from_directory(str(file))
                                print("Data==",data)
                                print("Data[0]==",data[0])
                                edu=get_value(data[0],'education')
                                print("edu==",edu)
                                skills=get_value(data[0],'skills')
                                print("Skills==",skills)
                                exp=get_value(data[0],'experience')
                                print("exp",exp)
                                cname=get_value(data[0],'name')
                                print("candidate name=",cname)
                                cmono=get_value(data[0],'mobile_number')
                                print("Mobile number=",cmono)
                                cemail=get_value(data[0],'email')
                                print("email==",cemail)
                                final_data=[]
                                final_data.append(edu)
                                final_data.append(skills)
                                final_data.append(exp)
                                y = list(chain(*final_data))
                                
                                print("Final data==",y)
                                with open('testes.csv', 'w',encoding="utf-8") as out_file:# writing the user input values into test.csv file
                                        writer = csv.writer(out_file)
                                        writer.writerow(['Resume'])
                                        writer.writerow([y])
                                print('File writen')
                                preclass=pre.process()
                                score=sc.process(jobpost,preclass)
                                cmd="SELECT * FROM resu WHERE sys_fname='"+str(file)+"'"
                                print(cmd)
                                conn.execute(cmd)
                                cursor=conn.fetchall()
                                isRecordExist=0
                                for row in cursor:
                                        isRecordExist=1
                                if(isRecordExist==1):
                                        print("Update")
                                        cmd="UPDATE resu set score='"+str(score)+"' where sys_fname='"+str(file)+"'"
                                        print(cmd)
                                        print("Updated Successfully")
                                        conn.execute(cmd)
                                        mydb.commit()
                                        
                                else:
                                        print("insert")
                                        cmd="INSERT INTO resu(pname,job,sys_fname,score,mono,email) Values('"+str(cname)+"','"+str(jobpost)+"','"+str(str(file))+"','"+str(score)+"','"+str(cmono)+"','"+str(cemail)+"')"
                                        print(cmd)
                                        print("Inserted Successfully")
                                        conn.execute(cmd)
                                        mydb.commit()
                                
                                resumes_data.append(data)
                                fname.append(str(file))
        print("resumes_data==",resumes_data)
        print("filename==",fname)
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from resu order by score desc")
        #fetching all records from database
        data=cursor.fetchall()
        return render_template("shortlist.html",data=data) 
        
        
                        
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/rupload",methods=['POST'])
def rupload():
    if request.method == 'POST':
            pno=request.form['job']
            uname=session.get('cname')
            file = request.files['res']
            if 'res' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
            if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
            if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    #path=uname
                    pathlib.Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                    return render_template('upload.html',message="Uploaded Successfully")
@app.route('/rbupload', methods=['GET','POST'])
def uploadbulk():
        if flask.request.method == "POST":
                files = flask.request.files.getlist("file[]")
                for file in files:
                        if file and allowed_file(file.filename):
                                filename = secure_filename(file.filename)
                                print("Filename==",file.filename)
                                pathlib.Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
                                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                        else:
                                return render_template('uploadbulk.html',message="Uploaded Failed")
                return render_template('uploadbulk.html',message="Uploaded Success")
        else:
                return render_template('uploadbulk.html',message="Uploaded Failed")


        
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
@app.route("/usignin",methods=['POST']) 
def usignin():
        cid=request.form['uname']
        pin=request.form['pass']
        cmd="SELECT * FROM user WHERE uname='"+cid+"' and pass='"+pin+"'"
        print(cmd)
        conn.execute(cmd)
        cursor=conn.fetchall()
        isRecordExist=0
        for row in cursor:
                isRecordExist=1
        if(isRecordExist==1):
                session['cname']=request.form['uname']
                return render_template("uhome.html")
        else:
                return render_template("ulogin.html",message="Invalid UserName or Password")

@app.route("/rsignin",methods=['POST']) 
def rsignin():
        uname=request.form['uname']
        passw=request.form['pass']
        if(uname=="admin"):
                if(passw=="eswar"):
                        session['uname']=request.form['uname']
                        return render_template("rhome.html")
                else:
                        return render_template("rlogin.html",message="Invalid Password")
        else:
                return render_template("rlogin.html",message="Invalid UserName")

@app.route("/usignup",methods=['POST']) 
def usignup():
        name=request.form['name']
        uname=request.form['uname']
        passw=request.form['pass']
        email=request.form['email']
        mobile=request.form['mono']
        addr=request.form['addr']
        cmd="SELECT * FROM user WHERE uname='"+uname+"' or email='"+email+"'"
        print(cmd)
        conn.execute(cmd)
        cursor=conn.fetchall()
        isRecordExist=0
        for row in cursor:
                isRecordExist=1
        if(isRecordExist==1):
                print("Username Already Exists")
                return render_template("ureg.html",message="Username or email Already Exists")
        else:
                print("insert")
                cmd="INSERT INTO user(name,uname,pass,email,mono,addr) Values('"+str(name)+"','"+str(uname)+"','"+str(passw)+"','"+str(email)+"','"+str(mobile)+"','"+addr+"')"
                print(cmd)
                print("Inserted Successfully")
                conn.execute(cmd)
                mydb.commit()
                return render_template("ulogin.html",message="Inserted SuccesFully")

@app.route("/logout")
def log_out():
    session.clear()
    return redirect(url_for('hello'))
# start() 
if __name__=="__main__":
        app.run(debug=True)
        
        

