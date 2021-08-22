#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cctype>


// checks if string starts w/ a prefix
// WORKS (basic test cases)
bool startsWith(const std::string &text, const std::string &prefix)
{
    return (text.find(prefix) == 0);
}

// remove whitespace from beginning of a string
// WORKS (basic test cases)
void stripBeginWhitespace(std::string &text)
{
    int start = 0;
    while (text[start] == ' ' || text[start] == '\n' || text[start] == '\t' || text[start] == '\r')
        start++;
    text = text.substr(start);
}

// remove whitespace from end of a string
// WORKS (basic test cases)
void stripEndWhitespace(std::string &text)
{
    int end = text.length();
    while (text[end - 1] == ' ' || text[end - 1] == '\n' || text[end - 1] == '\t' || text[end - 1] == '\r')
      end--;
    text = text.substr(0, end);
}

// remove whitespace from beginning and end
void stripEdgeWhitespace(std::string &text)
{
    stripBeginWhitespace(text);
    stripEndWhitespace(text);
}

// extract single-line field and strip whitespace
std::string extractField(const std::string &line, int startPos)
{
    // extract, strip whitespace, and return
    std::string ans = line.substr(startPos);
    stripEdgeWhitespace(ans);
    return ans;
}

void formatName(std::string &name)
{
    long unsigned int semicolon = name.find(';');

    // leave as-is if there's no semi colon or if the format is not as expected
    if (semicolon == std::string::npos || name.length() < semicolon + 2) return ;

    std::string temp = name.substr(0, semicolon),
                revised = name.substr(semicolon + 2);

    name = revised + " " + temp;
}

void appendToField(std::string &orig, const std::string &addon)
{
    if (orig == "")
      orig = addon;
    else
      orig = orig + ';' + addon;
}

void alphaDigitOnly(std::string &text)
{
    std::string ans = "";
    int len = text.length();
    for (int i = 0; i < len; i++)
        if (isdigit(text[i]) || isalpha(text[i]))
          ans.push_back(text[i]);

    text = ans;
}

void removeQuotes(std::string &text)
{
    std::replace(text.begin(), text.end(), '\"', ' ');
    std::replace(text.begin(), text.end(), '\'', ' ');
}

// pybind11 export
int txt_to_df_cpp(std::string input_file, std::string output_file, bool append, bool header)
{
    // setup IO
    std::ifstream fin(input_file);
    std::ofstream fout;

    // initialize ofstream depending on append param
    if (append)
    {
        fout = std::ofstream(output_file, std::ios::app);
    }
    else
    {
        fout = std::ofstream(output_file);

        // output header line to CSV (if necessary)
        if (header) fout << "WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References,Claims\n";
    }

    // variables holding patent properties
    std::string currID = "",
                title = "",
                appDate = "",
                issDate = "",
                inventor = "",
                assignee = "",
                iclClass = "",
                refs = "",
                currLine,
                tempLine,
                tempInvt = "",
                tempAssg = "",
                tempClass = "",
                tempRef = "",
                currClaims = "",
                tempClaims = "";
                
    bool inPatent = false,
         gotAPD = false,
         gotISD = false,
         inClaims = false;

    // read input file line-by-line and store patent data
    getline(fin, currLine);
    int countPat = 0;
    while (!fin.eof())
    {
        // look at current line
        if (startsWith(currLine, "PATN"))
        {
            // print past patent (unless this is the first one)
            if (inPatent)
            {
                // remove quotes from text claims field first to avoid CSV issues
                removeQuotes(currClaims);
                removeQuotes(inventor);
                removeQuotes(assignee);
                removeQuotes(title);

                fout << currID
                  << ",\"" << title
                  << "\"," << appDate
                  << "," << issDate
                  << ",\"" << inventor
                  << "\",\"" << assignee
                  << "\"," << iclClass
                  << "," << refs
                  << ",\"" << currClaims
                  << "\"\n";
            }
            else inPatent = true;

            // update counter/tracker vars
            countPat++;
            gotAPD = false;
            gotISD = false;
            title = "";
            appDate = "";
            issDate = "";
            tempInvt = "";
            inventor = "";
            tempAssg = "";
            assignee = "";
            tempClass = "";
            iclClass = "";
            tempRef = "";
            refs = "";
            currClaims = "";
            tempClaims = "";
            inClaims = false;
        }
        else if (inPatent && startsWith(currLine, "TTL  "))
        {
            title = extractField(currLine, 5);
        }
        else if (inPatent && startsWith(currLine, "WKU  "))
        {
            currID = extractField(currLine, 5);
        }
        else if (inPatent && !gotAPD && startsWith(currLine, "APD  "))
        {
            gotAPD = true;
            appDate = extractField(currLine, 5);
        }
        else if (inPatent && !gotISD && startsWith(currLine, "ISD  "))
        {
            gotISD = true;
            issDate = extractField(currLine, 5);
        }
        else if (inPatent && startsWith(currLine, "INVT"))
        {
            // read next line to get inventor name (and confirm format)
            getline(fin, tempLine);
            if (startsWith(tempLine, "NAM  "))
            {
                tempInvt = extractField(tempLine, 5);
                formatName(tempInvt);
            }

            // add this inventor to set of inventors for this patent
            appendToField(inventor, tempInvt);
        }
        else if (inPatent && startsWith(currLine, "ASSG"))
        {
            // read next line to get assignee name (and confirm format)
            getline(fin, tempLine);
            if (startsWith(tempLine, "NAM  "))
            {
                tempAssg = extractField(tempLine, 5);

                // fix name format if person (and not corporation)
                if (tempAssg.find(';') != std::string::npos)
                  formatName(tempAssg);
            }

            // add this assignee to set of assignees for this patent
            appendToField(assignee, tempAssg);
        }
        else if (inPatent && startsWith(currLine, "ICL  "))
        {
            tempClass = extractField(currLine, 5);
            appendToField(iclClass, tempClass);
        }
        else if (inPatent && startsWith(currLine, "UREF"))
        {
            // read next line to get patent number (and confirm format)
            getline(fin, tempLine);
            if (startsWith(tempLine, "PNO  "))
            {
                tempRef = extractField(tempLine, 5);
                alphaDigitOnly(tempRef);
            }

            // add this reference to set of references for this patent
            appendToField(refs, tempRef);
        }
        else if (inPatent && (startsWith(currLine, "CLMS") || startsWith(currLine, "DCLM")))
        {
            // we're in claims, text will be coming soon
            inClaims = true;
        }
        // start of claims section marked with STM
        else if (inPatent && inClaims && startsWith(currLine, "STM "))
        {
            tempClaims = extractField(currLine, 5);
            stripEdgeWhitespace(tempClaims);
            currClaims = tempClaims;
        }
        else if (inPatent && inClaims && startsWith(currLine, "NUM "))
        {
            // don't do anything, but don't want to go to else branch either
        }
        else if (inPatent && inClaims && (startsWith(currLine, "PAR  ") ||
                                          startsWith(currLine, "PA1  ") ||
                                          startsWith(currLine, "PAL  ") ||
                                          startsWith(currLine, "     ")))
        {
            // add claims text
            tempClaims = extractField(currLine, 5);
            stripEdgeWhitespace(tempClaims);
            currClaims += tempClaims;
        }
        else
        {
            // not in claims anymore
            inClaims = false;
        }

        // read next line
        getline(fin, currLine);
    }

    // output details of last patent
    removeQuotes(currClaims);
    removeQuotes(inventor);
    removeQuotes(assignee);
    removeQuotes(title);
    fout << currID
         << ",\"" << title
         << "\"," << appDate
         << "," << issDate
         << ",\"" << inventor
         << "\",\"" << assignee
         << "\"," << iclClass
         << "," << refs
         << ",\"" << currClaims
         << "\"\n";

    // close IO
    fin.close();
    fout.close();

    // return number of patents
    return countPat;
}