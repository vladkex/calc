# -*- coding: utf-8 -*-
import os
from flask import render_template, flash, redirect, url_for, make_response, session, send_from_directory
from app import app, conn
from app.forms import LoginForm, WindowForm, CreateAccountForm, ChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, logout_user, login_required, login_user, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Пожалуйста, войдите, чтобы открыть эту страницу."


class User(UserMixin):
	def __init__(self, id_):
		self.id = id_

	def __repr__(self):
		return "%d/%d" % self.id


@login_manager.user_loader
def load_user(user_id):
	return User(user_id)


cursor = conn.cursor()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
	if not current_user.is_authenticated:
		user = [None, None]
	else:
		cursor.execute('select name, login from account where id = %s', (current_user.id,))
		user = cursor.fetchone()
	return render_template('index.html', title='Главная страница', user=user)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/account')
@login_required
def account():
	cursor.execute('select name, login, status from account where id = %s', (current_user.id,))
	user = cursor.fetchone()
	return render_template('account.html', title='Личный кабинет', user=user)


@app.route('/myWindows')
@login_required
def myWindows():
	cursor.execute('select name, login, status from account where id = %s', (current_user.id,))
	user = cursor.fetchone()
	cursor.execute('select window_.id, firmProfile.title, window_.height, window_.width, window_.price from window_ inner join firmProfile on window_.idProfileFirm = firmProfile.id  where idAccount = %s', (current_user.id,))
	windows = cursor.fetchall()
	cursor.execute('select leaf.idWindow, firmFitting.title, leaf.height, leaf.width, fillMaterial.title from leaf inner join firmFitting on leaf.idFirmFitting = firmFitting.id inner join fillMaterial on leaf.idFillMaterial = fillMaterial.id where leaf.idWindow IN (select id from window_ where idAccount = %s)', (current_user.id,))
	leafs = cursor.fetchall()
	return render_template('myWindows.html', title='История окон', user=user, windows=windows, leafs=leafs)


@app.route('/newAccount', methods=['GET', 'POST'])
@login_required
def newAccount():
	cursor.execute('select name, login, status from account where id = %s', (current_user.id,))
	user = cursor.fetchone()
	if user[2] == 0:
		flash('Отказано в доступе')
		return redirect(url_for('account'))
	form = CreateAccountForm()
	if form.validate_on_submit():
		cursor.execute('select * from account where login = %s', (form.login.data,))
		check_user = cursor.fetchone()
		if check_user:
			flash('Учетная запись с таким логином уже существует!')
			return redirect(url_for('newAccount'))
		cursor.execute('insert into account (login, passwordHash, name, status) values (%s, %s, %s, %s);', (form.login.data, generate_password_hash(form.password.data), form.name.data, form.level.data,))
		conn.commit()
		flash('Учетная запись для {} создана успешно!'.format(form.name.data))
		flash('Login: {}'.format(form.login.data))
		flash('Password: {}'.format(form.password.data))
		return redirect(url_for('account'))
	return render_template('newAccount.html', title='Создание аккаунта', form=form, user=user)


@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
	cursor.execute('select name, login, passwordHash from account where id = %s',(current_user.id,))
	user = cursor.fetchone()
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if check_password_hash(user[2], form.passwordOld.data) and form.passwordNew1.data == form.passwordNew2.data:
			cursor.execute('update account set passwordHash = %s where id = %s', (generate_password_hash(form.passwordNew1.data), current_user.id,))
			conn.commit()
			flash('Пароль был успешно изменен')
			return redirect(url_for('account'))
		else:
			flash('Старый пароль введен неверно или новые пароли не совпадают')
			return redirect(url_for('changePassword'))
	return render_template('changePassword.html', title='Сменить пароль', form=form, user=user)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Вы вышли из профиля')
	return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	user = [None, None]
	if current_user.is_authenticated:
		flash('Вы уже авторизированны')
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
		login_user(user_id, remember=form.remember_me.data)
		flash('Вы успешно авторизировались')
		return redirect(url_for('account'))
	return render_template('login.html', title='Вход', form=form, user=user)


@app.route('/calk', methods=['GET', 'POST'])
def calk():
	if not current_user.is_authenticated:
		id_ = None
		user = [None, None]
	else:
		id_ = current_user.id
		cursor.execute('select name, login from account where id = %s', (id_,))
		user = cursor.fetchone()
	form = WindowForm()
	if form.validate_on_submit():
		priceWindow = calkWindow(form)
		cursor.execute('insert into window_ (width, height, idProfileFirm, idWindowType, price, idAccount) values (%s, %s, %s, %s, %s, %s)', (form.width.data, form.height.data, form.FirmProfile.data, form.WindowType.data, priceWindow, id_))
		cursor.execute('select max(id) from window_')
		record = cursor.fetchall()
		idwindow = record[0][0]
		if int(form.WindowType.data) == 4:
			cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)', (idwindow, form.width.data, form.widthLeaf1.data, form.mechanism1.data, form.fillMaterial1.data, form.FirmFitting.data,))
			cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)', (idwindow, form.width.data, form.widthLeaf2.data, form.mechanism2.data, form.fillMaterial2.data, form.FirmFitting.data,))
		else:
			if int(form.WindowType.data) >= 1:
				cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)', (idwindow, form.widthLeaf1.data, form.height.data, form.mechanism1.data, form.fillMaterial1.data, form.FirmFitting.data,))
			if int(form.WindowType.data) >= 2:
				cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)', (idwindow, form.widthLeaf2.data, form.height.data, form.mechanism2.data, form.fillMaterial2.data, form.FirmFitting.data,))
			if int(form.WindowType.data) == 3:
				cursor.execute('insert into leaf (idWindow, width, height, idMechanism, idFillMaterial, idFirmFitting) values (%s, %s, %s, %s, %s, %s)', (idwindow, form.widthLeaf3.data,form.height.data,form.mechanism3.data,form.fillMaterial3.data,form.FirmFitting.data,))
		conn.commit()
		flash('Цена данного изделия - {} рублей'.format(priceWindow / 100))

		return redirect(url_for('calk'))
	return render_template('calk.html', title='Калькулятор', form=form, user=user)


def calkWindow(form):
	priceWindow = 0
	idType = 0
	sizeDetail = 1
	price = 2
	cursor.execute('select idType, sizeDetail, price from profileDetail where idFirm = %s', (form.FirmProfile.data,))
	profileDetail = cursor.fetchall()
	conn.commit()

	# цена подставочного профиля
	podstava = 0
	while profileDetail[podstava][idType] != 5:
		podstava += 1
	priceWindow += int(form.width.data / 1000 * profileDetail[podstava][price])

	# коррекция размера высоты из-за подставочного профиля
	if form.WindowType.data == '4':
		if form.widthLeaf1.data == form.widthLeaf2.data:
			form.widthLeaf1.data = int(form.widthLeaf1.data - profileDetail[podstava][sizeDetail] / 2)
			form.widthLeaf2.data = int(form.widthLeaf2.data - profileDetail[podstava][sizeDetail] / 2)
		else:
			form.widthLeaf2.data = form.widthLeaf2.data - profileDetail[podstava][sizeDetail]
	form.height.data = form.height.data - profileDetail[podstava][sizeDetail]

	# цена рамы
	rama = 0
	while profileDetail[rama][idType] != 1:
		rama += 1
	priceWindow += int((form.height.data / 1000 * 2 + form.width.data / 1000 * 2) * profileDetail[rama][price])

	# цена импоста
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

	priceLeaf = 0
	formL = form

	priceLeaf += calkLeaf(profileDetail, rama, impost, formL, formL.widthLeaf1.data, formL.fillMaterial1.data, formL.mechanism1.data, 0)
	if form.WindowType.data == '4' or form.WindowType.data == '2':
		priceLeaf += calkLeaf(profileDetail, rama, impost, formL, formL.widthLeaf2.data, formL.fillMaterial2.data, formL.mechanism2.data, 0)
	elif form.WindowType.data == '3':
		priceLeaf += calkLeaf(profileDetail, rama, impost, formL, formL.widthLeaf2.data, formL.fillMaterial2.data, formL.mechanism2.data, 1)
		priceLeaf += calkLeaf(profileDetail, rama, impost, formL, formL.widthLeaf3.data, formL.fillMaterial3.data, formL.mechanism3.data, 0)
	priceWindow += priceLeaf

	# коррекция размера высоты из-за подставочного профиля
	if form.WindowType.data == '4':
		if form.widthLeaf1.data == form.widthLeaf2.data:
			form.widthLeaf1.data = int(form.widthLeaf1.data + profileDetail[podstava][sizeDetail] / 2)
			form.widthLeaf2.data = int(form.widthLeaf2.data + profileDetail[podstava][sizeDetail] / 2)
		else:
			form.widthLeaf2.data = form.widthLeaf2.data + profileDetail[podstava][sizeDetail]
	form.height.data = form.height.data + profileDetail[podstava][sizeDetail]

	return priceWindow


def calkLeaf(profileDetail, rama, impost, form, sizeLeaf, materialLeaf, mehanizmLeaf, center):
	priceLeaf = 0
	idType = 0
	sizeDetail = 1
	price = 2
	shelka = (2, 5, 7, 13)
	LeafRamaImpost = int(sizeLeaf - profileDetail[rama][sizeDetail] - profileDetail[impost][sizeDetail] / 2)

	# номер в массиве уплотнителя для стекла
	ElasticGlass = 0
	while profileDetail[ElasticGlass][idType] != 8 and profileDetail[ElasticGlass][sizeDetail] != 1:
		ElasticGlass += 1

	# цена вкладышей
	vkladish = 0
	while profileDetail[vkladish][idType] != 7:
		vkladish += 1
	priceLeaf += profileDetail[vkladish][price] * 6

	# высчитывание размеров
	nahlest = 0
	while profileDetail[nahlest][idType] != 9:
		nahlest += 1
	if form.WindowType.data == '4':
		heightElasticRama = int(LeafRamaImpost - (profileDetail[nahlest][sizeDetail] - shelka[1]) * 2)
		widthElasticRama = int(form.width.data - (profileDetail[rama][sizeDetail] + profileDetail[nahlest][sizeDetail] - shelka[1]) * 2)
	else:
		if center:
			widthElasticRama = int(sizeLeaf - profileDetail[impost][sizeDetail] - (profileDetail[nahlest][sizeDetail] - shelka[1]) * 2)
		else:
			widthElasticRama = int(LeafRamaImpost - (profileDetail[nahlest][sizeDetail] - shelka[1]) * 2)
		heightElasticRama = int(form.height.data - (profileDetail[rama][sizeDetail] + profileDetail[nahlest][sizeDetail] - shelka[1]) * 2)

	if mehanizmLeaf != 1:
		leaf = 0
		while profileDetail[leaf][idType] != 2:
			leaf += 1
		if form.WindowType.data == '4':
			CentrHeightLeaf = int(LeafRamaImpost - (shelka[3] + profileDetail[leaf][sizeDetail]) * 2)
			CentrWidthLeaf = int(form.width.data - (profileDetail[rama][sizeDetail] + shelka[3] + profileDetail[leaf][sizeDetail]) * 2)
		else:
			if center:
				CentrWidthLeaf = int(sizeLeaf - profileDetail[impost][sizeDetail] - (shelka[3] + profileDetail[leaf][sizeDetail]) * 2)
			else:
				CentrWidthLeaf = int(LeafRamaImpost - (shelka[3] + profileDetail[leaf][sizeDetail]) * 2)
			CentrHeightLeaf = int(form.height.data - (profileDetail[rama][sizeDetail] + shelka[3] + profileDetail[leaf][sizeDetail]) * 2)

		heightShtapik = int(CentrHeightLeaf + shelka[1] * 2)
		widthShtapik = int(CentrWidthLeaf + shelka[1] * 2)
		heightLeaf = int(CentrHeightLeaf + (profileDetail[leaf][sizeDetail] + profileDetail[nahlest][sizeDetail]) * 2)
		widthLeaf = int(CentrWidthLeaf + (profileDetail[leaf][sizeDetail] + profileDetail[nahlest][sizeDetail]) * 2)
		heightElasticGlass = int(CentrHeightLeaf - (profileDetail[nahlest][sizeDetail] + shelka[1]) * 2)
		widthElasticGlass = int(CentrWidthLeaf - (profileDetail[nahlest][sizeDetail] + shelka[1]) * 2)
		heightElasticLeaf = int(heightLeaf - shelka[1] * 2)
		widthElasticLeaf = int(widthLeaf - shelka[1] * 2)
		heightFillMaterial = int(CentrHeightLeaf - (profileDetail[vkladish][sizeDetail] + shelka[0]) * 2)
		widthFillMaterial = int(CentrWidthLeaf - (profileDetail[vkladish][sizeDetail] + shelka[0]) * 2)
		
		# цена рамы створки
		priceLeaf += int((widthLeaf / 1000 * 2 + heightLeaf / 1000 * 2) * profileDetail[leaf][price])
		
		# цена резинки створки прилегающей к стеклу
		priceLeaf += int((heightElasticGlass / 1000 * 2 + widthElasticGlass / 1000 * 2) * profileDetail[ElasticGlass][price])

		# цена резинки створки прилегающей к раме
		ElasticLeaf = 0
		while profileDetail[ElasticLeaf][idType] != 8 and profileDetail[ElasticLeaf][sizeDetail] != 0:
			ElasticLeaf += 1
		priceLeaf += int((heightElasticLeaf / 1000 * 2 + widthElasticLeaf / 1000 * 2) * profileDetail[ElasticLeaf][price])

		# цена резинки рамы прилегающей к створке
		priceLeaf += int((heightElasticRama / 1000 * 2 + widthElasticRama / 1000 * 2) * profileDetail[ElasticLeaf][price])
	else:
		if form.WindowType.data == '4':
			CentrHeightLeaf = int(LeafRamaImpost)
			CentrWidthLeaf = int(form.width.data - profileDetail[rama][sizeDetail] * 2)
		else:
			if center:
				CentrWidthLeaf = int(sizeLeaf - profileDetail[impost][sizeDetail])
			else:
				CentrWidthLeaf = int(LeafRamaImpost)
			CentrHeightLeaf = int(form.height.data - profileDetail[rama][sizeDetail] * 2)
		
		heightFillMaterial = int(CentrHeightLeaf - (profileDetail[vkladish][sizeDetail] + shelka[0]) * 2)
		widthFillMaterial = int(CentrWidthLeaf - (profileDetail[vkladish][sizeDetail] + shelka[0]) * 2)
		heightShtapik = int(CentrHeightLeaf + shelka[1] * 2)
		widthShtapik = int(CentrWidthLeaf + shelka[1] * 2)

		# цена резинки рамы прилегающей к стеклу
		priceLeaf += int((heightElasticRama / 1000 * 2 + widthElasticRama / 1000 * 2) * profileDetail[ElasticGlass][price])

	# цена заполнения
	cursor.execute('select id, thickness, price from fillMaterial where id = %s', (materialLeaf,))
	fillMaterial = cursor.fetchone()
	priceLeaf += int((heightFillMaterial / 1000 * 2 + widthFillMaterial / 1000 * 2) * fillMaterial[price])

	# цена штапика
	shtapik = 0
	while profileDetail[shtapik][idType] != 4 and profileDetail[shtapik][sizeDetail] != fillMaterial[sizeDetail]:
		shtapik += 1
	priceLeaf += int((heightShtapik / 1000 * 2 + widthShtapik / 1000 * 2) * fillMaterial[price])

	return priceLeaf