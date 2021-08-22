# update documentation
import sys, traceback, datetime
import urllib.request, shutil, zipfile, re
from os import remove
from lxml import etree
from io import BytesIO
import pandas as pd

from patentpy.utility import get_date_tues

def extractFields1(parsed):
    # process current patent
    # check bibliographic data format 
    try:
        WKU = parsed.find(".//B110//PDAT").text
        title = parsed.find(".//B540//PDAT").text
        app_date = parsed.find(".//B220//PDAT").text
        issue_date = parsed.find(".//B140//PDAT").text
    except:
        return ""         # write nothing / skip 
    
    
    # get Inventor(s)
    xml_inventors = parsed.findall(".//B721//NAM")
    inventors = []
    for i in range(len(xml_inventors)):
        first_name, last_name = xml_inventors[i].find(".//FNM//PDAT"), xml_inventors[i].find(".//SNM//PDAT")
        inventor = "{} {}".format(first_name.text if first_name is not None else "", last_name.text if last_name is not None else "")
        inventors.append(inventor)
    inventors = ";".join(inventors) if inventors else ""
    
    # get Assignee(s)
    xml_assignees = parsed.findall(".//B731//NAM")
    assignees = []
    if xml_assignees:
        for i in range(len(xml_assignees)):
            assignee = xml_assignees[i].find(".//ONM//PDAT")
            if assignee is None:
                first_name, last_name = xml_assignees[i].find(".//FNM//PDAT"), xml_assignees[i].find(".//SNM/PDAT")
                assignee = "{} {}".format(first_name.text if first_name is not None else "", last_name.text if last_name is not None else "")
            else:
                assignee = assignee.text
            assignees.append(assignee)
    assignees = ";".join(assignees) if assignees else ""
    
    # get ICL Class(es)
    icl_class = parsed.findall(".//B511/PDAT")
    if icl_class:
        for i in range(len(icl_class)):
            icl_class[i] = icl_class[i].text
    icl_class = ";".join(icl_class) if icl_class else ""
    
    # get Ref(s)
    xml_references = parsed.findall(".//PCIT")
    references = []
    if xml_references:
        for i in range(len(xml_references)): 
            if xml_references[i].find(".//CTRY") is None:
                references.append(xml_references[i].find(".//DNUM//PDAT").text)
    references = ";".join(references) if references else ""
    
    # get Claims
    claims = parsed.findall(".//CL//CLM//PDAT")
    for i in range(len(claims)):
        claims[i] = claims[i].text if claims[i].text else ""
    claims = "".join(claims).replace("\"", "") if claims else ""
    return "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"\n".format(WKU, title, app_date, issue_date, inventors, assignees, icl_class, references, claims)

def xml1_to_df(input_file, output_file, append, header):
    write_mode = 'a' if append else 'w'
    with open(input_file, 'rb') as f1, open (output_file, write_mode) as f2:
        if header:
            f2.write("WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References,Claims\n")

        # initialize vars and parser
        currLine = f1.readline()
        parser = etree.XMLParser(recover=True)        # ignore escaped characters for now, add recognization later
        countPat, inPatent = 0, False
        while currLine:
            # check if closing patent tag
            if currLine[0:8] == b'</PATDOC' and inPatent:
                parser.feed(currLine)
                parsed = parser.close()
                f2.write(extractFields1(parsed))
                parser = etree.XMLParser(recover=True)
                inPatent = False
            elif currLine[0:7] == b'<PATDOC':
                inPatent = True
                countPat += 1
            if inPatent:
                parser.feed(currLine)
                
            currLine = f1.readline()   
            
    return countPat


def convert_xml1_to_df(dates_df, output_file = None):
    """Converts multiple XML files (2002-2004, XML version 2.5) to CSV format or a dataframe.
    
    Iterates through each row in dates_df DataFrame and downloads zip file from United States Patent 
    Trademark Office (USPTO) url corresponding to patent data from that row's 'year' and 'week'. 
    Extracts each zip folder (containing a XML file) and parses files (extracting fields and 
    converting to csv file format). If no output file is provided, a temporary csv file is created, 
    read into pandas dataframe and returned (zip, xml, and any temporary files are cleaned up).
    
    Args: 
        date_df (DataFrame): dataframe with columns: 1) 'year' and 2) 'week'.
        output_file (str, default None): path of '.csv' file to store data. 
    
    Returns:
        Dataframe or bool: returns ``pandas.DataFrame`` object if ouput_file is ``None`` and at least one file's
        data is able to be parsed else returns ``None``

    Raises:
        ValueError: 
            if `dates_df` does not contain columns 1) 'year' or 2) 'week' or if `output_file` is not a
            '.csv' file.
    """
    # check format of df; internal function so should not occur
    if not ('year' == dates_df.columns[0] and 'week' == dates_df.columns[1]):
        raise ValueError("`dates_df` parameter must have `year` and `week` columns; current columns = {}"
                         .format(dates_df.columns))
        
    # if output_file provided, check if .csv
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
            f.close()        # close file if exists
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
        curr_file = "pg{:02d}{:02d}{:02d}".format(curr_year-2000, curr_month, curr_day)
        curr_url = txt_uspto_url + "{}/".format(curr_year) + curr_file + ".zip"
        curr_file += ".xml"
        
        # try to download data with complete file name
        # make more modular - wrap in function, call in try block,
        with urllib.request.urlopen(curr_url) as res, open(dest_file, 'w+b') as out_file:
            shutil.copyfileobj(res, out_file)

        # uncompress (regex to match inconsistent formats)
        regexToMatch = re.compile(curr_file, re.IGNORECASE)
        with zipfile.ZipFile(dest_file, 'r') as zip_uspto:
            fileFound = False
            for file in zip_uspto.infolist():
                if regexToMatch.search(file.filename):
                    zip_uspto.extract(file)
                    curr_file = file.filename
                    fileFound = True
            if not fileFound:
                try:
                    raise FileNotFoundError("Unable to extract file {} for year {}, week {}".format(curr_file, curr_year, curr_week)) 
                except FileNotFoundError as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, e.__traceback__, limit=1)
                    continue
                finally:
                    remove(dest_file)

        # delete zip
        remove(dest_file)

        # temperary output file to hold csv if no output file specified
        temp_output_file = "temp-patent-package-output.csv"
        
        # convert to xml1 data to csv format
        try:
            xml1_to_df(curr_file, output_file if output_file is not None else temp_output_file, append, header)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, e.__traceback__, limit=1)
            continue
        finally:
            # remove xml before next iteration, skip this year's week's data if unable to read
            remove(curr_file)
        
        # get df for that year, week if no output file specified
        if output_file is None:
            try:
                curr_df = pd.read_csv(temp_output_file)
                df_store.append(curr_df)
            finally:
                remove(temp_output_file)

    return pd.concat(df_store, ignore_index=True) if len(df_store) > 1 and output_file is None else None


