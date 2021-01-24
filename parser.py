def formatted_date(date_string):
    day = date_string[6:] + "/" if date_string[6:] != "00" else ""
    return date_string[4:6] + "/" + day + date_string[:4] 

def get_next_element(file, curr_line):
    # current line to evaluate input line by line and add to field as necessary
    # current field to store all read values from particular tag
    curr_field = curr_line.strip('\n')
    next_line = file.readline()
    first_char = next_line[0] if next_line else ""
    while first_char == " ":
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

def parsing_function(file_name):
    with open(file_name, 'r') as f:
        # current line to evaluate input line by line and add to field as necessary
        # current field to store all read values from particular tag
        curr_line = f.readline()
        curr_field, next_line = get_next_element(f, curr_line)
        while next_line:
            # find length of tag and retrieve from current field
            tag, value = retrieve_tag_val(curr_field)
            if (not value):
                #collect subfields 
                subfields = {}
                while " " in next_line:
                    temp_subfield, next_line = get_next_element(f, next_line)
                    sub_tag, sub_value = retrieve_tag_val(temp_subfield)
                    subfields[sub_tag] = (sub_value)
            if tag == "PATN":
                print(subfields['WKU'],subfields['TTL'],formatted_date(subfields['APD']),formatted_date(subfields['ISD']), sep=", ", end=", ")
            elif tag == "INVT":    
                print("%s (%s; %s)" % (subfields['NAM'],subfields['CTY'],subfields['STA']), end=", ")
            elif tag == "UREF":
                print("%s (%s %s)" % (subfields['PNO'],subfields['NAM'],formatted_date(subfields['ISD'])), end="; ")
            elif tag == "ABST":
                print('"%s"' % subfields['PAL'], end=", ")
            curr_field, next_line = get_next_element(f, next_line)
    return 0


parsing_function('test.txt')

# can do .find operation and test position (-1 means not found) or can check first 3-4 characters for a match...





# parsing_function('pftaps19760106_wk01.txt')
