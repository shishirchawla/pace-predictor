from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from config import config
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly

def analyse_activities():
  df = pd.read_csv(config['running_output_file'], parse_dates=['start_date'])

  start_date = df.iloc[0].start_date

  today = datetime.now()
  today_month = today.month
  today_year = today.year

  last_month = start_date.month
  last_year = start_date.year
  lastlast = last_year
  lastlastm = last_month

  fast_speeds = list()
  xaxis_labels = list()
  while(True):
    if last_year == today_year and last_month == today_month+1:
      break

    # generate clusters for each month
    #mask = (df['start_date'].dt.month == last_month) & (df['start_date'].dt.year == last_year)
    mask = (df['start_date'].dt.month <= last_month) & (df['start_date'].dt.year <= last_year)
    masked_df = df.loc[mask]
    #masked_df['day'] = masked_df['start_date'].dt.day

    masked_df = masked_df[[
        #'day',
        'average_speed',
        'distance'
      ]]

    masked_np = masked_df.as_matrix()

    ## NEW
    # fit a gaus
    masked_np_fit = masked_np[:, 0].reshape(masked_np.shape[0], 1)
    mean = masked_np[0, 0]
    variance = 0.0
    # estimate a gaus if number of points in the array are greater than 1
    if len(masked_np_fit) > 1:
      gmm = GaussianMixture(1)
      gmm.fit(masked_np_fit)

      mean = gmm.means_.flatten()[0]
      variance = gmm.covariances_.flatten()[0]


    # select all values that are greater than or equal to one standard
    # deviaiton away
    new_data_point = masked_df[masked_df['average_speed'] >= mean+variance]['average_speed'].median()
    # convert m per second to min per km
    new_data_point = ((1/new_data_point)*1000)/60
    fast_speeds.append(new_data_point)

    ## END

    ''' # kmeans
    # create 3 clusters (slow, medium, fast) for each month
    clusters = 3
    if len(masked_df.index) < 3:
      clusters = len(masked_df.index)

    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(masked_np[:, 1:2])
    y_kmeans = kmeans.predict(masked_np[:, 1:2])

    print masked_np[0:10]


    # FIXME Remove the following two lines
    #plt.scatter(masked_np[:, 0], masked_np[:, 2], c=y_kmeans, s=50, cmap='viridis')
    #plt.plot(masked_np[:, 0], masked_np[:, 4])


    centers = kmeans.cluster_centers_

    # add fast speed centroid for the month
    fast_speeds.append([str(last_month)+'/'+str(last_year), np.max(centers)])

    # FIXME Remove the following two lines
    #plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.7)
    #plt.plot(centers[:, 0], centers[:, 1], linewidth=2)
    #plt.show()
    '''

    #break
    xaxis_labels.append(str(last_month)+'/'+str(last_year))

    if last_month == 12:
      last_year += 1
      last_month = 1
    else:
      last_month = last_month+1

  ''' # kmeans
  fast_speeds_np = np.array([np.array(xi) for xi in fast_speeds])
  print fast_speeds_np
  plt.scatter(np.arange(len(fast_speeds)), fast_speeds_np[:, 1], c='black', s=50, alpha=0.7)
  #plt.plot(centers[:, 0], centers[:, 1], linewidth=2)

  plt.xticks(np.arange(len(fast_speeds)), fast_speeds_np[:, 0], rotation=65)

  plt.savefig('static/analysis.png')
  '''

  fig = {
    'data': [{
        'x': xaxis_labels,
        #'y': fast_speeds_np[:, 1],
        'y': fast_speeds,
        'mode': 'lines+markers',
        #'marker': {'color': 'rgb(23, 123, 181)'},
        'marker': {'color': 'rgb(244, 26, 14)'},
        'line':{'shape':'spline','color':'rgb(212, 211, 217)'}
    }],
    'layout': {
        'xaxis': {'title': 'Timeline'},
        'yaxis': {'title': 'Pace (min/km)',
          'autorange':'reversed',
          'tickfont' : {
              'color':'rgb(0, 0, 0)'
          },
          'titlefont' : {
              'color':'rgb(0, 0, 0)'
          },
          'hoverformat': '.2f'
        },
        'hoverlabel': {
          'bgcolor': 'black',
          'font': {'color': 'rgb(244, 26, 14)'}
        }
    }
  }

  prediction_model = np.poly1d(np.polyfit(np.arange(len(fast_speeds)),fast_speeds,3))
  predicted_pace = prediction_model(len(fast_speeds))

  race_pace = '<em>' + str(int(predicted_pace)) + ':' + str(int((predicted_pace-int(predicted_pace))*60)) + ' min/km</em>'

  plot_text = 'Your predicted race pace is ' + race_pace
  plot = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

  return plot, plot_text


if __name__ == '__main__':
  analyse_activities()

