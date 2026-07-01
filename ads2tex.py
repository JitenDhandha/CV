import os
import sys
import ads
import datetime

def main():
    
    # DEFINE THE ADS LIBRARY ID
    ADS_LIBRARY = "-9hd8iXUQl6bWu8xYksd5A"
    # SET THE ADS DEV KEY (in GitHub secrets, so omitted here, but can be run locally)
    # os.environ["ADS_DEV_KEY"] = "insert_dev_key_here"

    # Query ADS for the papers in the library
    papers = ads.SearchQuery(q=f"docs(library/{ADS_LIBRARY})", fl=["bibcode", "author", "title", "pub", "volume", "page", "pubdate"])
    # Sort the papers by publication date (newest first)
    papers = sorted(papers, key=lambda x: x.pubdate, reverse=True)

    # Read the output TeX file
    if len(sys.argv) < 1:
        print("Usage: python bib2text.py <tex_file>")
        sys.exit(1)
    doc = sys.argv[1]
    with open(doc,"r") as f:
        all_text = f.read()

    # Empty variables to store the TeX strings and counters
    first_author_tex = ""
    first_author_counter = 0
    contrib_author_tex = ""
    contrib_author_counter = 0

    # Process the papers and populate the TeX strings and counters
    # (with custom processing if needed)
    for i, paper in enumerate(papers):
        
        # Some custom processing
        # Fix "Acedo, Eloy de Lera" to "de Lera Acedo, Eloy"
        paper.author = ["de Lera Acedo, Eloy" if "Acedo" in author else author for author in paper.author]
        # Fix publisher for 2025arXiv250200852P
        if paper.bibcode == "2025arXiv250200852P":
            paper.pub = "Accepted at NeurIPS 2024 (Machine Learning and the Physical Sciences Workshop)"
        # Ignore SKA chapter (2026arXiv260630947C)
        if paper.bibcode == "2026arXiv260630947C":
            continue
        # Common fixes
        math_dict = {"λ": "$\\lambda$", "μ": "$\\mu$", "α": "$\\alpha$", "β": "$\\beta$"}
        for key, value in math_dict.items():
            paper.title[0] = paper.title[0].replace(key, value)
        
        # Process the month and year to convert "YYYY-MM-DD" to "Month YYYY"
        date = datetime.datetime.strptime(paper.pubdate.replace("-00",""), "%Y-%m")
        # Generate the date TeX string
        date_tex = date.strftime("%B %Y")
        
        # Process the authors to convert "Dhandha, Jiten" to "J. Dhandha"
        authors = []
        for author in paper.author:
            if "," not in author:
                first_name = author
                last_name = ""
            else:
                first_name = author.split(",")[1].strip()
                first_name = " ".join([f"{x[0]}." for x in first_name.split(" ")])
                last_name = author.split(",")[0].strip()
            authors.append(f"{first_name} {last_name}")
        # Generate the author TeX string
        if len(authors) > 25:
            author_tex = authors[0] + " et al."
        else:
            author_tex = ", ".join(authors)
            author_tex = author_tex.replace("J. Dhandha", "\\textbf{J. Dhandha}")
            
        # Process the generate the title Tex string (with \textit{})
        title = paper.title[0]
        link = f"https://ui.adsabs.harvard.edu/abs/{paper.bibcode}"
        title_tex = f"\\href{{{link}}}{{\\textit{{{title}}}}}"
            
        # Process the journal, volume, and page TeX strings
        journal = paper.pub.replace("&", "\\&")
        volume = paper.volume if paper.volume else ""
        page = paper.page[0] if paper.page else ""
        # Generate the journal, volume, and page TeX string
        pub_tex = f"{journal}, {volume}, {page}"
            
        # Create the paper text
        paper_tex = \
f"""
    {date_tex} & {author_tex}, {title_tex}, {pub_tex} \\\\
"""
        paper_tex = paper_tex.replace(", ,", ",")
        
        # Append to the correct string
        if authors[0] == "J. Dhandha":
            first_author_tex += paper_tex
            first_author_counter += 1
        else:
            contrib_author_tex += paper_tex
            contrib_author_counter += 1
        
    # Write the updated TeX file 
    # (inserting the counters and paper texts in the correct places)
    with open(doc,"w") as f:
        paper_counter_star_idx = all_text.find("% Start of paper counter")
        paper_counter_end_idx = all_text.find("% End of paper counter")
        fa_start_idx = all_text.find("% Start of first author papers")
        fa_end_idx = all_text.find("% End of first author papers")
        ca_start_idx = all_text.find("% Start of contributing author papers")
        ca_end_idx = all_text.find("% End of contributing author papers")
        all_text = all_text[:paper_counter_star_idx] + \
                    "% Start of paper counter " + \
                   f"\nI have \\textbf{{{first_author_counter} first author}} publications and \\textbf{{{contrib_author_counter} contributing author}} publications.\n" + \
                   all_text[paper_counter_end_idx:fa_start_idx] + \
                   "% Start of first author papers " + first_author_tex + \
                    all_text[fa_end_idx:ca_start_idx] + \
                    "% Start of contributing author papers " + contrib_author_tex + \
                    all_text[ca_end_idx:]
        f.write(all_text)

if __name__ == "__main__":
    main()