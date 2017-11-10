
from flask import Flask, request, redirect, url_for, render_template, flash, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import time, os
from datetime import datetime
import sys
# sys.path.insert(0, './egeria')


from egeria.helper import check_directory, get_script_path
from egeria.query_engine import QueryEngineHtml
from egeria.parse_nvvp_report import ReadNvvpReport
from config import doc2info 
from config import host, port, similarity_threshold


app = Flask(__name__)
app.config.from_object(__name__)
bootstrap = Bootstrap(app)

# setup upload folder
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['pdf'])
check_directory(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


# set up log folder 
LOG_FOLDER = './logs'
check_directory(LOG_FOLDER)
app.config['LOG_FOLDER'] = LOG_FOLDER
app.config['LOG_FREQUENCY'] = 10
app.config['LOG_COUNT'] = 0
app.config['LOG_FILE'] = None

# setup host, port number, and default similarity threshold
app.config['HOST'] = host
app.config['PORT'] = port
app.config['SIM_THR'] = similarity_threshold # default similarity threshold
#sim_thr = similarity_threshold 

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'hard to guess string'


# setup  query engines
script_path = './'
queryEngines = {}
allowed_docs = sorted(doc2info.keys())
for doc in allowed_docs:
	model_dir = os.path.join(script_path, 'models/'+doc)
	template_dir = os.path.join(script_path, 'templates/'+doc)
	queryEngines[doc] = QueryEngineHtml(model_dir, template_dir, docname=doc)

app.config["queryEngines"] = queryEngines

# setup report parser
app.config["reportParser"] = ReadNvvpReport()


def update_log(query, client_ip, sim_thr, docname, issues=''):
	loginfo = str(datetime.now())
	#time.strftime('%y-%m-%d %H:%M:%S') 
	loginfo+='\nSearch by query: '+ query
	loginfo+='\nclient ip: '+ client_ip 
	loginfo+='\nthreshold: '+ str(sim_thr)
	loginfo+='\ndoc: '+ docname
	if len(issues)>0:
		loginfo+='\nissues: '+ str(issues)
	loginfo+='\n\n'

	if app.config['LOG_FILE']==None or app.config['LOG_COUNT'] >= app.config['LOG_FREQUENCY']:
		app.config['LOG_FILE']=time.strftime('%y.%m.%d-%H.%M.%S')+'.txt'
		app.config['LOG_COUNT'] = 0
	filename =os.path.join(app.config['LOG_FOLDER'], app.config['LOG_FILE'])
	app.config['LOG_COUNT'] += 1
	with open(filename, 'a') as f:
		f.write(loginfo)
	#print 'write log to filename:', filename, ', log_count:', app.config['LOG_COUNT']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

########################
# Route #
########################
# this directed to opencl/cuda/openacc selection page
@app.route("/", methods=['GET'])
def homepage():
	return render_template('homepage.html', host=app.config['HOST'], port=app.config['PORT'])


@app.route('/openacc/guide', methods=['GET'])
def show_guide():
	return send_from_directory('./static/openacc/', 'openacc.htm')

@app.route("/<docname>", methods=['GET'])
@app.route("/<docname>/summary", methods=['GET'])
def show_summary(docname):
	# print 'show summary of', docname 
	if docname in allowed_docs:
	# if request.method == 'GET':
		template = docname+'/summary.html'
		return render_template(template, 
								host=app.config['HOST'], 
								port=app.config['PORT'], 
								sim_thr=app.config['SIM_THR'], 
								docname=docname)
	# else:
	else:
		return redirect(url_for('homepage')) 
		# return redirect(url_for('show_summary', docname=docname)) 

# this directed to raw page
@app.route("/<docname>/raw", methods=['GET'])
def show_raw(docname):
    # if request.method == 'GET':
    if docname in allowed_docs:
    	template = docname+'/raw.html'
        return render_template(template, 
        						host=app.config['HOST'], 
        						port=app.config['PORT'], 
        						sim_thr=app.config['SIM_THR'], 
        						docname=docname)
    else:
        return redirect(url_for('homepage')) 
            

@app.route('/<docname>/search', methods=['GET', 'POST'])
def search(docname):
	if docname not in allowed_docs:
		return redirect(url_for('homepage')) 
	if request.method== "POST":
		client_ip = request.remote_addr
		sim_thr = float(request.form['sim_thr'])
		query = request.form['search']
		#print type(sim_thr), sim_thr
		if len(query):
			update_log(query, client_ip, sim_thr, docname)
			issueDict = {'description': query}
			resultsHtml = app.config["queryEngines"][docname].performQuery([issueDict], sim_thr)

			return render_template_string(resultsHtml, 
											host=app.config['HOST'], 
											port=app.config['PORT'], 
											query= query, 
											sim_thr=sim_thr,
											docname = docname)   
		# check if the post request has the file part
		elif 'file' in request.files:
			f = request.files['file']
			# if user does not select file, browser also submit a empty part without filename
			if f.filename == '':
				flash('No selected file or query!')
				return redirect(url_for('show_summary', docname=docname)) 
                
			if f and allowed_file(f.filename):
				filename = secure_filename(f.filename)
				timestamp = time.strftime('%m%d%H%M%S')
				fn = timestamp+'_'+filename
				f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))

				issues = app.config["reportParser"].report2issues(app.config['UPLOAD_FOLDER'],fn)
				#print '-------------------------------'
				update_log(fn, client_ip, sim_thr, docname, issues)
				# print time.strftime('%y-%m-%d %H:%M:%S') + '\tsearch by file: '+ fn,', threshold:', sim_thr 
				#pprint(issues)

				resultsHtml = app.config["queryEngines"][docname].performQuery(issues, sim_thr)
				#return json.dumps(sents, indent=4, sort_keys = True
				return render_template_string(resultsHtml, 
												host=app.config['HOST'], 
												port=app.config['PORT'], 
												query= "", 
												sim_thr=sim_thr,
												docname=docname) 		
			else:
				flash('File is not valid!')
				return redirect(url_for('show_summary', docname=docname)) 
		else:
			flash('No query!')

	return redirect(url_for('show_summary', docname=docname)) 
                
          

if __name__ == '__main__':
    
	app.run(host='0.0.0.0', port=app.config['PORT'], threaded=True)
	




