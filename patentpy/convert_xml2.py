# test with multiple years, weeks data v4+
import sys, traceback, datetime
import urllib.request, shutil, zipfile, re
from os import remove
from lxml import etree
from io import BytesIO
import pandas as pd

from patentpy.utility import get_file_name

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
    """Function that takes USPTO (2005-`present`) data from XML file, extracts pertinent fields, 
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