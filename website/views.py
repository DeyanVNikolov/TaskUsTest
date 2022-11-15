import os
import uuid
from os.path import join, dirname, realpath

import requests
from flask import abort
from flask import current_app as app
from werkzeug.utils import secure_filename, send_from_directory

global csrfg
from .models import Task

from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from website import CAPTCHA1
from . import db
from .mailsender import sendregisterationemailboss
from .models import Worker, Boss

from .translator import getword

views = Blueprint('views', __name__)

homepage = "views.home"
workerspage = "views.workers"
oneworkerpage = "views.worker"

global csrfg


class StatusDenied(Exception):
    print("StatusDenied Exception")


def checkmaintenance():
    # Not in use
    pass


@views.errorhandler(StatusDenied)
def redirect_on_status_denied(error):
    print(error)
    return render_template("maintenance.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie)), 403


@views.route('/', methods=['GET'])
def home():
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'
    return render_template("home.html", profilenav=getword("profilenav", cookie), loginnav=getword("loginnav", cookie),
                           signupnav=getword("signupnav", cookie), tasksnav=getword("tasksnav", cookie),
                           workersnav=getword("workersnav", cookie), adminnav=getword("adminnav", cookie),
                           logoutnav=getword("logoutnav", cookie), homenav=getword("homenav", cookie),
                           user=current_user, tooltext1=getword("tooltext1", cookie),
                           tooltext2=getword("tooltext2", cookie), tooltext3=getword("tooltext3", cookie),
                           employees=getword("workersnav", cookie), tasks=getword("tasksnav", cookie),
                           register=getword("signup", cookie), login=getword("login", cookie),
                           boss=getword("boss", cookie), worker=getword("worker", cookie),
                           enterpassword=getword("enterpassword", cookie), enteremail=getword("enteremail", cookie),
                           notregistered=getword("notregistered", cookie), registerhere=getword("registerhere", cookie),
                           logout=getword("logout", cookie), profile=getword("profile", cookie))


@views.route("/home", methods=['GET'])
def homeredirect():
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'
    return redirect(url_for("views.home"))


@views.route('/profile')
@login_required
def profile():
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'
    return render_template("profile.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), user=current_user,
                           emailtext=getword("emailshort", request.cookies.get('locale')),
                           nametext=getword("name", request.cookies.get('locale')),
                           profiletext=getword("profiletext", request.cookies.get('locale')),
                           changepassword=getword("changepassword", request.cookies.get('locale')),
                           deleteaccount=getword("deleteaccount", request.cookies.get('locale')),
                           myfiles=getword("myfiles", request.cookies.get('locale')))


@views.route('/boss')
@login_required
def boss():
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.accounttype == "boss":
        return redirect(url_for(homepage))

    if current_user.accounttype == "worker":
        if current_user.boss_id is not None:
            return redirect(url_for(homepage))

    return render_template("boss.html", profilenav=getword("profilenav", cookie), loginnav=getword("loginnav", cookie),
                           signupnav=getword("signupnav", cookie), tasksnav=getword("tasksnav", cookie),
                           workersnav=getword("workersnav", cookie), adminnav=getword("adminnav", cookie),
                           logoutnav=getword("logoutnav", cookie), homenav=getword("homenav", cookie),
                           user=current_user, boss=getword("boss", cookie),
                           accessmessage=getword("accessmessage", cookie), youridtext=getword("youridtext", cookie),
                           id=getword("idemail", cookie))


@views.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.accounttype == 'worker' and current_user.boss_id is None:
        return redirect(url_for('views.boss'))

    if current_user.accounttype == 'boss':
        return redirect(url_for(workerspage))

    if request.method == 'POST':
        typeform = request.form.get('typeform')
        if typeform == 'done':
            taskid = request.form.get('task_id')
            task = Task.query.get(taskid)
            task.complete = "2"
            db.session.commit()
        elif typeform == 'notdone':
            taskid = request.form.get('task_id')
            taskpost = Task.query.get(taskid)
            taskpost.complete = "0"
            db.session.commit()
            return redirect(url_for('views.tasks'))

    taskstodisplay = []

    for task in Task.query.filter_by(worker_id=current_user.id).all():
        taskstodisplay.append(
            {"task": task.task, "complete": task.complete, "actual_id": task.actual_id, "task_id": task.id,
             "title": task.title, "ordernumber": task.ordernumber})

    return render_template("tasks.html", profilenav=getword("profilenav", cookie), loginnav=getword("loginnav", cookie),
                           signupnav=getword("signupnav", cookie), tasksnav=getword("tasksnav", cookie),
                           workersnav=getword("workersnav", cookie), adminnav=getword("adminnav", cookie),
                           logoutnav=getword("logoutnav", cookie), homenav=getword("homenav", cookie),
                           notdone=getword("notdone", cookie), tasktitle=getword("tasktitle", cookie),
                           moreinfo=getword("moreinfo", cookie), user=current_user, taskslist=taskstodisplay,
                           tasktext=getword("tasktext", cookie), statustext=getword("statustext", cookie),
                           workertext=getword("workertext", cookie), done=getword("done", cookie),
                           tasktextplural=getword("tasktextplural", cookie), notstarted=getword("NotStarted", cookie),
                           completed=getword("completed", cookie), started=getword("started", cookie))


@views.route('/workers', methods=["GET", "POST"])
@login_required
def workers():
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.is_authenticated:
        if current_user.accounttype == "worker":
            return redirect(url_for(homepage))

    taskstodisplay = []

    if request.method == "POST":
        if request.form.get("typeform") == "add":
            id = request.form.get('ID')

            if id == "" or id is None:
                flash(getword("missingid", cookie), category="error")
            else:
                worker = Worker.query.filter_by(registrationid=id).first()
                if worker is None:
                    flash(getword("noworkerwithid", cookie), category="error")
                else:
                    if worker.boss_id is None:
                        worker.boss_id = current_user.id
                        db.session.commit()
                        flash(getword("workeradded", cookie), category="success")
                    else:
                        flash(getword("workeralreadyadded", cookie), category="error")
        elif request.form.get("typeform") == "delete":
            id = request.form.get('worker_id')
            worker = Worker.query.filter_by(registrationid=id).first()
            if worker.boss_id is not None and worker.boss_id != current_user.id:
                flash(getword("workernotfound", cookie), category="error")

            if worker is None:
                flash(getword("noworkerwithid", cookie), category="error")
            else:
                if worker.boss_id is None:
                    flash(geword("workeralreadyremoved", cookie), category="error")
                else:
                    try:
                        worker.boss_id = None
                        for task in Task.query.filter_by(worker_id=worker.id).all():
                            db.session.delete(task)
                        db.session.commit()
                        flash(getword("workerremoved", cookie), category="success")
                    except Exception as e:
                        flash(e, category="error")
        elif request.form.get("typeform") == "task":
            task = request.form.get('task')
            title = request.form.get('title')
            if task == "" or task is None or title == "" or title is None:
                flash(getword("missingtask", cookie), category="error")
            else:
                try:
                    workerslist = request.form.getlist('worker')
                    if len(workerslist) == 0:
                        flash(getword("noworkersselected", cookie), category="error")
                        return redirect(url_for(workerspage))
                    workersl = Worker.query.filter(Worker.id.in_(workerslist)).all()
                    tasknum = 0
                    acid = str(uuid.uuid4())
                    for workerg in workersl:
                        tasknum += 1
                        new_task = Task(task=task, title=title, worker_id=workerg.id, boss_id=current_user.id,
                                        actual_id=acid, ordernumber=tasknum)
                        db.session.add(new_task)
                        db.session.commit()
                    flash(getword("taskadded", cookie), category="success")
                    redirect(url_for(workerspage))
                except Exception as e:
                    flash(e, category="error")
        elif request.form.get("typeform") == "workermenu":
            workerid = request.form.get('worker_id')
            return redirect(url_for(oneworkerpage, id=workerid))

    for task in Task.query.filter_by(boss_id=current_user.id).all():
        taskstodisplay.append({"task": task.task, "actual_id": task.actual_id, "ordernumber": task.ordernumber})

    for task in taskstodisplay:
        if task["ordernumber"] != 1:
            taskstodisplay.remove(task)

    return render_template("workers.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), user=current_user, idtext=getword("idtext", cookie),
                           addworker=getword("addworker", cookie), delete=getword("delete", cookie),
                           taskslist=taskstodisplay, workertext=getword("workertext", cookie),
                           addtask=getword("addtask", cookie), email=getword("email", cookie),
                           name=getword("name", cookie), selectall=getword("selectall", cookie),
                           deselectall=getword("deselectall", cookie), workermenu=getword("workermenu", cookie),
                           submit=getword("submit", cookie), selectworkers=getword("selectworkers", cookie),
                           signupemploy=getword("signupemploy", cookie), here=getword("here", cookie),
                           myfiles=getword("empmyfiles", cookie))


@views.route('/worker/<path:id>', methods=["GET", "POST"])
@login_required
def worker(id):
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.accounttype == "worker":
        return redirect(url_for(homepage))

    worker = Worker.query.filter_by(id=id).first()
    if worker is None:
        return redirect(url_for(workerspage))
    if worker.boss_id != current_user.id:
        return redirect(url_for(workerspage))

    taskstodisplay = []

    for task in Task.query.filter_by(worker_id=worker.id).all():
        taskstodisplay.append(
            {"task": task.task, "complete": task.complete, "actual_id": task.actual_id, "task_id": task.id,
             "ordernumber": task.ordernumber, "title": task.title, "comment": task.comment})
    if request.method == "POST":
        typeform = request.form.get('typeform')
        taskid = request.form.get('task_id')
        if Task.query.filter_by(id=taskid).first().boss_id != current_user.id:
            flash(getword("youcantedittask", cookie), category="error")
            return redirect(url_for(workerspage))
        if typeform == 'done':
            taskid = request.form.get('task_id')
            task = Task.query.get(taskid)
            task.complete = True
            db.session.commit()
            return redirect(url_for(oneworkerpage, id=id))
        elif typeform == 'delete':
            taskid = request.form.get('task_id')
            task = Task.query.get(taskid)
            db.session.delete(task)
            db.session.commit()
            return redirect(url_for(oneworkerpage, id=id))
        elif typeform == 'notdone':
            taskid = request.form.get('task_id')
            taskpost = Task.query.get(taskid)
            taskpost.complete = False
            db.session.commit()
            return redirect(url_for(oneworkerpage, id=id))
        elif typeform == 'deletefromall':
            taskid = request.form.get('task_id')
            task = Task.query.get(taskid)
            task_actual_id = task.actual_id
            for task in Task.query.filter_by(actual_id=task_actual_id).all():
                db.session.delete(task)
            db.session.commit()
            return redirect(url_for(oneworkerpage, id=id))

    return render_template("worker.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), notdone=getword("notdone", cookie),
                           moreinfo=getword("moreinfo", cookie), workerid=id, user=current_user, worker=worker,
                           taskslist=taskstodisplay, tasktext=getword("tasktext", cookie),
                           statustext=getword("statustext", cookie), workertext=getword("workertext", cookie),
                           done=getword("done", cookie), tasktextplural=getword("tasktextplural", cookie),
                           notstarted=getword("NotStarted", cookie), completed=getword("completed", cookie),
                           delete=getword("delete", cookie), started=getword("started", cookie),
                           deletefromall=getword("deletefromall", cookie), workeridtext=getword("workeridtext", cookie))


@views.route('/uploaded_file/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    checkmaintenance()

    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if not current_user.is_authenticated:
        flash(getword("youneedtobeloggedin", cookie), category="error")
        return redirect(url_for('auth.login'))

    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        if current_user.accounttype == "worker":
            imageid = filename.split("_")[0]

            # check if imageid is either workerid or bossid
            worker = Worker.query.filter_by(id=imageid).first()
            if worker is None:
                boss = Boss.query.filter_by(id=imageid).first()
                if boss is None:
                    return redirect(url_for(homepage))
                else:
                    if current_user.boss_id != boss.id:
                        return redirect(url_for(homepage))
            else:
                if worker.id != current_user.id:
                    return redirect(url_for(homepage))
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, environ=request.environ)


        elif current_user.accounttype == "boss":
            imageid = filename.split("_")[0]
            if Boss.query.filter_by(id=imageid).first() is not None:
                if Boss.query.filter_by(id=imageid).first().id == current_user.id:
                    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, environ=request.environ)
            elif Worker.query.filter_by(id=imageid).first() is not None:
                if Worker.query.filter_by(id=imageid).first().boss_id == current_user.id:
                    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, environ=request.environ)

            flash(getword("nopermtoviewthisview", cookie), category="error")
            return redirect(url_for(homepage))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, environ=request.environ)


@views.route("/static/uploads/<path:filename>", methods=["GET"])
def get_file(filename):
    return redirect(url_for('views.uploaded_file', filename=filename))


def hastebin(text):
    r = requests.post("https://hastebin.com/documents", data=text)
    return "https://hastebin.com/raw/" + r.json()["key"]


@views.route('/task/<int:id>', methods=["GET", "POST"])
@login_required
def task(id):
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    taskdata = Task.query.filter_by(id=id).first()
    if taskdata is None:
        flash(getword("tasknotfound", cookie), category="error")
        return redirect(url_for(homepage))

    if current_user.accounttype == "worker":
        if taskdata.worker_id != current_user.id:
            flash(getword("tasknotfound", cookie), category="error")
            return redirect(url_for(homepage))
    elif current_user.accounttype == "boss":
        if taskdata.boss_id != current_user.id:
            flash(getword("tasknotfound", cookie), category="error")
            return redirect(url_for(homepage))

    if request.method == "POST":
        typeform = request.form.get('typeform')
        taskid = request.form.get('task_id')

        if taskid != str(id):
            flash(getword("tasknotfound", cookie), category="error")
            return redirect(url_for("views.task", id=id))

        task = Task.query.filter_by(id=taskid).first()
        if task is None:
            flash(getword("tasknotfound", cookie), category="error")
            return redirect(url_for("views.task", id=id))

        if Task.query.filter_by(id=taskid).first().boss_id != current_user.id:
            if Task.query.filter_by(id=taskid).first().worker_id != current_user.id:
                flash(getword("youcantedittask", cookie), category="error")
                return redirect(url_for("views.task", id=id))

        if typeform == 'done':
            taskid = request.form.get('task_id')
            taskcomment = request.form.get('comment')
            taskpost = Task.query.get(taskid)
            taskpost.complete = "2"
            taskpost.comment = taskcomment
            db.session.commit()
            return redirect(url_for('views.task', id=id))
        elif typeform == 'notdone':
            taskid = request.form.get('task_id')
            taskpost = Task.query.get(taskid)
            taskpost.complete = False
            db.session.commit()
            return redirect(url_for('views.task', id=id))
        elif typeform == "hastebin":
            if request.form.get('commenthaste') == "" or request.form.get('commenthaste') is None:
                flash(getword("nocontent", cookie), category="error")
                return redirect(url_for('views.task', id=id))
            if len(request.form.get('commenthaste')) > 20000:
                flash(getword("toolong20kmax", cookie), category="error")
                return redirect(url_for('views.task', id=id))
            hastebinlink = hastebin(request.form.get('commenthaste'))
            return render_template("task.html", profilenav=getword("profilenav", cookie),
                                   loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                                   tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                                   adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                                   homenav=getword("homenav", cookie),
                                   markyourtaskasdonetext=getword("markyourtaskasdonetext", cookie),
                                   photolinktexttitle=getword("photolinktexttitle", cookie),
                                   photouploader=getword("photouploader", cookie), copy=getword("copy", cookie),
                                   sevendaylimit=getword("sevendaylimit", cookie),
                                   submitcodetext=getword("submitcodetext", cookie), showhastebinmodal=True,
                                   hastebinlink=hastebinlink, print=getword("print", cookie), user=current_user,
                                   notdone=getword("notdone", cookie), task=taskdata.task, task1=taskdata,
                                   title=taskdata.title, taskid=id, done=getword("done", cookie),
                                   tasktext=getword("tasktext", cookie), statustext=getword("statustext", cookie),
                                   workertext=getword("workertext", cookie),
                                   tasktextplural=getword("tasktextplural", cookie),
                                   notstarted=getword("NotStarted", cookie), completed=getword("completed", cookie),
                                   delete=getword("delete", cookie), starttext=getword("starttext", cookie),
                                   started=getword("started", cookie), uploadtext=getword("uploadtext", cookie))
        elif typeform == "uploadimage":
            ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash(getword("nofileselected", cookie), category="error")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                # check file size
                if file.content_length > 15000000:
                    flash(getword("filetoobig15mb", cookie), category="error")
                    return redirect(url_for('views.task', id=id))
                # check if file is suspicious
                suspicious_file_types = ['application/x-dosexec', 'application/x-msdownload',
                                         'application/x-msdos-program', 'application/x-msi', 'application/x-winexe',
                                         'application/x-shockwave-flash', 'application/x-shockwave-flash2-preview',
                                         'application/x-java-applet', 'application/x-java-bean',
                                         'application/x-java-vm', ]
                if file.content_type in suspicious_file_types:
                    flash(getword("wecannotacceptthisfile", cookie), category="error")
                    return redirect(url_for('views.task', id=id))
                filename = secure_filename(file.filename)
                finalfilename = str(current_user.id) + "_" + filename
                UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')
                path = join(UPLOADS_PATH, finalfilename)
                file.save(path)
                imageurl = url_for('views.uploaded_file', filename=finalfilename)

                return render_template("task.html", profilenav=getword("profilenav", cookie),
                                       loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                                       tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                                       adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                                       homenav=getword("homenav", cookie),
                                       markyourtaskasdonetext=getword("markyourtaskasdonetext", cookie),
                                       photolinktexttitle=getword("photolinktexttitle", cookie),
                                       photouploader=getword("photouploader", cookie), showimagemodal=True,
                                       imageurl=imageurl, copy=getword("copy", cookie), hastebinlink=None,
                                       showhastebinmodal=False, sevendaylimit=getword("sevendaylimit", cookie),
                                       submitcodetext=getword("submitcodetext", cookie), print=getword("print", cookie),
                                       user=current_user, notdone=getword("notdone", cookie), task=taskdata.task,
                                       task1=taskdata, title=taskdata.title, taskid=id, done=getword("done", cookie),
                                       tasktext=getword("tasktext", cookie), statustext=getword("statustext", cookie),
                                       workertext=getword("workertext", cookie),
                                       tasktextplural=getword("tasktextplural", cookie),
                                       notstarted=getword("NotStarted", cookie), completed=getword("completed", cookie),
                                       delete=getword("delete", cookie), starttext=getword("starttext", cookie),
                                       started=getword("started", cookie), uploadtext=getword("uploadtext", cookie))
            else:
                flash(getword("invalidtype", cookie), category="error")
                return redirect(url_for('views.task', id=id))
        elif typeform == "start":
            taskid = request.form.get('task_id')
            taskpost = Task.query.get(taskid)
            taskpost.complete = "1"
            db.session.commit()
            return redirect(url_for('views.task', id=id))

    return render_template("task.html", profilenav=getword("profilenav", cookie), loginnav=getword("loginnav", cookie),
                           signupnav=getword("signupnav", cookie), tasksnav=getword("tasksnav", cookie),
                           workersnav=getword("workersnav", cookie), adminnav=getword("adminnav", cookie),
                           logoutnav=getword("logoutnav", cookie), homenav=getword("homenav", cookie),
                           markyourtaskasdonetext=getword("markyourtaskasdonetext", cookie),
                           photolinktexttitle=getword("photolinktexttitle", cookie),
                           photouploader=getword("photouploader", cookie), copy=getword("copy", cookie),
                           sevendaylimit=getword("sevendaylimit", cookie),
                           submitcodetext=getword("submitcodetext", cookie), showimagemodal=False,
                           showhastebinmodal=False, hastebinlink=None, print=getword("print", cookie),
                           user=current_user, notdone=getword("notdone", cookie), task=taskdata.task, task1=taskdata,
                           title=taskdata.title, taskid=id, done=getword("done", cookie),
                           tasktext=getword("tasktext", cookie), statustext=getword("statustext", cookie),
                           workertext=getword("workertext", cookie), tasktextplural=getword("tasktextplural", cookie),
                           notstarted=getword("NotStarted", cookie), completed=getword("completed", cookie),
                           delete=getword("delete", cookie), starttext=getword("starttext", cookie),
                           started=getword("started", cookie), uploadtext=getword("uploadtext", cookie))


@views.route('/urlout/<path:url>', methods=["GET", "POST"])
def urlout(url):
    abort(403)
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'
    return render_template("urlout.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), url=url, user=current_user,
                           youllberedirectedto=getword("youllberedirectedto", cookie), here=getword("here", cookie),
                           ifyourenotredirected=getword("ifyourenotredirected", cookie),
                           oryoucango=getword("oryoucango", cookie), home=getword("home", cookie),
                           thirdpartylink=getword("thirdpartylink", cookie),
                           infiveseconds=getword("infiveseconds", cookie))


@views.route('/contact', methods=["GET", "POST"])
def contact():
    checkmaintenance()
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    return render_template("contact.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), user=current_user,
                           contactus=getword("contactus", cookie), contactusmessage=getword("contactusmessage", cookie),
                           contactname=getword("contactname", cookie), contactemail=getword("contactemail", cookie))


@views.route('/testpastebin', methods=["GET", "POST"])
def testpastebin():
    abort(403)
    return "false"


@views.route("/printtask/<int:id>", methods=["GET", "POST"])
def printtask(id):
    abort(403)
    checkmaintenance()
    # cookie
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    taskdata = Task.query.filter_by(id=id).first()

    worker = Worker.query.filter_by(id=taskdata.worker_id).first()
    worker_id = worker.id
    workername = worker.first_name
    workeremail = worker.email

    if taskdata is None:
        flash(getword("tasknotfound", cookie), category="error")
        return redirect(url_for(homepage))

    if current_user.accounttype == "worker":
        if taskdata.worker_id != current_user.id:
            flash(getword("tasknotfound", cookie), category="error")
            return redirect(url_for(homepage))

    elif current_user.accounttype == "boss":
        if taskdata.boss_id != current_user.id:
            flash(getword("tasknotfound", cookie), category="error")
            return redirect(url_for(homepage))

    return render_template("printtask.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), user=current_user, task=taskdata.task, task1=taskdata,
                           title=taskdata.title, taskid=id, workerid=worker_id, notdone=getword("notdone", cookie),
                           workeremail=workeremail, workername=workername, boss=current_user.first_name, cookie=cookie,
                           workeridtext=getword("workeridtext", cookie),
                           workeremailtext=getword("workeremailtext", cookie),
                           workernametext=getword("workernametext", cookie),
                           taskstatustext=getword("taskstatustext", cookie), attext=getword("attext", cookie),
                           requestedbytext=getword("requestedbytext", cookie),
                           startedtext=getword("startedtext", cookie))


@views.route("/files/<path:id>", methods=["GET", "POST"])
def files(id):

    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.accounttype == "worker":
        if current_user.id != id:
            flash(getword("workernotfound", cookie), category="error")
            return redirect(url_for(homepage))
    elif current_user.accounttype == "boss":
        if current_user.id != id:
            if Worker.query.filter_by(id=id).first().boss_id != current_user.id:
                flash(getword("workernotfound", cookie), category="error")
                return redirect(url_for(homepage))

    # check static/uploads for files starting with id
    files = []
    splitnames = []
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        # split by _
        file1 = file.split("_")
        if str(file1[0]) == str(id):
            files.append(file)

    print(files)
    return render_template("files.html", profilenav=getword("profilenav", cookie), loginnav=getword("loginnav", cookie),
                           signupnav=getword("signupnav", cookie), tasksnav=getword("tasksnav", cookie),
                           workersnav=getword("workersnav", cookie), adminnav=getword("adminnav", cookie),
                           logoutnav=getword("logoutnav", cookie), homenav=getword("homenav", cookie),
                           user=current_user, files=files, splitnames=splitnames)


@views.route("/docs", methods=["GET"], subdomain="docs")
def docs():
    return "Hey"


@views.route("/privacy", methods=["GET"])
def privacy():
    abort(403)


@views.route("/employ/sign-up", methods=["GET", "POST"])
def employ_signup():

    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.accounttype == "worker":
        return redirect(url_for(homepage))

    captcha = CAPTCHA1.create()

    if request.method == 'POST':
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')
        if c_hash is None:
            return render_template("hash_error.html", profilenav=getword("profilenav", cookie),
                                   loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                                   tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                                   adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                                   homenav=getword("homenav", cookie), user=current_user)

        if not CAPTCHA1.verify(c_text, c_hash):
            flash(getword("captchawrong", cookie), category='error')
            return redirect(url_for('views.employ_signup'))

        email = request.form.get('email')

        try:
            v = validate_email(email, check_deliverability=True)
            email = v["email"]
            parts1 = email.split('@')
            if parts1[1] == "tasklify.me":
                flash(getword("tasklifymedomainnotallowed", cookie), category='error')
                return redirect(url_for('views.employ_signup'))
        except EmailNotValidError as e:
            flash(e, category='error')
            return redirect(url_for('views.employ_signup'))

        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Worker.query.filter_by(email=email).first()
        if not user:
            user = None

        if user:
            flash(getword("emailalreadyexists", cookie), category='error')
        elif len(email) < 4:
            flash(getword("emailtooshort", cookie), category='error')
        elif len(first_name) < 2:
            flash(getword("nametooshort", cookie), category='error')
        elif password1 != password2:
            flash(getword("passwordsdontmatch", cookie), category='error')
        elif len(password1) < 8:
            flash(getword("passwordtooshort", cookie), category='error')
        else:
            key = uuid.uuid4().hex
            new_user = Worker(email=email, first_name=first_name,
                              password=generate_password_hash(password1, method='sha256'), accounttype="worker",
                              registrationid=key)

            db.session.add(new_user)
            db.session.commit()
            flash(getword("accountcreated", cookie), category='success')
            sendregisterationemailboss(email, first_name)
            return redirect(url_for('views.workers'))

    return render_template("employ_signup.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), user=current_user, captcha=captcha,
                           emailtext=getword("email", cookie), nametext=getword("name", cookie),
                           passwordtext=getword("password", cookie), passwordconfirm=getword("cnewpassword", cookie),
                           submit=getword("submit", cookie), firstandlast=getword("firstandlast", cookie),
                           signup=getword("signupemploy", cookie), enteremail=getword("enteremail", cookie),
                           alreadyhaveaccount=getword("alreadyhaveaccount", cookie),
                           loginhere=getword("loginhere", cookie),
                           databeingproccessed=getword("databeingproccessed", cookie),
                           employreccode=getword("employreccode", cookie),
                           addemployeeinfosignup=getword("addemployeeinfosignup", cookie))


@views.route("/add/employee", methods=["GET", "POST"])
def add_employee():

    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.accounttype == "worker":
        return redirect(url_for(homepage))

    if request.method == 'POST':
        if request.form.get("typeform") == "add":
            id = request.form.get('ID')

            if id == "" or id is None:
                flash(getword("missingid", cookie), category="error")
            else:
                worker = Worker.query.filter_by(registrationid=id).first()
                if worker is None:
                    flash(getword("noworkerwithid", cookie), category="error")
                else:
                    if worker.boss_id is None:
                        worker.boss_id = current_user.id
                        db.session.commit()
                        flash(getword("workeradded", cookie), category="success")
                    else:
                        flash(getword("workeralreadyadded", cookie), category="error")

    return render_template("add_employee.html", profilenav=getword("profilenav", cookie),
                           loginnav=getword("loginnav", cookie), signupnav=getword("signupnav", cookie),
                           tasksnav=getword("tasksnav", cookie), workersnav=getword("workersnav", cookie),
                           adminnav=getword("adminnav", cookie), logoutnav=getword("logoutnav", cookie),
                           homenav=getword("homenav", cookie), user=current_user,
                           addemployee=getword("addemployee", cookie),
                           addemployeeinfo=getword("addemployeeinfo", cookie), enterid=getword("enterid", cookie),
                           submit=getword("submit", cookie), databeingproccessed=getword("databeingproccessed", cookie),
                           addemployeeinfosignup=getword("addemployeeinfosignup", cookie),
                           addworker=getword("addworker", cookie), goback=getword("goback", cookie))