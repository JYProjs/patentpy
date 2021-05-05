import sys, traceback, datetime
import urllib.request, shutil, zipfile
from os import remove
import pandas as pd

from convert_funcs import txt_to_df
from patentpy.utility import get_date_tues


def convert_txt_to_df(dates_df, output_file = None):
    """Converts multiple TXT files to CSV format or a dataframe.
    
    Iterates through each row in dates_df DataFrame and downloads zip file from United States Patent 
    Trademark Office (USPTO) url corresponding to patent data from that row's 'year' and 'week'. 
    Extracts each zip folder (contains txt file) and parses TXT files (using helper function `txt_to_df`), 
    extracting fields and converting to csv file format. If no output file is provided then a 
    temporary csv file is created, read into pandas dataframe and returned (zip, txt, and any 
    temporary files are cleaned up).
    
    Args: 
        date_df (DataFrame): dataframe with columns: 1) 'year' and 2) 'week'.
        output_file (str, default None): path of '.csv' file to store data. 
    
    Returns:
        Dataframe or bool: returns ``pandas.DataFrame`` object if ouput_file is ``None`` and at least one file's
        data is able to be parsed else returns ``None``

    Raises:
        ValueError: 
            if `dates_df` does not contain columns 1) 'year' or 2) 'week' or if `output_file` is not a
            ".csv" file.
    """
    # check format of df; internal function so should not occur
    if not ('year' == dates_df.columns[0] and 'week' == dates_df.columns[1]):
        raise ValueError("`dates_df` parameter must have `year` and `week` columns; current columns = {}"
                         .format(dates_df.columns))
        
    # if output_file provided, check is .csv
    if output_file is not None:
        if not isinstance(output_file, str):
            raise ValueError("`output_file` parameter must be a path in the form of a string")
        elif output_file[len(output_file)-4:len(output_file)] != ".csv":
            raise ValueError('`output_file` parameter must be a ".csv" file')
    
    # base vars
    txt_uspto_url = "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/"
    dest_file = "temp-output.zip"
    
    # list to store data frames
    df_store = [None]       # to allow concat with only 1 df
    
    # default txt_to_df values
    header = True
    append = False
    
    # check if header is needed
    if output_file is not None:
        try:
            f = open(output_file)
        except FileNotFoundError:        # no file exists, create file and write header
            with open(output_file, 'w+') as f:
                f.write("WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References,Claims\n")
        else:
            f.close()        # close file if exists?
        finally:
            header = False
            append = True
    
    # convert all rows in df to that year & week's tuesday date (if exists)
    for row, curr_year, curr_week in dates_df.itertuples():
        # throw error if incorrect date but continue execution of other rows
        try:
            file_date = get_date_tues(curr_year, curr_week)
        except ValueError as ve:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, ve.__traceback__, limit=1)
            continue
        
        # get file name and url
        curr_month, curr_day = file_date.month, file_date.day
        curr_file = "pftaps{}{:02d}{:02d}_wk{:02d}".format(curr_year, curr_month, curr_day, curr_week)
        curr_url = txt_uspto_url + "{}/".format(curr_year) + curr_file + ".zip"
        curr_file += ".txt"
        
        # try to download data with complete file name
        # add error handling to skip url error, delete temp files, etc.
        # make more modular - wrap in function, call in try block,
        with urllib.request.urlopen(curr_url) as res, open(dest_file, 'w+b') as out_file:
            shutil.copyfileobj(res, out_file)
            
        # uncompress
        try:
            with zipfile.ZipFile(dest_file, 'r') as zip_uspto:
                zip_uspto.extract(curr_file)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, e.__traceback__, limit=1)
            continue
        finally:
            # delete zip
            remove(dest_file)
        
        # temperary output file to hold csv if no output file specified
        temp_output_file = "temp-patent-package-output.csv"
        
        # convert to txt data to csv format
        try:
            txt_to_df(curr_file, output_file if output_file is not None else temp_output_file, append, header)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, e.__traceback__, limit=1)
            continue
        finally:
            remove(curr_file)
        
        # get df for that year, week if no output file specified
        if output_file is None:
            try:
                curr_df = pd.read_csv(temp_output_file)
                df_store.append(curr_df)
            finally:
                remove(temp_output_file)
            
    return pd.concat(df_store, ignore_index=True) if len(df_store) > 1 and output_file is None else None