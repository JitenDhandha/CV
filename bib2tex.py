import sys
from pybtex.database import parse_file

def parse_bib_data(bib_data):
    
    def strip_braces(s):
        if isinstance(s, str):
            return s.replace("{", "").replace("}", "")
        elif isinstance(s, list):
            return [str(x).replace("{", "").replace("}", "") for x in s]
    
    # Sort the entries by year
    bib_entries = sorted(bib_data.entries.values(), key=lambda x: int(x.fields['year']), reverse=True)
    
    # Extract the information and store it in lists
    titles = []
    authors = []
    months = []
    years = []
    journals = []
    volumes = []
    pages = []
    links = []
    
    for entry in bib_entries:
        
        titles.append(strip_braces(entry.fields['title']))
        
        author = strip_braces(entry.persons['author']) # Strip braces
        for i in range(len(author)):
            a = author[i]
            a_split = a.split(",")
            first_name = a_split[1].strip()
            last_name = a_split[0].strip()
            first_name = " ".join([f"{x[0]}." for x in first_name.split(" ")]) # Convert first name to initials
            author[i] = f"{first_name} {last_name}" # Swap first and last name
        authors.append(author)
        
        months.append(strip_braces(entry.fields['month']))
        
        years.append(strip_braces(entry.fields['year']))
        
        journal = strip_braces(entry.fields['journal'])
        if journal == '\\mnras':
            journal = 'Monthly Notices of the Royal Astronomical Society'
        elif journal == '\\apj':
            journal = 'The Astrophysical Journal'
        elif journal == '\\apjl':
            journal = 'The Astrophysical Journal Letters'
        elif journal == '\\apjs':
            journal = 'The Astrophysical Journal Supplement Series'
        elif journal == '\\aap':
            journal = r'Astronomy \& Astrophysics'
        journals.append(journal)
        
        if 'volume' not in entry.fields:
            volume = ''
        else:
            volume = strip_braces(entry.fields['volume'])
        volumes.append(volume)
        
        if 'pages' not in entry.fields:
            page = ''
        else:
            page = strip_braces(entry.fields['pages'])
        pages.append(page)
        
        links.append(strip_braces(entry.fields['adsurl']))
    
    return titles, authors, months, years, journals, volumes, pages, links

def main():
    
    # Check the number of arguments
    if len(sys.argv) < 2:
        print("Usage: python bib2text.py <bib_file> <tex_file>")
        sys.exit(1)
    
    # Load the bib file
    bib_file_path = sys.argv[1]
    bib_data = parse_file(bib_file_path)
    titles, authors, months, years, journals, volumes, pages, links = parse_bib_data(bib_data)

    # Load the tex file
    doc = sys.argv[2]
    with open(doc,"r") as f:
        all_text = f.read()
    
    # Empty strings to store the tex data
    first_author_text = ""
    contrib_author_text = ""

    # Convert the bib data to tex
    for i in range(len(titles)):
        author_tex = ", ".join(authors[i])
        author_tex = author_tex.replace("J. Dhandha", "\\textbf{J. Dhandha}")
        paper_text = \
f"""
    {months[i]} {years[i]} &
    {author_tex}
    \\href{{{links[i]}}}{{\\textit{{{titles[i]}}}}},
    {journals[i]}, {volumes[i]}, {pages[i]} \\\\
"""
        paper_text = paper_text.replace(", ,", ",")
        if authors[i][0] == "J. Dhandha":
            first_author_text += paper_text
        else:
            contrib_author_text += paper_text
        
    # Find the correct location to insert the text and write the file
    with open(doc,"w") as f:
        fa_start_idx = all_text.find("% Start of first author papers")
        fa_end_idx = all_text.find("% End of first author papers")
        ca_start_idx = all_text.find("% Start of contributing author papers")
        ca_end_idx = all_text.find("% End of contributing author papers")
        all_text = all_text[:fa_start_idx] + \
                   "% Start of first author papers " + first_author_text + \
                    all_text[fa_end_idx:ca_start_idx] + \
                    "% Start of contributing author papers " + contrib_author_text + \
                    all_text[ca_end_idx:]
        f.write(all_text)

if __name__ == "__main__":
    main()