# -*- coding: utf-8 -*-
import os
from flask import render_template, flash, redirect, url_for, make_response, session
from app import app, conn
from app.forms import LoginForm, WindowForm, CreateAccountForm, ChangePasswordForm
from wtforms import StringField
from wtforms.widgets import PasswordInput
from http import cookies
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, logout_user, login_required, login_user, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

cursor = conn.cursor()

class User(UserMixin):
	def __init__(self, id):
		self.id = id
	def __repr__(self):
		return "%d/%s/%s/%s/%d" % (self.id)

@login_manager.user_loader
def load_user(user_id):
	return User(user_id)

#conn = psycopg2.connect(dbname='calculator_windows_and_doors', user='postgres', password='v15l02a97d', host='localhost')
#user = {'name': None, 'login': None, 'level': None}

@app.route('/')
@app.route('/index')
def index():
	if not current_user.is_authenticated:
		user = [None, None]
	else:
		cursor.execute('select name, login from account where id = %s',(current_user.id,))
		user = cursor.fetchone()
	return render_template('index.html', title='Главная страница', user=user)

@app.route('/account')
@login_required
def account():
	cursor.execute('select name, login, status from account where id = %s',(current_user.id,))
	user = cursor.fetchone()
	return render_template('account.html', title='Личный кабинет', user=user)

@app.route('/newAccount', methods=['GET', 'POST'])
@login_required
def newAccount():
	cursor.execute('select name, login, status from account where id = %s',(current_user.id,))
	user = cursor.fetchone()
	form = CreateAccountForm()
	if form.validate_on_submit():
		cursor.execute('select * from account where login = %s', (form.login.data,))
		check_user = cursor.fetchone()
		if check_user:
			flash('Учетная запись с таким логином уже существует!')
			return redirect(url_for('newAccount'))
		cursor.execute('insert into account (login, passwordHash, name, status) values (%s, %s, %s, %s);',
		(form.login.data, generate_password_hash(form.password.data), form.name.data, form.level.data,))
		conn.commit()
		flash('Учетная запись для {} создана успешно!'.format(form.name.data))
		flash('Login: {}'.format(form.login.data))
		flash('Pasword: {}'.format(form.password.data))
		return redirect(url_for('account'))
	return render_template('newAccount.html', title='Создание аккаунта', form=form, user=user)
	'''if record and record[0][0] != 0:
		form = CreateAccountForm()
		if form.validate_on_submit():
			cursor = conn.cursor()
			cursor.execute('select * from account where login = %s', (form.login.data,))
			conn.commit()
			newRecord = cursor.fetchall()
			if newRecord:
				#cursor.close()
				flash('Учетная запись с таким логином уже существует!')
				return redirect(url_for('account'))
			cursor.execute('insert into account (login, passwordHash, name, status) values (%s, %s, %s, %s);',
			(form.login.data, generate_password_hash(form.password.data), form.name.data, form.level.data,))
			conn.commit()
			cursor.close()
			flash('Учетная запись для {} создана успешно!'.format(form.name.data))
			flash('Login: {}'.format(form.login.data))
			flash('Pasword: {}'.format(form.password.data))
			return redirect(url_for('account'))
	else:
		flash('Отказано в доступе')
		return redirect(url_for('index'))
	return render_template('newAccount.html', title='Создание аккаунта', form=form, user=user)'''

@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
	cursor.execute('select name, login, passwordHash from account where id = %s',(current_user.id,))
	user = cursor.fetchone()
	if form.validate_on_submit():
		if check_password_hash(user[2], form.passwordOld.data) and form.passwordNew1.data == form.passwordNew2.data:
			cursor.execute('update account set passwordHash = %s where id = %s',
			(generate_password_hash(form.passwordNew1.data), current_user.id,))
			conn.commit()
			flash('Пароль был успешно изменен')
			return redirect(url_for('account'))
		else:
			flash('Старый пароль введен неверно или новые пароли не совпадают')
			return redirect(url_for('changePassword'))
	'''if user['login'] != None:
		form = ChangePasswordForm()
		if form.validate_on_submit():
			cursor = conn.cursor()
			cursor.execute('select passwordHash from account where login = %s', (user['login'],))
			conn.commit()
			record = cursor.fetchall()
			if check_password_hash(record[0][0], form.passwordOld.data) and form.passwordNew1.data == form.passwordNew2.data:
				cursor.execute('update account set passwordHash = %s where login = %s',
				(generate_password_hash(form.passwordNew1.data), user['login'],))
				conn.commit()
				cursor.close()
				flash('Пароль был успешно изменен')
				return redirect(url_for('account'))
			else:
				cursor.close()
				flash('Старый пароль введен неверно или новые пароли не совпадают')
				return redirect(url_for('changePassword'))
	else:
		flash('Отказано в доступе, вы не авторизированы')
		return redirect(url_for('index'))
	return render_template('changePassword.html', title='Смена пароля', form=form)#, user=user)'''

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Вы вышли из профиля')
	return redirect(url_for('index'))
	'''global user
	user = {'name': None, 'login': None, 'level': None}
	return redirect(url_for('index'))'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	user = [None, None]
	#global user
	if current_user.is_authenticated:
		flash('Вы уже авторизированы')
		return redirect(url_for('account'))
	form = LoginForm()
	if form.validate_on_submit():
		cursor.execute('select id, passwordHash from account where login = %s', (form.username.data,))
		user = cursor.fetchone()
		if user is None or not check_password_hash(user[1], form.password.data):
			flash('Неверный логин или пароль')
			return redirect(url_for('login'))
		id = user[0]
		user_id = User(id)
		login_user(user_id, remember = form.remember_me.data)
		flash('Вы успешно авторизировались')
		return redirect(url_for('index'))
	return render_template('login.html', title='Вход', form=form, user=user)

	'''#if user['login'] == None:
		form = LoginForm()
		if form.validate_on_submit():
			cursor = conn.cursor()
			cursor.execute('select passwordHash, login, name, status from account where login = %s',
			(form.username.data,))
			conn.commit()
			record = cursor.fetchall()
			cursor.close()
			if record and check_password_hash(record[0][0], form.password.data):
				user['name'] = record[0][2]
				user['login'] = record[0][1]
				#user['password'] = form.password.data
				user['level'] = record[0][3]
				flash('Добрый день {}, вы успешно авторизировались'.format(user['name']))
				return redirect(url_for('account'))
			else:
				flash('Неверный логин или пароль')
		return render_template('login.html', title='Вход', form=form)#, user=user)
	else:
		flash('Вы уже авторизированы')
		return redirect(url_for('account'))'''

@app.route('/calk', methods=['GET', 'POST'])
def calk():
	if not current_user.is_authenticated:
		user = [None, None]
	else:
		cursor.execute('select name, login from account where id = %s',(current_user.id,))
		user = cursor.fetchone()
	form = WindowForm()
	if form.validate_on_submit():
		idwindow = None
		priceWindow = calkWindow(form)
		priceLeaf = (0,0,0)

		cursor.execute('insert into window_ (width, height, idProfileFirm, idWindowType, price) values (%s, %s, %s, %s, %s)',
		(form.width.data,form.height.data,form.FirmProfile.data,form.WindowType.data,priceWindow,))
		cursor.execute('select max(id) from window_')
		record = cursor.fetchall()
		idwindow = record[0][0]
		#conn.commit()
		if(form.WindowType.data == '4'):
			cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)',
				(idwindow, form.width.data,form.widthLeaf1.data,form.mechanism1.data,form.fillMaterial1.data,form.FirmFitting.data,))
			cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)',
				(idwindow, form.width.data,form.widthLeaf2.data,form.mechanism2.data,form.fillMaterial2.data,form.FirmFitting.data,))
		else:
			if(int(form.WindowType.data) >= 1):
				cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)',
					(idwindow, form.widthLeaf1.data,form.height.data,form.mechanism1.data,form.fillMaterial1.data,form.FirmFitting.data,))
			if(int(form.WindowType.data) >= 2):
				cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)',
					(idwindow, form.widthLeaf2.data,form.height.data,form.mechanism2.data,form.fillMaterial2.data,form.FirmFitting.data,))
			if(int(form.WindowType.data) == 3):
				cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)',
					(idwindow, form.widthLeaf3.data,form.height.data,form.mechanism3.data,form.fillMaterial3.data,form.FirmFitting.data,))
		conn.commit()
		flash('Цена данного изделия'.
			format(form.FirmProfile.data, form.FirmFitting.data, form.width.data, form.height.data))

		return redirect(url_for('calk'))
	return render_template('calk.html', title='Калькулятор', form=form, user=user)

def calkWindow(form):
	priceWindow = 0
	idType = 0
	sizeDetail = 1
	price = 2
	metr = 1000
	cursor = conn.cursor()
	cursor.execute('select idType, sizeDetail, price from profileDetail where idFirm = %s', (form.FirmProfile.data,))
	profileDetail = cursor.fetchall()
	conn.commit()
	#цена рамы
	rama = 0
	while profileDetail[rama][idType] != 1:
		rama += 1
	priceWindow += int((form.height.data / 1000 * 2 + form.width.data / 1000 * 2) * profileDetail[rama][price])

	#цена подставочного профиля
	podstava = 0
	while profileDetail[podstava][idType] != 5:
		podstava += 1
	priceWindow += int(form.width.data / 1000 * profileDetail[podstava][price])

	#цена импоста
	impost = 0
	while profileDetail[impost][idType] != 3:
		impost += 1
	soedImpost = 0
	while profileDetail[soedImpost][idType] != 3:
		soedImpost += 1
	if form.WindowType.data == '4':
		priceWindow += int((form.width.data - profileDetail[rama][sizeDetail] * 2) / 1000 * profileDetail[impost][price])
		priceWindow += int(profileDetail[soedImpost][price] * 2)
	else:
		priceWindow += int((form.height.data - profileDetail[rama][sizeDetail] * 2) / 1000 * profileDetail[impost][price] * (int(form.WindowType.data) - 1))
		priceWindow += int(profileDetail[soedImpost][price] * 2 * (int(form.WindowType.data) - 1))

	#цена вкладышей
	vkladish = 0
	while profileDetail[vkladish][idType] != 7:
			vkladish += 1
	if form.WindowType.data == '4':
		priceWindow += int(profileDetail[vkladish][price] * 6 * 2)
	else:
		priceWindow += int(profileDetail[vkladish][price] * 6 * int(form.WindowType.data))

	cursor.close()
	return priceWindow