def formatted_date(date_string):
    day = date_string[6:] + "/" if date_string[6:] != "00" else ""
    return date_string[4:6] + "/" + day + date_string[:4]

def formatted_text(text_string):
    # replace all double quotes with single quotes and 
    # use double quotes at begin and end to escape commas
    text_string = text_string.replace('"','')
    return '"' + text_string + '"' 

def get_next_element(file, curr_line):
    # current line to evaluate input line by line and add to field as necessary
    # current field to store all read values from particular tag
    curr_field = curr_line.strip('\n')
    next_line = file.readline()
    first_char = next_line[0] if next_line else ""
    while first_char == " " or next_line=="\n":
        next_line = next_line.strip()
        curr_field += " " + next_line
        next_line = file.readline() 
        first_char = next_line[0] if next_line else ""
    return curr_field, next_line

def retrieve_tag_val(tag_value):
    tag_length = tag_value.find(' ')
    tag = tag_value[:tag_length] if tag_length + 1 else tag_value
    value = tag_value[tag_length+1:].strip() if tag_length + 1 else ""
    return tag, value

def get_subfields_generic(file, next_line):
    subfields = {}
    while " " in next_line:
        temp_subfield, next_line = get_next_element(file, next_line)
        sub_tag, sub_value = retrieve_tag_val(temp_subfield)
        if sub_tag not in subfields:
            subfields[sub_tag] = [sub_value]
        else:
            subfields[sub_tag].append(sub_value)
    return subfields, next_line 

def get_subfields_combined(file, next_line):
    combined_subfields = ""
    while " " in next_line:
        temp_subfield, next_line = get_next_element(file, next_line)
        sub_tag, sub_value = retrieve_tag_val(temp_subfield)
        if sub_tag == "PAC":
            combined_subfields += sub_value + ": "
        elif sub_tag=="NUM":
            continue
        else:
            combined_subfields += sub_value
    return combined_subfields, next_line 


def parsing_function(file_name):
    with open(file_name, 'r') as f:
        # current line to evaluate input line by line and add to field as necessary
        # current field to store all read values from particular tag
        curr_line = f.readline()
        curr_field, next_line = get_next_element(f, curr_line)
        while next_line:
            # find length of tag and retrieve from current field
            tag = retrieve_tag_val(curr_field)[0]
            if tag == "PATN":
                subfields, next_line = get_subfields_generic(f, next_line)
                patent_no = ''.join(subfields['WKU'])
                title = formatted_text(''.join(subfields['TTL']))
                applied_date, issue_date = formatted_date(''.join(subfields['APD'])), formatted_date(''.join(subfields['ISD']))
                print('')
                print(patent_no, title, applied_date, issue_date, sep=",", end=",")
            elif tag == "INVT":
                subfields, next_line = get_subfields_generic(f, next_line)
                invt_name = ''.join(subfields['NAM']) if 'NAM' in subfields else ""
                invt_city = ''.join(subfields['CTY']) if 'CTY' in subfields else ""
                invt_state = ''.join(subfields['STA']) if 'STA' in subfields else ""
                if "INVT" in next_line:
                    print("%s (%s; %s)" % (invt_name, invt_city, invt_state), end = "; ")
                else:
                    print("%s (%s; %s)" % (invt_name, invt_city, invt_state), end=",")
            elif tag == "UREF":
                subfields, next_line = get_subfields_generic(f, next_line)
                ref_patent_no = ''.join(subfields['PNO']) if 'PNO' in subfields else ""
                ref_name = ''.join(subfields['NAM']) if 'NAM' in subfields else ""
                ref_date = formatted_date(''.join(subfields['ISD'])) if 'ISD' in subfields else ""
                if "UREF" in next_line:
                    print("%s (%s %s)" % (ref_patent_no, ref_name, ref_date), end = "; ")
                else:
                    print("%s (%s %s)" % (ref_patent_no, ref_name, ref_date), end=",")
            elif tag == "ABST":
                subfields, next_line = get_subfields_generic(f, next_line)
                abst_pal = formatted_text(''.join(subfields['PAL']))
                print(abst_pal, end=",")
            elif tag=="BSUM" or tag=="CLMS" or tag=="DRWD" or tag=="DETD":
                comb_subfields, next_line = get_subfields_combined(f, next_line)
                comb_subfields = formatted_text(comb_subfields)
                print(comb_subfields, end=',')
                # elif tag == "CLMS":
                #     #to-do
                # elif tag == "DRWD":
                #     #to-do
                # elif tag == "DETD":
                #     #to-do
                # elif tag == "CLAS":
                #     #to-do
            curr_field, next_line = get_next_element(f, next_line)
    return 0


parsing_function('test2.txt')

# # fix ending with a , instead replace with \n
# creating headers in csv and converting print statments to csv
# account for missing sub-tags in ABST, ASSG, PATN, etc
# account for missing major-tags, i.e. ASSG, DRWD
# account for random ass tables... done?




# parsing_function('pftaps19760106_wk01.txt')
