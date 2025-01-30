import pandas as pd
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from enum import Enum
from pathlib import Path
import statsmodels.api as sm
import statsmodels.formula.api as smf
import linearmodels as lm
from linearmodels.panel import compare
import pyarrow
import geopandas as gpd
from linearmodels import PanelOLS

DATAPATH = Path(__file__).parent.parent.parent.absolute().resolve()

class user_input(Enum):
    data_folder = "E:\P_Data_Import\Data_Import\Output"
    data_file_name = "\\armington_data"

class data_selection(Enum):
    year_min = 1990
    year_max = 2022
    countries_origin = 'USA'
    item_subset = '1876' # 1876.0 for Paper and Paperboard; 1865.0 for Industrial Roundwood
    color_set = 'Blues' #'Purples', 'Blues', 'Reds', 'Oranges', 'OrRd'
    color_special = 'coral'#'#fef0c1'

def read_data(folder: str = user_input.data_folder.value,
              file_name: str = user_input.data_file_name.value):
    data = pd.read_parquet(str(folder + file_name + ".parquet"))
    return data

def scatter_plot(data: pd.DataFrame, x: str, y: str):
    ax = data.plot.scatter(x=x,
                           y=y)
    plt.show()

def results_summary_to_dataframe(results):
    '''take the result of an statsmodel results table and transforms it into a dataframe'''
    pvals = results.pvalues
    coeff = results.params
    conf_lower = results.conf_int()[0]
    conf_higher = results.conf_int()[1]

    results_df = pd.DataFrame({"pvals":pvals.round(3),
                               "Coefficient":coeff.round(3),
                               "conf_lower":conf_lower.round(3),
                               "conf_higher":conf_higher.round(3)
                                })

    #Reordering...
    results_df = results_df[["Coefficient","pvals","conf_lower","conf_higher"]]
    return results_df

def data_preperation_armington(data:pd.DataFrame):
    data['LD'] = data.Production - data.Export_Quantity
    data['M'] = data.Quantity
    data['M_total'] = data.Import_Quantity
    data['P_i'] = data.Value / data.Quantity
    data['P'] = data.Import_Value / data.Import_Quantity
    data['ln_M_LD'] = np.log(data.M / data.LD)
    data['ln_P_P_i'] = np.log(data.P / data.P_i)
    data = data[['Year','Reporter_Code','LD','M','M_total','P_i','P','ln_M_LD','ln_P_P_i']].drop_duplicates()
    #data.to_csv('armington.csv')
    return data

def pooled_regression(data: pd.DataFrame, lhs: list, rhs: list):
    reg = lm.PooledOLS(data[lhs], data[rhs], check_rank=True)
    pooled_reg = reg.fit()
    print(pooled_reg)
    return pooled_reg

def least_square_dummy_variable_estimation(data: pd.DataFrame, formula: str):
    data.to_csv('lsdv_input.csv')
    res = smf.ols(formula=formula, data=data).fit()
    print(res.summary())
    dfres = results_summary_to_dataframe(res)
    dfres['ISO'] = dfres.index.str[-4:-1]
    dfres = dfres[dfres['pvals'] < 0.05]
    dfres = dfres[dfres['Coefficient'] >= 0]
    dfres = dfres.sort_values(by=["Coefficient"],ascending=False)
    dfres.to_csv('lsdv_results.csv')
    dfres.info()
    return dfres

def random_effects_regression(data: pd.DataFrame, lhs: list, rhs: list):
    reg = lm.RandomEffects(data[lhs], data[rhs])
    re_reg = reg.fit()
    print(re_reg)
    return re_reg

def fixed_effects_regression(data:pd.DataFrame, lhs: list, rhs: list):
    reg = lm.PanelOLS(data[lhs], data[rhs], entity_effects=True, time_effects=False)
    fe_reg = reg.fit(use_lsdv=True,cov_type="clustered", cluster_entity=True)
    print(fe_reg)
    return fe_reg

def gme_estimation(data: pd.DataFrame, lhs: list, rhs: list, fixed_effects: list):
    gme_model = gme.EstimationModel(estimation_data = data,
                                    lhs_var = lhs,
                                    rhs_var = rhs,
                                    fixed_effects = fixed_effects)
    estimates = gme_model.estimate()
    results = estimates['all']
    gme_reg = results.summary()
    print(gme_reg)
    return gme_reg

def armington_estimations(data: pd.DataFrame):
    print(data)
    data["ISO"] = data.Reporter_Code
    Reporter_Code = pd.Categorical(data.Reporter_Code)
    data["Year"] = data.Year
    data["Reporter_Code"] = Reporter_Code
    data_gme = data
    data = data.set_index(['Reporter_Code', "Year"])

    # select variables
    formula = 'ln_M_LD ~ ln_P_P_i + C(ISO)'
    endog_var = ['ln_M_LD']
    exog_vars = ['ln_P_P_i']
    exog = sm.add_constant(data[exog_vars])
    fixed_effects_gme = [None]

    lsdv_reg = least_square_dummy_variable_estimation(formula=formula, data=data)
    pooled_reg = pooled_regression(data=data, lhs=endog_var, rhs=exog_vars)
    re_reg = random_effects_regression(data=data, lhs=endog_var, rhs=exog_vars)
    fe_reg = fixed_effects_regression(data=data, lhs=endog_var, rhs=exog_vars)
    #gme_reg = gme_estimation(data=data, lhs=endog_var, rhs=exog_vars, fixed_effects=fixed_effects_gme)

    # compare models
    try:
        print(compare({"FE": fe_reg, "RE": re_reg, "Pooled": pooled_reg}))
    except NameError:
        pass

    return lsdv_reg

def worldplot(data_for_plot: pd.DataFrame, name_of_plot: str):
    name_of_plot = (name_of_plot + '_' + 
                    data_selection.countries_origin.value + '_' + 
                    data_selection.item_subset.value)
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world.to_crs('+proj=robin')    
    print(world)
    world = world.merge(data_for_plot, left_on='iso_a3', right_on="ISO", how='left')
    fig, ax = plt.subplots(figsize=(75 / 2.54, 30 / 2.54))
    ax.set_title(name_of_plot)

    world[world.iso_a3 == data_selection.countries_origin.value].plot(color=data_selection.color_special.value, ax=ax)

    world.boundary.plot(ax=ax, color='gray', linewidth=0.5)
    world.plot(column='Coefficient', cmap= data_selection.color_set.value, linewidth=0.5, ax=ax, legend=True)
    wm = plt.get_current_fig_manager()
    wm.window.state('zoomed')
    plt.show()
    fig.savefig(str(name_of_plot + '.png'), dpi = 900)

def main():
    data = read_data()
    data = data_preperation_armington(data=data)
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.dropna()
    data.info()
    lsdv_results = armington_estimations(data)
    #worldplot(data_for_plot = armington_results, name_of_plot = 'LSDV_Armington')
    

main()