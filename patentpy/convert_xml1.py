import sys, traceback, datetime
from os import remove
from lxml import etree
from io import BytesIO
import pandas as pd

from patentpy.utility import get_file_name, uncompress_zip, download_zip

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
                ref = xml_references[i].find(".//DNUM//PDAT").text
                if ref is not None:
                    references.append(ref)
    references = ";".join(references) if references else ""
    
    # get Claims
    claims = parsed.findall(".//CL//CLM//PDAT")
    for i in range(len(claims)):
        claims[i] = claims[i].text if claims[i].text else ""
    claims = "".join(claims).replace("\"", "") if claims else ""
    return "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"\n".format(WKU, title, app_date, issue_date, inventors, assignees, icl_class, references, claims)


def xml1_to_df(input_file, output_file, append, header):
    """Function that takes USPTO (2002-2004) data from XML file, extracts pertinent fields, 
    and creates (or appends to) CSV output.

    Args: 
        input_file:  `string`, path of '.xml' file to read data from
        output_file: `string`, path of '.csv' file to store data
        append:  `bool`, open and writes to output_file in append mode if ``true``
        header: `bool`, prints header as first line to csv output_file if ``true``
    
    Returns:
        `int` -- number of patents read from XML file
    """
    write_mode = 'a' if append else 'w'
    with open(input_file, 'rb') as f1, open (output_file, write_mode, encoding='utf-8') as f2:
        if header:
            f2.write("WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References,Claims\n")

        # initialize vars and parser
        currLine = f1.readline()
        parser = etree.XMLParser(recover=True)        # ignore escaped characters for now, add recognization later
        countPat, inPatent = 0, False
        while currLine:
            # check if closing patent tag
            if currLine[0:8] == b'</PATDOC' and inPatent:
                parser.feed(currLine.decode("utf-8", "replace"))
                parsed = parser.close()
                f2.write(extractFields1(parsed))
                parser = etree.XMLParser(recover=True)
                inPatent = False
            elif currLine[0:7] == b'<PATDOC':
                inPatent = True
                countPat += 1
            if inPatent:
                parser.feed(currLine.decode("utf-8", "replace"))
                
            currLine = f1.readline()   
            
    return countPat