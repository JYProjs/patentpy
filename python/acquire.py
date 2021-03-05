import datetime
import numpy as np
import pandas as pd

from python.convert_txt import convert_txt_to_df

# User-facing function `get_bulk_patent_data()`
def get_bulk_patent_data(year, week, output_file = None):
    """Obtains USPTO data in csv or dataframe from user-inputted values, `year` and `week`.  
    
    User-friendly function that utilizes `convert_txt_to_df` helper function after error 
    checking user-inputted `year` and `week` values (May either both be integer values or 
    equal-length lists). Used to get data from multiple files, each corresponding to a 
    'year'-'week' pair, from USPTO website (which may be stored as TXT, XML1, or XML2 file formats).

    Note: Current version only supports TXT file formats. XML1 and XML2 will be supported in the following
    release. 
    
    Args: 
        year (int, List[int]): integer or list of integers for 'year' in 'year'-'week' 
            pair corresponding to patent grant issued that 'week' of 'year'
        week (int, List[int]): integer or list of integers for 'week in 'year'-'week' 
            pair corresponding to patent grant issued that 'week' of 'year'
        output_file (str, optional): path of '.csv' file to store data, default `None` 
    
    Returns:
        DataFrame, Boolean: returns pandas DataFrame object if ouput_file is `None` else returns boolean `True`

    Raises:
        ValueError: If 'year' or 'week' are not both integers or equally-sized lists of 
            integers, are missing values, or are invalid (i.e. week > 53, year < 1776). 
        
            Note: This purposely does not raise error if there is no week 53 patent data available 
            for given year as a feature.
    """
    # convert to list if int
    year = [year] if isinstance(year, int) else year
    week = [week] if isinstance(week, int) else week

    # not list, int, or float error
    if not ( isinstance(year, list) and isinstance(week, list) ):
        raise ValueError("`year` and `week` parameters must be integers")
    # unequal length lists error
    if len(year) != len(week):
        raise ValueError("`year` and `week` parameters should be of equal lengths: \nyear = {}\nweek = {}"
                         .format(year, week))
    # missing/none values error
    if not ( all(x is not None for x in year) and 
            all(x is not None for x in week) ):
        raise ValueError("`year` and `week` parameters must not have missing or null values: \nyear = {}\nweek = {}"
                         .format(year, week))
    # values of wrong type error
    if not ( all(isinstance(x, int) for x in year) and 
            all(isinstance(x, int) for x in week) ):
        raise ValueError("`year` and `week` parameters should be integer values: \nyear = {}\nweek = {}"
                         .format(year, week))
    # get current day
    # add buffer for not yet uploaded current week of USPTO bulk patent data?
    curr_day = datetime.datetime.now()
    
    # check if year and week are valid
    if not all(x >= 1976 and x <= curr_day.year for x in year):
        raise ValueError("`year` value(s) must be between 1976 and current year, inclusive")
    if not all(x >= 1 and x <= 53 for x in week):
        raise ValueError("`week` value(s) must be between 1 and 53, inclusive")
        
    # create dataframe
    dates_df = pd.DataFrame(data = np.c_[year,week], columns = ['year', 'week'])
    
    # separate for different formats
    # what is sgml 2001 and patft 1971-1975??
    dates_df_txt = dates_df[dates_df['year'] <= 2001]
    dates_df_xml1 = dates_df[(dates_df['year'] >= 2002) & (dates_df['year'] <= 2004)]
    dates_df_xml2 = dates_df[dates_df['year'] >= 2005]
    
    # combine if no output file(return df)
    df_store = []
    
    df_store.append(convert_txt_to_df(dates_df_txt, output_file = output_file))
    # df_store.append(convert_xml1_to_df(dates_df_xml1, output_file = output_file)) # placeholder
    # df_store.append(convert_xml2_to_df(dates_df_xml2, output_file = output_file)) # placeholder

    return pd.concat(df_store) if output_file is None else True