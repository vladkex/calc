# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired
from app import app, conn


cursor = conn.cursor()


class LoginForm(FlaskForm):
	username = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	remember_me = BooleanField('Запомнить меня')
	submit = SubmitField('Войти')


class CreateAccountForm(FlaskForm):
	name = StringField('ФИО', validators=[DataRequired()])
	login = StringField('Логин', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	level = IntegerField('Уровень доступа')
	submit = SubmitField('Создать')


class ChangePasswordForm(FlaskForm):
	passwordOld = PasswordField('Старый пароль', validators=[DataRequired()])
	passwordNew1 = PasswordField('Новый пароль', validators=[DataRequired()])
	passwordNew2 = PasswordField('Повторите пароль', validators=[DataRequired()])
	submit = SubmitField('Сменить')


class WindowForm(FlaskForm):
	cursor.execute("select id, title from firmProfile")
	firmProfile = cursor.fetchall()

	cursor.execute("select id, title from firmFitting")
	firmFitting = cursor.fetchall()

	cursor.execute("select id, title from windowType")
	windowType = cursor.fetchall()

	cursor.execute("select id, title from fillMaterial")
	fillMaterial = cursor.fetchall()

	cursor.execute("select id, title from mechanism")
	mechanism = cursor.fetchall()
	conn.commit()

	FirmProfile = SelectField('Фирма профиля', choices=firmProfile, coerce=int)
	FirmFitting = SelectField('Фирма фурнитуры', choices=firmFitting, coerce=int)
	width = IntegerField('Ширина')
	height = IntegerField('Высота')
	WindowType = SelectField('Тип окна', choices=windowType, coerce=int)
	
	widthLeaf1 = IntegerField('Размер')
	fillMaterial1 = SelectField('Материал заполнения', choices=fillMaterial, coerce=int)
	mechanism1 = SelectField('Открывание', choices=mechanism, coerce=int)

	widthLeaf2 = IntegerField('Размер')
	fillMaterial2 = SelectField('Материал заполнения', choices=fillMaterial, coerce=int)
	mechanism2 = SelectField('Открывание', choices=mechanism, coerce=int)

	widthLeaf3 = IntegerField('Размер')
	fillMaterial3 = SelectField('Материал заполнения', choices=fillMaterial, coerce=int)
	mechanism3 = SelectField('Открывание', choices=mechanism, coerce=int)
	
	submit = SubmitField('Посчитать')