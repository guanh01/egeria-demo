
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
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['HOST'] = host
app.config['PORT'] = port


# setup the summary html directory
app.config['INDEX_FILE'] = "./templates/index.html"


# setup  query engine
queryEngine = QueryEngineHtml("./models/")
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
        return render_template('index.html', host=app.config['HOST'], port=app.config['PORT'])
    else:
        return redirect(url_for('index')) 

# this directed to raw page
@app.route("/index", methods=['GET'])
def rawIndex():
    if request.method == 'GET':
        return render_template('rawIndex.html', host=app.config['HOST'], port=app.config['PORT'])
    else:
        return redirect(url_for('index')) 
            

@app.route('/search_by_file', methods=['POST'])
def search_by_file():
    
    if request.method== "POST":
        # check if the post request has the file part
        if 'file' in request.files:
            f = request.files['file']
            # if user does not select file, browser also submit a empty part without filename
            if f.filename == '':
                flash('No selected file!')
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
                
                resultsHtml = app.config["queryEngine"].performQuery(issues, app.config['INDEX_FILE'])
                #return json.dumps(sents, indent=4, sort_keys = True)
                return render_template_string(resultsHtml, host=app.config['HOST'], port=app.config['PORT'], query= "") 		
            else:
                flash('File is not valid!')
    return redirect(url_for('index'))
                
             
# 
@app.route('/search_by_query', methods=['POST'])
def search_by_query():
    if request.method== "POST":
        if request.form['search']:
            query = request.form['search']
            print '-------------------------------'
            print time.strftime('%y-%m-%d %H:%M:%S') + '\t Search by query: ' + query
            issueDict = {'description': query, 'title': query}
            resultsHtml = app.config["queryEngine"].performQuery([issueDict], app.config['INDEX_FILE'])
            return render_template_string(resultsHtml, host=app.config['HOST'], port=app.config['PORT'], query= query)   
        else:
            flash('No query!')
            
    return redirect(url_for('index'))




if __name__ == '__main__':
    
	app.run(host='0.0.0.0', port=app.config['PORT'], threaded=True)
	




