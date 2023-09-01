import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

#

# gwd1 = pd.read_csv('ddw2020-present_2023-07-03_1.csv')
# gwd2 = pd.read_csv('ddw2020-present_2023-07-03_2.csv')
# gwd3 = pd.read_csv('ddw2020-present_2023-07-03_3.csv')
# gwd = pd.concat([gwd1, gwd2, gwd3], axis=0)
# gwd.to_pickle("pickled_ddw.pkl")

gwd = pd.read_pickle("pickled_ddw.pkl")
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
        
        if i % 100000 == 0:
            print('********************************')
            print(i)
            print(df_grouped.loc[i,param_col])
            print('\n')
        if df_grouped.loc[i,param_col] in search_params:
            params_per_group[group_id].add(df_grouped.loc[i,param_col])
    
    return params_per_group     

key_params = ['Chloride', 'Sulfate', 'Sodium', 'Potassium', 'Magnesium', 'Calcium', \
              'Specific Conductivity', 'Total Dissolved Solids', 'Alkalinity, total']

grouping = ["gm_well_id","src_samp_collection_date","src_samp_collection_time"]

# Number of parameters vs sample
# search_dict = search_by_grouping(gwd, key_params, grouping, "gm_chemical_name")
# for sample_id in search_dict.keys():
#     search_dict[sample_id] = len(list(search_dict[sample_id]))

# #counting time
# no_params_hist = [0] * (len(key_params) + 1)
# for sample_id in search_dict.keys():
#     no_params_hist[search_dict[sample_id]] += 1

# print(no_params_hist)

# Parameter vs number of samples
no_samples_hist = [0] * (len(key_params) + 1)
for i in range(0,len(key_params)):
    key_param = key_params[i]
    search_dict = search_by_grouping(gwd, key_param, grouping, "gm_chemical_name")

    for sample_id in search_dict.keys():
        if len(search_dict[sample_id]) > 0:
            no_samples_hist[i] += 1

print(no_samples_hist)

plt.bar(range(0,len(no_samples_hist)),no_samples_hist)
plt.xlabel('Number of given parameters measured')
plt.ylabel('Number of samples')
plt.show()