from flask import request
from app import  db, telegrambot
from config import Config, OriginSystemConfig


from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, SportsCoeff, SportsGroup, Sports, Surveys, SurveysQuestion, GroupCoeff, OriginSystemUsers, Place
from flask import flash, redirect, url_for, render_template
from app.forms import LoginForm, RegistrationForm, NewSportGroupForm, NewSportForm, SportEdit,  GroupCoeffForm, MessageSend, ReportForm, PlaceForm
from werkzeug.urls import url_parse
from datetime import date, timedelta

from microapp import app, ctx





@app.route('/' + OriginSystemConfig.TOKEN, methods=['POST'])
def getMessage():
	telegrambot.bot.process_new_updates([telegrambot.telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200

@app.route('/')
@app.route('/index')
@login_required
def index():
	telegrambot.bot.remove_webhook()
	telegrambot.bot.set_webhook(url="{}{}".format(Config.APP_URL,OriginSystemConfig.TOKEN))

	date_list =[]
	result=[]
	row_count=0
	end_date = date.today()
	begin_date =  date.today() + timedelta(days = ( 1-date.today().day))
	cur_date = []
	cur_date.append(begin_date.strftime('%m-%d'))
	cur_date.append(end_date.strftime('%m-%d'))
	query = ''
	

	for i in range(0,(end_date - begin_date).days+1):
		date_list.append((begin_date + timedelta(days=i)).strftime('%m-%d'))

		if i ==(end_date - begin_date).days:
				query += 'SUM(sr.score) FILTER (where date=\'{0}\') as \"{0}\" '.format(begin_date + timedelta(days=i))
		else:
				query += 'SUM(sr.score) FILTER (where date=\'{0}\') as \"{0}\",'.format(begin_date + timedelta(days=i))
	query = ('select u.name as usern, sum(sr.score), ' 
		+ (query )
		+ 'from surveyresult as sr join users as u on sr.id_users=u.id '
		+ 'where sr.date >=\'{}\' and  sr.date <= \'{}\' '.format(begin_date, end_date)
		+ 'group by (usern) order by 2 desc;')

	colscount = len(date_list)+2

	result=db.engine.execute(query)

	query_by_place = ('select u.name as usern,  SUM(sr.score) as tsum '
		+ 
		'from surveyresult as sr join users as u on sr.id_users=u.id '
		+
		'join surveys as sur on sr.id_surveys=sur.id '
		+
		'join sports as sp on sur.id_sports=sp.id '
		+
		'join sportsgroup as spg on sp.id_sportsgroup=spg.id '
		+
		'join place as p on p.id=sr.id_place '
		+
		'where sr.date >=\'{}\' and  sr.date <= \'{}\' and '.format(begin_date, end_date)
		+
		'p.name != \'No Place\' '
		+
		'group by(u.name) order by 2;')

	result_by_place=db.engine.execute(query_by_place)

	return render_template('index.html', title='Home', result=result, result_p=result_by_place, date_list=date_list, rows=row_count, cols=colscount, date=cur_date)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, display_name=form.display_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)




@app.route('/create_sport_group', methods=['GET', 'POST'])
@login_required
def create_sport_group():
    
    if current_user.get_role() !='admin':
    	return redirect(url_for('index.html'))
    
    form = NewSportGroupForm()

    if form.validate_on_submit():

    	sportgroup = SportsGroup(
    		name=form.name.data,
    		rus_name=form.rus_name.data,
    		rank=form.rank.data)
    	db.session.add(sportgroup)
    	db.session.commit()
    	ctx.push()
    	telegrambot.sports_gr, telegrambot.sports_gr_commands = telegrambot.create_sports_group_description()
    	ctx.pop()
    	flash('New sport group \"{}\" have been saved.'.format(form.name.data))
    	return redirect(url_for('create_sport_group'))
    elif request.method == 'GET':
    	pass

    return render_template('create_sport_group.html', title='Create Sport Group',
                           form=form)



@app.route('/create_sport', methods=['POST'])
@login_required
def validate_sport_form():

	
	categories_sp = [(str(c.id), str(c.name)) for c in SportsGroup.query.all()]
	categories_place = [(str(c.id), str(c.name)) for c in Place.query.all()]
	form = NewSportForm(request.form)
	form.sport_group.choices = categories_sp
	form.place.choices = categories_place


	if form.validate_on_submit():
		print(form.place.data)
		
		sport = Sports(
			name=form.name.data,
		 rus_name=form.rus_name.data,
		 rank=form.rank.data,
		 id_sportsgroup=int(form.sport_group.data))

		survey=Surveys(
			name=form.name.data,
			sports=sport)

		question_0 = SurveysQuestion(
			survey_question='Введите дату тренировки в формате мм.дд. Пример, 08.17',
			question_index=0,
			parameter='date',
			surveys=survey,
			id_questiontypes=1)

		question_1 = SurveysQuestion(
			survey_question=form.question_1.data,
			question_index=1,
			parameter=form.parameter_1.data,
			surveys=survey,
			id_questiontypes=1)

		question_2 = SurveysQuestion(
			survey_question=form.question_2.data,
			question_index=2,
			parameter=form.parameter_2.data,
			surveys=survey,
			id_questiontypes=1)
		if form.criteria.data is None:
			coeffs=SportsCoeff(
			criteria_description=form.criteria_desc.data,
			criteria=1,
			coeff1=form.coeff1.data,
			coeff2=form.coeff1.data,
			sport=sport,
			bottom=form.bottom.data,
			upper=form.bottom.data)
		else:
			coeffs=SportsCoeff(
			criteria_description=form.criteria_desc.data,
			criteria=form.criteria.data,
			coeff1=form.coeff1.data,
			coeff2=form.coeff2.data,
			sport=sport,
			bottom=form.bottom.data,
			upper=form.bottom.data)


		db.session.add(sport)
		sport.sportsplace.append(Place.query.filter_by(id=form.place.data).first())
		db.session.add(survey)
		db.session.add(question_0)
		db.session.add(question_1)
		db.session.add(question_2)
		db.session.add(coeffs)
		db.session.commit()
		flash('New sport \"{}\" has been saved.'.format(form.name.data))
		ctx.push()
		telegrambot.survey_questions = telegrambot.create_survey_questions()
		telegrambot.sports, telegrambot.sport_text, telegrambot.sport_commands  = telegrambot.create_sport_description()
		telegrambot.sport_coef=telegrambot.create_sport_coeff()
		ctx.pop()
		return redirect(url_for('create_sport'))
	return render_template('sport_create.html', title='Sport Create', form=form)

@app.route('/create_sport', methods=['Get'])
@login_required
def create_sport():

    
    if current_user.get_role() !='admin':
    	return redirect(url_for('index.html'))

    categories_sp = [(str(c.id), str(c.name)) for c in SportsGroup.query.all()]
    categories_place = [(str(c.id), str(c.name)) for c in Place.query.all()]
    form = NewSportForm(request.form)
    form.sport_group.choices = categories_sp
    form.place.choices = categories_place

    return render_template('sport_create.html', title='Sport Create',
                           form=form)


@app.route('/sports', methods=['GET', 'POST'])
@login_required
def sports_all():
	sport_list=Sports.query.join(SportsGroup, SportsGroup.id==Sports.id_sportsgroup).all()

	return render_template('sports.html', title='Sport List', sport_list=sport_list)

@app.route('/sport_edit/<sport>', methods=['GET'])
@login_required
def sport_edit1(sport):




	
	if current_user.get_role() !='admin':
		return redirect(url_for('index.html'))

	sport=Sports.query.filter_by(name=sport).join(SportsGroup, SportsGroup.id==Sports.id_sportsgroup).first_or_404()
	sport_coeff=SportsCoeff.query.filter_by(sport=sport).first_or_404()
	form = SportEdit(request.form)

	form.name.default=sport.name
	form.rus_name.default=sport.rus_name
	form.rank.default=sport.rank
	
	form.criteria.default=sport_coeff.criteria
	form.criteria_desc.default=sport_coeff.criteria_description	
	
	form.coeff1.default=sport_coeff.coeff1
	form.coeff2.default=sport_coeff.coeff2
	form.bottom.default=sport_coeff.bottom
	form.upper.default=sport_coeff.upper
	
	categories_sp = [(str(c.id), str(c.name)) for c in SportsGroup.query.all()]
	categories_place = [(str(c.id), str(c.name)) for c in Place.query.all()]
	
	form.sport_group.choices = categories_sp
	form.sport_group.default=sport.sportsgroup.name
	form.place.choices = categories_place

	form.process()

	return render_template('sport_edit.html', title='Sport Edit', form=form)

@app.route('/sport_edit/<sport>', methods=['POST'])
@login_required
def sport_edit(sport):

	categories_sp = [(str(c.id), str(c.name)) for c in SportsGroup.query.all()]
	categories_place = [(str(c.id), str(c.name)) for c in Place.query.all()]
	form = SportEdit(request.form)
	form.sport_group.choices = categories_sp
	form.place.choices = categories_place


	if form.validate_on_submit():

		sport=Sports.query.filter_by(name=sport).first()
		sport.name=form.name.data
		sport.rus_name=form.rus_name.data
		sport.rank=form.rank.data 

		survey=Surveys.query.filter_by(sports=sport).first()
		survey.name=form.name.data
	

		sport_coeff=SportsCoeff.query.filter_by(sport=sport).first_or_404()
		sport_coeff.coeff1=form.coeff1.data
		sport_coeff.coeff2=form.coeff2.data
		sport_coeff.criteria=form.criteria.data
		sport_coeff.criteria_description=form.criteria_desc.data
		sport_coeff.bottom=form.bottom.data
		sport_coeff.upper=form.upper.data
		sport.sportsplace.append(Place.query.filter_by(id=form.place.data).first())
		db.session.commit()

		try:
			sport.sportsplace.append(Place.query.filter_by(id=form.place.data).first())
			db.session.commit()
		except:
			pass

		ctx.push()

		telegrambot.sports, telegrambot.sport_text, telegrambot.sport_commands  = telegrambot.create_sport_description()
		telegrambot.sports_gr, telegrambot.sports_gr_commands = telegrambot.create_sports_group_description()

		telegrambot.sport_coef=telegrambot.create_sport_coeff()
		ctx.pop()

		flash('Sport \"{}\" has been updated.'.format(form.name.data))
		return redirect(url_for('sports_all'))
	


	return render_template('sport_edit.html', title='Sport Edit', form=form)

@app.route('/group_coeff_edit', methods=['Get'])
@login_required
def group_coeff_check():
	group_coeff=GroupCoeff.query.first()
	form = GroupCoeffForm(request.form)
	form.description.default = group_coeff.description
	form.value.default = group_coeff.coeff
	form.process()

	return render_template('group_coeff.html', title='Group Coefficient', form=form)

@app.route('/group_coeff_edit', methods=['POST'])
@login_required
def group_coeff_up():
	group_coeff=GroupCoeff.query.first()
	form = GroupCoeffForm(request.form)
	if form.validate_on_submit():
		group_coeff=GroupCoeff.query.first()
		group_coeff.description=form.description.data
		group_coeff.coeff=form.value.data
		db.session.commit()
		ctx.push()
		telegrambot.group_coef = GroupCoeff.query.first().coeff
		ctx.pop()
		flash('Coefficient for group has been saved.')
		return redirect(url_for('sports_all'))

	return render_template('group_coeff.html', title='Group Coefficient', form=form)



@app.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message_to_users():
    
    if current_user.get_role() !='admin':
    	return redirect(url_for('index.html'))
    form = MessageSend()
    if form.validate_on_submit():
    	cid = OriginSystemUsers.query.join(User, OriginSystemUsers.id_users == User.id).filter_by(is_active=True).all()
    	for item in cid:	
    		telegrambot.bot.send_message(item.system_userid, form.message_text.data)

    	flash('Your message send')
    	return redirect(url_for('send_message_to_users'))
    elif request.method == 'GET':
    	pass

    return render_template('send_message.html', title='Send Message',form=form)




@app.route('/report', methods=['GET','POST'])
@login_required
def report_generate():

	
	form = ReportForm()
	date_list =[]
	result=[]
	row_count=0
	end_date = form.enddate.data
	begin_date =  form.begindate.data
	query = ''

	for i in range(0,(end_date - begin_date).days+1):
		date_list.append((begin_date + timedelta(days=i)).strftime('%m-%d'))

		if i ==(end_date - begin_date).days:
				query += 'SUM(sr.score) FILTER (where date=\'{0}\') as \"{0}\" '.format(begin_date + timedelta(days=i))
		else:
				query += 'SUM(sr.score) FILTER (where date=\'{0}\') as \"{0}\",'.format(begin_date + timedelta(days=i))
	query = ('select sur.name as sport, sum(sr.score), sr.parameter_1, ' 
		+ (query )
		+ 'from surveyresult as sr join users as u on sr.id_users=u.id join surveys as sur on sr.id_surveys=sur.id '
		+ 'where sr.date >=\'{}\' and  sr.date <= \'{}\' and u.id={} '.format(begin_date, end_date, current_user.id)
		+ 'group by (sport, sr.parameter_1) order by 2 desc;')

	colscount = len(date_list)+2
	

	result=db.engine.execute(query)

	if form.validate_on_submit():
		
		end_date = form.enddate.data
		begin_date =  form.begindate.data
		query = ''
		date_list =[]
		for i in range(0,(end_date - begin_date).days+1):
			date_list.append((begin_date + timedelta(days=i)).strftime('%m-%d'))

			if i ==(end_date - begin_date).days:
				query += 'SUM(sr.score) FILTER (where date=\'{0}\') as \"{0}\" '.format(begin_date + timedelta(days=i))
			else:
				query += 'SUM(sr.score) FILTER (where date=\'{0}\') as \"{0}\",'.format(begin_date + timedelta(days=i))
		query = ('select sur.name as sport, sum(sr.score), sr.parameter_1, ' 
			+ (query )
			+ 'from surveyresult as sr join users as u on sr.id_users=u.id join surveys as sur on sr.id_surveys=sur.id  '
			+ 'where sr.date >=\'{}\' and  sr.date <= \'{}\' and u.id={}  '.format(begin_date, end_date, current_user.id)
			+ 'group by (sport, sr.parameter_1) order by 2 desc;')
		

		result=db.engine.execute(query)
		row_count=result.rowcount
		colscount = len(date_list)+2
		
		return render_template('report.html', title='Report', form=form, result=result, date_list=date_list, rows=row_count, cols=colscount)


	return render_template('report.html', title='Report', form=form, result=result, date_list=date_list, rows=row_count, cols=colscount)



@app.route('/places', methods=['GET','POST'])
@login_required
def places():
	result=Place.query.filter_by(is_active=True).all()
	form = PlaceForm()
	if form.validate_on_submit():
		place = Place(name=form.name.data, url=form.url.data)
		db.session.add(place)
		db.session.commit()
		ctx.push()
		telegrambot.places, telegrambot.keyboard_places = telegrambot.place()
		telegrambot.sports, telegrambot.sport_text, telegrambot.sport_commands  = telegrambot.create_sport_description()
		ctx.pop()
		flash('New place was added')
		return render_template('places.html', title='Place', form=form, result=result)


	return render_template('places.html', title='Places', form=form, result=result)


@app.route('/place_edit/<place>', methods=['GET'])
@login_required
def place_get(place):
	
	if current_user.get_role() !='admin':
		return redirect(url_for('places.html'))

	place=Place.query.filter_by(name=place).first_or_404()
	
	form = PlaceForm(request.form)

	form.name.default=place.name
	form.url.default=place.url
	form.process()

	return render_template('place.html', title=place.name, form=form)

@app.route('/place_edit/<place>', methods=['POST'])
@login_required
def place_edit(place):


	form = PlaceForm(request.form)

	if form.validate_on_submit():

		place=Place.query.filter_by(name=place).first()
		place.name=form.name.data
		place.url=form.url.data

		db.session.commit()

		ctx.push()

		telegrambot.places, telegrambot.keyboard_places = telegrambot.place()
		ctx.pop()

		flash('Place \"{}\" has been updated.'.format(form.name.data))
		return redirect(url_for('places'))
	


	return render_template('sport_edit.html', title='Place Edit', form=form)







