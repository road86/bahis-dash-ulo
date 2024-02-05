from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px


def ReportsSickDead(sub_bahis_sourcedata, dates, periodClick, figheight):

    tmp = sub_bahis_sourcedata["date"].dt.date.value_counts()
    tmp = tmp.to_frame()
    tmp["counts"] = tmp["date"]
    tmp["date"] = pd.to_datetime(tmp.index)

    if periodClick == 3:
        tmp = tmp["counts"].groupby(tmp["date"]).sum().astype(int)
    if periodClick == 2:
        tmp = tmp["counts"].groupby(tmp["date"].dt.to_period("W-SAT")).sum().astype(int)
    if periodClick == 1:
        tmp = tmp["counts"].groupby(tmp["date"].dt.to_period("M")).sum().astype(int)
    tmp = tmp.to_frame()
    tmp["date"] = tmp.index
    tmp["date"] = tmp["date"].astype("datetime64[D]")

    fig = px.bar(tmp, x="date", y="counts", labels={"date": "", "counts": "No. of Reports"})
    fig.update_layout(height=figheight, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_xaxes(
        range=[
            datetime.strptime(dates[0], "%Y-%m-%d") - timedelta(days=6),
            datetime.strptime(dates[1], "%Y-%m-%d") + timedelta(days=6),
        ]
    )
    fig.add_annotation(
        x=datetime.strptime(dates[1], "%Y-%m-%d")
        - timedelta(
            days=int(((datetime.strptime(dates[1], "%Y-%m-%d") - datetime.strptime(dates[0], "%Y-%m-%d")).days) * 0.08)
        ),
        y=max(tmp),
        text="total reports " + str("{:,}".format(sub_bahis_sourcedata["date"].size)),
        showarrow=False,
        font=dict(family="Courier New, monospace", size=12, color="#ffffff"),
        align="center",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8,
    )

    if periodClick == 3:
        tmp = sub_bahis_sourcedata[["sick", "dead"]].groupby(sub_bahis_sourcedata["date"]).sum().astype(int)
    if periodClick == 2:
        tmp = (
            sub_bahis_sourcedata[["sick", "dead"]]
            .groupby(sub_bahis_sourcedata["date"].dt.to_period("W-SAT"))
            .sum()
            .astype(int)
        )
    if periodClick == 1:
        tmp = (
            sub_bahis_sourcedata[["sick", "dead"]]
            .groupby(sub_bahis_sourcedata["date"].dt.to_period("M"))
            .sum()
            .astype(int)
        )

    tmp = tmp.reset_index()
    tmp = tmp.rename(columns={"date": "date"})
    tmp["date"] = tmp["date"].astype("datetime64[D]")
    figSick = px.bar(tmp, x="date", y="sick", labels={"date": "", "sick": "No. of Sick Animals"})
    figSick.update_traces(marker_color="black")
    figSick.update_layout(height=figheight, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    figSick.update_xaxes(
        range=[
            datetime.strptime(dates[0], "%Y-%m-%d") - timedelta(days=6),
            datetime.strptime(dates[1], "%Y-%m-%d") + timedelta(days=6),
        ]
    )  # manual setting should be done better with [start_date,end_date] annotiation is invisible and bar is cut
    figSick.add_annotation(
        x=datetime.strptime(dates[1], "%Y-%m-%d")
        - timedelta(
            days=int(((datetime.strptime(dates[1], "%Y-%m-%d") - datetime.strptime(dates[0], "%Y-%m-%d")).days) * 0.08)
        ),
        y=max(tmp),
        text="total sick " + str("{:,}".format(int(sub_bahis_sourcedata["sick"].sum()))),  # realy outlyer
        showarrow=False,
        font=dict(family="Courier New, monospace", size=12, color="#ffffff"),
        align="center",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8,
    )

    figDead = px.bar(tmp, x="date", y="dead", labels={"date": "", "dead": "No. of Dead Animals"})
    figDead.update_layout(height=figheight, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    figDead.update_traces(marker_color="red")
    figDead.update_xaxes(
        range=[
            datetime.strptime(dates[0], "%Y-%m-%d") - timedelta(days=6),
            datetime.strptime(dates[1], "%Y-%m-%d") + timedelta(days=6),
        ]
    )
    figDead.add_annotation(
        x=datetime.strptime(dates[1], "%Y-%m-%d")
        - timedelta(
            days=int(((datetime.strptime(dates[1], "%Y-%m-%d") - datetime.strptime(dates[0], "%Y-%m-%d")).days) * 0.08)
        ),
        y=max(tmp),
        text="total dead " + str("{:,}".format(int(sub_bahis_sourcedata["dead"].sum()))),  # really
        showarrow=False,
        font=dict(family="Courier New, monospace", size=12, color="#ffffff"),
        align="center",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8,
    )

    return fig, figSick, figDead
