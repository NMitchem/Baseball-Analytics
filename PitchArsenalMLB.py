# Made by Noah Mitchem for MLB Pitchers
# Vertical pitch breaks seem off, don't know what other data can be used
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import plot
import numpy as np
from matplotlib import cm
from pybaseball import playerid_lookup
from pybaseball import statcast_pitcher
file = statcast_pitcher("2019-03-25","2019-10-01", playerid_lookup("scherzer","max")["key_mlbam"][0])
def colorcode(speed):
    speed1 = int((speed - 50) * 4.3)
    co = np.array(cm.magma(speed1)) * 255
    return "rgb(" + str(int(co[0])) + "," + str(int(co[1])) + "," + str(int(co[2])) + ")"
data = []
data1 = []
pitchTrack = 0
breaks = 0
x = {}
extremes = []
differentPitches = file["pitch_type"].unique().size
totalPitches = file.index.size
color=["rgb(102, 204, 0)","rgb(0, 214, 214)","rgb(204, 0, 0)","rgb(255, 153, 0)","rgb(153, 0, 255)"]
for i in file["pitch_type"].unique():
    x[i] =100 * round(file.set_index("pitch_type").loc[i].index.size/totalPitches, 3)
data = []
x = dict(sorted(x.items(), key=lambda kv: kv[1],reverse = False))
las = ""
check={}
for i in x:
    check[i]=color[pitchTrack]
    ax = go.Bar(
        x= [x[i]],
        y= [i],
        text = [str(round(x[i],1))+"%"],
        width = [.3],
        orientation = "h",
        showlegend=False,
        textposition=['inside'],hoverinfo='skip',
        marker=dict(
        color=color[pitchTrack]))
    pitchTrack+=1
    data1.append(ax)
    las=x[i]
tempMin=1000
tempMax=0
pitchTrack=.5
for i in x:
    breaks += 1
    f = file.set_index("pitch_type").loc[i]["release_speed"].mean()
    f2 = file.set_index("pitch_type").loc[i]["release_speed"].max()
    f3 = file.set_index("pitch_type").loc[i]["release_speed"].min()
    if f3<tempMin:
        tempMin=f3
    if f2>tempMax:
        tempMax=f2
    extremes = [f3,f,f2]
    ranges = (f2-f3)/50
    xLine=np.linspace(f3,f2,num=75)
    yLine=[pitchTrack]*75
    ax = go.Scatter(
    x=xLine,
    y=yLine,
    mode = 'markers',
    hovertemplate="%{x:.1f}",
    showlegend=False,
    name = i,
    marker=dict(
        color=[colorcode(i) for i in xLine],size=15,)
    )
    data.append(ax)
    ax = go.Scatter(
    x=[f],
    y=[pitchTrack],
    mode = 'markers+text',
    hovertemplate="Average: %{x:.1f}",
    name = i,
    showlegend=False,
    text=[str(round(f,1))],
    textposition='top center',
    marker=dict(
        color="rgb(60,0,60)",size=25,symbol="line-ns-open")
    )
    pitchTrack+=1
    data.append(ax)
ranges=np.linspace(tempMin-4,tempMax+4,num=500)
ax = go.Scatter(
    x=ranges,
    y=[0]*500,
    mode = 'markers',
    name = "Scale",
    marker=dict(
        color=[colorcode(i) for i in ranges],size=15,),
    showlegend=False,
    hoverinfo="skip"
    )
data.append(ax)
colors=[]
tempShapes={}
for i in file["pitch_type"].unique():
    f = file.set_index("pitch_type").loc[i]["pfx_z"] * 12
    f2 = file.set_index("pitch_type").loc[i]["pfx_x"] * 12
    tempShapes[i]=[f,f2]
    f.name = i
    ax = go.Scatter(
    mode = "markers",
    x = f2,
    y = f,
    name = i,
    opacity = 0.0,
    hoverinfo="skip",
    showlegend=False
    )
    colors.append(ax)
def shapes(breaks,col):
    V=breaks[0]
    H=breaks[1]
    template={
        'type': 'circle',
        'xref': 'x',
        'yref': 'y',
        'x0': np.percentile(H,10),
        'y0': np.percentile(V,10),
        'x1': np.percentile(H,90),
        'y1': np.percentile(V,90),
        'xref':"x3",
        "yref":"y3",
        'opacity': 0.8,
        'fillcolor': col,
        'line': {
            'color': col,
        }
    }
    return template
ellipse=[shapes(tempShapes[i],check[i]) for i in tempShapes]
layout = go.Layout()
fig = go.Figure(data=data, layout=layout)
fig = tools.make_subplots(rows=1, cols=3,horizontal_spacing=0.001)
for i in data:
    fig.append_trace(i, 1, 2)
for i in data1:
    fig.append_trace(i, 1, 1)
for i in colors:
    fig.append_trace(i,1,3)
fig['layout'].update(shapes=ellipse)
fig['layout']['xaxis1'].update(side= 'top',range=[las+5,0])
fig['layout']['xaxis2'].update(range=[tempMin-3, tempMax+4])
fig['layout']['yaxis2'].update(showticklabels=False,range=[0,differentPitches])
fig['layout']['yaxis3'].update(title="Vertical Break(inches)",dtick=6)
fig['layout']['xaxis3'].update(title="Horizontal Break(inches)",domain= [0.72, 1],dtick=6,)
plot(fig, filename=('Max scherzer Pitch Arsenal.html'))
