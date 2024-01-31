import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html, State

import pandas as pd
import json
from datetime import date
from dash.dash import no_update
import ReportsSickDead
import plotly.express as px
import glob
import os

import numpy as np
from datetime import datetime

app = Dash(
    __name__,
    # use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
)

dash.register_page(__name__,)  # register page to main dash app
pd.options.mode.chained_assignment = None


def get_pathnames(sourcepath):
    # 1 Nation # reminder: found shapefiles from the data.humdata.org

    geofilename = glob.glob(sourcepath + "newbahis_geo_cluster*.csv")[
        -1
    ]  # the available geodata from the bahis project (Masterdata)
    dgfilename = os.path.join(sourcepath, "Diseaselist.csv")  # disease grouping info (Masterdata)
    sourcefilename = os.path.join(
        sourcepath, "preped_data2.csv"
    )  # main data resource of prepared data from old and new bahis
    farmdatafilename = glob.glob(
        sourcepath + "bahis_farm_assessment_p2_table*.csv"
    )[-1]

    path1 = os.path.join(sourcepath, "processed_geodata", "divdata.geojson")  # 8 Division
    path2 = os.path.join(sourcepath, "processed_geodata", "distdata.geojson")  # 64 District
    path3 = os.path.join(sourcepath, "processed_geodata", "upadata.geojson")  # 495 Upazila
    return geofilename, dgfilename, sourcefilename, farmdatafilename, path1, path2, path3


def fetchsourcedata(sourcefilename):  # fetch and prepare source data
    bahis_data = pd.read_csv(sourcefilename)
    bahis_data["from_static_bahis"] = bahis_data["basic_info_date"].str.contains(
        "/"
    )  # new data contains -, old data contains /
    bahis_data["basic_info_date"] = pd.to_datetime(bahis_data["basic_info_date"], errors="coerce")
    del bahis_data["Unnamed: 0"]
    bahis_data = bahis_data.rename(
        columns={
            "basic_info_date": "date",
            "basic_info_division": "division",
            "basic_info_district": "district",
            "basic_info_upazila": "upazila",
            "patient_info_species": "species_no",
            "diagnosis_treatment_tentative_diagnosis": "tentative_diagnosis",
            "patient_info_sick_number": "sick",
            "patient_info_dead_number": "dead",
        }
    )
    # assuming non negative values from division, district, upazila, speciesno, sick and dead
    bahis_data[["division", "district", "species_no"]] = bahis_data[["division", "district", "species_no"]].astype(
        np.uint16
    )
    bahis_data[["upazila", "sick", "dead"]] = bahis_data[["upazila", "sick", "dead"]].astype(
        np.int32
    )  # converting into uint makes odd values)
    #    bahis_data[['species', 'tentative_diagnosis', 'top_diagnosis']]=bahis_data[['species',
    #                                                                                'tentative_diagnosis',
    #                                                                                'top_diagnosis']].astype(str)
    # can you change object to string and does it make a memory difference`?
    bahis_data["dead"] = bahis_data["dead"].clip(lower=0)
    bahis_data = bahis_data[bahis_data['date'] >= datetime(2019, 7, 1)]
    # limit to static bahis start
    return bahis_data


def fetchgeodata(geofilename):  # fetch geodata from bahis, delete mouzas and unions
    geodata = pd.read_csv(geofilename)
    geodata = geodata.drop(
        geodata[(geodata["loc_type"] == 4) | (geodata["loc_type"] == 5)].index
    )  # drop mouzas and unions
    geodata = geodata.drop(["id", "longitude", "latitude", "updated_at"], axis=1)
    geodata["parent"] = geodata[["parent"]].astype(np.uint16)  # assuming no mouza and union is taken into
    geodata[["value"]] = geodata[["value"]].astype(np.uint32)
    geodata[["loc_type"]] = geodata[["loc_type"]].astype(np.uint8)
    return geodata


def created_date(sourcefilename):
    create_time = os.path.getmtime(sourcefilename)
    created_date = datetime.fromtimestamp(create_time).date()
    return created_date


def fetchdisgroupdata(dgfilename):  # fetch and prepare disease groups
    bahis_dgdata = pd.read_csv(dgfilename)
    # bahis_dgdata= bahis_dgdata[['species', 'name', 'id', 'Disease type']]
    # remark what might be helpful: reminder: memory size
    bahis_dgdata = bahis_dgdata[["name", "Disease type"]]
    bahis_dgdata = bahis_dgdata.dropna()
    # bahis_dgdata[['name', 'Disease type']] = str(bahis_dgdata[['name', 'Disease type']])
    # can you change object to string and does it make a memory difference?
    bahis_dgdata = bahis_dgdata.drop_duplicates(subset="name", keep="first")
    bahis_distype = bahis_dgdata.drop_duplicates(subset="Disease type", keep="first")
    return bahis_dgdata, bahis_distype


def fetchDiseaselist(bahis_data):
    dislis = bahis_data["top_diagnosis"].unique()
    dislis = pd.DataFrame(dislis, columns=["Disease"])
    dislis = dislis["Disease"].sort_values().tolist()
    dislis.insert(0, "All Diseases")
    return dislis


def date_subset(dates, bahis_data):
    tmask = (bahis_data["date"] >= pd.to_datetime(dates[0])) & (bahis_data["date"] <= pd.to_datetime(dates[1]))
    return bahis_data.loc[tmask]


def disease_subset(cDisease, sub_bahis_sourcedata):
    if "All Diseases" in cDisease:
        sub_bahis_sourcedata = sub_bahis_sourcedata
    else:
        sub_bahis_sourcedata = sub_bahis_sourcedata[sub_bahis_sourcedata["top_diagnosis"] == cDisease]
    return sub_bahis_sourcedata


sourcepath = "exported_data/"           # called also in Top10, make global or settings parameter
geofilename, dgfilename, sourcefilename, farmdatafilename, path1, path2, path3 = get_pathnames(sourcepath)
bahis_data = fetchsourcedata(sourcefilename)
[bahis_dgdata, bahis_distypes] = fetchdisgroupdata(dgfilename)
bahis_geodata = fetchgeodata(geofilename)
img_logo = "assets/Logo.png"
created_dated = created_date(sourcefilename)  # implement here


ULOsub_bahis_sourcedata = bahis_data
ULOstart_date = date(2019, 1, 1)
ULOlast_date = max(bahis_data['date']).date()
ULOdates = [ULOstart_date, ULOlast_date]
ULOcreated_date = created_date(sourcefilename)

ULOddDList = []

# bahis_geodata = fetchgeodata(geofilename)
subDist = bahis_geodata


def yearlyComp(bahis_data, diseaselist):
    monthly = bahis_data.groupby(
        [bahis_data["date"].dt.year.rename("Year"), bahis_data["date"].dt.month.rename("Month")]
    )["date"].agg({"count"})
    monthly = monthly.rename({"count": "reports"}, axis=1)
    monthly = monthly.reset_index()
    monthly['reports'] = monthly['reports'] / 1000
    monthly["Year"] = monthly["Year"].astype(str)
    figYearlyComp = px.bar(
        data_frame=monthly,
        x="Month",
        y="reports",
        labels={"reports": "Reports in Thousands"},
        color="Year",
        barmode="group",
    )
    figYearlyComp.update_xaxes(dtick="M1")  # , tickformat="%B \n%Y")
    figYearlyComp.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            ticktext=['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'],
            title=""
        ),
        title={
            'text': "Disease dynamics for \"" + str(diseaselist) + "\"",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    return figYearlyComp


def open_data(path):
    with open(path) as f:
        data = json.load(f)
    return data


def decode(pathname):
    ULONo = ""
    for x in range(0, 12):
        ULONo = ULONo + str(int(ord(pathname[x])) - 66)
    return int(int(ULONo) / 42)


# ULOSelUpa = 201539 = 000.008.464.638 = JJJ JJH DFD FCH
# BBB BBJ FHF HEJ in decimal 66 66 66  66 66 74  70 72 70  72 69 74
# minus 66 gives 000 008 464 638 
# divide by 42 gives 201539

# 201539 multiply by 42
# take each character and add 66
# take decimal number to character



def layout(upazilano):
    ULOSelUpa = int(upazilano)
    Upazila = str(bahis_geodata[bahis_geodata["value"] == ULOSelUpa]['name'].iloc[0].capitalize())
    return html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div([
            dbc.Row(
                [
                    dbc.Col(
                        html.Label("BAHIS dashboard", style={"font-weight": "bold",
                                                             "font-size": "200%"}),
                        width=5,
                    ),
                    dbc.Col(
                        html.Img(src=img_logo, height="30px"),
                        width=3,
                        # align='right'
                    )
                ],
                justify="end",
                align="center"
            )
        ]),
        html.Br(),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col([
                                                dbc.Row(html.Label(Upazila, style={"font-weight":
                                                                                   "bold", "font-size": "150%"})),
                                                dbc.Row(html.Label(ULOSelUpa, id="upazilano", hidden=True))]
                                            ),
                                            dbc.Col([
                                                    dcc.Dropdown(
                                                        ULOddDList,
                                                        "All Diseases",
                                                        id="ULODiseaselist",
                                                        multi=False,
                                                        clearable=False,
                                                    )]
                                                    ),
                                            dbc.Col(
                                                dcc.DatePickerRange(
                                                    id="ULOdaterange",
                                                    min_date_allowed=ULOstart_date,
                                                    start_date=date(2023, 1, 1),
                                                    max_date_allowed=ULOcreated_date,
                                                    end_date=ULOlast_date,  # date(2023, 12, 31)
                                                ),
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    dcc.Graph(id="ULOfigMonthly"),
                                ]
                            )
                        )
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            [
                                                                                dbc.Row(dcc.Graph
                                                                                        (id="ULOReportsLA")),
                                                                                dbc.Row(dcc.Graph
                                                                                        (id="ULOSickLA")),
                                                                                dbc.Row(dcc.Graph
                                                                                        (id="ULODeadLA")),
                                                                            ]
                                                                        ),
                                                                        dbc.Col(
                                                                            [
                                                                                dcc.Slider(
                                                                                    min=1,
                                                                                    max=3,
                                                                                    step=1,
                                                                                    marks={1: 'Reports monthly',
                                                                                           2: 'Reports weekly',
                                                                                           3: 'Reports daily',
                                                                                           },
                                                                                    value=2,
                                                                                    vertical=True,
                                                                                    id="ULOLAperiodSlider"
                                                                                )
                                                                            ],
                                                                            width=1,
                                                                        ),
                                                                    ]
                                                                )
                                                            ],
                                                        )
                                                    )
                                                ],
                                                label="Large Animal Reports",
                                                tab_id="ULOReportsLATab",
                                            ),
                                            dbc.Tab(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                dbc.Row([
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Row(dcc.Graph(id="ULOReportsP")),
                                                                            dbc.Row(dcc.Graph(id="ULOSickP")),
                                                                            dbc.Row(dcc.Graph(id="ULODeadP")),
                                                                        ]
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Slider(
                                                                                min=1,
                                                                                max=3,
                                                                                step=1,
                                                                                marks={1: 'Reports monthly',
                                                                                       2: 'Reports weekly',
                                                                                       3: 'Reports daily',
                                                                                       },
                                                                                value=2,
                                                                                vertical=True,
                                                                                id="ULOPperiodSlider"
                                                                            )
                                                                        ],
                                                                        width=1,
                                                                    ),
                                                                ])
                                                            ],
                                                        )
                                                    )

                                                ],
                                                label="Poultry Reports",
                                                tab_id="ULOReportsPTab",
                                            ),
                                        ],
                                        id="ULOtabs",
                                    )
                                ]
                            ),
                        ),
                    ],
                    width=6,
                ),
            ]),
        html.Br(),
        html.Div(id="dummy"),
        html.Label('Data from ' + str(created_dated), style={'text-align': 'right'}),
    ])


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="dummy"),
    html.Div(id="layout")
])

firstrun = True


@app.callback(
    Output("layout", "children"),
    Input("dummy", "id"),
    State("url", "pathname"))
def display_page(dummy, pathname):
    
    return layout(decode(pathname[1:]))


@app.callback(
    # dash cleintsied callback with js
    Output("ULODiseaselist", "options"),
    Output("ULOReportsLA", "figure"),
    Output("ULOSickLA", "figure"),
    Output("ULODeadLA", "figure"),
    Output("ULOReportsP", "figure"),
    Output("ULOSickP", "figure"),
    Output("ULODeadP", "figure"),
    Output("ULOfigMonthly", "figure"),
    Input("ULOdaterange", "start_date"),  # make state to prevent upate before submitting
    Input("ULOdaterange", "end_date"),  # make state to prevent upate before submitting
    Input("ULOLAperiodSlider", "value"),
    Input("ULOPperiodSlider", "value"),
    Input("ULODiseaselist", "value"),
    Input("ULOtabs", "active_tab"),
    State("url", "pathname")
)
def update_whatever(
    ULOstart_date,
    ULOend_date,
    ULOLAperiodClick,
    ULOPperiodClick,
    ULOdiseaselist,
    ULOtabs,
    ULOSelUpa,
):
    ULOSelUpa = decode(ULOSelUpa[1:])  # int(int(ULOSelUpa[1:]) / 42)
    global firstrun, \
        ULOddDList, \
        ULOpath, \
        ULOvariab, \
        ULOsubDistM, \
        ULOtitle, \
        ULOsub_bahis_sourcedata, \
        ULOsubDist

    if firstrun is True:  # inital settings
        ULOddDList = fetchDiseaselist(ULOsub_bahis_sourcedata)
        firstrun = False

    ULOsubDist = bahis_geodata.loc[bahis_geodata["value"].astype("string").str.startswith(str(ULOSelUpa))]
    ULOsub_bahis_sourcedata = bahis_data.loc[bahis_data["upazila"] == ULOSelUpa]
    ULOsub_bahis_sourcedata4yc = disease_subset(ULOdiseaselist, ULOsub_bahis_sourcedata)

    ULOdates = [ULOstart_date, ULOend_date]
    ULOsub_bahis_sourcedata = date_subset(ULOdates, ULOsub_bahis_sourcedata)
    ULOsub_bahis_sourcedata = disease_subset(ULOdiseaselist, ULOsub_bahis_sourcedata)

    ULOfigMonthly = yearlyComp(ULOsub_bahis_sourcedata4yc, ULOdiseaselist)

    if ULOtabs == "ULOReportsLATab":
        lanimal = ["Buffalo", "Cattle", "Goat", "Sheep"]
        ULOsub_bahis_sourcedataLA = ULOsub_bahis_sourcedata[ULOsub_bahis_sourcedata["species"].isin(lanimal)]
        ULOfigheight = 175
        ULOfiggLAR, ULOfiggLASick, ULOfiggLADead = ReportsSickDead.ReportsSickDead(ULOsub_bahis_sourcedataLA,
                                                                                   ULOdates, ULOLAperiodClick,
                                                                                   ULOfigheight)
        return (
            ULOddDList,
            ULOfiggLAR,
            ULOfiggLASick,
            ULOfiggLADead,
            no_update,
            no_update,
            no_update,
            ULOfigMonthly,
        )

    if ULOtabs == "ULOReportsPTab":
        poultry = ["Chicken", "Duck", "Goose", "Pegion", "Quail", "Turkey"]
        ULOsub_bahis_sourcedataP = ULOsub_bahis_sourcedata[ULOsub_bahis_sourcedata["species"].isin(poultry)]
        ULOfigheight = 175
        ULOfiggPR, ULOfiggPSick, ULOfiggPDead = ReportsSickDead.ReportsSickDead(ULOsub_bahis_sourcedataP, ULOdates,
                                                                                ULOPperiodClick, ULOfigheight)
        return (
            ULOddDList,
            no_update,
            no_update,
            no_update,
            ULOfiggPR,
            ULOfiggPSick,
            ULOfiggPDead,
            ULOfigMonthly,
        )


# Run the app on localhost:80
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)  # maybe debug false to prevent second loading
else:
    server = app.server
