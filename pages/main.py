import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div([
    html.H2("Welcome to the San Joaquin Valley Air Quality Index Analysis Project!"),
    html.P("In this project, we worked on analyzing the Air Quality Index (AQI) of San Joaquin Valley and on determining the effectiveness of the ISR Rule 9510."),
    html.H3("What is AQI?"),
    html.P("An AQI is the standard measure of pollution in an air pollutant. There exist 6 common types of unhealthy air pollutants in the air that we breathe daily: "),
    html.Ul([
        html.Li("PM25: particulate matter that is 2.5 micrometers or smaller in diameter; risks: can get deep into lungs and bloodstream due to their tiny size"),
        html.Br(),
        html.Li("PM10: particulate matter that is 10 micrometers or smaller in diameter; risks: can also enter lungs and bloodstream and cause cancers and infections"),
        html.Br(),
        html.Li("CO: carbon monoxide; risks: causes damage to heart, headaches, extremely dangerous for people with heart disease"),
        html.Br(),
        html.Li("SO2: sulfur dioxide; risks: causes serious respiratory illnesses and damages the environment"),
        html.Br(),
        html.Li("NO2: nitrogen dioxide; risks: highly dangerous to respiratory infections, especially in children"),
        html.Br(),
        html.Li("Ozone: ground-level ozone; risks: causes lung irritation and asthma")
    ]),
    html.H3("Why do analysis of AQI?"),
    html.P("Because these pollutants are very unhealthy to humans, the environment, and biodiversity, it is critical to find out if the levels of these pollutants have been decreasing or increasing. With the help of analysis, we can make make better-informed decisions such as introducing and adopting policies that decrease these pollutants."),
    html.H3("Why choose San Joaquin Valley?"),
    html.P("Based on aggregate analysis, our team found out that California is the worst air polluted state in the U.S., and San Joaquin Valley is the worst air polluted region in California. Furthermore, as the U.S. Environmental Protection Agency (EPA) has started to place monitors that record these pollutants starting from 1970, there was enough low-granular data that we could do analyses on."),
    html.H3("What is ISR Rule 9510 and why determine its effectiveness?"),
    html.P("Indirect Source Review (ISR) Rules are local air pollution rules that limit air pollution caused by indirect sources such as building constructions and car traffic. As there are many ISR Rules, we decided to focus on ISR Rule 9510. This rule was adopted in SJV in 2006 and requires new construction projects to limit their air pollution causing to certain boundaries based on the project's scale. By determining the effectiveness of the ISR Rule 9510, we can help governments and organizations to make an informed decision."),
    html.H3("How to interpret an AQI level?"),
    html.Ul([
        html.Li("0 - 50: Good"),
        html.Li("51 - 100: Moderate"),
        html.Li("101 - 150: Unhealthy for Sensitive Groups"),
        html.Li("151 - 200: Unhealthy"),
        html.Li("201 - 300: Very Unhealthy"),
        html.Li("301 - 500: Hazardous")
    ]),
    html.H3("How the data was collected?"),
    html.P("The U.S. EPA installed monitors throughout all counties of San Joaquin Valley (and the entire country), and the monitors record ambient (local) pollutants in terms of micrograms per cubic meter for particulates or parts per million for gases."),
    html.H3("Project Highlights:"),
    html.Img(src="/assets/ISR_9510_Effectiveness_Plot.png", style={"width": "80%"}),
    html.Br(),
    html.Img(src="/assets/LSTM_Model_Visual.png", style={"width": "80%"})
])