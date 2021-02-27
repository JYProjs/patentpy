# convert multiple TXT files
# internal function
# date_df: column1 = year; column2 = week
# output_file should be a CSV
# returns data frame of patent data of output_file == NULL; TRUE otherwise
# if:
#   - output_file = NULL is used to acquire data and stored into `df1`
#   - output_file = <filename> is used to acquire data and then read into `df2` with `read.csv`
#     (read.csv(<filename>, colClasses = rep("character", 8), na.strings = c("NA", "N/A", "")))
import sys, traceback, datetime
import urllib.request, shutil, zipfile
from os import remove
import pandas as pd

from convert_funcs import txt_to_df
from python.utility import get_date_tues


def convert_txt_to_df(dates_df, output_file = None):
    # check format of df; internal function so should not occur
    if not ('year' in dates_df.columns and 'week' in dates_df.columns):
        raise ValueError("`dates_df` parameter must have `year` and `week` columns; current columns = {}"
                         .format(dates_df.columns))
        
    # if output_file provided, check is .csv ----- move to acquire?
    if output_file is not None:
        if not isinstance(output_file, str):
            raise ValueError("`output_file` parameter must be a path in the form of a string")
        elif output_file[len(output_file)-4:len(output_file)] == ".csv":
            raise ValueError('`output_file` parameter must be a ".csv" file')
    
    # base vars
    txt_uspto_url = "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/"
    dest_file = "temp-output.zip"
    
    # list to store data frames
    df_store = []
    
    # default txt_to_df values
    header = True
    append = False
    
    # check if header is needed
    if output_file is not None:
        try:
            f = open(output_file)
        except FileNotFoundError:        # no file exists, create file and write header
            with open(output_file, 'w+') as f:
                f.write("WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References\n")
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
        with zipfile.ZipFile(dest_file, 'r') as zip_uspto:
            zip_uspto.extract(curr_file)
        # delete zip
        remove(dest_file)
        
        # temperary output file to hold csv if no output file specified
        temp_output_file = "temp-patent-package-output.csv"
        
        # convert to txt data to csv format
        txt_to_df(curr_file, output_file if output_file is not None else temp_output_file, append, header)
        remove(curr_file)
        
        # get df for that year, week if no output file specified
        if output_file is None:
            try:
                curr_df = pd.read_csv(temp_output_file)
                df_store.append(curr_df)
            finally:
                remove(temp_output_file)
            
    return pd.concat(df_store) if output_file is None else True