

import os
import io
import base64
import numpy as np 
import pandas as pd
import flask
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


app = flask.Flask(__name__)
app.config['EXPLAIN_TEMPLATE_LOADING¶']=True
# TODO: A secret key is included in the sample so that it works but if you
# use this code in your application please replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.


@app.route('/')
def index():
    return flask.render_template('calculate.html')

@app.route('/', methods=['POST'])
# def my_form_post():
#     text = flask.request.form['confidence_level']

def plot_png():
    confidence_level=float(flask.request.form['confidence_level'])
    segment_size=float(flask.request.form['segment_size'])
    coversion_rate=float(flask.request.form['coversion_rate'])
    #return '<img width="600" height="600" src="data:image/png;base64,{}">'.format(plot_url)
    return flask.redirect(flask.url_for('plot', cf=confidence_level, ss=segment_size,cr= coversion_rate))
    # return flask.Response(output.getvalue(), mimetype='image/png')



@app.route('/plot')
def plot():
    cf=float(flask.request.args.get('cf', None))
    ss=float(flask.request.args.get('ss', None))
    cr=float(flask.request.args.get('cr', None))
    fig = plot_delta_and_sample(cf, ss, cr)
    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()
    
    # return flask.render_template('result')
    return flask.render_template('result.html', plot_url=plot_url, cf=cf, ss=ss, cr=cr)
    # return '<img width="600" height="600" src="data:image/png;base64,{}">'.format(plot_url)
def plot_delta_and_sample(p, s=1000000, t=0.0234):
    fig = plt.Figure(figsize=[10,10])
    axis = fig.add_subplot(1, 1, 1)
    x = np.linspace(0,20000,100) 
    z_test=norm.ppf(p)
    y = z_test*np.sqrt(((0.5*0.5)/x)*(s-x)/(s-1))

    _=axis.plot(x,y)
    #plt.xlim(-3,3)
    #plt.ylim(-3,3)

    _=axis.set_xlabel("sample-size")
    _=axis.set_ylabel("delta")
    
    return fig

@app.route('/download')
def download():
    cf=float(flask.request.args.get('cf', None))
    ss=float(flask.request.args.get('ss', None))
    cr=float(flask.request.args.get('cr', None))
    final_df=dataframe(cf, ss, cr)
    resp = flask.make_response(final_df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp
def dataframe(p,s=1000000,baseline=0.0234, step=1000):
    
    delta_min=[]
    delta_max=[]
    sample_size=[]
    final_massive=[]
    for x in np.arange(0,20000,step): #x - sample_size
        z_test=norm.ppf(p) #ztest critical value
        y = z_test*np.sqrt(((0.5*0.5)/x)*(s-x)/(s-1)) #y - delta
        delta_min=baseline-baseline*y
        delta_max=baseline+baseline*y
        sample_size=x
        final_massive.append([delta_min,delta_max,sample_size])
    final_df=pd.DataFrame(final_massive)
    final_df.columns=['CR_max', 'CR_min', 'sample_size']
    return final_df





if __name__ == '__main__':
    # When running locally with Flask's development server this disables
    # OAuthlib's HTTPs verification. When running in production with a WSGI
    # server such as gunicorn this option will not be set and your application
    # *must* use HTTPS.
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0')