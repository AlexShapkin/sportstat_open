from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login





@login.user_loader
def load_user(id):
    return User.query.get(int(id))



class Role(db.Model):
	__tablename__ = 'roles'
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(50), unique=True)



class OriginSystem(db.Model):

    __tablename__ = 'originsystem'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __repr__(self):
        return self.id

class Place(db.Model):

    __tablename__ = 'place'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique =True)
    url=db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.id


class SportsGroup(db.Model):

    __tablename__ = 'sportsgroup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    rus_name = db.Column(db.String(120))
    rank = db.Column(db.Integer, default =1)

    def __repr__(self):
        return self.id


SportLinkPlace = db.Table( 'sportlinkplace', 

	db.Column('id_sport',db.Integer, db.ForeignKey('sports.id')),
	db.Column('id_place',db.Integer, db.ForeignKey('place.id')) )



class Sports(db.Model):

    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    rus_name = db.Column(db.String(120))
    rank = db.Column(db.Integer, default =1)
    id_sportsgroup = db.Column(db.Integer, db.ForeignKey('sportsgroup.id'))
    sportsgroup = db.relationship("SportsGroup", backref=db.backref('sportsgroup', lazy='dynamic'))
    sportsplace = db.relationship("Place", secondary = SportLinkPlace)


    def __repr__(self):
        return self.id


class SportsCoeff(db.Model):

    __tablename__ = 'sportscoeff'
    id = db.Column(db.Integer, primary_key=True)
    criteria_description = db.Column(db.String(120))
    criteria = db.Column(db.Float)
    coeff1 = db.Column(db.Float)
    coeff2 = db.Column(db.Float)
    id_sport = db.Column(db.Integer, db.ForeignKey('sports.id'))
    sport = db.relationship("Sports", backref=db.backref('sportcoeff', lazy='dynamic'))
    bottom = db.Column(db.Float)
    upper = db.Column(db.Float)

    def sport_coeff_table():
    	table= SportsCoeff.query.join(Sports, (Sports.id==SportsCoeff.id_sport))
    	return table

    def __repr__(self):
        return self.id


class BotCommands(db.Model):

    __tablename__ = 'botcommands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.String(500))
    id_originsystem = db.Column(db.Integer, db.ForeignKey('originsystem.id'))
    originsystem= db.relationship("OriginSystem", backref=db.backref('originsystembotscommands', lazy='dynamic'))

    def __repr__(self):
        return self.id


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    id_originsystem = db.Column(db.Integer, db.ForeignKey('originsystem.id'))
    originsystem= db.relationship("OriginSystem", backref =db.backref('originsystem', lazy='dynamic'))
    display_name=db.Column(db.String(120),  default='bot_anonymous')
    password_hash = db.Column(db.String(128))
    id_rolemodel = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2)
    #roles=db.relationship('Role', secondary = 'user_roles')

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
    	self.password_hash = generate_password_hash(password)
    	return self.password_hash
    
    def check_password(self, password):
    	return check_password_hash(self.password_hash, password)

    def get_role(self):
    	return Role.query.filter_by(id=self.id_rolemodel).first().name

class UserRoles(db.Model):
	__tablename__ = 'user_roles'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
	role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class UserSession(db.Model):
    __tablename__ = 'usersession'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Integer, default=0)
    id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", backref=db.backref('usersession', lazy='dynamic'))
    id_botcommand = db.Column(db.Integer, db.ForeignKey('botcommands.id'))
    botcommand= db.relationship("BotCommands", backref=db.backref('botcommandssession', lazy='dynamic'))


    def __repr__(self):
        return '<User {}>'.format(self.name)


class QuestionTypes(db.Model):
    """docstring for SurveyRecord"""
    __tablename__ = 'questiontypes'
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(120))

    def __repr__(self):
        return '<id {}>'.format(self.id)


class OriginSystemCommands(db.Model):

    __tablename__ = 'originsystemcommands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(500))
    id_originsystem = db.Column(db.Integer, db.ForeignKey('originsystem.id'))
    originsystem= db.relationship("OriginSystem", backref =db.backref('originsystemucommands', lazy='dynamic'))

    def __repr__(self):
        return '<id {}>'.format(self.id)


class OriginSystemUsers(db.Model):
    __tablename__ = 'originsystemusers'
    id = db.Column(db.Integer, primary_key=True)
    system_username = db.Column(db.String(120))
    system_userid = db.Column(db.String(120))
    id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", backref=db.backref('originsystemuser', lazy='dynamic'))
    id_originsystem = db.Column(db.Integer, db.ForeignKey('originsystem.id'))
    originsystem= db.relationship("OriginSystem", backref =db.backref('originsystemusers', lazy='dynamic'))
    

    
    def get_id_users(userid):
    	return OriginSystemUsers.query.filter_by(system_userid=str(userid)).first().id_users

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Surveys(db.Model):
	"""docstring for SurveyRecord"""
	__tablename__='surveys'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique = True)
	id_sports = db.Column(db.Integer, db.ForeignKey('sports.id'))
	sports = db.relationship("Sports", backref=db.backref('sportstosurveys', lazy='dynamic'))


	def __repr__(self):
		return '<id {}>'.format(self.id)


class SurveysQuestion(db.Model):
	"""docstring for SurveyRecord"""
	__tablename__='surveysquestion'
	id = db.Column(db.Integer, primary_key=True)
	survey_question = db.Column(db.String(500))
	question_index = db.Column(db.Integer)
	parameter = db.Column(db.String(120))
	id_surveys = db.Column(db.Integer, db.ForeignKey('surveys.id'))
	surveys= db.relationship("Surveys", backref =db.backref('surveylink', lazy='dynamic'))
	id_questiontypes = db.Column(db.Integer, db.ForeignKey('questiontypes.id'))
	questiontypes= db.relationship("QuestionTypes", backref =db.backref('questiontype', lazy='dynamic'))


	def __repr__(self):
		return self.id



class CurrentSurvey(db.Model):
	"""docstring for SurveyRecord"""
	__tablename__='currentsurvey'
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime(), default = datetime.utcnow)
	user_time = db.Column(db.DateTime())
	state = db.Column(db.Integer, default=0)
	step = db.Column(db.Integer, default=0)
	id_surveys = db.Column(db.Integer, db.ForeignKey('surveys.id'))
	surveys= db.relationship("Surveys", backref =db.backref('surveycurrentsurveylink', lazy='dynamic'))
	question_quantity = db.Column(db.Integer)
	id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
	user= db.relationship("User", backref =db.backref('currentsurveyforuser', lazy='dynamic'))


	def get_currentsurvey_id_by_id_users(userid):
		return (CurrentSurvey.query.filter_by(
			id_users=OriginSystemUsers.get_id_users(userid), state =0)
		.order_by(CurrentSurvey.timestamp.desc()).first().id)

	def __repr__(self):
		return '<id {}>'.format(self.id)


class CurrentQuestion(db.Model):
	"""docstring for SurveyRecord"""
	__tablename__='currentquestion'
	id = db.Column(db.Integer, primary_key=True)
	result = db.Column(db.String(500), default='')
	state = db.Column(db.Integer, default=0)
	questionsend = db.Column(db.Integer, default=0)
	answerreceive = db.Column(db.Integer, default=0)
	id_currentsurvey = db.Column(db.Integer, db.ForeignKey('currentsurvey.id'))
	currentsurvey= db.relationship("CurrentSurvey", backref =db.backref('currentsurveylink', lazy='dynamic'))
	id_surveyquestion = db.Column(db.Integer, db.ForeignKey('surveysquestion.id'))
	surveyquestion = db.relationship("SurveysQuestion", backref =db.backref('currentquestionlink', lazy='dynamic'))
	reply = db.Column(db.Integer, default=0)

	def __repr__(self):
		return '<id {}>'.format(self.id)


class SurveyResult(db.Model):

	__tablename__ = 'surveyresult'
	id = db.Column(db.Integer, primary_key=True)
	parameter_1 = db.Column(db.Float)
	id_quest_1 = db.Column(db.Integer, db.ForeignKey('surveysquestion.id'))
	parameter_2 = db.Column(db.Float)
	id_quest_2 = db.Column(db.Integer, db.ForeignKey('surveysquestion.id'))
	date = db.Column(db.DateTime(), default = datetime.utcnow)
	score = db.Column(db.Float)
	id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
	user= db.relationship("User", backref =db.backref('surveyforuser', lazy='dynamic'))
	id_currentsurvey = db.Column(db.Integer)
	id_surveys = db.Column(db.Integer, db.ForeignKey('surveys.id'))
	surveys= db.relationship("Surveys", backref =db.backref('resultsurveylink', lazy='dynamic'))
	id_place = db.Column(db.Integer, db.ForeignKey('place.id'), default=1)





	def __repr__(self):
		return '<id {}>'.format(self.id)


class GroupCoeff(db.Model):

	__tablename__ = 'groupcoeff'
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(200))
	coeff=db.Column(db.Float)


class NewSport(db.Model):

	__tablename__ = 'newsport'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	description = db.Column(db.String(200))
	id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
	user= db.relationship("User", backref =db.backref('newsportuser', lazy='dynamic'))
	
	def __repr__(self):
		return '<id {}>'.format(self.id)


def create_db_object(ClassName):

    db.session.add(ClassName)
    db.session.commit()
    return "check"

def question_number_for_survey(survey_id):
	return SurveysQuestion.query.filter_by(id_surveys = survey_id).count()

def current_question_for_sending_to_user(user_id):
	result = CurrentQuestion.query.filter_by(
		id_currentsurvey = current_survey_for_user(user_id).id, state=0).order_by(
		CurrentQuestion.id.desc()).first()
	return result

def current_survey_for_user(user_id):
	result = CurrentSurvey.query.filter_by(
		id_users=user_id, state=0
		).order_by(CurrentSurvey.timestamp.desc()).first()
	return result

def get_id(ClassName, key):
    get_id = ClassName.query.filter_by(name=key).first()
    return get_id.id


def get_name(ClassName, key):
    get_id = ClassName.query.filter_by(name=key.lower()).first()
    return get_id.name

def print_result():
	result = get_all(BotCommands)
	for item in result:
		print(item.bot_command)


def create_commands (command_name, sport_desc, orsys_name):
	create_db_object(BotCommands(name=command_name,description=sport_desc, id_originsystem=get_id(OriginSystem, orsys_name)))
	return 0

def create_sports (sport_name, sport_desc):
	create_db_object(Sports(name=sport_name, rus_name=sport_desc))
	return 0


def create_questions(s_q, param, q_index, surv, q_type):
	create_db_object(SurveysQuestion(survey_question=s_q, question_index=q_index, parameter=param,
		id_surveys=get_id(Surveys, surv), id_questiontypes=QuestionTypes.query.filter_by(question_type=q_type.lower()).first().id))
	return 0

def create_question_types (question_type):
	create_db_object(QuestionTypes(question_type=question_type))
	return 0

def call_question(user_id):
	result =SurveysQuestion.query.filter_by(
		id=CurrentQuestion.query.filter_by(id_currentsurvey=CurrentSurvey.query.filter_by(id_users=user_id, state=0).order_by(CurrentSurvey.timestamp.desc()).first().id, questionsend=0).first().id_surveyquestion).first().survey_question
	return result

def current_question_flag_update(user_id, column_name, value):
	db.session.query(CurrentQuestion).filter(
		CurrentQuestion.id==current_question_for_sending_to_user(user_id).id).update(
		{column_name: value})
	db.session.commit()

def current_question_answer_proccess (user_id, value):
	db.session.query(CurrentQuestion).filter(
		CurrentQuestion.id==current_question_for_sending_to_user(user_id).id).update(
		{'answerreceive': 1, 'result':value})
	db.session.commit()

def current_survey_step_update(user_id):

	value = CurrentSurvey.query.filter_by(
		id =current_survey_for_user(user_id).id, state=0).first().step

	db.session.query(CurrentSurvey).filter_by(
		id =current_survey_for_user(user_id).id, state=0).update(
		{'step': (value+1)})
	db.session.commit()

def current_survey_state_update(user_id, survey_id):
	db.session.query(CurrentSurvey).filter_by(
		id =survey_id, state=0).update(
		{'state': 1})
	db.session.commit()


def current_question_all_disable(user_id):
	db.session.query(CurrentQuestion).filter(
		CurrentQuestion.id_currentsurvey==current_survey_for_user(user_id).id).update(
		{'state': 404})
	#db.session.commit()

def current_survey_disable(user_id):
	db.session.query(CurrentSurvey).filter_by(
		id =current_survey_for_user(user_id).id, state=0).update(
		{'state': 404})
	#db.session.commit()

def current_user_session_upgrade(user_id, state_value=1):
	db.session.query(UserSession).filter_by(
		id_users =user_id, state=0).update(
		{'state': state_value})
	#db.session.commit()

def update_question_result(data, id):
	db.session.query(CurrentQuestion).filter(
		CurrentQuestion.id_currentsurvey==CurrentSurvey.get_currentsurvey_id_by_id_users(id), CurrentQuestion.state==0,
		).update({'result':data, 'state':1})
	db.session.commit()
	return 0

def check_user_seesion(user_id):
	result = UserSession.query.filter_by(
		id_users=user_id, state=0).first()
	return result

def session_disabled(user_id):
	current_user_session_upgrade(user_id, state_value=404)
	db.session.commit()

def current_survey_all_obj_disable(user_id):
	current_question_all_disable(user_id)
	current_survey_disable(user_id)
	db.session.commit()

def cur_question_reply_flag(cur_q_id):
	db.session.query(CurrentQuestion).filter_by(
		id =cur_q_id).update(
		{'reply': 1})
	db.session.commit()	


def check_user(username):
    if User.query.filter_by(name=username).first() is not None:
    	user = User.query.filter_by(name=username).first()
    	return user
    else:
    	return None

def user_analysis_for_period(current_date, begin_date, user_id):
	

	filter_query = str('select  sur.name, u.name,  SUM(sr.score) as tsum from surveyresult as sr ' +
 'join users as u on sr.id_users=u.id join surveys  as sur on sr.id_surveys=sur.id where sr.date >=\'{0}\' and '+
 ' sr.date <= \'{1}\' and u.id = {2} group by(sur.name, u.name) order by 1,2;').format(
	begin_date, current_date, user_id)
	cross_query = str('select * from crosstab ($${}$$) as final_pivot (sport character varying(120),'+
	' my_score double precision) order by my_score desc;').format(filter_query)
	result = db.engine.execute(cross_query)

	

	return result



def user_analysis_format_all_sports(result):
	message_text = ''
	for item in result:
		message_text += ('Твои результат с начала месяца по {}_res составляет {} баллов \n'
		.format(item[0],item[1]))# future add command for analytics by sport by day

	if message_text =='':
		message_text += ('Результаты с начала месяца отсутствуют (')
	return message_text




def users_total_score(current_date, begin_date, user_id, number = 1000):

	if user_id =='all':
		#sprint('check')
		filter_query = str('select  u.name, u.name,  SUM(sr.score) as tsum from surveyresult as sr ' +
 'join users as u on sr.id_users=u.id join surveys  as sur on sr.id_surveys=sur.id where sr.date >=\'{0}\' and '+
 ' sr.date <= \'{1}\'  group by(u.name, u.name) order by 1,2;').format(
		begin_date, current_date)
		cross_query = str('select * from crosstab ($${}$$) as final_pivot (usern character varying(120),'+
	' my_score double precision) order by my_score desc LIMIT {};').format(filter_query, number)
		result = db.engine.execute(cross_query)
		
		return result

	else:
		filter_query = str('select  u.name,u.name,   SUM(sr.score) as tsum from surveyresult as sr ' +
 'join users as u on sr.id_users=u.id join surveys  as sur on sr.id_surveys=sur.id where sr.date >=\'{0}\' and '+
 ' sr.date <= \'{1}\' and u.id = {2} group by(u.name, u.name) order by 1,2;').format(
		begin_date, current_date, user_id)
		cross_query = str('select * from crosstab ($${}$$) as final_pivot (usern character varying(120),'+
	' my_score double precision) order by my_score desc;').format(filter_query)
		result = db.engine.execute(cross_query)
		
		return result

def users_total_score_format(result):
	message_text=''
	for item in result:
		message_text += '{} : {} \n'.format(item[0],item[1])
	message_text ='Твой результат с начала месяца: \n' +message_text 

	return message_text

def top_users(result):
	message_text='Топ спортсменов с начала месяца: \n'
	for item in result:
		message_text += '{} : {} \n'.format(item[0],item[1])

	return message_text


def user_records(user_id, begin_date, end_date):
	filter_query =  str('select sr.id, sr.date, sur.name, '+
		'sr.parameter_1, sr.parameter_2, sr.score  from surveyresult as sr'+
		'  join surveys as sur on sr.id_surveys=sur.id where sr.date>=\'{}\' and'+
		' sr.date<=\'{}\' and sr.id_users={};').format(begin_date, end_date, user_id)
	result = db.engine.execute(filter_query)
	return result

def user_records_format(result):
	message_text=''
	for item in result:
		message_text += ('ID {}|{}|{}|сколько {}|с кем {}|баллы {} \n').format(
			item[0],item[1].strftime('%m-%d'),item[2],item[3],item[4], item[5])
	if message_text == '':
		return None

	return message_text	

def user_record_delete(id, user_id):
	SurveyResult.query.filter_by(id_users=user_id, id=id).delete()
	#db.session.commit()

def user_display_name_update(user_id, value):
	db.session.query(User).filter_by(
		id =user_id).update(
		{'display_name': value})
	 #db.session.commit()	






