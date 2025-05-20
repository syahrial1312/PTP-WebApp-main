import base64
from datetime import date
from datetime import datetime,timedelta
import bcrypt
import io
import os
import qrcode
import time
import zipfile
from flask import Flask, render_template, redirect, url_for, flash, session, request, send_file
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, SelectField, TextAreaField, TimeField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, InputRequired

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Fou90ryan10**'
app.config['MYSQL_DB']='ptp_webapp'
app.secret_key= '1ve5r76wetex7t278'
# app.config['WTF_CSRF_ENABLED'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql= MySQL(app)

# Folder penyimpanan sementara
UPLOAD_FOLDER = 'uploads'
ZIP_FOLDER = 'zips'
DOWNLOAD_FOLDER='downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)


def uploadFile(file, machine_id):
    if file.filename == '':
        return "Nama file kosong!", False
    
    if file:
         # Simpan file sementara
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # Konversi ke ZIP
        zip_filename = file.filename.rsplit('.', 1)[0] + ".zip"
        zip_path = os.path.join(ZIP_FOLDER, zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(file_path, arcname=file.filename)
        # Simpan ke database
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
            
        # Store data into database
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO backup (name, file, machine_id) VALUES (%s, %s, %s)", (zip_filename, zip_data, machine_id))
            mysql.connection.commit()
            print("Succes")
            os.remove(file_path)
            os.remove(zip_path)
        except Exception as e:
            print("Gagal:")
            print(e)
        finally:
            cursor.close()
        
        return f"File {zip_filename} berhasil diupload & disimpan di database!", True

class akunForm(FlaskForm):
    username = StringField("Name",validators=[DataRequired()])
    password= PasswordField("Password", validators=[DataRequired()])
    role = SelectField("Pilih Role", choices=[
        ("maintenance", "Maintenance"),
        ("master", "Master")
    ])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Name",validators=[DataRequired()])
    password= PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
    
class mesinForm(FlaskForm):
    nama = StringField("nama")
    tipe_mesin = StringField("tipe_mesin")
    tipe_plc = StringField("tipe_plc")
    tipe_hmi = StringField("tipe_hmi")
    line = StringField("line")
    submit = SubmitField("Update")
    
class backupForm(FlaskForm):
    file = StringField("File")
    submit = SubmitField("Upload")

class pmForm(FlaskForm):
    time = StringField("Time")
    tipe_pm = StringField("Tipe PM")
    id_mesin = StringField("ID Mesin")
    sparepart=IntegerField("Sparepart")
    qty=IntegerField("Qty")
    submit = SubmitField("Submit")

class WOForm(FlaskForm):
    mesin = StringField("Mesin")  # ID mesin sebagai pilihan
    tanggal = DateField("Tanggal", format='%Y-%m-%d',validators=[InputRequired()])
    deskripsi = TextAreaField("Deskripsi Laporan")
    # waktu_laporan = TimeField("Waktu Laporan", format='%H:%M', validators=[DataRequired()])
    peminta = StringField("Peminta")
    tanggalDikerjakan=DateField("Tanggal Dikerjakan", format='%Y-%m-%d')
    jam_mulai = TimeField("Start Time", format='%H:%M')
    jam_selesai = TimeField("Finish Time", format='%H:%M')
    sparepart = IntegerField("Sparepart")  # ID sparepart sebagai pilihan
    qty = IntegerField("Qty") # type: ignore
    pic = IntegerField("PIC")  # ID maintenance sebagai pilihan
    submit = SubmitField("Submit")

class ExecuteWOForm(FlaskForm):
    tanggalDikerjakan = DateField("Tanggal Dikerjakan", format='%Y-%m-%d', validators=[InputRequired()])
    jam_mulai = TimeField("Start Time", format='%H:%M')
    jam_selesai = TimeField("Finish Time", format='%H:%M')
    sparepart = IntegerField("Sparepart")
    qty = IntegerField("Qty")
    pic = IntegerField("PIC")
    submit = SubmitField("Submit")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/scanner')
def scanner():
    if 'user_id'not in session:
        flash("Silakan login terlebih dahulu", "warning")
        return redirect(url_for('login'))

    print(session['user_id'])
    if session['user_id'] == 1:
        loginText = "maintenance"
    elif session['user_id'] == 2 :
        loginText="master"
    else:
        loginText = "produksi"

    print(loginText)
    return render_template('scanner.html', role=loginText)

@app.route('/register', methods=['GET','POST'])
def register():
    form = akunForm()
    if form.validate_on_submit():
        print("Buttonnnnnnnnnnnnnnnnnnnn")
        username=form.username.data
        password=form.password.data
        role=form.role.data
        hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    
        #Store data into database
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role))
            mysql.connection.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}", "danger")
        finally:
            cursor.close()
        # cursor.execute("INSERT INTO users (username,password,role) VALUES (%s,%s,%s)",(username, hashed_password, role))
        # mysql.connection.commit()
        # cursor.close()
        # return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("SUCCESSS")
        username=form.username.data
        password=form.password.data
        
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        print(user)
        cursor.close()
        passw=bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8'))
        print(passw)
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['user_id']=user[0] #user_id
            print(session['user_id'])
            flash("Login berhasil", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login gagal. Cek kembali username dan password")
            # return redirect(url_for('login'))
            
    return render_template('logins.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Silakan login terlebih dahulu", "warning")
        time.sleep(5)
        return redirect(url_for('login'))
    
    print(session['user_id'])
    if session['user_id'] == 1:
        loginText="maintenance"
    else:
        loginText="master"

    thisMonth = date.today().month
    thisYear = date.today().year
    today = date.today()
    print(today, thisMonth, thisYear)
    # print(session['user_id'])
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT role,name FROM users WHERE id=%s", (session['user_id'],))
    user_role = cursor.fetchone()[0]  # Ambil role user dari database
    cursor.execute("""SELECT COUNT(id) FROM machine;""")
    nMesin = cursor.fetchone()[0]
    print(nMesin)
    cursor.execute("""SELECT MONTH(report_time) AS bulan, COUNT(*) AS jumlah_wo
                        FROM wo WHERE YEAR(report_time)=%s GROUP BY bulan order by bulan""",
                   (thisYear,))
    woPerMonth = cursor.fetchall()
    print(woPerMonth)
    cursor.execute("""SELECT name, SUM(qty) AS total_qty
                        FROM (
                            SELECT sparepart_id, qty FROM pm_sparepart LEFT JOIN pm ON pm_id=pm.id
                            WHERE YEAR(time)=%s
                            UNION ALL
                            SELECT sparepart_id, qty FROM wo_sparepart LEFT JOIN wo ON wo_id=wo.id
                            WHERE YEAR(report_time)=%s
                        ) AS combined JOIN sparepart ON sparepart_id=sparepart.id GROUP BY sparepart_id order by total_qty DESC""",
                   (thisYear, thisYear))
    mostUseSparepart = cursor.fetchmany(5)
    print(mostUseSparepart)
    cursor.execute("""SELECT name, COUNT(machine_id) AS jumlah
                       FROM machine JOIN wo ON machine_id=machine.id
                       WHERE MONTH(report_time)=%s GROUP BY name ORDER BY jumlah DESC""",
                   (thisMonth,))
    brokenMachine = cursor.fetchmany(5)
    print(brokenMachine)
    cursor.execute("""SELECT m.name, pm.time, pm.pm_type, pm.job_description,pm.id
                       FROM pm LEFT JOIN machine m ON machine_id=m.id
                       WHERE pm.time>=%s""",
                   (today,))
    upcomingPm = cursor.fetchmany(5)
    print(upcomingPm)
    cursor.close()

    return render_template("dashboard.html",
                           role=user_role,
                           totalMesin=nMesin,
                           woPerBulan=woPerMonth,
                           sparepartTerpakai=mostUseSparepart,
                           mesinRusak=brokenMachine,
                           pmMendatang=upcomingPm)

@app.route("/machine")
def machine():
    if 'user_id' not in session:
        flash("Silakan login untunk mengakses halaman ini", "warning")
        return redirect(url_for('login'))

    print(session['user_id'])
    if session['user_id'] == 1:
        loginText = "maintenance"
    elif session['user_id'] == 2:
        loginText = "master"
    else:
        loginText = "produksi"

    print(loginText)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, line, machine_type FROM machine")
    mesin = cursor.fetchall()
    kategori_mesin={}
    line_list={}
    for m in mesin:
        line=m[2]
        if line not in line_list:
            line_list[line]=[]
        line_list[line].append(m)
    for m in mesin:
        kategori = m[3]
        if kategori not in kategori_mesin:
            kategori_mesin[kategori] = []
        kategori_mesin[kategori].append(m)
    cursor.close()
    print(mesin)
    return render_template("listMesin.html", role=loginText, mesin=mesin, kategori_mesin=kategori_mesin, line_list=line_list)

@app.route("/machine/add", methods=['GET', 'POST'])
def add_machine():
    message = None
    if request.method == "POST":
        nama = request.form['nama']
        tipe_mesin = request.form['tipe_mesin']
        tipe_plc = request.form['tipe_plc']
        tipe_hmi = request.form['tipe_hmi']
        line = request.form['line']
        manufactur = request.form['manufactur']
        speed = request.form['speed']
        kapasitas = request.form['kapasitas']
        tahun = request.form['tahun']
        id = f"BO{nama}{line}"
        print(f"Data ada:{nama},{tipe_mesin},{tipe_plc},{tipe_hmi},{line},{manufactur},{speed},{kapasitas},{tahun}")
        cursor = mysql.connection.cursor()
        cursor.execute("""INSERT INTO machine (id,name,machine_type,plc_type,hmi_type,line,manufacturer,speed,capacity,yom)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (id, nama, tipe_mesin, tipe_plc, tipe_hmi, line, manufactur, speed, kapasitas, tahun))
        mysql.connection.commit()
        print("Submited to database")
        message = "Submitted to database"
        cursor.close()
        return redirect(url_for('machine'))

    return render_template('machine_add.html', messsage=message)

@app.route("/machine/<machine_id>")
def machine_detail(machine_id):
    if 'user_id' not in session:
        loginText="maintenance"
        user_role="notLogin"
        # flash("Silakan login terlebih dahulu", "warning")
        # return redirect(url_for('login'))

    today=date.today()
    cursor = mysql.connection.cursor()

    if 'user_id' in session:
        # Ambil role user
        cursor.execute("SELECT role FROM users WHERE id=%s", (session['user_id'],))
        user_role = cursor.fetchone()[0]


    # Ambil data mesin
    cursor.execute("SELECT * FROM machine WHERE id = %s", (machine_id,))
    machine = cursor.fetchone()

    if not machine:
        flash("Mesin tidak ditemukan!", "danger")
        return redirect(url_for('dashboard'))

    data = {
        "id": machine[0],
        "nama": machine[1],
        "tipe_mesin": machine[2],
        "tipe_plc": machine[3],
        "tipe_hmi": machine[4],
        "line": machine[5],
        "manufacturer" : machine[6],
        "speed" : machine[7],
        "capacity" : machine[8],
        "year" : machine[9],
        "today_maintenance": [],
        "maintenance_history": [],
        "next_maintenance": [],
    }
    
    if user_role in ["maintenance", "master"]:
        cursor.execute("""
            SELECT pm.time, pm.pm_type, s.name, ps.qty
            FROM pm
            JOIN pm_sparepart ps ON pm.id = ps.pm_id
            JOIN sparepart s ON ps.sparepart_id = s.id
            WHERE pm.machine_id = %s AND pm.time < %s
            ORDER BY pm.time DESC
        """, (machine_id, today,))
        data["maintenance_history"] = cursor.fetchall()
        print(data["maintenance_history"])
        cursor.execute("""
            SELECT pm.time, pm.pm_type, s.name, ps.qty
            FROM pm
            JOIN pm_sparepart ps ON pm.id = ps.pm_id
            JOIN sparepart s ON ps.sparepart_id = s.id
            WHERE pm.machine_id = %s AND pm.time >= %s
            ORDER BY pm.time ASC
        """, (machine_id, today,))
        data["next_maintenance"] = cursor.fetchall()
        print(data["next_maintenance"])
    # # Jika user adalah Produksi, ambil data produksi harian
    # if user_role in ["produksi", "master"]:
    #     cursor.execute("""
    #         SELECT SUM(qty) FROM pm WHERE id_mesin = %s
    #     """, (machine_id,))
    #     data["total_produksi"] = cursor.fetchone()[0]

    # cursor.close()
    
    # qr=qrcode.make(f"https://8c15-210-79-138-82.ngrok-free.app/machine/"+machine_id)
    qr=qrcode.make(f"https://739d-118-137-165-189.ngrok-free.app/machine/"+machine_id)
    buffer = io.BytesIO()
    qr.save(buffer, "PNG")
    qr_base64= base64.b64encode(buffer.getvalue()).decode()
    # print(qr_base64)
    return render_template("detailMesin.html", data=data, role=user_role, qr=qr_base64)

@app.route('/machine/update/<machine_id>', methods=['GET','POST'])
def update_machine(machine_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM machine WHERE id=%s", (machine_id,))
    mesin = cursor.fetchone()
    cursor.close()
    data = {
        "id": mesin[0],
        "nama": mesin[1],
        "tipe_mesin": mesin[2],
        "tipe_plc": mesin[3],
        "tipe_hmi": mesin[4],
        "line": mesin[5],
    }
    form=mesinForm()
    nama=form.nama.data, 
    tipe_mesin=form.tipe_mesin.data, 
    tipe_plc=form.tipe_plc.data, 
    tipe_hmi=form.tipe_hmi.data, 
    line=form.line.data
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        cursor.execute("""UPDATE machine SET 
                       name=%s, 
                       machine_type=%s, 
                       plc_type=%s, 
                       hmi_type=%s, 
                       line=%s
                       WHERE id=%s""", (nama, tipe_mesin, tipe_plc, tipe_hmi, line, machine_id,))
        mysql.connection.commit()
        cursor.close()
        flash("Data berhasil diupdate", "success")

        return redirect(url_for('update_machine', machine_id=machine_id))
    return render_template("updateMesin.html", data=data, form=form)

@app.route('/machine/sparepart/<machine_id>')
def machineSparepart(machine_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT s.id, s.name, ms.qty
                   FROM sparepart s 
                   JOIN machine_sparepart ms ON ms.sparepart_id = s.id
                   WHERE ms.machine_id=%s""", (machine_id,))
    sperpart: object = cursor.fetchall()
    print(sperpart)
    print(machine_id)
    
    return render_template("sparepartPadaMesin.html", spareparts=sperpart, machineId=machine_id)


@app.route('/machine/sparepart/update/<machine_id>', methods=['GET', 'POST'])
def update_ms(machine_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, line FROM machine WHERE id=%s", (machine_id,))
    machine = cursor.fetchone()
    cursor.execute("""SELECT id, name FROM sparepart""")
    allSpareparts = cursor.fetchall()
    cursor.execute("""SELECT s.id, s.name ms,qty
                   FROM sparepart s JOIN machine_sparepart ms ON ms.sparepart_id = s.id
                   WHERE ms.machine_id=%s""", (machine_id,))
    usedSpareparts = cursor.fetchall()
    data={
        "allSpareparts": allSpareparts,
        "usedSpareparts": usedSpareparts,
        "machine": machine
    }
    cursor.close()
    
    if request.method=='POST':
        spareparts_id=request.form.getlist("sparepart_id[]")
        spareparts_qty=request.form.getlist("sparepart_qty[]")
        last_sparepart=[row[0] for row in usedSpareparts]
        cursor=mysql.connection.cursor()
    
        # Menghapus yang tidak ada dalam sparepart sekarang
        for i in range(len(last_sparepart)):
            id=(last_sparepart[i])
            spareparts_id=[(i) for i in spareparts_id]
            if id not in spareparts_id:
                cursor.execute("DELETE FROM machine_sparepart WHERE machine_id=%s AND sparepart_id=%s", (machine_id, id))
             
        # Menambahkan atau mengupdate sparepart
        for i in range(len(spareparts_id)):
            # print("masuk loop")
            id=(spareparts_id[i])
            if  id not in last_sparepart:
                # print("masuk if ")
                cursor.execute("INSERT INTO machine_sparepart (machine_id, sparepart_id, qty) VALUES (%s,%s,%s)",
                               (machine_id,spareparts_id[i], spareparts_qty[i]))
            else:
                # print("masuk else")
                cursor.execute("""UPDATE machine_sparepart SET qty=%s
                               WHERE machine_id=%s AND sparepart_id=%s""",
                               (spareparts_qty[i],machine_id,spareparts_id[i]))
        mysql.connection.commit()
        cursor.close()
        print("Submit sukses")
        flash("Berhasil di Update!", "success")
        return redirect(url_for('machineSparepart', machine_id=machine_id))

    return render_template("updateSparepartPadaMesin.html", data=data)


@app.route('/machine/backup/<machine_id>', methods=['GET', 'POST'])
def backup(machine_id, file_path=None):
    if request.method == 'POST':  
        # Jika ada file yang diunggah, lakukan upload
        if 'file' in request.files:
            print("Yes")
            file = request.files['file']
            if file.filename != '':
                message, success= uploadFile(file, machine_id)
                return redirect(url_for('backup', machine_id=machine_id, message=message, success=success))
            # os.remove(file.filename)
            #Just save to internal storage
                # file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                # file.save(file_path)
                # return redirect(url_for('backup', machine_id=machine_id))
    
    # Jika ada parameter backup_id, lakukan download
    backup_id = request.args.get('backup_id')
    if backup_id:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, file FROM backup WHERE id = %s", (backup_id,))
        result = cursor.fetchone()
        if result:
            filename,fileData = result
            file_path = os.path.join("downloads", filename)
            
            with open(file_path, "wb") as f:
                f.write(fileData)
            
            return send_file(file_path, as_attachment=True)
        os.remove(file_path)
        
        # file_path = os.path.join(app.config["UPLOAD_FOLDER"], backup_id)
        # if os.path.exists(file_path):
        #     return send_from_directory(app.config["UPLOAD_FOLDER"], backup_id, as_attachment=True)
        
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT id, name, time FROM backup WHERE machine_id=%s", (machine_id,))
    backups = cursor.fetchall()
    cursor.close()
    
    # Jika GET biasa, tampilkan daftar file
    # backups = [(f, f) for f in os.listdir(app.config["UPLOAD_FOLDER"])]
    return render_template('backupMesin.html', machine_id=machine_id, backups=backups)

@app.route('/sparepart', methods=['GET', 'POST'])
def sparepart():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sparepart")
    spareparts = cursor.fetchall()
    # spareparts={
    #     "id":spareparts[0],
    #     "nama":spareparts[1],
    #     "spesifikasi":spareparts[2],
    #     "satuan":spareparts[3]
    # }
    cursor.close()

    if request.method == "POST":
        print("ok")
        id = request.form["id"]
        print(id)
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM sparepart WHERE id=%s", (id,))
        mysql.connection.commit()
        flash("Data Berhasil Dihapus!","warning")
        return redirect(url_for('sparepart'))
    return render_template('sparepart.html', spareparts=spareparts)


@app.route('/sparepart/edit/<sparepart_id>', methods=['GET','POST'])
def sparepart_edit(sparepart_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sparepart WHERE id=%s", (sparepart_id,))
    sparepart = cursor.fetchone()
    if request.method == "POST":
        nama = request.form["nama"]
        spesifikasi = request.form["spesifikasi"]
        satuan = request.form["satuan"]
        cursor.execute("""UPDATE sparepart SET name=%s, spesification=%s, unit=%s
                           WHERE id=%s""", (nama, spesifikasi, satuan, sparepart_id))
        mysql.connection.commit()
        cursor.close()
        flash("Data Berhasil Diupdate","success")
        return redirect(url_for('sparepart'))
    return render_template('editSparepart.html', sparepart=sparepart)


@app.route('/sparepart/add', methods=['GET', 'POST'])
def sparepart_add():
    print("Mau tambahin sparepart ya?")
    if request.method == 'POST':
        print("test aja inimah")
        nama = request.form["nama"]
        spesifikasi = request.form["spesifikasi"]
        satuan = request.form["satuan"]
        id = request.form["id"]
        print(id)
        print(nama, spesifikasi, satuan)

        cursor = mysql.connection.cursor()
        cursor.execute("""INSERT INTO sparepart (id,name,spesification,unit) 
                       VALUES (%s,%s,%s,%s)""", (id, nama, spesifikasi, satuan,))
        mysql.connection.commit()
        cursor.close()
        flash("Berhasil Ditambahkan","success")
        return redirect(url_for('sparepart'))
    elif request.method=="POST":
        flash("Gagal Ditambahkan","error")
    return render_template('tambahSparepart.html')

@app.route('/pm')
def pm():
    if not 'user_id' in session:
        flash("Silakan login terlebih dahulu", "warning")
        return redirect(url_for('login'))

    user_id=session['user_id']
    # print(user_id)
    today=date.today()
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    role = cursor.fetchone()
    # print(role[0])
    cursor.execute("""SELECT pm.time, pm.pm_type, m.name, m.line, m.id, pm.id, m.machine_type
                   FROM pm
                   JOIN machine m ON pm.machine_id=m.id
                   WHERE time>=%s  
                   order by pm.time ASC""", (today,))
    pmAll = cursor.fetchall()
    print(role[0])
    planPm = {}
    for m in pmAll:
        kategori = m[6]
        if kategori not in planPm:
            planPm[kategori] = []
        planPm[kategori].append(m)
    cursor.close()
    print(planPm)
    return render_template("rencanaPreventiveMaintenance.html", pm=planPm, role=role)

@app.route('/pm/history')
def historyPM():
    if not 'user_id' in session:
        flash("Silakan login terlebih dahulu", "warning")
        return redirect(url_for('login'))

    user_id=session['user_id']
    # print(user_id)
    today=date.today()
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    role = cursor.fetchone()
    # print(role[0])
    cursor.execute("""SELECT pm.time, pm.pm_type, m.name, m.line, m.id, pm.id, m.machine_type
                       FROM pm
                       JOIN machine m ON pm.machine_id=m.id
                       WHERE time<=%s ORDER BY time DESC""", (today,))
    pm = cursor.fetchall()
    pmHistory = {}
    cursor.close()
    for p in pm:
        kategori = p[6]
        if kategori not in pmHistory:
            pmHistory[kategori] = []
        pmHistory[kategori].append(p)

    print(pmHistory)
    return render_template("historyPreventiveMaintenance.html", pmHistory=pmHistory, role=role)

@app.route('/historyCorrectiveMaintenance')
def historyCorrectiveMaintenance():
    if not 'user_id' in session:
        flash("Silakan login terlebih dahulu", "warning")
        return redirect(url_for('login'))

    user_id=session['user_id']
    # print(user_id)
    today=date.today()
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    role = cursor.fetchone()
    # print(role[0])
    cursor.execute("""SELECT WO.id, WO.report_time, WO.machine_id, WO.requester,MACHINE.name AS machine_name
        FROM WO
        JOIN MACHINE ON WO.machine_id = MACHINE.id
        WHERE WO.stat = 1
        ORDER BY WO.report_time DESC; """)
    cm = cursor.fetchall()
    historyCm = {}
    print(historyCm)
    for c in cm:
        kategori = c[4]
        if kategori not in historyCm:
            historyCm[kategori] = []
        historyCm[kategori].append(c)
    cursor.close()
    return render_template("historyCorrectiveMaintenance.html", historyCm=historyCm, role=role)

@app.route('/historyCorrectiveMaintenance/detail/<cm_id>', methods=['GET', 'POST'])
def detailHistoryCorrectiveMaintenance(cm_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT WO.id, WO.report_time, WO.machine_id, WO.requester as Pemohon,
                             WO.start_time, WO.finish_time, m.name AS machine_name, us.name AS PIC, WO.description, WO.tgl_kerja
                      FROM WO
                      JOIN MACHINE m ON WO.machine_id = m.id
                      JOIN USERS us ON WO.user_id = us.id
                      WHERE WO.id = %s
                      ORDER BY WO.report_time DESC;""", (cm_id,))
    correctiveMaintenance = cursor.fetchone()
    print(correctiveMaintenance)
    start_time = correctiveMaintenance[4]
    finish_time = correctiveMaintenance[5]
    if finish_time < start_time:
        finish_time += timedelta(days=1)
    duration = finish_time - start_time
    print("Start:",correctiveMaintenance[4])
    print("Finish:", correctiveMaintenance[5])
    print("Durasi:", duration)

    cursor.execute("""SELECT ws.sparepart_id as idSparepart, s.name as namaSparepart, ws.qty, s.unit
                      FROM wo_sparepart ws 
                      JOIN sparepart s ON ws.sparepart_id = s.id
                      WHERE wo_id = %s;""", (cm_id,))
    usedSparepartsCorMain = cursor.fetchall()
    print(usedSparepartsCorMain)
    cursor.close()
    return render_template("detailHistoryCorrectiveMaintenance.html",wo=correctiveMaintenance,spareparts=usedSparepartsCorMain,durasi=duration)

@app.route('/pm/history/detail/<his_id>',methods=['GET','POST'])
def detailHistoryPreventiveMaintenance(his_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT PM.id, PM.time, PM.machine_id, PM.pm_type,
                                 PM.job_description, m.name AS machine_name
                          FROM PM
                          JOIN MACHINE m ON PM.machine_id = m.id
                          WHERE PM.id = %s
                          ORDER BY PM.time DESC;""", (his_id,))
    detailPreventiveMaintenance = cursor.fetchone()
    print(correctiveMaintenance)
    cursor.execute("""SELECT ps.sparepart_id as idSparepart, s.name as namaSparepart, ps.qty, s.unit
                          FROM pm_sparepart ps 
                          JOIN sparepart s ON ps.sparepart_id = s.id
                          WHERE pm_id = %s;""", (his_id,))
    usedSparepartsPreMain = cursor.fetchall()
    print(usedSparepartsPreMain)
    cursor.close()
    return render_template("detailHistoryPreventiveMaintenance.html", detPreMain=detailPreventiveMaintenance,
                           usSpaPreMain=usedSparepartsPreMain)

@app.route('/pm/add', methods=['GET', 'POST'])
def addPM():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM sparepart")
    allSpareparts = cursor.fetchall()
    cursor.execute("SELECT id, name FROM machine")
    allMesin = cursor.fetchall()
    data={
        "allSpareparts": allSpareparts,
        "allMesin": allMesin
    }
    if request.method=='POST':
        id_mesin=request.form["id_mesin"]
        id_mesin=id_mesin.split(" ")[0]
        # print(id_mesin)
        time=request.form["time"]
        tipe_pm=request.form["tipe_pm"]
        spareparts_id=request.form.getlist("sparepart_id[]")
        spareparts_qty=request.form.getlist("sparepart_qty[]")
        cursor.execute("SELECT id FROM pm")
        last_id = cursor.fetchone()
        # id_pm=cursor.lastrowid
        # print(id_pm)
        cursor.execute("INSERT INTO pm (machine_id, time, pm_type) VALUES (%s,%s,%s)", (id_mesin, time, tipe_pm))
        # cursor.execute("SELECT id FROM pm")
        mysql.connection.commit()
        id_pm=cursor.lastrowid
        print(id_pm)
        for i in range(len(spareparts_id)):
            cursor.execute("INSERT INTO pm_sparepart (pm_id, sparepart_id, qty) VALUES (%s,%s,%s)", (id_pm, spareparts_id[i], spareparts_qty[i]))
        mysql.connection.commit()
        cursor.close()
        flash("Berhasil Ditambahkan","success")

        return redirect(url_for("pm"))

    elif request.method=="POST":
        flash("Gagal Ditambahkan","error")

    return render_template("tambahPreventiveMaintenance.html", data=data)

@app.route('/pm/edit/<pm_id>', methods=['GET', 'POST'])
def editPM(pm_id):

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT pm.id, pm.time, pm.pm_type, pm.machine_id FROM pm WHERE id=%s", (pm_id,))
    pm = cursor.fetchone()
    if pm is None:
        flash("Data PM tidak ditemukan.", "error")
        return redirect(url_for("pm"))
    cursor.execute("""SELECT ps.sparepart_id, s.name, ps.qty
                   FROM pm_sparepart ps JOIN sparepart s ON ps.sparepart_id=s.id
                   WHERE pm_id=%s""", (pm_id,))
    usedSpareparts = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM sparepart")
    allSpareparts = cursor.fetchall()
    cursor.close()
    data = {
        "id_pm": pm[0],
        "time": pm[1],
        "tipe_pm": pm[2],
        "id_mesin": pm[3],
        "usedSpareparts": usedSpareparts,
        "allSpareparts": allSpareparts
    }
    #print(data["usedSpareparts"])
    # Ambil data dari HTML
    if request.method=='POST':
        #id_mesin=request.form["id_mesin"]
        time=request.form["time"]
        tipe_pm=request.form["tipe_pm"]
        spareparts_id=request.form.getlist("sparepart_id[]")
        spareparts_qty=request.form.getlist("sparepart_qty[]")
        #print("Sparepart sekarang:")
        last_sparepart=[row[0] for row in usedSpareparts]
        # last_sparepart = list(map(int, last_sparepart))
        print(last_sparepart)
        cursor=mysql.connection.cursor()
        cursor.execute("""UPDATE pm SET
                        time=%s, pm_type=%s
                       WHERE id=%s""", ( time, tipe_pm, data["id_pm"]))
        print(len(spareparts_id))
    
        # Menghapus yang tidak ada dalam sparepart sekarang
        for i in range(len(last_sparepart)):
            id=(last_sparepart[i])
            #print(id)
            spareparts_id=[(i) for i in spareparts_id]
            if id not in spareparts_id:
                #print("Masuk if")
                cursor.execute("DELETE FROM pm_sparepart WHERE pm_id=%s AND sparepart_id=%s", (data["id_pm"], id))
            else:
                print("masih ada")
             
        # Menambahkan atau mengupdate sparepart
        for i in range(len(spareparts_id)):
            #print("masuk loop")
            id=(spareparts_id[i])
            # print(f"id: {id}, type: {type(id)}")
            # print(f"last_sparepart: {last_sparepart}, type: {[type(n) for n in last_sparepart]}")
            # print(id)
            if  id not in last_sparepart:
                #print("masuk if ")
                cursor.execute("INSERT INTO pm_sparepart (pm_id, sparepart_id, qty) VALUES (%s,%s,%s)",
                               (data["id_pm"],spareparts_id[i], spareparts_qty[i]))
            else:
                #print("masuk else")
                cursor.execute("""UPDATE pm_sparepart SET qty=%s
                               WHERE pm_id=%s AND sparepart_id=%s""",
                               (spareparts_qty[i],data["id_pm"],spareparts_id[i]))
        mysql.connection.commit()
        cursor.close()
        #print("Submit sukses")
        flash("Berhasil di Update!", "success")
        return redirect(url_for("pm"))    
    elif request.method=="POST":
        flash("Gagal di Update!","error")

    return render_template("editPreventiveMaintenance.html", data=data)

@app.route('/workorder', methods=['GET', 'POST'])
def correctiveMaintenance():
    if not 'user_id' in session:
        flash("Silakan login terlebih dahulu", "warning")
        return redirect(url_for('login'))

    user_id=session['user_id']
    form=WOForm()
    cursor=mysql.connection.cursor()
    cursor.execute("Select id, name from machine")
    allMesin=cursor.fetchall()
    if form.validate_on_submit():
        print("berhasilll")
        mesin = form.mesin.data
        tanggal = form.tanggal.data
        deskripsi = form.deskripsi.data
        # waktu_laporan = form.waktu_laporan.data
        peminta = form.peminta.data
        print(mesin)
        #today=date.today()
        cursor = mysql.connection.cursor()
        cursor.execute("""INSERT INTO wo (report_time,machine_id, description, requester) 
                       VALUES (%s,%s, %s, %s)""",
                       (tanggal,mesin, deskripsi, peminta))
        mysql.connection.commit()
        cursor.close()
        flash("Laporan berhasil ditambahkan!", "success")
        return redirect(url_for('correctiveMaintenance'))
    elif request.method=="POST":
        flash("Laporan Gagal Ditambahkan","error")

    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT wo.id, report_time, machine.name, description, requester
                   FROM wo JOIN machine ON wo.machine_id=machine.id
                   WHERE stat=FALSE""")
    workOrder = cursor.fetchall()
    #print(allMesin)
    cursor.close()
    return render_template("correctiveMaintenance.html", allMesin=allMesin, form=form, workorder=workOrder)


@app.route('/workorder/<wo_id>', methods=['GET', 'POST'])
def penyelesaianCorrectiveMaintenance(wo_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT id, machine_id, report_time, description, requester
                   FROM wo WHERE id = %s""", (wo_id,))
    woDetails=cursor.fetchone()
    cursor.execute("""SELECT id, name FROM sparepart""")
    spareparts = cursor.fetchall()
    form = ExecuteWOForm()
    reportTime=woDetails[2]
    print(reportTime)
    if form.validate_on_submit():
        tanggalDikerjakan = form.tanggalDikerjakan.data
        jam_mulai = form.jam_mulai.data
        jam_selesai = request.form["jam_selesai"]
        spareparts_id = request.form.getlist("sparepart_id[]")  # Ambil daftar ID sparepart
        spareparts_qty = request.form.getlist("sparepart_qty[]")  # Ambil daftar jumlah sparepart

        cursor = mysql.connection.cursor()
        pic=session['user_id']
        cursor.execute("""UPDATE wo SET 
                    report_time=%s,start_time=%s, finish_time=%s, user_id=%s, stat=%s,tgl_kerja=%s
                    WHERE id=%s""", (reportTime,jam_mulai, jam_selesai,pic, 1,tanggalDikerjakan, wo_id))
        
        # Simpan Sparepart ke dalam tabel wo_sparepart
        for i in range(len(spareparts_id)):
            cursor.execute("INSERT INTO wo_sparepart (wo_id, sparepart_id, qty) VALUES (%s, %s, %s)",
                           (wo_id, spareparts_id[i], spareparts_qty[i]))

        mysql.connection.commit()
        cursor.close()
        flash("Laporan Telah Selesai!", "success")
        return redirect(url_for('correctiveMaintenance'))
    elif request.method=="POST":
        flash("Laporan Gagal!", "error")
        print(form.errors)
    
    return render_template("penyelesaianCorrectiveMaintenance.html", form=form, wo=woDetails, spareparts=spareparts)

if __name__=='__main__':
    app.run(debug=True)