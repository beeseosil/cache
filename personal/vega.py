import altair as alt
from vega_datasets import data

alt.data_transformers.disable_max_rows()

data=data.birdstrikes()

data=data.assign(
	date=pd.to_datetime(
		data.Flight_Date.apply(lambda q: q[:q.index(' ')].strip())
	).astype('datetime64[ns]')
)

data['day']=data.date.dt.weekday
data['year']=data.date.dt.year

alt.Chart(data).mark_point().encode(
	alt.X('date',type='temporal').title('Spot'),
	alt.Y('Speed_IAS_in_knots').title('IAS'),
	alt.Color('day',type='nominal')
).save('o:/chart.html')
