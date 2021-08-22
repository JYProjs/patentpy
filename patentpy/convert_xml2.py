# test with multiple years, weeks data v4+
import sys, traceback, datetime
import urllib.request, shutil, zipfile, re
from os import remove
from lxml import etree
from io import BytesIO
import pandas as pd

from patentpy.utility import get_date_tues

def extractFields2(parsed):
    # process current patent
    # check if bibliographic is in the right format
    try:
        WKU = parsed.find(".//publication-reference//document-id//doc-number").text
        title = parsed.find(".//invention-title").text
        app_date = parsed.find(".//application-reference//date").text
        issue_date = parsed.find(".//publication-reference//date").text
    except:
        return ""       # write nothing and skip patent/extra text (i.e. dna/rna sequence)

    # get Inventor(s)
    xml_inventors = (parsed.findall(".//applicants//applicant//addressbook") or 
                 parsed.findall(".//us-parties//inventors//inventor//addressbook"))
    inventors = []
    if xml_inventors:
        for i in range(len(xml_inventors)):
            first_name, last_name = xml_inventors[i].find(".//first-name"), xml_inventors[i].find(".//last-name")
            inventor = "{} {}".format(first_name.text if first_name is not None else "", last_name.text if last_name is not None else "")
            inventors.append(inventor)
    inventors = ";".join(inventors) if inventors else ""

    # get Assignee(s)
    xml_assignees = parsed.findall(".//assignees//assignee")
    assignees = []
    if xml_assignees:
        for i in range(len(xml_assignees)):
            assignee = xml_assignees[i].find(".//addressbook//orgname")
            if assignee is None:
                first_name, last_name = xml_assignees[i].find(".//first-name"), xml_assignees[i].find(".//last-name")
                assignee = "{} {}".format(first_name.text if first_name is not None else "", last_name.text if last_name is not None else "")
            else:
                assignee = assignee.text
            assignees.append(assignee)
    assignees = ";".join(assignees) if assignees else ""

    # get ICL_class(es) - locarno or ipc format
    icl_class = (parsed.findall(".//classification-ipc//main-classification") or 
                 parsed.findall(".//classification-locarno//main-classification"))
    if icl_class:
        for i in range(len(icl_class)):
            icl_class[i] = icl_class[i].text
    else:
        # ipcr format
        icl_class = parsed.findall(".//classification-ipcr")
        for i in range(len(icl_class)):
            icl_components = [icl_class[i].find(".//section"), icl_class[i].find(".//class"), 
                              icl_class[i].find(".//subclass"), icl_class[i].find(".//main-group"),
                              icl_class[i].find(".//subgroup")]
            icl_class[i] = "{}{}{} {}{}".format(*[j.text if j is not None else "" for j in icl_components])
    icl_class = ";".join(icl_class) if icl_class else ""

    # get Refs
    all_references = parsed.findall(".//patcit")
    references = []
    if all_references:
        for i in range(len(all_references)): 
            if all_references[i].find(".//country").text == "US":
                references.append(all_references[i].find(".//doc-number").text)
    references = ";".join(references) if references else ""


    # get Claims
    claims = parsed.findall(".//claims//claim//claim-text")
    for i in range(len(claims)):
        claim_txt = claims[i].text if claims[i].text else ""
        claim_ref = claims[i].find(".//claim-ref")
        if claim_ref is not None:
            claim_ref_txt = claim_ref.text if claim_ref.text else ""
            claim_ref_tail = claim_ref.tail if claim_ref.tail else ""
            claim_txt += claim_ref_txt + claim_ref_tail
        claims[i] = claim_txt
    claims = "".join(claims).replace("\"", "") if claims else ""

    return "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"\n".format(WKU, title, app_date, issue_date, inventors, assignees, icl_class, references, claims)
        

def xml2_to_df(input_file, output_file, append, header):
    write_mode = 'a' if append else 'w'
    with open(input_file, 'rb') as f1, open (output_file, write_mode) as f2:
        if header:
            f2.write("WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References,Claims\n")

        # skip first two lines
        f1.readline()
        f1.readline()

        # initialize vars and parser
        currLine = f1.readline()
        parser = etree.XMLParser()
        countPat = 1
        while currLine:
            # each new xml within file
            if currLine[0:19] == b'<?xml version="1.0"':
                # skip line
                if f1.readline()[0:19] == b'<!DOCTYPE us-patent':
                    countPat += 1

                # reset params
                parsed = parser.close()
                f2.write(extractFields2(parsed))
                parser = etree.XMLParser()
            else:
                parser.feed(currLine)

            currLine = f1.readline()

        # get last patent
        parsed = parser.close()
        f2.write(extractFields2(parsed))
    return countPat

def convert_xml2_to_df(dates_df, output_file = None):
    """Converts multiple XML (version 4+) files to CSV format or dataframe.
    
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
        curr_file = "ipg{:02d}{:02d}{:02d}".format(curr_year-2000, curr_month, curr_day)
        curr_url = txt_uspto_url + "{}/".format(curr_year) + curr_file + ".zip"
        curr_file += ".xml"
        
        # try to download data with complete file name
        # make more modular - wrap in function, call in try block,
        with urllib.request.urlopen(curr_url) as res, open(dest_file, 'w+b') as out_file:
            shutil.copyfileobj(res, out_file)
        # uncompress
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
            xml2_to_df(curr_file, output_file if output_file is not None else temp_output_file, append, header)
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


