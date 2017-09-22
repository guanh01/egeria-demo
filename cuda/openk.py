
from flask import Flask, request, redirect, url_for, render_template, flash, render_template_string
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import time, os

import sys
sys.path.insert(0, '../utils')


from pprint import pprint
from Helper import checkDirectory
from QueryEngineHtml import QueryEngineHtml
from ReadNvvpReport import ReadNvvpReport


app = Flask(__name__)
app.config.from_object(__name__)
bootstrap = Bootstrap(app)

# setup upload folder
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['pdf'])
checkDirectory(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


# setup host and port number
from Config import host, port
from Config import similarity_threshold
sim_thr = similarity_threshold # default similarity threshold

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['HOST'] = host
app.config['PORT'] = port


# setup the summary html directory
app.config['INDEX_FILE'] = "./templates/index.html"


# setup  query engine
queryEngine = QueryEngineHtml("./models/", app.config['INDEX_FILE'])
app.config["queryEngine"] = queryEngine

# setup report parser
reportParser = ReadNvvpReport()
app.config["reportParser"] = reportParser



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# this directed to summary page
@app.route("/", methods=['GET'])
@app.route("/summary", methods=['GET'])
def index():
 
    if request.method == 'GET':
        return render_template('index.html', host=app.config['HOST'], port=app.config['PORT'], sim_thr=sim_thr)
    else:
        return redirect(url_for('index')) 

# this directed to raw page
@app.route("/index", methods=['GET'])
def rawIndex():
    if request.method == 'GET':
        return render_template('rawIndex.html', host=app.config['HOST'], port=app.config['PORT'], sim_thr=sim_thr)
    else:
        return redirect(url_for('index')) 
            

@app.route('/search', methods=['GET', 'POST'])
def search():
	if request.method== "POST":
		sim_thr = float(request.form['sim_thr'])
		query = request.form['search']
		#print type(sim_thr), sim_thr
		if len(query):
			print '-------------------------------'
			print time.strftime('%y-%m-%d %H:%M:%S') + '\t Search by query: ' + query
			issueDict = {'description': query}
			resultsHtml = app.config["queryEngine"].performQuery([issueDict], sim_thr)

			return render_template_string(resultsHtml, host=app.config['HOST'], port=app.config['PORT'], query= query, sim_thr=sim_thr)   
		# check if the post request has the file part
		elif 'file' in request.files:
			f = request.files['file']
			# if user does not select file, browser also submit a empty part without filename
			if f.filename == '':
				flash('No selected file or query!')
				return redirect(url_for('index'))
                
			if f and allowed_file(f.filename):
				filename = secure_filename(f.filename)
				timestamp = time.strftime('%m%d%H%M%S')
				fn = timestamp+'_'+filename
				f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))

				issues = app.config["reportParser"].report2issues(app.config['UPLOAD_FOLDER'],fn)
				print '-------------------------------'
				print time.strftime('%y-%m-%d %H:%M:%S') + '\t search by file: '+ fn
				pprint(issues)

				resultsHtml = app.config["queryEngine"].performQuery(issues, sim_thr)
				#return json.dumps(sents, indent=4, sort_keys = True
				return render_template_string(resultsHtml, host=app.config['HOST'], port=app.config['PORT'], query= "", sim_thr=sim_thr) 		
			else:
				flash('File is not valid!')
				return redirect(url_for('index'))
		else:
			flash('No query!')

	return redirect(url_for('index'))
                
          

if __name__ == '__main__':
    
	app.run(host='0.0.0.0', port=app.config['PORT'], threaded=True)
	




