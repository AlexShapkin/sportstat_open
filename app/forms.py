from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectField, FloatField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length, Optional
from app.models import User, SportsGroup, Sports
from wtforms.fields.html5 import DateField, URLField
from datetime import date, timedelta


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    display_name = StringField('DisplayName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class NewSportGroupForm(FlaskForm):
    name = StringField('Название группы, одним словом или через _ Латинецей (sport_group) ', validators=[DataRequired()])
    rus_name = TextAreaField('Описание группы', validators=[Length(min=0, max=40)])
    rank = IntegerField('Место в списке при отображении')
    submit = SubmitField('Submit')
    
    def validate_name(self, name):
        user = SportsGroup.query.filter_by(name=name.data).first()
        if user is not None:
            raise ValidationError('Please use a different name.')


class NewSportForm(FlaskForm):
    name = StringField('Название спорта, латинецей одинм словом или через _ (sport_name) ', validators=[DataRequired()])
    rus_name = TextAreaField('Описание спорта', validators=[Length(min=0, max=40)])
    rank = IntegerField('Место в списке при отображении', default=1)
    sport_group=SelectField('Group', choices=[])
    place=SelectField('Place', choices=[])
    question_1 = StringField('Вопрос про дистанцию/длительность/количество в единицах измерения',
    	validators=[DataRequired()], default='Какая дистанция была в километрах? (пример ответа: 100)')
    parameter_1 = StringField('Название параметра (distance/duration)', validators=[DataRequired()], default='distance')
    question_2 = StringField('Вопрос про тренировку с друзьями',
    	validators=[DataRequired()], default='Сколько человек из нашей группы тренировались вместе с тобой? (пример ответа: 0)')
    parameter_2 = StringField('Параметр группы', validators=[DataRequired()], default='group')
    coeff1 = FloatField("Коэффициент пересчета в баллы", validators=[DataRequired()])
    criteria = FloatField("значение кретерия для повышенния коэффициент (опционально)", validators=[Optional()])
    criteria_desc = TextAreaField('Описание критерия по смыслу (опционально)', validators=[Length(min=0, max=40)], default='отсутствует')
    coeff2 = FloatField("Коэффициент пересчета в баллы при высоких результатах (опционально)", validators=[Optional()])
    bottom=FloatField("Нижняя граница разумного значения", validators=[DataRequired()], default=1)
    upper=FloatField("Верхняя граница разумного значения", validators=[DataRequired()], default=1000)
    submit = SubmitField('Submit')
    
    def validate_name(self, name):

    	sport = Sports.query.filter_by(name=name.data).first()
    	#print(sport.id)

    	if sport is not None:
    		raise ValidationError('Please use a different name.')

class SportEdit(FlaskForm):
    name = StringField('Название спорта, латинецей одинм словом или через _ (sport_name) ', validators=[DataRequired()])
    rus_name = TextAreaField('Описание спорта', validators=[Length(min=0, max=40)])
    rank = IntegerField('Место в списке при отображении', validators=[DataRequired()])
    sport_group=StringField('Group')
    coeff1 = FloatField("Коэффициент пересчета в баллы", validators=[DataRequired()])
    criteria = FloatField("значение кретерия для повышенния коэффициент", validators=[DataRequired()])
    criteria_desc = TextAreaField('Описание критерия по смыслу', validators=[Length(min=0, max=40)])
    coeff2 = FloatField("Коэффициент пересчета в баллы при высоких результатах", validators=[DataRequired()])
    bottom=FloatField("Нижняя граница разумного значения", validators=[DataRequired()])
    upper=FloatField("Верхняя граница разумного значения", validators=[DataRequired()])
    place = SelectField('Place', choices=[])
    submit = SubmitField('Submit')
    
    def validate_name(self, name):

    	if not (name.data!=name.default and Sports.query.filter_by(name=name.data).first()):
    		raise ValidationError('Please use a different name.')

class GroupCoeffForm(FlaskForm):

    description = StringField("Коэффициента по группе", validators=[DataRequired()])
    value=FloatField("Нижняя граница разумного значения", validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_coeffg(self):
    	if 1<0:
    		raise ValidationError('Please use a different name.')

class MessageSend(FlaskForm):

    message_text = TextAreaField('Текст сообщения для всех пользователей', validators=[Length(min=0, max=40), DataRequired()])
    submit = SubmitField('Send')
    
    def validate_coeffg(self):
    	if 1<0:
    		raise ValidationError('Please use a different name.')
def date_validate(form, field):
    
    if field.name== 'begindate' and field.data  < (date.today() + timedelta(days = ( 1-date.today().day))):
        raise ValidationError('Результаты можно запросить за текущий месяц')
    elif field.name== 'enddate' and field.data  > date.today():
        raise ValidationError('Результаты можно запросить за текущий месяц')

class ReportForm(FlaskForm):
    begindate = DateField('Begin Date', format='%Y-%m-%d', default=date.today() + timedelta(days = ( 1-date.today().day)), validators=[date_validate])
    enddate = DateField('End Date', format='%Y-%m-%d', default=date.today(), validators=[date_validate])
    submit = SubmitField('Request')


class PlaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    url = URLField('URL',  validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_name(self, name):

        if  Sports.query.filter_by(name=name.data).first():
            raise ValidationError('Please use a different name.')




