
import telebot



#from telebot import types
from telebot import apihelper
from datetime import datetime, date,timedelta
from re import findall

from app import db
from app.models import (User, OriginSystem, OriginSystemUsers, BotCommands,
 Sports, SurveysQuestion, QuestionTypes, Surveys, NewSport, SurveyResult,
  CurrentSurvey, CurrentQuestion,SurveysQuestion,UserSession, SportsCoeff, SportsGroup, GroupCoeff, Place, SportLinkPlace)
from app.models import session_disabled
from app.models import create_db_object as cdo
from app.models import get_id as gi
from app.models import call_question as cq
from app.models import question_number_for_survey as qn
from app.models import current_survey_for_user
from app.models import current_survey_step_update
from app.models import current_question_flag_update
from app.models import current_question_answer_proccess
from app.models import current_survey_state_update
from app.models import current_survey_all_obj_disable
from app.models import check_user_seesion
from app.models import current_user_session_upgrade
from app.models import user_analysis_format_all_sports
from app.models import user_analysis_for_period
from app.models import users_total_score_format, users_total_score, top_users
from app.models import cur_question_reply_flag
from app.models import user_records, user_records_format, user_record_delete
from app.models import user_display_name_update


from microapp import ctx
from app.googlesheets import correct_analytical_result
from config import OriginSystemConfig

messenger = 'telegram'





originsystem = OriginSystem.query.filter_by(name=messenger).first().id

token = OriginSystemConfig.TOKEN


bot = telebot.TeleBot(token)


group_coef = GroupCoeff.query.first().coeff



def create_sports_group_description():
	sport_gr = {}
	
	sport_gr_commands = "Выбери спортивную группу из доступных:\n"
	for item in SportsGroup.query.order_by(SportsGroup.rank.asc()).all():
		sport_gr[item.name]={}
		sport_gr[item.name]['description']=item.rus_name
		sport_gr[item.name]['id']=item.id
		sport_gr[item.name]['sport_in']={}
		sport_list_command = 'доступны следующие виды:\n'
		for subitem in Sports.query.filter_by(id_sportsgroup=item.id).all():
			sport_list_command += str("/"+subitem.name+": "+ subitem.rus_name+ "\n")

		sport_gr[item.name]['sport_in']=sport_list_command

	for key in sport_gr.keys():
		sport_gr_commands += '/'+key + ": "
		sport_gr_commands += sport_gr[key]['description'] + "\n"
	
	return sport_gr, sport_gr_commands





def create_sport_description():
	sport = {}
	sport_text = "Сейчас доступны средующие виды сопрта: \n"
	sport_commands = "Выбери спорт из доступных  \n"
	for item in Sports.query.order_by(Sports.rank.asc()).all():
		sport[item.name]={}
		sport[item.name]['description']=item.rus_name
		sport[item.name]['id']=item.id
	for key in sport.keys():
		sport_text += key + ": "
		sport_text += sport[key]['description'] + "\n"
		sport_commands += '/'+key + ": "
		sport_commands += sport[key]['description'] + "\n"
	sport_text += "Для внесения новых результатов воспользуйтес командой /add"
	return sport, sport_text, sport_commands

def create_botscommand_description(originsys):
	botCommands={}
	for item in BotCommands.query.filter_by(id_originsystem=originsys).all():
		botCommands[item.name]={}
		botCommands[item.name]['description']=item.description
		botCommands[item.name]['id']=item.id
	help_text = "Ты можешь использовать следующие команды: \n"
	for key in botCommands.keys():  # generate help text
		help_text += "/" + key + ": "
		help_text += botCommands[key]['description'] + "\n"
	return botCommands, help_text

def create_survey_questions():
	surveys_question={}
	surveys_result = Surveys.query.all()
	survey_list = [value.name for value in surveys_result]
	
	for item in survey_list:
		result = SurveysQuestion.query.filter_by(id_surveys=gi(Surveys, item)).all()
		surveys_question[item]={}
		for record in result:
			surveys_question[item][record.question_index]={}
			surveys_question[item][record.question_index]['parameter']=record.parameter
			surveys_question[item][record.question_index]['question']=record.survey_question
			surveys_question[item][record.question_index]['qtype']=QuestionTypes.query.filter_by(id=record.id_questiontypes).first().question_type
		surveys_question[item]['numberofquestions']=len(result)


	return surveys_question

def create_sport_coeff():
	sport_coef={}
	
	result = db.engine.execute(
'select  sp.name,co.coeff1 as coeff1, co.criteria as criteria, co.coeff2 as coeff2,'+
' co.bottom, co.upper from sportscoeff as co join sports as sp on co.id_sport=sp.id;'
)
	
	for item in result:

		sport_coef[item[0]]={}
		sport_coef[item[0]]['c1']=item[1]
		sport_coef[item[0]]['cr']=item[2]
		sport_coef[item[0]]['c2']=item[3]
		sport_coef[item[0]]['bottom']=item[4]
		sport_coef[item[0]]['upper']=item[5]


	return sport_coef


def place():
	places= {}
	keyboard_places = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard = True)
	result = Place.query.all()
	for item in result:
		places[item.id]=item.name
		keyboard_places.row(item.name)
	return places, keyboard_places


survey_questions = create_survey_questions()

sports, sport_text, sport_commands  = create_sport_description()

botCommands, help_text = create_botscommand_description(originsystem)

sport_coef=create_sport_coeff()

sports_gr, sports_gr_commands = create_sports_group_description()

places, keyboard_places = place()

#apihelper.proxy = {'https': "https://119.161.98.131:3128"}
#bot.remove_webhook()
#bot.polling(none_stop=True, interval=0)





keyboard_commands = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard = True)
keyboard_commands.row('/add', '/add_to_date')
keyboard_commands.row('/my_result','/top50', '/help')







@bot.message_handler(commands=['start'])
def command_start(message):
	ctx.push()
	cid = message.chat.id
	usname = message.from_user.username
	text = message.text.replace('/','')
	if usname is None:
		bot.send_message(cid, "Наш бот работает c использованием Telegram username. \n Пожалуйста, заполни это поле в настройках Telegram и повторно вызови команду /start .")
		return 0


	if not User.query.filter_by(name=usname).first():  # if user hasn't used the "/start" command yet:
		cdo(User(name=usname, id_originsystem=gi(OriginSystem, messenger)))
		cdo(OriginSystemUsers(system_username=usname, system_userid=cid, id_users=gi(User, usname), id_originsystem=gi(OriginSystem, messenger)))
		#bot.send_message(cid, "Привет! Теперь мы познакомились ) \n Выбери команду внизу или нажми /help для вызова списка доступных команд", reply_markup=keyboard_commands)
		bot.send_message(cid, "Привет! Пришли имя для отображения в рейтинге (не более 30 символов)")
		ctx.pop()
		return 0
	else:
		user_info = User.query.filter_by(name=usname).first()
		if user_info.display_name == 'bot_anonymous':

			cur_session = check_user_seesion(user_info.id)
			if cur_session is not None:
				session_disabled(user_info.id)	
			cdo(UserSession(id_users=user_info.id, id_botcommand=botCommands[text]['id']))
			bot.send_message(cid, "Привет! Пришли имя для отображения в рейтинге (не более 30 символов)")
			ctx.pop()
			return 0
		bot.send_message(cid,
			"Привет, {}! \n Выбери команду внизу или нажми /help для вызова списка доступных команд.".format(user_info.display_name),
		 reply_markup=keyboard_commands)
		ctx.pop()
		return 0



@bot.message_handler(commands=sports_gr.keys())
def sports_group_desc(message):
    ctx.push()
    cid = message.chat.id
    text=message.text.replace('/','')
    bot.send_message(cid, sports_gr[text]['sport_in'], reply_markup=keyboard_commands)
    ctx.pop()
    return 0



@bot.message_handler(commands=['help'])
def command_help(message):
    ctx.push()
    cid = message.chat.id
    bot.send_message(cid, help_text)
    ctx.pop()
    return 0

@bot.message_handler(commands = ['sport'])
def command_sport_desc(message):
	ctx.push()
	cid=message.chat.id
	bot.send_message(cid, sport_text, reply_markup=keyboard_commands)
	ctx.pop()
	return 0

@bot.message_handler(commands=['my_result'])
def command_myresult(message):
	ctx.push()
	cid = message.chat.id
	user_id = OriginSystemUsers.query.filter_by(system_userid=str(cid)).first().id_users
	current_date = date.today()
	begin_date = current_date + timedelta(days = ( 1-current_date.day))
	message_text = users_total_score_format(users_total_score(current_date,begin_date,user_id))
	message_text_bysport = user_analysis_format_all_sports(
		user_analysis_for_period(
			current_date, begin_date,user_id))
	message_text +=message_text_bysport
	bot.send_message(cid, message_text, reply_markup=keyboard_commands)
	
	ctx.pop()
	return 0

@bot.message_handler(commands=['top50'])
def command_top50(message):
	ctx.push()
	cid = message.chat.id
	current_date = date.today()
	begin_date = current_date + timedelta(days = ( 1-current_date.day))
	message_text = top_users(users_total_score(current_date,begin_date,'all', number=50))

	bot.send_message(cid, message_text, reply_markup=keyboard_commands)
	
	ctx.pop()
	return 0

@bot.message_handler(commands=['delete'])
def command_delete(message):
	ctx.push()
	day_deep = 7 # определяет глубину записей за 7 дней от сегодня
	cid = message.chat.id
	text=message.text.replace('/','')
	user_id = OriginSystemUsers.query.filter_by(system_userid=str(cid)).first().id_users
	cur_session = check_user_seesion(user_id)
	if cur_session is not None:
		session_disabled(user_id)	
	cdo(UserSession(id_users=user_id, id_botcommand=botCommands[text]['id']))
	current_date = date.today()
	begin_date = current_date + timedelta(days = ((-1)*day_deep))
	result = user_records_format(user_records(user_id, begin_date, current_date))
	if result is None:
		bot.send_message(cid,
		 'За последние {} дней не было внесено новых данных'.format(day_deep),
		  reply_markup=keyboard_commands)
		ctx.pop()
		return 0

	message_text = 'В системе за 7 дней есть записи: \n '+result + '\n для удаления записи пришли ее ID. например, 5'

	bot.send_message(cid, message_text, reply_markup=keyboard_commands)
	
	ctx.pop()
	return 0


@bot.message_handler(commands=['add','add_to_date'])
def command_add(message):
	ctx.push()
	cid = message.chat.id
	text=message.text.replace('/','')
	user_id = OriginSystemUsers.query.filter_by(system_userid=str(cid)).first().id_users
	cur_session = check_user_seesion(user_id)
	if cur_session is not None:
		session_disabled(user_id)	
	cdo(UserSession(id_users=user_id, id_botcommand=botCommands[text]['id']))
	bot.send_message(cid, sports_gr_commands, reply_markup=keyboard_commands)
	
	ctx.pop()
	return 0



@bot.message_handler(commands = sports.keys())
def command_sport(message):
	ctx.push()
	cid=message.chat.id
	user_id = OriginSystemUsers.query.filter_by(system_userid=str(cid)).first().id_users
	cur_session = check_user_seesion(user_id)
	if cur_session is None:
		bot.send_message(cid,
		 "Тебе для начала нужно выбрать команду. \n Для вызова списка доступных команд воспользуйся командой /help",
			reply_markup=keyboard_commands)
		ctx.pop()
		return 0	
	surveys_id = Surveys.query.filter_by(name=message.text.replace('/','')).first().id
	if current_survey_for_user(user_id) is not  None:
		current_survey_all_obj_disable(user_id)

	cdo(CurrentSurvey(
		id_surveys=surveys_id,
		id_users=user_id,
		user_time=datetime.fromtimestamp((int(message.date))).strftime('%Y-%m-%d'),
		question_quantity=qn(Surveys.query.filter_by(name=message.text.replace('/','')).first().id)
		))
	if cur_session.id_botcommand == botCommands['add']['id']:

		cdo(CurrentQuestion(
			id_currentsurvey=CurrentSurvey.query.filter_by(id_users=user_id).order_by(CurrentSurvey.timestamp.desc()).first().id,
			id_surveyquestion=SurveysQuestion.query.filter_by(id_surveys=surveys_id, question_index=1).first().id
			))

	if cur_session.id_botcommand == botCommands['add_to_date']['id']:

		cdo(CurrentQuestion(
			id_currentsurvey=CurrentSurvey.query.filter_by(id_users=user_id).order_by(CurrentSurvey.timestamp.desc()).first().id,
			id_surveyquestion=SurveysQuestion.query.filter_by(id_surveys=surveys_id, question_index=0).first().id
			))

	bot.send_message(cid, cq(user_id), reply_markup=keyboard_commands)
	current_question_flag_update(user_id, 'questionsend', 1)
	ctx.pop()
	return 0

@bot.message_handler(commands=['new'])
def command_new(message):
    cid = message.chat.id
    user_id = OriginSystemUsers.query.filter_by(system_userid=str(cid)).first().id_users
    cur_session = check_user_seesion(user_id)
    if cur_session is not None:
    	session_disabled(user_id)
    cdo(UserSession(id_users=user_id, id_botcommand=botCommands[message.text]['id']))
    bot.send_message(cid, 'Пришли мне, пожалуйста, название нового вида спорта')
    return 0

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	ctx.push()
	cid = message.chat.id
	user_id = OriginSystemUsers.query.filter_by(system_userid=str(cid)).first().id_users
	cur_session = check_user_seesion(user_id)
	if cur_session is None:
		bot.send_message(cid,
		 "Тебе для начала нужно выбрать команду. \n Для вызова списка доступных команд воспользуйся командой /help",
			reply_markup=keyboard_commands)
		ctx.pop()
		return 0
	if message.text[0] == '/':
		bot.send_message(cid, "Тебе необходимо выбрать сначала команду из доступных. \n Для списка доступных команд воспользуйся \n /help", reply_markup=keyboard_commands)
		ctx.pop()
		return 0

	if cur_session.id_botcommand == botCommands['add']['id']:

		cur_survey = CurrentSurvey.query.filter_by(
		id_users=user_id, state=0
		).order_by(CurrentSurvey.timestamp.desc()).first()
				
		current_question = CurrentQuestion.query.filter_by(
							id_currentsurvey=cur_survey.id, state=0, answerreceive=0).order_by(
						CurrentQuestion.id.desc()).first()
		
		question_base=SurveysQuestion.query.filter_by(
						id=current_question.id_surveyquestion).first()	

		survey = Surveys.query.filter_by(id=cur_survey.id_surveys).first()	
		users_number = User.query.filter_by(is_active=True).count()	

		if question_base.question_index == 1:
			try:
				float(message.text)
			except:
				bot.send_message(cid,
			 "Тебе необходимо прислать ответ в чиловом формате, например 5.4",
				reply_markup=keyboard_commands)
				ctx.pop()
				return 0

		if question_base.question_index == 2:
			try:
				int(message.text)
			except:
				bot.send_message(cid,
			 "Тебе необходимо прислать ответ в целочисленном формате, например 5",
				reply_markup=keyboard_commands)
				ctx.pop()
				return 0

		if question_base.question_index == 3:
			if message.text in (places.values()):
				pass
			else:
				bot.send_message(cid,
			 "Выбери из доступных (см. клавиатуру внизу)",
				reply_markup=keyboard_places)
				ctx.pop()
				return 0


	
		if current_question.reply ==0 and question_base.question_index == 1:
			if float(message.text) < sport_coef[survey.name]['bottom'] or float(message.text) > sport_coef[survey.name]['upper']:
				bot.send_message(cid,
				 'Пожалуйстаб проверь, что значение введено правильно. \n Еще раз отправь ответ на вопрос',
				  reply_markup=keyboard_commands)
				cur_question_reply_flag(current_question.id)
				ctx.pop()
				return 0
		if current_question.reply ==0 and question_base.question_index == 2:
			if float(message.text) > users_number:
				bot.send_message(cid,
					'Пожалуйстаб проверь, что значение введено правильно (Нас сейчас {} спортсменов). \n Еще раз отправь ответ на вопрос'.format(users_number),
					reply_markup=keyboard_commands)
				cur_question_reply_flag(current_question.id)
				ctx.pop()
				return 0	

		current_question_answer_proccess(user_id, message.text)
		current_question_flag_update(user_id, 'state', 1)
		current_survey_step_update(user_id)	
		


		while cur_survey.step<(cur_survey.question_quantity-1): #костыль -1

		
			cdo(CurrentQuestion(
				id_currentsurvey=cur_survey.id,
				id_surveyquestion=SurveysQuestion.query.filter_by(
					id_surveys=survey.id,
					question_index=question_base.question_index+1
					).first().id
				))
			if (question_base.question_index+1)==3:				
				bot.send_message(cid, cq(user_id), reply_markup=keyboard_places)
			else:
				bot.send_message(cid, cq(user_id), reply_markup=keyboard_commands)	

			current_question_flag_update(user_id, 'questionsend', 1)
			ctx.pop()
			return 0	

		current_survey_state_update(user_id, cur_survey.id)
		current_user_session_upgrade(user_id)
		db.session.commit()
		question = CurrentQuestion.query.filter_by(id_currentsurvey=cur_survey.id).order_by(CurrentQuestion.id)
		sport_name = survey.name	
	

		if float(question[0].result) < sport_coef[sport_name]['cr']:
			score=(1+group_coef*int(question[1].result))*(float(question[0].result)*sport_coef[sport_name]['c1'])
		else:
			score =(1+group_coef*int(question[1].result))*(float(question[0].result)*sport_coef[sport_name]['c2'])

		

		if cur_survey.question_quantity ==4:
			id_place = Place.query.filter_by(name=question[2].result).first().id
		else:
			id_place=1	

		cdo(SurveyResult(
			parameter_1=abs(float(question[0].result)),
			id_quest_1=question[0].id_surveyquestion,
			parameter_2=abs(int(question[1].result)),
			id_quest_2=question[1].id_surveyquestion,
			date=cur_survey.user_time,
			id_users=user_id,
			id_currentsurvey=cur_survey.id,
			id_surveys=cur_survey.id_surveys,
			score=round(score,1),
			id_place=id_place
			))
		bot.send_message(cid, 'Твои данные внесены, получено {} баллов! \n Если ты хочешь добавить еще тренировку, нажми  /add'.format(round(score,1)), reply_markup=keyboard_commands)
		ctx.pop()	

		return 0

	if cur_session.id_botcommand == botCommands['add_to_date']['id']:
		cur_survey = CurrentSurvey.query.filter_by(
		id_users=user_id, state=0
		).order_by(CurrentSurvey.timestamp.desc()).first()
				
		current_question = CurrentQuestion.query.filter_by(
							id_currentsurvey=cur_survey.id, state=0, answerreceive=0).order_by(
						CurrentQuestion.id.desc()).first()
		
		question_base=SurveysQuestion.query.filter_by(
						id=current_question.id_surveyquestion).first()	

		survey = Surveys.query.filter_by(id=cur_survey.id_surveys).first()

		if question_base.question_index==0:
			new_date = findall(r'(\d+)', message.text)
			
			try:
				new_date = '{}-{}-{}'.format(date.today().year, new_date[0], new_date[1])
				new_date=datetime.strptime(new_date, '%Y-%m-%d')
				
			except:
				bot.send_message(cid,
			 ('Дата введена в неправильно формате! \n'+ 'Правильный формат месяц.день\n'+
			 	'Пример: 08.17'),
				reply_markup=keyboard_commands)
				ctx.pop()
				return 0
			
			if new_date.date() < (date.today() + timedelta(days = (-10))) or new_date.date() > date.today():
					
				bot.send_message(cid,
			 ('Дата не может быть больше текущей даты: {} \n, или меньше, чем {} \n '.format((date.today()),(date.today() + timedelta(days = (-10))))+
			  'Пришли дату повторно'),
				reply_markup=keyboard_commands)
				ctx.pop()
				return 0

			current_question_answer_proccess(user_id, new_date)
			current_question_flag_update(user_id, 'state', 1)
			current_survey_step_update(user_id)
			cdo(CurrentQuestion(
				id_currentsurvey=cur_survey.id,
				id_surveyquestion=SurveysQuestion.query.filter_by(
					id_surveys=survey.id,
					question_index=question_base.question_index+1
					).first().id
				))
			bot.send_message(cid, cq(user_id), reply_markup=keyboard_commands)	
			current_question_flag_update(user_id, 'questionsend', 1)
			ctx.pop()
			return 0

		if question_base.question_index==1:
			try:
				float(message.text)
			except:
				bot.send_message(cid,
			 "Тебе необходимо прислать ответ в чиcловом формате, например 5.4",
				reply_markup=keyboard_commands)
				ctx.pop()
				return 0

		if question_base.question_index==2:
			try:
				int(message.text)
			except:
				bot.send_message(cid,
			 "Тебе необходимо прислать ответ в чиcловом формате, например 5",
				reply_markup=keyboard_commands)
				ctx.pop()
				return 0

		if question_base.question_index == 3:
			if message.text in (places.values()):
				pass
			else:
				bot.send_message(cid,
			 "Выбери из доступных (см. клавиатуру внизу)",
				reply_markup=keyboard_places)
				ctx.pop()
				return 0

		users_number = User.query.filter_by(is_active=True).count()	
	
		if current_question.reply ==0 and question_base.question_index == 1:
			if float(message.text) < sport_coef[survey.name]['bottom'] or float(message.text) > sport_coef[survey.name]['upper']:
				bot.send_message(cid,
				 'Пожалуйстаб проверь, что значение введено правильно. \n Еще раз отправь ответ на вопрос',
				  reply_markup=keyboard_commands)
				cur_question_reply_flag(current_question.id)
				ctx.pop()
				return 0
		if current_question.reply ==0 and question_base.question_index == 2:
			if float(message.text) > users_number:
				bot.send_message(cid,
					'Пожалуйстаб проверь, что значение введено правильно (Нас сейчас {} спортсменов). \n Еще раз отправь ответ на вопрос'.format(users_number),
					reply_markup=keyboard_commands)
				cur_question_reply_flag(current_question.id)
				ctx.pop()
				return 0	

		current_question_answer_proccess(user_id, message.text)
		current_question_flag_update(user_id, 'state', 1)
		current_survey_step_update(user_id)	

		while cur_survey.step<cur_survey.question_quantity:
		
			cdo(CurrentQuestion(
				id_currentsurvey=cur_survey.id,
				id_surveyquestion=SurveysQuestion.query.filter_by(
					id_surveys=survey.id,
					question_index=question_base.question_index+1
					).first().id
				))
						
			if (question_base.question_index+1)==3:			
				bot.send_message(cid, cq(user_id), reply_markup=keyboard_places)
			else:
				bot.send_message(cid, cq(user_id), reply_markup=keyboard_commands)	
			current_question_flag_update(user_id, 'questionsend', 1)
			ctx.pop()
			return 0	

		current_survey_state_update(user_id, cur_survey.id)
		current_user_session_upgrade(user_id)
		db.session.commit()
		question = CurrentQuestion.query.filter_by(id_currentsurvey=cur_survey.id).order_by(CurrentQuestion.id)
		sport_name = survey.name	
	

		if float(question[1].result) < sport_coef[sport_name]['cr']:
			score=(1+group_coef*int(question[2].result))*(float(question[1].result)*sport_coef[sport_name]['c1'])
		else:
			score =(1+group_coef*int(question[2].result))*(float(question[1].result)*sport_coef[sport_name]['c2'])	

		if cur_survey.question_quantity ==4:
			id_place = Place.query.filter_by(name=question[3].result).first().id
		else:
			id_place=1

		cdo(SurveyResult(
			parameter_1=abs(float(question[1].result)),
			id_quest_1=question[1].id_surveyquestion,
			parameter_2=abs(int(question[2].result)),
			id_quest_2=question[2].id_surveyquestion,
			date=question[0].result,
			id_users=user_id,
			id_currentsurvey=cur_survey.id,
			id_surveys=cur_survey.id_surveys,
			score=round(score,1),
			id_place = id_place
			))

		bot.send_message(cid, 'Твои данные внесены, получено {} баллов! \n Если ты хочешь добавить еще тренировку, нажми  /add'.format(round(score,1)), reply_markup=keyboard_commands)
		try:
			correct_analytical_result(user_id,User.query.filter_by(id=user_id).first().name,question[0].result)
		except:
			print('Google not update, CurrentSurvey ID={}'.format(cur_survey.id))

		ctx.pop()	

		return 0




	if cur_session.id_botcommand == botCommands['delete']['id']:
		try:
			int(message.text)
		except:
			bot.send_message(cid,
		 "Тебе необходимо прислать ответ в целочисленном формате, например, 5",
			reply_markup=keyboard_commands)
			ctx.pop()
			return 0
		current_date = date.today()
		begin_date = current_date + timedelta(days = (-5))
		#result = user_records(user_id, begin_date, current_date)
		if int(message.text) in [item[0] for item in user_records(user_id,begin_date, current_date)]:
			record_date = datetime.strftime(SurveyResult.query.filter_by(id=int(message.text)).first().date, '%Y-%m-%d %H:%M:%S')
			user_record_delete(int(message.text), user_id)
			current_user_session_upgrade(user_id)
			db.session.commit()
			bot.send_message(cid,
		 ("ID {} удалена").format(message.text),
			reply_markup=keyboard_commands)
			
			try:
				correct_analytical_result(user_id, User.query.filter_by(id=user_id).first().name,record_date)
			except:
				print('Google not update, CurrentSurvey ID={}'.format(cur_survey.id))

			ctx.pop()
			return 0
		else:
			bot.send_message(cid,
		 "Тебе необходимо прислать ID из присланного списка",
			reply_markup=keyboard_commands)
			ctx.pop()
			return 0
		
		ctx.pop()
		return 0		
		

	if cur_session.id_botcommand == botCommands['start']['id']:
		user_display_name_update(user_id, message.text)
		current_user_session_upgrade(user_id)
		db.session.commit()
		bot.send_message(cid,
		 "Привет, {}! \n Выбери команду внизу или нажми /help для вызова списка доступных команд." .format(message.text),
			reply_markup=keyboard_commands)
		ctx.pop()
		return 0






