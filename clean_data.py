import statistics as st
import pandas as pd
import math

def Normalize(data, attribute, method):
    if (method == 'scaling'):
        data_min = min(data[attribute])
        data_max = max(data[attribute])
        data[attribute] = (data[attribute] - data_min)/(data_max - data_min)
    return data

def Fill_by_Average(data, attribute):
    filled_data = data
    temp = []
    median = st.mean([x for x in data[attribute] if str(x) != 'nan'])
    for d in data[attribute]:
        #Need to check when the data is missing
        if (math.isnan(d)):
            d = median
        
        temp.append(d)
    
    filled_data[attribute] = temp
    return filled_data

def Fill_by_Mode(data, attribute):
    filled_data = data
    temp = []
    median = st.mode([x for x in data[attribute] if str(x) != 'nan'])
    for d in data[attribute]:
        #Need to check when the data is missing
        if (math.isnan(d)):
            d = median
        
        temp.append(d)
    
    filled_data[attribute] = temp
    return filled_data

def Fill_by_Median(data, attribute):
    filled_data = data
    temp = []
    median = st.median([x for x in data[attribute] if str(x) != 'nan'])
    for d in data[attribute]:
        #Need to check when the data is missing
        if (math.isnan(d)):
            d = median
        
        temp.append(d)
    
    filled_data[attribute] = temp
    return filled_data

def Detele_Missing(data, attribute):
    for i in range(len(data[attribute])):
        if (math.isnan(data[attribute].at[i])):
            data = data.drop([i])

    return data

def remove_outliers(data, attribute, method):
    if (method == 'z-score'):
        avg = st.mean(data[attribute])
        std = st.stdev(data[attribute])
        print(avg)
        print(std)

        for i in range(len(data[attribute])):
            z = (data[attribute].at[i] - avg)/std
            if (abs(z) > 3):
                data = data.drop([i])

    return data
def Convert_Data_Format(data, format):
    pass

def Combine_data(data, method):
    pass

def Encoding_categorical(data):
    pass

def Text_cleaning(data, attribute, method):
    cleaned_data = data
    temp = []
    if (method == 'lowercase'):
        for d in data[attribute]:
            d = d.lower()
            temp.append(d)
        
        cleaned_data[attribute] = temp

    return cleaned_data


def Unit_conversion(data, attribute, ori, after):
    converted_data = data
    temp = []
    if (ori == 'ug' or ori == 'μg' and after == 'mg'):
        for d in data[attribute]:
            if (d == ori):
                d = d/1000
            
            temp.append(d)
    
        converted_data[attribute] = temp

    return converted_data

data = {
  "calories": [390,390,390,390,390,390,390,390,390,390,1],
  "duration": [390,390,390,390,390,390,390,390,390,390,1]
}


#load data into a DataFrame object:
df = pd.DataFrame(data)
print(df)

df = remove_outliers(df, 'calories', 'z-score')
print(df)