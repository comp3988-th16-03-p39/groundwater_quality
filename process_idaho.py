import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

#

gwd = pd.read_pickle("pickled_EDMS.pkl")
gwd.drop_duplicates()
gwd = gwd.reset_index()
gwd = gwd.drop(columns = ['index'])

def search_by_grouping (df, search_params: set, grouping: list, param_col: str):
    grouping_2 = copy.copy(grouping)
    grouping_2.append(param_col)
    df_grouped = df[grouping_2]
    df_grouped = df_grouped.drop_duplicates()
    df_grouped = df_grouped.reset_index()
    df_grouped = df_grouped.drop(columns = ['index'])
    

    params_per_group = dict()
    for i in range(0,df_grouped.shape[0]):
        group_id = list()
        for group_col in grouping:
            # print(group_col)
            # print('-*-\n')
            # print(df.loc[i,group_col])
            group_id.append(df.loc[i,group_col])
            # print('\n')
        group_id = tuple(group_id)

        if not ( group_id in params_per_group.keys() ):
            params_per_group[group_id] = set()

        if df_grouped.loc[i,param_col] in search_params:
            params_per_group[group_id].add(df_grouped.loc[i,param_col])
    
    return params_per_group     

key_params = ['Chloride', 'Sulfate', 'Sodium', 'Potassium', 'Magnesium', 'Calcium', \
              'Specific Conductance', 'Total Dissolved Solids', 'Water Temperature', 'pH']

grouping = ["SampleNumber"]

search_dict = search_by_grouping(gwd, key_params, grouping, "CharName")
for sample_id in search_dict.keys():
    search_dict[sample_id] = len(list(search_dict[sample_id]))

#counting time
no_params_hist = [0] * (len(key_params) + 1)
for sample_id in search_dict.keys():
    no_params_hist[search_dict[sample_id]] += 1

print(no_params_hist)
plt.bar(range(0,len(no_params_hist)),no_params_hist)
plt.xlabel('Number of given parameters measured')
plt.ylabel('Number of samples')
plt.show()