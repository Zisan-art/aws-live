from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about",methods=['POST'])
def about():
    return render_template('aboutus.html')

@app.route("/addemp",methods=['POST'])
def AddEmp():
    return render_template('AddEmp.html')

@app.route("/add", methods=['POST'])
def Add():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    job_title = request.form['job_title']
    salary = request.form['salary']
    bonus = request.form['bonus']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, job_title, salary, bonus))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route("/getemp", methods=['GET', 'POST'])
def getpage():
    return render_template('GetEmp.html')


@app.route("/fetchdata", methods=['POST'])
def GetEmp():
    emp_id = request.form['emp_id']
    sysdate = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    select_sql = "SELECT * FROM employee WHERE emp_id = (%s)"
    cursor = db_conn.cursor()
    img_url = ""
    try:
        cursor.execute(select_sql,(emp_id))
        print("Fetching single row")        
        # Fetch one record from SQL query output
        record = cursor.fetchone()
        print("Fetched: ",record)
        if record is None:
            print("No data found.")
            
        else:
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"

            img_url = "https://chuazisan-s3-bucket.s3.amazonaws.com/{0}".format(
                emp_image_file_name_in_s3)
            
            calc_payroll = record[6] + record[7]
    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("fetch data done...")
    if record is None:
        return render_template('GetEmpOutput.html', 
                           out_id="ID Not Exist", 
                           out_fname="NULL", 
                           out_lname="NULL",
                           out_skill="NULL",
                           out_location="NULL",
                           out_jobtitle="NULL",
                           out_salary="NULL",
                           out_bonus="NULL",
                           out_payroll="NULL",
                           out_date="NULL",                               
                           image_url=img_url
                          )
    else :
        return render_template('GetEmpOutput.html', 
                           out_id=record[0], 
                           out_fname=record[1], 
                           out_lname=record[2],
                           out_skill=record[3],
                           out_location=record[4],
                           out_jobtitle=record[5],
                           out_salary=record[6],
                           out_bonus=record[7],
                           out_payroll=str(calc_payroll),
                           out_date=sysdate,
                           image_url=img_url
                          )

@app.route("/updateemp", methods=['GET', 'POST'])
def uppage():
    return render_template('UpdateEmp.html')

@app.route("/fetchup", methods=['POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']
    select_sql = "SELECT * FROM employee WHERE emp_id = (%s)"
    cursor = db_conn.cursor()
    img_url = ""
    try:
        cursor.execute(select_sql,(emp_id))
        print("Fetching single row")        
        # Fetch one record from SQL query output
        record = cursor.fetchone()
        print("Fetched: ",record)
        if record is None:
            return "Employee Not Found. To add new record, please proceed to Home Page."
            
    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("fetch data done...")
    return render_template('UpdateEmpContent.html', 
                           out_id=record[0], 
                           out_fname=record[1], 
                           out_lname=record[2],
                           out_skill=record[3],
                           out_location=record[4],
                           out_jobtitle=record[5],
                           out_salary=record[6],
                           out_bonus=record[7]
                          )

@app.route("/upemp", methods=['POST'])
def UpEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    job_title = request.form['job_title']
    salary = request.form['salary']
    bonus = request.form['bonus']
    emp_image_file = request.files['emp_image_file']

    update_sql = "UPDATE employee SET first_name=(%s), last_name=(%s), pri_skill=(%s), location=(%s), job_title=(%s), salary=(%s), bonus=(%s) WHERE emp_id = (%s)"
    cursor = db_conn.cursor()

    try:
    
        cursor.execute(update_sql, (emp_id, first_name, last_name, pri_skill, location, job_title, salary, bonus))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        if emp_image_file.filename is not None:
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"

            s3 = boto3.resource('s3')
            obj = s3.Object(custombucket, emp_image_file_name_in_s3)
            obj.delete()
            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('UpdateEmpOutput.html', name=emp_name)

@app.route('/deleteemp', methods=['POST'])
def deleteEmp():
    return render_template('DeleteEmp.html')

@app.route('/delete', methods=['POST'])
def delete():
    emp_id = request.form['emp_id']
    delete_sql = "DELETE FROM employee WHERE emp_id = (%s)"
    select_sql = "SELECT * FROM employee WHERE emp_id = (%s)"
    cursor = db_conn.cursor()
    img_url = ""
    try:
        cursor.execute(select_sql,(emp_id))
        print("Fetching single row")        
        # Fetch one record from SQL query output
        record = cursor.fetchone()
        print("Fetched: ",record)
        if record is None:
            print("No data found.")
            
        else:
            cursor.execute(delete_sql, (emp_id))
            db_conn.commit()
            
            object_name = "emp-id-" + str(emp_id) + "_image_file"
            s3 = boto3.resource('s3')
            s3.Object(custombucket, object_name).delete()
            record = cursor.fetchone()
            obj = s3.Object(custombucket, object_name)
            
    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("delete data done...")
    return render_template('DeleteEmpOutput.html', deleted_id=emp_id)

@app.route("/fsd")
def fsdpage():
    return render_template('fongsukdien.html')
@app.route("/fmw")
def fmwpage():
    return render_template('mengwen.html')
@app.route("/ethan")
def ethanpage():
    return render_template('ethanlim.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
