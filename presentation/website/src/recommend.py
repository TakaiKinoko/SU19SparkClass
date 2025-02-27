"""
CSCI-GA.3033-001: Big Data Application Development
Team Project Code
Cody Gilbert, Fang Han, Jeremy Lao

Class Usage: 
from recommend import plotTopLenders
plotter = plotTopLenders()
plotter.plot(n) # n is the number of top lenders to be shown

Note: 
The orca executable is required to export figures as static images, as performed in plot().
To install:  $conda install -c plotly plotly-orca

@author: Fang Han
"""
from plotly.subplots import make_subplots
from src.forms import RegistrationForm
import pandas as pd
import numpy as np
import os
import logging
import logging.config
import plotly.offline as offline
import plotly.graph_objects as go


class plotTopLenders(): 
    def __init__(self, df = None):
        # Create logger
        logging.config.fileConfig('src/log/logging.conf')
        self.logger = logging.getLogger('entry.recommend')
        self.logger.info('Instantiating plotTopLenders class')
        
        # Get the predicted data
        self.tmp_jsonPath = os.path.join(os.getcwd(),'src/tmp/tmp.json')
        if df is None:
            self.df = pd.read_json(self.tmp_jsonPath)   
        else: 
            self.df = df
        
    def getLenders(self, top = 3): # static method 
        """
        First transform the dataframe:
        Split the probability column which is an array into two columns, 
        'tag_1' for approve, 'tag_2' for deny, 
        then sort by approve in descending order
        """
        self.logger.info('Creating the top %d lenders' % top)
        tmp = self.df[2].apply(pd.Series)                                                                                                                                                               
        probs = tmp['values'].apply(pd.Series)
        probs = probs.rename(columns = lambda x : 'tag_' + str(x))  
        self.df = pd.concat([self.df[:], probs[:]], axis=1).sort_values(by='tag_1', ascending=False)  
        lenders = self.df[0].unique()
        self.topN = lenders[:top]
        self.logger.debug('Top %d lenders: \n' % top +
                          '%s' % np.array2string(self.topN))
        
    def getYearlyRates(self, top = 3):
        """
        Create a dictionary that maps lender names to their probability each year
        """
        self.logger.info('Creating yearly rates')
        years = range(2007, 2018)
        self.years = []
        self.lendersByYear = dict.fromkeys(self.topN) 
        self.lendersPeak = dict.fromkeys(self.topN) # get the peak historic probability of each lender
        for name in self.topN:
            lenderData = self.df[self.df[0] == name]
            accum = []
            for i in years:
                year = lenderData[lenderData[1] == i]
                accum.append(year['tag_1'].values[0].astype('float'))    
                self.years.append(i)
            self.lendersByYear[name] = accum
            self.lendersPeak[name] = max(accum)

    def plot(self, form, top = 3):
        '''
        Performs the plotting of the predicted data over time,
        and creates the page shown to the user
        '''
        self.logger.info('Plotting probabilities')
        self.getLenders(top)
        self.getYearlyRates(top)
        
        ETHNICITY = {"1":"Hispanic or Latino",
                    "2": "Not Hispanic or Latino"}
        RACE = {"1": "American Indian or Alaska Native",
                "2": "Asian",
                "3": "Black or African American",
                "4": "Native Hawaiian or Other Pacific Islander",
                "5": "White"}
        GENDER = {"1": "Male",
                "2": "Female"}
        STATE = {"01":"AL",
                "02":"AK",
                "04":"AZ",
                "05":"AR",
                "06":"CA",
                "08":"CO",
                "09":"CT",
                "10":"DE",
                "12":"FL",
                "13":"GA",
                "15":"HI",
                "16":"ID",
                "17":"IL",
                "18":"IN",
                "19":"IA",
                "20":"KS",
                "21":"KY",
                "22":"LA",
                "23":"ME",
                "24":"MD",
                "25":"MD",
                "26":"MI",
                "27":"MN",
                "28":"MS",
                "29":"MO",
                "30":"MT",
                "31":"NE",
                "32":"NV",
                "33":"NH",
                "34":"NJ",
                "35":"NM",
                "36":"NY",
                "37":"NC",
                "38":"ND",
                "39":"OH",
                "40":"OK",
                "41":"OR",
                "42":"PA",
                "44":"RI",
                "45":"SC",
                "46":"SD",
                "47":"TN",
                "48":"TX",
                "49":"UT",
                "50":"VT",
                "51":"VA",
                "53":"WA",
                "55":"WI",
                "56":"WY"}

        gender = GENDER[form.gender.data]
        state = STATE[form.state.data]
        loanAmnt = form.loanAmnt.data
        income = form.income.data
        race = RACE[form.race.data]
        ethnicity = ETHNICITY[form.ethnicity.data]

        #UserInfoString = "Gender: {0}{4}Income: {1}{4}Race: {2}{4}Ethnicity: {3}{4} ".format(gender, income, race, ethnicity, "\n")

        # turn lendersPeak into a dataframe                                                                       
        tab_df = pd.DataFrame.from_dict({'Lender': list(self.lendersPeak.keys()), 
                                        'Highest Historic Probability Of Approval':list(self.lendersPeak.values())}) 
        fig = go.Figure()
        ############################ SET UP SUBPLOTS ###########################
        ########################################################################
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            specs=[[{"type": "table"}],
                [{"type": "table"}],
                [{"type": "scatter"}]]
        )
        
        ############################ PLOT TABLE ################################
        ########################################################################
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["User Gender", "State", "User Income", "Loan Amount", "Race", "Ethinicity"],
                    font=dict(size=10),
                    align="center"
                ),
                cells=dict(
                    values=[[gender], [state], [income], [loanAmnt], [race], [ethnicity]],
                    align = "center")
                ),
                row=1, col=1
        )

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["Lender", "Highest <br>Historic Probability<br> Of Approval"],
                    font=dict(size=10),
                    align="center"
                ),
                cells=dict(
                    values=[tab_df[k].tolist() for k in tab_df.columns[0:]],
                    align = "center")
                ),
                row=2, col=1
        )
        
        ############################ SCATTER PLOT ##############################
        ########################################################################        
        for lender in self.lendersByYear.keys():
            fig.add_trace(
                go.Scatter(
                    x = self.years,
                    y = self.lendersByYear[lender],
                    mode="lines+markers+text",
                    name = lender,
                    text=["", "", lender],
                    textposition="middle center", 
                ),
                row = 3, col = 1
            )
        
        fig.update_layout(
            template="plotly_dark",
            height=800,
            showlegend=True,
            title_text="Top Lenders We'd Recommend To You: ",
        )
        # to plot in a separate browser window
        offline.plot(fig,
              filename='src/templates/lenderRecommendations.html', validate=True)

