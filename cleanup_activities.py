from config import config
import json
import requests
import datetime
import pandas as pd
from pandas.io.json import json_normalize

def download_all_activities(access_token):
  get_activities_url = 'https://www.strava.com/api/v3/athlete/activities'

  start_date = config['start_date']
  # empty activities file
  open(config['output_file'], "w");
  while(True):
    request_params = {
        'after' : start_date
      }

    r = requests.get(url=get_activities_url, headers={'Authorization': 'access_token ' + access_token}, params=request_params)
    response_json = r.json()

    last_date = response_json[len(response_json)-1]['start_date']
    print 'last date', last_date

    utc_time = datetime.datetime.strptime(last_date, "%Y-%m-%dT%H:%M:%SZ")
    epoch_time = (utc_time - datetime.datetime(1970, 1, 1)).total_seconds()
    last_date = epoch_time

    data = json.dumps(r.json(), indent=4, sort_keys=True)

    with open(config['output_file'], "a") as of:
      of.write(data)

    if len(response_json) < 30:
      break

    start_date = last_date

def cleanup_activities():
  activities_json = load_activities_into_json()
  activities_df = remove_except_run(activities_json)
  activities_df.to_csv(config['running_output_file'])

def load_activities_into_json():
  activities_json = None

  with open(config['output_file']) as af:
    activities_json = json.loads(af.read())

  return activities_json

def remove_except_run(activities_json):

  df = json_normalize(activities_json)
  df = df.loc[df['type'] == 'Run']
  df = df[['average_speed', 'distance', 'moving_time', 'start_date', 'total_elevation_gain', 'start_latitude', 'start_longitude']]

  print 'number of running activities: ', len(df.index)
  return df


# Utility function for search and replace
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

def replace(file_path, pattern, subst):
  #Create temp file
  fh, abs_path = mkstemp()
  with fdopen(fh,'w') as new_file:
    with open(file_path) as old_file:
      for line in old_file:
        new_file.write(line.replace(pattern, subst))
  #Remove original file
  remove(file_path)
  #Move new file
  move(abs_path, file_path)


if __name__ == '__main__':
  cleanup_activities()

