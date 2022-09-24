from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFError
from werkzeug.security import generate_password_hash, check_password_hash

from website import CAPTCHA1
from . import db
from .models import Worker, Boss
import uuid
from .translator import getword

auth = Blueprint('auth', __name__)
global csrfg


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    else:
        if request.method == 'POST':
            accounttype = request.form.get('accounttype')
            email = request.form.get('email')
            password = request.form.get('password')

            if accounttype == 'worker':
                user = Worker.query.filter_by(email=email).first()
            else:
                user = Boss.query.filter_by(email=email).first()

            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    if accounttype == 'worker':
                        return redirect(url_for('views.boss'))
                    else:
                        return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user,
                           emailtext=getword("email", cookie),
                           passwordtext=getword("password", cookie),
                           logintext=getword("login", cookie),
                           enterpassword=getword("enterpassword", cookie),
                           enteremail=getword("enteremail", cookie),
                           registerhere=getword("registerhere", cookie),
                           notregistered=getword("notregistered", cookie))


@auth.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Logged out successfully!', category='success')
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.is_authenticated:
        if current_user.accounttype == 'worker' and current_user.boss_id is None:
            return redirect(url_for('views.boss'))
        else:
            return redirect(url_for('views.home'))
    captcha = CAPTCHA1.create()
    if request.method == 'POST':
        accounttype = request.form.get('accounttype')
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')
        if c_hash is None:
            return render_template("hash_error.html", user=current_user)

        if not CAPTCHA1.verify(c_text, c_hash):
            flash('Captcha is incorrect.', category='error')
            return redirect(url_for('auth.sign_up'))

        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if accounttype == 'worker':
            user = Worker.query.filter_by(email=email).first()
        elif accounttype == 'boss':
            user = Boss.query.filter_by(email=email).first()
        else:
            user = None
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            if accounttype == 'worker':
                key = uuid.uuid4().hex
                new_user = Worker(email=email, first_name=first_name,
                                  password=generate_password_hash(password1, method='sha256'), accounttype="worker", registrationid=key)
            elif accounttype == 'boss':
                new_user = Boss(email=email, first_name=first_name,
                                password=generate_password_hash(password1, method='sha256'), accounttype="boss")
            else:
                flash('Account type not selected.', category='error')
                return redirect(url_for('auth.sign_up'))

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            if accounttype == 'worker':
                return redirect(url_for('views.boss'))
            else:
                return redirect(url_for('views.home'))


    return render_template("sign_up.html", user=current_user, captcha=captcha,
                           emailtext=getword("email", cookie),
                           nametext=getword("name", cookie),
                           passwordtext=getword("password", cookie),
                           passwordconfirm=getword("cnewpassword", cookie),
                           submit=getword("submit", cookie),
                           firstandlast=getword("firstandlast", cookie),
                           signup=getword("signup", cookie),
                           enteremail=getword("enteremail", cookie),
                           alreadyhaveaccount=getword("alreadyhaveaccount", cookie),
                           loginhere=getword("loginhere", cookie))

@auth.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'

    if current_user.is_authenticated and current_user.accounttype == 'boss':
        if current_user.workers:
            flash('You have workers, you cannot delete your account.', category='error')
            return redirect(url_for('views.home'))

    if request.method == 'POST':
        checkbox = request.form.get('confirm')
        password = request.form.get('password')
        email = current_user.email
        if checkbox == 'on':
            if current_user.accounttype == 'worker':
                user = Worker.query.filter_by(email=email).first()
            else:
                user = Boss.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    db.session.delete(user)
                    db.session.commit()
                    flash('Account deleted successfully!', category='success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Incorrect password, try again.', category='error')
        else:
            flash('You must confirm you want to delete your account.', category='error')


    return render_template("delete_account.html", user=current_user,
                           deleteaccount=getword("deleteaccount", cookie),
                           confirmtext=getword("confirmdelete", cookie),
                           password=getword("password", cookie),
                           enterpassword=getword("enterpassword", cookie))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if 'locale' in request.cookies:
        cookie = request.cookies.get('locale')
    else:
        cookie = 'en'
    captcha = CAPTCHA1.create()
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        password3 = request.form.get('password3')
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')
        if c_hash is None:
            return render_template("hash_error.html", user=current_user)

        confirm = request.form.get('confirm')
        email = current_user.email
        if current_user.accounttype == 'worker':
            user = Worker.query.filter_by(email=email).first()
        else:
            user = Boss.query.filter_by(email=email).first()
        if not CAPTCHA1.verify(c_text, c_hash):
            flash('Captcha is incorrect.', category='error')
            return redirect(url_for('auth.change_password'))

        if not confirm == 'on':
            flash('You must confirm you want to change your password.', category='error')
            return redirect(url_for('auth.change_password'))

        if user:
            if check_password_hash(user.password, password1):
                if password2 != password3:
                    flash('Passwords don\'t match.', category='error')
                elif len(password2) < 7:
                    flash('Password must be at least 7 characters.', category='error')
                else:
                    user.password = generate_password_hash(password2, method='sha256')
                    db.session.commit()
                    flash('Password changed successfully!', category='success')
                    return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')

    return render_template("change_password.html", user=current_user, captcha=captcha,
                           changepassword=getword("changepassword", cookie),
                           oldpassword=getword("oldpassword", cookie),
                           newpassword=getword("newpassword", cookie),
                           cnewpassword=getword("cnewpassword", cookie),
                           confirmtext=getword("confirm", cookie),
                           enterpassword=getword("enterpassword", cookie))


@auth.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description, user=current_user), 400
