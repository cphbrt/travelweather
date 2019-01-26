from darksky import forecast
from datetime import date, timedelta

LOCATION = 35.846621999999996, -86.36526959999999

API_KEY='848314873d786d02ace0c34bfc27c484'

weekday = date.today()
with forecast(API_KEY, *LOCATION) as location:
    print(location.daily.summary, end = '\n---\n')
    for day in location.daily:
        day = dict(day = date.strftime(weekday, '%a'),
                   sum = day.summary,
                   tempMin = day.temperatureMin,
                   tempMax = day.temperatureMax
                   )
        print('{day}: {sum} Temp range: {tempMin} - {tempMax}'.format(**day))
        weekday += timedelta(days=1)