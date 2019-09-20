
from app import db
import gspread
import json
from pathlib import Path
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from threading import Timer

from microapp import ctx

from config import GoogleConfig


MAGIC_NUMBER = 64


def rowcol_to_a1(row, col):
    """Translates a row and column cell address to A1 notation.
    :param row: The row of the cell to be converted.
                Rows start at index 1.
    :type row: int, str
    :param col: The column of the cell to be converted.
                Columns start at index 1.
    :type row: int, str
    :returns: a string containing the cell's coordinates in A1 notation.
    Example:
    >>> rowcol_to_a1(1, 1)
    A1
    """
    row = int(row)
    col = int(col)

    div = col
    column_label = ''

    while div:
        (div, mod) = divmod(div, 26)
        if mod == 0:
            mod = 26
            div -= 1
        column_label = chr(mod + MAGIC_NUMBER) + column_label

    label = '%s%s' % (column_label, row)
    label_letter = '%s'%(column_label)

    return label, label_letter



def analytical_result():
	
	ctx.push()
	base_path = Path(__file__).parent
	file_path = (base_path / "../file_name.json").resolve() #credentials path
	scope = ['https://spreadsheets.google.com/feeds', 
         'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(file_path,
                                                               scope)
	gs = gspread.authorize(credentials)
	book = gs.open(GoogleConfig.GOOGLE_BOOK)
	date=datetime.utcnow().strftime('%Y-%m-%d')
	filter_query = 'select u.name as Usern, sr.date as TrDate,  SUM(sr.score) as tsum from surveyresult as sr join users as u on sr.id_users=u.id join surveys as sur on sr.id_surveys=sur.id where sr.date=\'{}\' group by(u.name, sr.date) order by 1,2;'.format(date)
	cross_query = 'select * from crosstab ($${}$$) as final_pivot (usern character varying(120), score double precision);'.format(filter_query)
	final = db.engine.execute(cross_query)


	if final.rowcount == 0:
		Timer(300.0, analytical_result).start()
		return 0	



	wks=book.worksheet(GoogleConfig.GOOGLE_LIST)
	gs_users =list(wks.col_values(1))
	last_row = len(gs_users)



	extract ={}
	for item in final:
		if item.usern not in gs_users:
			wks.update_cell(last_row+1,1, item.usern)
			last_row +=1
		extract[item.usern]=float(item.score)


	gs_users =list(wks.col_values(1))

	last_col = len(list(wks.row_values(1)))




	if wks.cell(1, last_col).value==date:
		last_col -=1 
	
	range_label_letter = rowcol_to_a1(1,int(last_col+1))[1]
	user_objects = wks.range(range_label_letter+'1:'+range_label_letter+str(last_row))


	for j in range(len(gs_users)):
		if gs_users[j] in extract.keys():
			user_objects[j].value=extract[gs_users[j]]
		else:
			user_objects[j].value =0


	user_objects[0].value=date
	wks.update_cells(user_objects)


	Timer(300.0, analytical_result).start()
	ctx.pop()
	


try:
	analytical_result()
except:
	print('Google not upload')


def correct_analytical_result(user_id, user_name, date):
	
	ctx.push()
	base_path = Path(__file__).parent
	file_path = (base_path / "../file_name.json").resolve() #credentials path
	scope = ['https://spreadsheets.google.com/feeds', 
         'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(file_path,
                                                               scope)

	
	gs = gspread.authorize(credentials)
	book = gs.open(GoogleConfig.GOOGLE_BOOK)
	#date=datetime.utcnow().strftime('%Y-%m-%d')
	filter_query = ('select u.name as Usern, sr.date as TrDate,  SUM(sr.score) as tsum '+
		' from surveyresult as sr join users as u on sr.id_users=u.id '+
		' join surveys as sur on sr.id_surveys=sur.id where sr.date=\'{}\' and u.id = {} '+
		' group by(u.name, sr.date) order by 1,2;').format(date, user_id)
	
	final = db.engine.execute(filter_query)
	date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S' )
	wks=book.worksheet(GoogleConfig.GOOGLE_LIST)
	gs_user =wks.find(user_name)
	gs_date = wks.find(date.strftime('%Y-%m-%d'))


	if final.rowcount == 0:
		
		wks.update_cell(gs_user.row, gs_date.col, 0)
		ctx.pop()
		return 0
	else:
		for item in final:
			wks.update_cell(gs_user.row, gs_date.col, item.tsum)
		ctx.pop()
		return 0

	

def analytical_result_custom_date(date):
	
	ctx.push()
	base_path = Path(__file__).parent
	file_path = (base_path / "../mysportstat-d492ccb41876.json").resolve()
	scope = ['https://spreadsheets.google.com/feeds', 
         'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(file_path,
                                                               scope)
	gs = gspread.authorize(credentials)
	book = gs.open(GoogleConfig.GOOGLE_BOOK)
	date=date
	filter_query = 'select u.name as Usern, sr.date as TrDate,  SUM(sr.score) as tsum from surveyresult as sr join users as u on sr.id_users=u.id join surveys as sur on sr.id_surveys=sur.id where sr.date=\'{}\' group by(u.name, sr.date) order by 1,2;'.format(date)
	cross_query = 'select * from crosstab ($${}$$) as final_pivot (usern character varying(120), score double precision);'.format(filter_query)
	final = db.engine.execute(cross_query)


	if final.rowcount == 0:
		Timer(300.0, analytical_result).start()
		#print('is none')
		return 0	



	wks=book.worksheet(GoogleConfig.GOOGLE_LIST)
	gs_users =list(wks.col_values(1))
	last_row = len(gs_users)



	extract ={}
	for item in final:
		#print(item.usern)
		#print(gs_users)
		if item.usern not in gs_users:
			wks.update_cell(last_row+1,1, item.usern)
			last_row +=1
		extract[item.usern]=float(item.score)


	gs_users =list(wks.col_values(1))

	last_col = len(list(wks.row_values(1)))




	if wks.cell(1, last_col).value==date:
		last_col -=1 
	
	range_label_letter = rowcol_to_a1(1,int(last_col+1))[1]
	user_objects = wks.range(range_label_letter+'1:'+range_label_letter+str(last_row))


	for j in range(len(gs_users)):
		if gs_users[j] in extract.keys():
			user_objects[j].value=extract[gs_users[j]]
		else:
			user_objects[j].value =0


	user_objects[0].value=date
	wks.update_cells(user_objects)



	ctx.pop()
	


