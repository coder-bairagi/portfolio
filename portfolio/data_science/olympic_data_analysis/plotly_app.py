from dash import html, dcc
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from django.templatetags.static import static
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from data_science.olympic_data_analysis import olympic_data_preprocessor as odp

df = odp.get_preprocess_data()
medal_tally_df = odp.extract_medal_tally(df)
years, countries = odp.extract_years_countries(df)

# Creating a DjangoDash application
app = DjangoDash(
    'oda',
    external_stylesheets=[
        static('porfolio/custom.css'),
        dbc.themes.BOOTSTRAP
    ]
)

# Define the layout
app.layout = dbc.Container(fluid=True, children=[
    # First Row
    dbc.Row([
        dbc.Col(
            html.Div([
                dbc.Label("Select an Option", className="fs-6 fw-semibold ps-1"),
                dbc.RadioItems(
                id="select-from-radio",
                options=[
                    {"label": "Medal Tally", "value": "Medal Tally"},
                    {"label": "Overall Analysis", "value": "Overall Analysis"},
                    {"label": "Country-wise Analysis", "value": "Country-wise Analysis"},
                    {"label": "Athlete-wise Analysis", "value": "Athlete-wise Analysis"},
                ],
                value="Medal Tally",
                className="fs-6 fw-normal ps-3"
                ),
                dbc.Label("Select Year", className="fs-6 fw-semibold pt-3 pb-1 ps-1"),
                dbc.Select(
                    id="select-from-years",
                    options=years,
                    value="Overall",
                    className="fs-6 fw-medium py-3 ps-3"
                ),
                dbc.Label("Select Countries", className="fs-6 fw-semibold pt-3 pb-1 ps-1"),
                dbc.Select(
                    id="select-from-countries",
                    options=countries,
                    value="Overall",
                    className="fs-6 fw-medium py-3 ps-3"
                ),
            ], className="p-5"),
            width=3
        ),
        dbc.Col(
            [
                html.Div(
                    [
                        html.Img(src=static("img/olympic-logo.png"), className="pt-3", style={"width": "130px"}),
                        html.H3("Olympic Dash", className="mb-0 ps-2")
                    ],
                className="d-flex align-items-center my-1 ps-4",
                ),
                dcc.Loading(
                    id="loading-spinner",
                    type="default",
                    style={'position': 'absolute', 'top': '100px'},
                    children=[html.Div(
                        # Placeholder for table and graphs
                        id="render-output",
                        className="pb-4 pt-2 ps-4 pe-5"
                    )]
                ),
            ],
            width=9
        )
    ]),
])

# Callback decorators and functions
# Callback to disable/enable year selectbox on selection of radio value
@app.callback(
        [
            Output(component_id="select-from-countries", component_property="disabled"),
            Output(component_id="select-from-years", component_property="disabled"),
        ],
        Input(component_id="select-from-radio", component_property="value")
)

def toogle_year_dropdown(analysis_type):
    if analysis_type == "Medal Tally":
        return False, False
    elif analysis_type == "Overall Analysis":
        return True, True
    elif analysis_type == "Country-wise Analysis":
        return False, True
    return True, True

@app.callback(
    Output(component_id="render-output", component_property="children"),
    [
        Input(component_id="select-from-radio", component_property="value"),
        Input(component_id="select-from-years", component_property="value"),
        Input(component_id="select-from-countries", component_property="value"),
    ]
)

def render_table(analysis_type, selected_year, selected_country):
    # Graph configuration dict
    config = {
        'displaylogo': False,
    }
    # for medal tally
    if analysis_type == "Medal Tally":
        temp_df = odp.extract_medal_tally(df, selected_year, selected_country)
        heading = ""
        if selected_year == "Overall" and selected_country == "Overall":
            heading = "Medal Distribution for All Countries and Years"
        elif selected_year == "Overall" and selected_country != "Overall":
            from_year = str(temp_df['Year'].min())
            to_year = str(temp_df['Year'].max())
            heading = "Medal Distribution for " + selected_country + " from " + from_year + " to " + to_year
        elif selected_year != "Overall" and selected_country == "Overall":
            heading = "Medal Distribution for All Countries in " + selected_year
        if selected_year != "Overall" and selected_country != "Overall":
            heading = "Medal Distribution for " + selected_country + " in " + selected_year
        content = [
            html.H5(heading, className="mb-3"),
            dbc.Table.from_dataframe(temp_df, striped=True, bordered=True, hover=True),
        ]
        return html.Div((content))
    # for overall analysis
    elif analysis_type == "Overall Analysis":
        top_stats = odp.extract_top_stats(df)
        # Graph of participating nations over the years
        region_over_yrs = odp.get_data_over_yrs(df, "Region")
        region_over_yrs_fig = px.line(region_over_yrs, x="Edition", y="Number of Region")
        # Graph of events over the years
        event_over_yrs = odp.get_data_over_yrs(df, "Event")
        event_over_yrs_fig = px.line(event_over_yrs, x="Edition", y="Number of Event")
        # Graph of athletes over the years
        athlete_over_yrs = odp.get_data_over_yrs(df, "Name")
        athlete_over_yrs_fig = px.line(athlete_over_yrs, x='Edition', y='Number of Name')
        athlete_over_yrs_fig.update_layout(
            yaxis_title='Number of Athlete'
        )
        # Graph of athletes over the years
        yr_sport_event_heatmap = odp.get_heatmap_data(df)
        yr_sport_event_heatmap_fig = px.imshow(yr_sport_event_heatmap, text_auto=True, width=900, height=900)
        yr_sport_event_heatmap_fig.update_layout(xaxis = dict(
            tickmode='array',
            tickvals=yr_sport_event_heatmap.columns,
            ticktext=[str(year) for year in yr_sport_event_heatmap.columns],
            tickangle=-90
        ))
        return html.Div([
            html.H4("Top Statistics", className="mb-3"),
            dbc.Row([
                dbc.Row([
                    dbc.Col([html.P("Editions", className="mb-1 fw-normal fs-5"), html.P(top_stats["edition"], className="fs-4 fw-semibold")], width=4),
                    dbc.Col([html.P("Hosts", className="mb-1 fw-normal fs-5"), html.P(top_stats["host"], className="fs-4 fw-semibold")], width=4),
                    dbc.Col([html.P("Sports", className="mb-1 fw-normal fs-5"), html.P(top_stats["sport"], className="fs-4 fw-semibold")], width=4),
                ]),
                dbc.Row([
                    dbc.Col([html.P("Events", className="mb-1 fw-normal fs-5"), html.P(top_stats["event"], className="fs-4 fw-semibold")], width=4),
                    dbc.Col([html.P("Nations", className="mb-1 fw-normal fs-5"), html.P(top_stats["nation"], className="fs-4 fw-semibold")], width=4),
                    dbc.Col([html.P("Athletes", className="mb-1 fw-normal fs-5"), html.P(top_stats["athlete"], className="fs-4 fw-semibold")], width=4),
                ]),
            ]),
            html.H4("Participating Nations over the Years", className="mt-3"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=region_over_yrs_fig, config=config)], width=12),
            ]),
            html.H4("Events over the Years", className="mt-3"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=event_over_yrs_fig, config=config)], width=12),
            ]),
            html.H4("Athletes over the Years", className="mt-3"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=athlete_over_yrs_fig, config=config)], width=12),
            ]),
            html.H4("Distribution of Events over the Years in Each Sport", className="mt-3"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=yr_sport_event_heatmap_fig, config=config)], width=12),
            ]),
        ])
    # for country-wise analysis
    elif analysis_type == "Country-wise Analysis":
        if selected_country == "Overall":
            return html.Div([
                dbc.Alert("Please Select a Country to View Country-wise Analysis", color="warning", className="mt-3"),
            ])
        else:
            medal_over_yrs = odp.get_medal_over_yrs(df, selected_country)
            medal_over_yrs_fig = px.line(medal_over_yrs, x='Year', y='Medal')
            medal_heatmap = odp.get_medal_heatmap_data(df, selected_country)
            medal_heatmap_fig = px.imshow(medal_heatmap, x=medal_heatmap.columns, y=medal_heatmap.index, text_auto=True, width=900, height=900,   aspect='auto')
            medal_heatmap_fig.update_layout(xaxis = dict(
                tickmode='array',
                tickvals=medal_heatmap.columns,
                ticktext=[str(year) for year in medal_heatmap.columns],
                tickangle=-90
            ))
            most_successful_table = odp.get_most_successful(df, selected_country)
            return html.Div([
                html.H4("Medals over Years for " + selected_country, className="mt-3"),
                dbc.Row([
                    dbc.Col([dcc.Graph(figure=medal_over_yrs_fig, config=config)], width=12),
                ]),
                html.H4("Medals over Years in Each Sport for " + selected_country, className="mt-3"),
                dbc.Row([
                    dbc.Col([dcc.Graph(figure=medal_heatmap_fig, config=config)], width=12),
                ]),
                html.H4("Top 10 Successful Athletes of " + selected_country, className="mt-3 mb-4"),
                dbc.Row([
                    dbc.Col([dbc.Table.from_dataframe(most_successful_table, striped=True, bordered=True, hover=True)], width=12),
                ]),
            ])
    # for athlete-wise analysis
    else:
        winner_df = odp.get_winner_df(df)
        age_probdist = odp.get_age_probdist(winner_df)
        age_probdist_fig = ff.create_distplot(age_probdist[0], age_probdist[1], show_rug=False, show_hist=False, colors=['#FFD700', '#C0C0C0', '#CD7F32'])
        age_probdist_fig.update_layout(width=900, height=600, legend_title_text='Medal')
        age_probdist_fig.update_xaxes(title_text='Age')
        age_sport_probdist = odp.age_sport_probdist(winner_df)
        age_sport_probdist_fig = ff.create_distplot(age_sport_probdist['winners_age'], age_sport_probdist['sports_list'], show_rug=False, show_hist=False)
        age_sport_probdist_fig.update_layout(width=900, height=600, legend_title_text='Sport')
        age_sport_probdist_fig.update_xaxes(title_text='Age')
        height_weight_relation = odp.fill_height_weight(winner_df)
        height_weight_relation_fig = px.scatter(height_weight_relation, x='Weight', y='Height', color='Medal', symbol='Sex')
        height_weight_relation_fig = go.Figure(height_weight_relation_fig)
        for trace in height_weight_relation_fig.data:
            if trace.name.endswith('F'):
                trace.update(marker=dict(symbol='x', size=8))
            else:
                trace.update(marker=dict(symbol='circle', size=5))
        height_weight_relation_fig.update_layout(width=900, height=600)
        male_vs_female = odp.get_male_female(df)
        male_vs_female_fig = px.line(male_vs_female, x='Year', y=['Female', 'Male'], labels={'value': 'Number of Participants', 'variable': 'Sex'}, color_discrete_sequence=['#FF0000', '#0000FF'])
        male_vs_female_fig.update_layout(width=900, height=600)
        return html.Div([
            html.H4("Probability Distribution of Age", className="mt-3 mb-0"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=age_probdist_fig, config=config)], width=12),
            ]),
            html.H4("Age Distribution of Gold Medal Winners wrt Sport", className="mt-3 mb-0"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=age_sport_probdist_fig, config=config)], width=12),
            ]),
            html.H4("Height and Weight Distribution of Medal Winners by Medal Type and Sex", className="mt-3 mb-0"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=height_weight_relation_fig, config=config)], width=12),
            ]),
            html.H4("Men vs Women Participation over the Years", className="mt-3 mb-0"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=male_vs_female_fig, config=config)], width=12),
            ]),
        ])