from flask import Flask, render_template, redirect, request, url_for, session
from analyse_activities import analyse_activities
from cleanup_activities import download_all_activities, cleanup_activities, replace

import requests
import fileinput
from config import config
import json
import urllib

app = Flask(__name__, static_url_path='')
app.secret_key = 'SECRET'

@app.route('/')
@app.route('/index')
def index():
  #show_analysis = request.args.get('plot')
  plot = ''
  plot_text = ''
  button_link = ''
  button_label = ''
  if 'plot' in session:
    button_label = 'Clear analysis'
    button_link = '/clear'
    plot = session['plot']
    plot_text = session['plot_text']
  else:
    button_label = 'Connect with Strava.'
    button_link = '/download'
  return render_template('index.html', title='Pace predictor', button_link=button_link, button_label=button_label, plot=plot, plot_text=plot_text)

@app.route('/clear')
def clear():
  session.clear()
  return redirect('/')

@app.route('/download')
def download():
  session.clear()
  request_params = {
      'client_id' : config['client_id'],
      'redirect_uri' : config['redirect_uri'],
      'response_type' : 'code'
    }

  return redirect(config['oauth_url']+'?'+urllib.urlencode(request_params))

@app.route('/code')
def oauth_code():
  auth_code = request.args.get('code')
  request_params = {
      'client_id' : config['client_id'],
      'client_secret' : config['client_secret'],
      'code' : auth_code
    }

  r = requests.post(url=config['oauth_token'], params=request_params)
  access_token = r.json()['access_token']
  # save access token to file
  with open('access_token', 'w') as atf:
    atf.write(access_token)

  ## DOWNLOAD AND CLEANUP ACTIVITIES
  # download all activities
  download_all_activities(access_token)
  # replace '][' with ','
  replace(config['output_file'], '][', ',')
  # cleanup activities
  cleanup_activities()
  # analyse activities
  plot, plot_text = analyse_activities()

  session['plot'] = plot
  session['plot_text'] = plot_text

  print plot_text

  # redirect back to home page
  return redirect(url_for('index'))


@app.route('/analyse', methods=['POST'])
def analyse():
  return analyse_activities()



