
# Data cleaning for m-score
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import string as st


compustat = pd.read_csv("compustat_1950_2018_annual_merged.csv")
compustat_1 = compustat[["gvkey", "conm" ,"datadate","fyear","sale","cogs","rect","act", \
                         "ppegt","dp","at","xsga","ni","oancf","lct","dltt"]]
compustat_2 = compustat_1.loc[compustat_1["fyear"] > 1987]
compustat_2 = compustat_2.loc[compustat_2['fyear'] < 2018]
com_3 = compustat_2[compustat_2['rect'] >= 0]
com_4 = com_3.dropna(subset = ["sale","cogs","act","ppegt","dp","at","xsga","ni","oancf","lct","dltt","rect"])
com_5 = com_4.fillna(0)

com_5.to_csv('m_score_dataset_final.csv', float_format = '%.6f', index = 0)

# create m score dataframe
def m_score_df():
    df = pd.read_csv('m_score_dataset_final.csv')
    
    # Create prvious year data
    df['pre_sale'] = df.sort_values(['fyear']).groupby('gvkey')['sale'].shift()
    df['pre_cogs'] = df.sort_values(['fyear']).groupby('gvkey')['cogs'].shift()
    df['pre_rect'] = df.sort_values(['fyear']).groupby('gvkey')['rect'].shift()
    df['pre_act'] = df.sort_values(['fyear']).groupby('gvkey')['act'].shift()
    df['pre_ppegt'] = df.sort_values(['fyear']).groupby('gvkey')['ppegt'].shift()
    df['pre_dp'] = df.sort_values(['fyear']).groupby('gvkey')['dp'].shift()
    df['pre_at'] = df.sort_values(['fyear']).groupby('gvkey')['at'].shift()
    df['pre_xsga'] = df.sort_values(['fyear']).groupby('gvkey')['xsga'].shift()
    df['pre_ni'] = df.sort_values(['fyear']).groupby('gvkey')['ni'].shift()
    df['pre_oancf'] = df.sort_values(['fyear']).groupby('gvkey')['oancf'].shift()
    df['pre_lct'] = df.sort_values(['fyear']).groupby('gvkey')['lct'].shift()
    df['pre_dltt'] = df.sort_values(['fyear']).groupby('gvkey')['dltt'].shift()
    
    # Create derived variable
    df['asset_qual'] = (df['at'] - df['act'] - df['ppegt']) / df['at']
    df['pre_asset_qual'] = (df['pre_at'] - df['pre_act'] - df['pre_ppegt']) / df['pre_at']
    
    df['DSRI'] = (df['rect']/df['sale']) / (df['pre_rect'] / df['pre_sale'])
    df['GMI'] =  ((df['pre_sale']-df['pre_cogs'])/df['pre_sale']) / ((df['sale']-df['cogs'])/df['sale'])
    df['AQI'] = df['asset_qual'] / df['pre_asset_qual']
    df['SGI'] = df['sale'] / df['pre_sale']
    df['DEPI'] = (df['pre_dp'] / (df['pre_dp'] + df['pre_ppegt'])) / (df['dp'] / (df['dp'] + df['ppegt']))
    df['SGAI'] = (df['xsga'] / df['sale']) / (df['pre_xsga'] / df['sale'])
    df['TA'] = (df['ni'] - df['oancf']) / df['at']
    df['LVGI'] = ((df['lct'] + df['dltt']) / df['at']) / ((df['pre_lct'] + df['pre_dltt']) / df['pre_at'])
    
    # M-score
    df['M-Score'] = -4.84 + .920 * df['DSRI'] + .528 * df['GMI'] + .404 * df['AQI'] \
                    + .892 * df['SGI'] + .115 * df['DEPI'] - .172 * df['SGAI'] + 4.679 * df['TA'] - .327 * df['LVGI']
    
    return df

# create m-score for specifc company
def m_score_company(company_name):
    company_name = company_name.upper()
    df = m_score_df()
    df1 = df[['gvkey','conm','fyear','M-Score']]
    df2 = df1[df1['conm'].str.contains(company_name)]
    df3 = df2.dropna()
    df3 = df3.reset_index()
    
    return df3

# graph of m-score for specifc company
company_name = 'netflix'

def m_score_trend_graph(company_name):
    df = m_score_company(company_name)
    company_name = df['conm'][0]
    df1 = df[['fyear','M-Score']]
    df1['fyear'] = df1['fyear'].round(1)
    df1 = df1.set_index('fyear')  
    company_name1 = st.capwords(company_name)
    
    fig, ax = plt.subplots(figsize = (13,8))
    ax.plot(df1, 'b^--')
    ax.axhline(y = -1.78, color = 'r', linestyle = '-')
    ax.axhline(y = -2.22, color = 'g', linestyle = '-')
    ax.set_title(company_name1 + ' : M Score across Year', fontsize = 15) 
    plt.show()