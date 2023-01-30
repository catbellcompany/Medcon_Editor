from ast import keyword
from copy import copy
from distutils import core
from glob import escape
from multiprocessing import AuthenticationError

from prompt_toolkit import PromptSession
from metadata.settings import get_Request_proxy as proxy
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
from nltk.tokenize import word_tokenize

def get_sub(x):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    sub_s = "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"
    res = x.maketrans(''.join(normal), ''.join(sub_s))
    return x.translate(res)

def get_super(x):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+−-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻⁼⁽⁾"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)

def preprocessed(text : str):
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, text)
    if sups != []:
        for sup in sups:
            text =text.replace(sup, get_super(sup))
    text = text.replace("<ˢᵘᵖ>", "").replace("</ˢᵘᵖ>", "")
    pattern = re.compile(u'<sub.*?sub>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    subs = re.findall(pattern, text)
    if subs != []:
        for sub in subs:
            text = text.replace(sub, get_sub(sub))
            
    text = text.replace("<ₛᵤ♭>", "").replace("</ₛᵤ♭>", "")
    text = text.replace("<italic>","").replace("</italic>","").replace("<i>", "").replace("</i>", "")
    text = text.replace('\xa0', '').replace('\r', '').replace('\t', '').replace('\n', '')
    return text


def metadata_type_molcells(doi : str):
    html_req = proxy.get_requests(doi)
    soup = BeautifulSoup(html_req.content, 'html.parser')
    
    origin_section01 = soup.find("div", class_ = "origin_section01")
    origin_section02 = soup.find("div", class_ = "origin_section02")
    origin_section03 = soup.find("div", class_ = "origin_section03", id="body00")
    
    copyright = "© The Korean Society for Molecular and Cellular Biology"
    journal_title = "Molecules and Cells"
    
    publication = origin_section01.find_all("p")[0].text.replace(";", '')
    published = origin_section01.find_all("p")[1].text 
    doi = origin_section01.find_all("p")[2].text
    
    article_title = str(origin_section02.find("h2")).replace("<h2>", "").replace("</h2>", '')
    article_title = preprocessed(article_title)
    authors = origin_section02.find("p", class_ = "authors").text.replace(" and", ", ").replace(",*", "*,")
    
    authors = re.sub(r'[0-9]+', '', authors)
    
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.replace("M.D.", "").replace("Ph.D.", "").replace("B.S.", "").replace("Ph.D","").replace("M.D", "").replace("Md. ", "")
    
    authors = authors.split(", ")
    
    corresp = []
    for author in authors:
        if "*" in author:
            corresp.append(author)
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    tmp = []
    for auth in authors:
        tmp.append(auth.replace(",", ""))
    authors = tmp
    tmp = []
    for cor in corresp:
        tmp.append(cor.replace("*", ""))
    corresp = tmp
    corresp = ", ".join(corresp).replace(",", "")
    for auth in authors:
        if auth == '':
            authors.remove(auth)
            
    
    abstract = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[0])
    abstract = abstract.replace("<p>", "").replace("</p>", "")
    abstract = preprocessed(abstract)
    
    abstract = abstract.split(". ")
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
            
    tmp = []
    for abs in abstract:
        txt = abs + "."
        txt = txt.replace("..", ".")
        
        tmp.append(txt)
    abstract = tmp
    keywords = origin_section03.find("p", class_ = "keyword")
    imgs = []
    
    if keywords == None:
        keywords = str(soup.find("div", class_ = "origin_section03", id="body01").find_all("p")[1])
        keywords = keywords.replace('<p>', '').replace('</p>','')
        keywords = keywords.replace('<strong>Keywords</strong>: ', '').replace(',', ';')
        keywords = preprocessed(keywords)
        abstract_img = soup.find("div", class_ = "origin_section03", id="body01").find_all("p")[0].find("img")['src']
        imgs.append(abstract_img)
        
    else:
        keywords = str(keywords)
        keywords = keywords.replace('<p class="keyword">', '').replace('</p>', '')
        keywords = keywords.replace('<strong>Keywords</strong> ', '').replace(',', ';')
        keywords = preprocessed(keywords)
    
    figures =soup.find_all("img", class_ = "view_img pointer btn_file")
    for fig in figures:
        imgs.append(fig['src'].replace("thumb/", ""))
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}
    
def metadata_type_jchestsurg(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    origin_section01 = soup.find("div", class_ = "origin_section01")
    #published
    
    published = origin_section01.text
    published = published[published.find("Published online") : ]
    published = published[:published.find("http")]
    
    publication = origin_section01.find_all("p")[0].text
    publication = publication.replace(";", "")

    #doi
    doi = origin_section01.text
    doi = doi[doi.find("http") : ]
    doi = doi[:doi.find('©')].replace("\n", "")
    doi = doi.replace('Copyright', '')
    copyright = "© Journal of Chest Surgery"
    journal_title = "Journal of Chest Surgery"
    
    origin_section02 = soup.find("div", class_ = "origin_section02")
    article_title = str(origin_section02.find("h2"))
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    article_title = preprocessed(article_title)

    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.replace("M.D.", "").replace("Ph.D.", "").replace("B.S.", "").replace("Ph.D","").replace("M.D", "").replace("Md. ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace("and ", ",")
    authors = re.sub(r'[0-9]+', '', authors)

    authors = authors.replace('<p class="authors">', "").replace("</p>", "")
    
    sup_pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(sup_pattern, authors)
    for sup in sups:
        authors = authors.replace(sup, "")
    
    a_pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    href = re.findall(a_pattern, authors)
    
    for a in href:
        authors = authors.replace(a, "").replace('<p>', '')
    
    sub_pattern = re.compile(u'<sub.*?sub>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    subs = re.findall(sub_pattern, authors)
    
    for sub in subs:
        authors = authors.replace(sub, "")
    authors = authors.split(", ")
    
    tmp = []
    
    for author in authors:
        if author == "" or author == " ":
            pass
        else:
            tmp.append(author.replace(",", "").replace("<p>", ""))
            
    authors = tmp
    corresp_section = str(origin_section02.find_all("p")[2])
    tmp = [] 
    for auth in authors:
        if auth in corresp_section:
            tmp.append(auth)
    
    
    corresp = tmp
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
                
    corresp = ", ".join(corresp)
    origin_section03 = soup.find("div", class_ = "origin_section03", id = "body00")
    
    abstract = str(origin_section03.find("div", class_ = "go_section").find_all("p")[0])
    abstract = abstract.replace('vs. ', 'vs.')
    b_pattern = re.compile(u'<b.*?b>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    bolds = re.findall(b_pattern, abstract)
    
    for b in bolds:
        abstract = abstract.replace(b, "").replace('<p>', '').replace("</p>", "")
    abstract = preprocessed(abstract)
    abstract = abstract.split(". ")

    i = 0
    tmp = []
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i]+ ". " +abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        txt = abs.replace('vs.', 'vs. ') + "."
        txt = txt.replace("..", ".")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
        tmp.append(txt.replace("<p>", "").replace("</p>", ""))
        
        i += 1        
    abstract = tmp
    
    keywords = str(origin_section03.find("div", class_ = "go_section").find_all("p")[1])
    keywords = preprocessed(keywords)
    keywords = keywords.replace('<p class="keyword">', "").replace("</p>", "")
    keywords = keywords.replace('<strong>Keywords</strong> ', '')
    keywords = keywords.replace('<p><strong>Keywords</strong>: ', '')
    keywords = keywords.replace(",", ";")
    
    tmp = [] 
    try:
        tmp.append(origin_section03[1].find("img")['src']) 
    except:
        pass
    figures = soup.find_all("img",class_ = "view_img pointer btn_file")
    for fig in figures:
        tmp.append(fig['src'].replace("thumb/", ""))
    imgs = tmp
    
    tmp = []
    
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_ijgii(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    origin_section01 = soup.find("div", class_ = "origin_section01")
    
    #published
    published = origin_section01.text
    published = published[published.find("Published online") : ]
    published = published[:published.find("http")]
    
    publication = origin_section01.find_all("p")[0].text
    publication = publication.replace(";", "")
    
    #doi
    doi = origin_section01.text
    doi = doi[doi.find("http") : ]
    doi = doi[:doi.find('©')].replace("\n", "").replace("Copyright ", "")
    
    copyright = "© International Journal of Gastrointestinal Intervention"
    journal_title = "International Journal of Gastrointestinal Intervention"
    
    origin_section02 = soup.find("div", class_ = "origin_section02")
    article_title = str(origin_section02.find("h2"))
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    article_title = preprocessed(article_title)
    
    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.replace("M.D.", "").replace("Ph.D.", "").replace("B.S.", "").replace("Ph.D","").replace("M.D", "").replace("Md. ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace("and ", ",")
    authors = re.sub(r'[0-9]+', '', authors)

    authors = authors.replace('<p class="authors">', "").replace("</p>", "")
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "").replace("<p>", "")
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    authors = authors.split(", ")
    
    corresp = []
    for author in authors:
        if "*" in author:
            corresp.append(author)
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    
    tmp = []
    
    for cor in corresp:
        txt = cor
        for sup in sups:
            txt = txt.replace(sup, "")
        txt = txt.replace("*", "")
        txt = txt.replace(",", "")
        tmp.append(txt)
    corresp = tmp
    tmp = []
    for auth in authors:
        txt = auth
        for sup in sups:
            txt = txt.replace(sup, "")
        txt = txt.replace(",", "")
        
        tmp.append(txt)
    authors = tmp
    corresp = ", ".join(corresp)

    origin_section03 = soup.find("div", class_ = "origin_section03", id = "body00")
    abstract = str(origin_section03.find("div", class_ = "go_section").find_all("p")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace("<p>", "").replace("</p>", "")
    abstract = abstract.replace('<p style="margin:5px;">', '')
    
    b_pattern = re.compile(u'<b.*?b>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    bolds = re.findall(b_pattern, abstract)
    
    for b in bolds:
        abstract = abstract.replace(b, "").replace('<p>', '')
    
    abstract = abstract.split(". ")
    i = 0
    tmp = []
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i]+". "+abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        
        txt = abs
        
        if "</b>" in abs:
            txt = abs[abs.find("</b> ") : ].replace("</b> ", "")
        txt = txt.replace('<br/>', '') + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
        
        i += 1        
    abstract = tmp
    
    keywords = str(origin_section03.find("div", class_ = "go_section").find_all("p")[1])
    keywords = preprocessed(keywords)
    
    keywords = keywords.replace('<p class="keyword">', "").replace("</p>", "")
    keywords = keywords.replace('<strong>Keywords</strong> ', '')
    keywords = keywords.replace('<p><strong>Keywords</strong>: ', '')
    keywords = keywords.replace(",", ";")

    tmp = [] 
    try:
        tmp.append(origin_section03[1].find("img")['src']) 
    except:
        pass
    
    figures = soup.find_all("img", class_ = "view_img pointer")
    for fig in figures:
        tmp.append(fig['src'].replace("thumb/", ""))
    imgs = tmp
    
    tmp = []
    
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_kjp(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    publication = soup.find("div", class_ = "pub-group pup-top-info").find_all("p")[0].text 
    publication = publication.replace(";", '')
    
    published = soup.find("div", class_ = "pub-group pup-top-info").find_all("p")[1].text 
    published = published[ : published.find("http")]
    
    doi = soup.find("div", class_ = "pub-group pup-top-info").find_all("p")[1].text
    doi = doi[doi.find("http") : ]
    
    journal_title = "Korean Journal of Pain"
    copyright = "© The Korean Pain Society"

    article_title = str(soup.find("div", class_ = "pub-title").find("h3"))
    article_title = article_title.replace('<h3>', '').replace('</h3>', '')
    article_title = preprocessed(article_title)
    
    base_info = soup.find("div", class_ = "pub-layer base_info")
    
    authors = str(base_info.find_all("p")[0]).replace("and ", ",")
    authors = authors.replace('<p class="-line">', '').replace('</p>', '')
    
    sup_pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(sup_pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    a_pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    hrefs =  re.findall(a_pattern, authors)
    for href in hrefs:
        authors = authors.replace(href, '')
        
    authors = authors.split(' , ')
    corresp = []
    corresp_sector = str(base_info.find_all("p")[2])
    
    corresp_sector = corresp_sector[ : corresp_sector.find("<br/><br/>")]
    
    for auth in authors:
        if auth.replace(" ", "") in corresp_sector.replace(" ", ""):
            corresp.append(auth)

    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
                
    corresp = ", ".join(corresp)
    
    try:
        abstract_area = str(soup.find("div", class_ = "pub_layer margin-six-top", id ="body00").find_all("p")[0])
        abstract_area = abstract_area.replace('<p style="margin:5px;">', '').replace('</p>', '').replace('<br/>', ' ')
        keywords = str(soup.find("div", class_ = "pub_layer margin-six-top", id ="body00").find_all("p")[1])
        keywords = preprocessed(keywords)
        
        keywords = keywords[keywords.find("<p><strong>Keywords</strong>: ") : ].replace('<p><strong>Keywords</strong>: ', '')
        keywords = keywords.replace("</p>", "")
    except:
        abstract_area = str(soup.find("div", class_ = "pub_layer margin-six-top", id ="body01").find_all("p")[0]).replace("<p>", "")
        abstract_area = abstract_area.replace('<p style="margin:5px;">', '').replace('</p>', '').replace('<br/>', ' ')
        keywords = "No Keywords"
    keywords = keywords.replace(",", ";")

        
    pattern = r'\[[^)]*\]'

    abstract_area = re.sub(pattern=pattern, repl='', string= abstract_area)
    abstract_area = preprocessed(abstract_area)
    b_pattern = re.compile(u'<b.*?b>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    bolds = re.findall(b_pattern, abstract_area)
    abstract = abstract_area.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b>", '')
        
        txt = txt + "."
        txt = txt.replace("..", '.')
        tmp.append(txt)
    
    abstract = tmp
    
    
    figs = soup.find_all("img", class_ = "view_img pointer")
    imgs = []
    for fig in figs:
        imgs.append(fig['src'].replace('thumb/', ''))
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_jee(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    origin_section01 = soup.find("div", class_ = "origin_section01")
    #published
    
    published = origin_section01.text
    published = published[published.find("Published online") : ]
    published = published[:published.find("http")]
    #doi
    doi = origin_section01.text
    doi = doi[doi.find("http") : ]
    doi = doi[:doi.find('©')].replace("\n", "")
    doi = doi[ : doi.find("Journal")]
    
    
    copyright = "© The Ecological Society of Korea"
    journal_title = "Journal of Ecology and Environment"

    origin_section02 = soup.find("div", class_ = "origin_section02")
    article_title = str(origin_section02.find("h2"))
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    article_title = preprocessed(article_title)
    
    publication = origin_section01.find_all("p")[1].text 
    
    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.replace("M.D.", "").replace("Ph.D.", "").replace("B.S.", "").replace("Ph.D","").replace("M.D", "").replace("Md. ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace(" and", ", ")
    authors = authors.replace('<p>', '').replace('</p>', '')
    
    sup_pattern = re.compile(u'<sup.*?/sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(sup_pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    a_pattern = re.compile(u'<a.*?/>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(a_pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    authors = authors.replace("</a>", "")
    authors = authors.replace(",,", ",")
    corresp = []
    authors = authors.split(", ")
    for auth in authors:
        if "*" in auth:
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(cor)
                
    corresp = ", ".join(corresp)
    corresp = corresp.replace("*", "")
    
    
    origin_section03 = soup.find("div", class_ = "origin_section03", id = "body00")
    abstract = str(origin_section03.find("div", class_ = "go_section").find_all("p")[0]).replace("–", "-")
    abstract = preprocessed(abstract)
    abstract = abstract.replace("<p>", "").replace("</p>", "").replace("<br/>", " ")
    
    abstract = abstract.split(". ")
    i = 0
    tmp = []
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i]+". "+abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        
        txt = abs + "."
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ]
            txt = txt.replace('</b> ', '')
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
        
        i += 1        
    abstract = tmp
    
    keywords = str(origin_section03.find("div", class_ = "go_section").find_all("p")[1])
    keywords = preprocessed(keywords)
    keywords = keywords.replace('<p class="keyword">', "").replace("</p>", "")
    keywords = keywords.replace('<strong>Keywords</strong> ', '')
    keywords = keywords.replace('<p><strong>Keywords</strong>: ', '')
    keywords = keywords.replace(",", ";")
    

    tmp = [] 
    try:
        tmp.append(origin_section03[1].find("img")['src']) 
    except:
        pass
    
    figures = soup.find_all("img", class_ = "view_img pointer")
    for fig in figures:
        tmp.append(fig['src'].replace("thumb/", ""))
    imgs = tmp
    
    tmp = []
    
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_biomolther(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    list_top = soup.find("div", class_ = "list_top")
    
    publication = list_top.find("div", class_ = "j_text_size").text
    publication = publication.replace('\xa0', '')
    publication = publication[ : publication.find("http")]
    publication = publication.replace(";", "")
    
    doi = list_top.find("div", class_ = "j_text_size").text
    doi = doi.replace('\xa0', '')
    doi = doi[doi.find("http") : ]

    journal_title = "Biomolecules and Therapeutics"
    copyright = "© The Korean Society of Applied Pharmacology"
    
    article_title = str(list_top.find("div", class_ = "tit j_text_size"))
    article_title = preprocessed(article_title)
    
    article_title = article_title.replace('<div class="tit j_text_size">' , '').replace('</div>', '')

    authors = str(list_top.find("div", class_ = "authors j_text_size"))
    authors = authors.replace("and ", ", ")
    
    authors = authors.replace('<div class="authors j_text_size">', '').replace('</div>', '').replace("and ", ",")
    sup_pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(sup_pattern, authors)
    
    authors = authors.split(", ")
    corresp = []
    
    for auth in authors:
        if "*" in auth :
            corresp.append(auth)
    
    tmp = []
    for auth in authors:
        txt = auth
        for sup in sups:
            txt = txt.replace(sup, "")
        tmp.append(txt)

    authors = tmp    
    
    tmp = []
    for cor in corresp:
        txt = cor
        for sup in sups:
            txt = txt.replace(sup, "")
        tmp.append(txt)
    corresp = tmp

    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    published = list_top.find("div", class_ = "date j_text_size").text
    published = published[published.find("Published online"):published.find(".")]
    abstract = str(soup.find("div", class_ = "Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<dd class="j_text_size">', '').replace('</dd>', '').replace("vs. ", 'vs.')
    abstract = abstract.replace('<dd class="jtextsize">', '')
    abstract = abstract.split(". ")
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1
    
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        txt = txt + "."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = str(soup.find("div", class_ = "Abstract").find_all("dd")[1]).replace('<dd class="j_text_size">', '').replace('</dd>', '').replace('<strong>Keywords</strong>: ', '')
    keywords = preprocessed(keywords)
    keywords = keywords.replace(",", ";")
    
    figures = soup.find_all("img", class_ = "view_img pointer")
    imgs = []
    for fig in figures:
        imgs.append(fig['src'].replace('thumb/', ''))
        
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_bmbreports(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    list_top = soup.find("div", class_ = "list_top")
    publication = list_top.find("div", class_ = "j_text_size").text
    publication = publication.replace('\xa0', '')
    publication = publication[ : publication.find("http")]
    publication = publication.replace(";", "")
    
    doi = list_top.find("div", class_ = "j_text_size").text
    doi = doi.replace('\xa0', '')
    doi = doi[doi.find("http") : ]
    
    journal_title = "Biochemistry and Molecular Biology Reports"
    copyright = "© Korean Society for Biochemistry and Molecular Biology"
    article_title = str(list_top.find("div", class_ = "tit j_text_size"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<div class="tit j_text_size">' , '').replace('</div>', '').replace('\xa0',' ')
    
    authors = str(list_top.find("div", class_ = "authors j_text_size")).replace("\xa0", " ")
    authors = authors.replace('<div class="authors j_text_size">', '').replace('</div>', '').replace("and ", ",").replace("amp;", "").replace("&", ",")
    sup_pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)

    a_pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    href = re.findall(a_pattern, authors)
    
    for a in href:
        authors = authors.replace(a, "")
    sups = re.findall(sup_pattern, authors)
    
    authors = authors.split(", ")
    corresp = []
    tmp = []
    for auth in authors:
        if "*" in auth :
            corresp.append(auth)
        txt = auth
        for sup in sups:
            txt = txt.replace(sup, '')
        tmp.append(txt)
    authors = tmp
    
    tmp = []
    for cor in corresp:
        txt = cor
        for sup in sups:
            txt = txt.replace(sup, "")
        tmp.append(txt)
    corresp = tmp
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)                   
    published = list_top.find("div", class_ = "date j_text_size").text
    published = published[published.find("Published online"):published.find(".")]
    
    abstract = str(soup.find("div", class_ = "Abstract").find_all("dd")[0]).replace("<span>","").replace("</span>","")
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace("\xa0", " ")
    
    abstract = abstract.split(". ")
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1
    
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        txt = txt + "."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = str(soup.find("div", class_ = "Abstract").find_all("dd")[1]).replace('<dd class="j_text_size">', '').replace('</dd>', '').replace('<strong>Keywords</strong>: ', '')
    keywords = preprocessed(keywords)
    keywords = keywords.replace(",", ";")
    
    figures = soup.find_all("img", class_ = "view_img pointer")
    imgs = []
    for fig in figures:
        imgs.append(fig['src'].replace('thumb/', ''))

    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_cpn(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    list_top = soup.find("div", class_ = "list_top")
    publication = list_top.find("div", class_ = "j_text_size").text
    publication = publication.replace('\xa0', '')
    publication = publication[ : publication.find("http")]
    publication = publication.replace(";", "")
    
    doi = list_top.find("div", class_ = "j_text_size").text
    doi = doi.replace('\xa0', '')
    doi = doi[doi.find("http") : ]
    
    journal_title = "Clinical Psychopharmacology and Neuroscience"
    copyright = "© The Korean College of Neuropsychopharmacology"
    
    article_title = str(list_top.find("div", class_ = "tit j_text_size"))
    article_title = preprocessed(article_title)
    
    article_title = article_title.replace('<div class="tit j_text_size">' , '').replace('</div>', '')
    
    authors = str(list_top.find("div", class_ = "authors j_text_size"))
    
    authors = authors.replace('<div class="authors j_text_size">', '').replace('</div>', '').replace("and ", ",").replace('amp;', '').replace('&', ',')
    sup_pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(sup_pattern, authors)
    
    a_pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    href = re.findall(a_pattern, authors)
    
    for a in href:
        authors = authors.replace(a, "")
    
    for sup in sups:
        authors = authors.replace(sup, "")
        
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        tmp.append(auth.replace("*", ""))
    authors = tmp
    
    corresp_section = str(list_top.find("div", style="padding:10px 0;", class_ = "j_text_size"))
    corresp_section = corresp_section[ : corresp_section.find("<br/><br/>")]
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)   
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    published = list_top.find("div", class_ = "date j_text_size").text
    published = published[published.find("Published online"):published.find(".")]
    abstract = str(soup.find("div", class_ = "Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)

    abstract = abstract.replace('<dd class="j_text_size">', '').replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace('<br/>', ' ')
    
    abstract = abstract.split(". ")
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1
    
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = str(soup.find("div", class_ = "Abstract").find_all("dd")[1]).replace('<dd class="j_text_size">', '').replace('</dd>', '').replace('<strong>Keywords</strong>: ', '')
    keywords = preprocessed(keywords)
    keywords = keywords.replace(",", ";")
    figures = soup.find_all("img", class_ = "view_img pointer")
    imgs = []
    for fig in figures:
        imgs.append(fig['src'].replace('thumb/', ''))
        
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}
    
def metadata_type_gnl(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    origin_section01 = soup.find("div", class_ = "origin_section01")
    origin_section02 = soup.find("div", class_ = "origin_section02")
    origin_section03 = soup.find("div", class_ = "origin_section03", id="body00")
    
    journal_title = "Gut and Liver"
    copyright = "© Gut and Liver"
    
    publication = origin_section01.find_all("p")[0].text 
    publication = publication[ : publication.find("http")]
    doi = origin_section01.find_all("p")[0].text 
    doi = doi[doi.find("http") : ]
    
    published = origin_section01.find_all("p")[1].text
    published = published[ : published.find("Published date")]
    
    article_title = str(origin_section02.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    
    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace("<p>", "").replace("</p>", "")
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    for sup in sups:
        authors = authors.replace(sup, "")
    authors = authors.split(", ")
    
    corresp_section = str(origin_section02.find_all("p")[2])
    corresp_section = corresp_section[ : corresp_section.find("</br></br>")]
    corresp = []
    
    for author in authors:
        if author.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(author)
    
    for cor in corresp:
        for auth in authors:
            if cor in auth:
                authors.remove(auth)
                
    corresp = ", ".join(corresp)
    
    abstract = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace("<p>","").replace("</p>", "").replace("<br/>", " ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt :
            txt = txt[txt.find("</b>") : ]
        txt = txt.replace("</b> ","").replace("<b>", "").replace("</br>" , "")
        tmp.append(txt)
    abstract = tmp
    i = 0
    for abs in abstract:
        try:
            if abstract[i + 1][0].islower():
                abstract[i] = abstract[i] +". " + abstract[i+1]
                abstract.remove(abstract[i+1])
                
        except:
            pass
        i += 1
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    
    abstract = tmp
    keywords = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[1])
    keywords = preprocessed(keywords)
    keywords = keywords.replace("<p>","").replace("</p>", "")
    keywords = keywords.replace(",",";")
    keywords = keywords.replace("<strong>Keywords</strong>: ","")
    
    imgs = []
    try:
        graphic_abstract = soup.find("div", class_="origin_section03", id="body01").find("p").find("img")
        imgs.append(graphic_abstract['src'])
    except:
        pass
    
    figs = soup.find_all("img", class_ = "view_img pointer btn-file")
    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_jams(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    article_info01 = soup.find("div", class_ = "article-info")
    article_info02 = soup.find("div", class_ = "article-info02")
    
    journal_title = "Journal of Acupuncture and Meridian Studies"
    copyright = "© Medical Association of Pharmacopuncture Institute"
    
    article_title = str(article_info01.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>","").replace("</h2>", "")
    
    authors = str(article_info01.find("div", class_ = "authors"))
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    authors = authors.replace('<div class="authors">', "").replace('</div>', "")
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    authors = authors.replace("*", "")
    authors = authors.split(", ")
    
    corresp_section = article_info01.find("div", class_ = "corres-author").text
    corresp = []
    
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ",""):
            corresp.append(auth)
            
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    publication = article_info02.find_all("p")[0].text
    published = article_info02.find_all("p")[1].text
    published = published[ : published.find("http")]
    doi = article_info02.find_all("p")[1].text
    doi = doi[doi.find("http") : ]

    abstract = str(soup.find("div", class_ = "article-info03 mb40", id="body00").find("div", class_ = "article-text mb40"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<div class="article-text mb40">', "").replace("</div>", "").replace("&lt;", "<").replace("&gt;", ">").replace("–", "-")
    abstract = abstract.replace("vs. ", "vs.").replace("<br/>"," ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ","")
        txt = txt + "."
        txt = txt.replace(".." , ".")
        
        tmp.append(txt)
    
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1

    abstract = tmp
    
    keywords = soup.find("div", class_ = "article-info03 mb40", id="body00").find_all("div", class_ = "article-text")[1].text
    keywords = keywords.replace(",", ";")
    
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer btn-file")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_jcp(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    origin_section01 = soup.find("div", class_ = "origin_section01")
    origin_section02 = soup.find("div", class_ = "origin_section02")
    origin_section03 = soup.find("div", class_ = "origin_section03", id="body00")
    
    journal_title = "Journal of Cancer Prevention"
    copyright = "© Korean Society of Cancer Prevention"
    
    publication = origin_section01.find_all("p")[0].text 
    published = origin_section01.find_all("p")[1].text 
    doi = origin_section01.find_all("p")[2].text 
    
    article_title = str(origin_section02.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    
    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace('<p class="color-black">', "").replace("</p>", "")
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")

    authors = authors.split(", ")

    corresp_section = str(origin_section02.find_all("p")[2]).replace("<p>", "").replace("</p>", "")
    corresp = []
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ",""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    

    abstract = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[0])
    abstract = preprocessed(abstract)
    
    abstract = abstract.replace("<p>","").replace("</p>", "").replace("<br/>", " ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt :
            txt = txt[txt.find("</b>") : ]
        txt = txt.replace("</b> ","").replace("<b>", "").replace("</br>" , "")
        tmp.append(txt)
    abstract = tmp
    i = 0
    for abs in abstract:
        try:
            if abstract[i + 1][0].islower():
                abstract[i] = abstract[i] +". " + abstract[i+1]
                abstract.remove(abstract[i+1])
                
        except:
            pass
        i += 1
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    
    abstract = tmp
    
    keywords = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[1])
    keywords = preprocessed(keywords)
    keywords = keywords.replace("<p>","").replace("</p>", "")
    keywords = keywords.replace(",",";")
    keywords = keywords.replace("<strong>Keywords</strong>: ","")
    
    
    imgs = []
    try:
        graphic_abstract = soup.find("div", class_="origin_section03", id="body01").find("p").find("img")
        imgs.append(graphic_abstract['src'])
    except:
        pass
    
    figs = soup.find_all("img", class_ = "view_img pointer")
    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_jmis(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    list_top = soup.find("div", class_ = "list_top")
    publication = list_top.find("div", class_ = "j_text_size").text
    publication = publication.replace('\xa0', '')
    publication = publication[ : publication.find("http")]
    publication = publication.replace(";", "")
    
    doi = list_top.find("div", class_ = "j_text_size").text
    doi = doi.replace('\xa0', '')
    doi = doi[doi.find("http") : ]
    
    journal_title = "Journal of Minimally Invasive Surgery"
    copyright = "© The Korean Society of Endo-Laparoscopic & Robotic Surgery"
    
    article_title = str(list_top.find("div", class_ = "tit j_text_size"))
    article_title = preprocessed(article_title)
    
    article_title = article_title.replace('<div class="tit j_text_size">' , '').replace('</div>', '')
    
    
    authors = str(list_top.find("div", class_ = "authors j_text_size"))
    
    authors = authors.replace('<div class="authors j_text_size">', '').replace('</div>', '').replace("and ", ",").replace('amp;', '').replace('&', ',')
    sup_pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(sup_pattern, authors)
    
    a_pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    href = re.findall(a_pattern, authors)
    
    for a in href:
        authors = authors.replace(a, "")
    
    for sup in sups:
        authors = authors.replace(sup, "")
        
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        tmp.append(auth.replace("*", ""))
    authors = tmp
    
    corresp_section = str(list_top.find("div", style="padding:10px 0;", class_ = "j_text_size"))
    corresp_section = corresp_section[ : corresp_section.find("<br/><br/>")]
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)   
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    published = list_top.find("div", class_ = "date j_text_size").text
    published = published[published.find("Published online"):published.find(".")]
    
    abstract = str(soup.find("div", class_ = "Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)

    abstract = abstract.replace('<dd class="j_text_size">', '').replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace('<br/>', ' ').replace("&lt;", "<").replace("&gt;", ">")
    
    abstract = abstract.split(". ")
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1
    
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("div", class_ = "Abstract").find_all("dd")[1].text
    keywords = keywords.replace(",", ";").replace("Keywords: ", "")
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_jnm(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    list_top = soup.find("div", class_ = "list_top")
    publication = list_top.find("div", class_ = "j_text_size").text
    publication = publication.replace('\xa0', '')
    publication = publication[ : publication.find("http")]
    publication = publication.replace(";", "")
    
    doi = list_top.find("div", class_ = "j_text_size").text
    doi = doi.replace('\xa0', '')
    doi = doi[doi.find("http") : ]

    journal_title = "Journal of Neurogastroenterology and Motility"
    copyright = "© The Korean Society of Neurogastroenterology and Motility"
    
    article_title = str(list_top.find("div", class_ = "tit j_text_size"))
    article_title = preprocessed(article_title)
    
    article_title = article_title.replace('<div class="tit j_text_size">' , '').replace('</div>', '')
    
    
    authors = str(list_top.find("div", class_ = "authors j_text_size"))
    
    authors = authors[ : authors.find("; ")]
    
    authors = authors.replace('<div class="authors j_text_size">', '').replace('</div>', '').replace("and ", ", ").replace('amp;', '').replace('&', ',').replace("</div","")
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    pattern = re.compile(u'<img.*?bottom', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, authors)
    
    for img_tag in img_tags:
        authors = authors.replace(img_tag, "")

    authors = authors.split(", ")
    
    for auth in authors:
        if auth == "" or auth == " ":
            authors.remove(auth)
    tmp = []
    for auth in authors:
        tmp.append(auth.replace(",","").replace("*",""))
    authors = tmp
    
    corresp_section = str(list_top.find("div", style="padding:10px 0;", class_ = "j_text_size"))
    if "</a> <br/>" in corresp_section:
        corresp_section = corresp_section[ : corresp_section.find("</a> <br/>")]
    corresp = []
    
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ", ""):
            corresp.append(auth)
            
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    published = list_top.find("div", class_ = "date j_text_size").text
    published = published[published.find("Published online"):]
    
    
    abstract = str(soup.find("div", class_ = "Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)

    abstract = abstract.replace('<dd class="j_text_size">', '').replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace('<br/>', ' ').replace("&lt;", "<").replace("&gt;", ">")
    
    abstract = abstract.split(". ")
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1
    
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("div", class_ = "Abstract").find_all("dd")[1].text
    keywords = keywords.replace(",", ";").replace("Keywords: ", "")
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp

    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_ijthyroid(doi : str):
    
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "International Journal of Thyroidology"
    copyright = "© 2021 Korean Thyroid Association"
    
    list_top = soup.find("div", class_ = "list_top")
    article_title = str(list_top.find("div", class_="tit j_text_size"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<div class="tit j_text_size">', '').replace('</div>', '')

    publication = list_top.find_all("div", class_="author j_text_size")[0].text
    publication = publication[:publication.find("http")]
    doi = list_top.find_all("div", class_="author j_text_size")[1].text
    doi = doi[doi.find("http") : ]
    published = list_top.find_all("div", class_="author j_text_size")[1].text
    published = published[ : published.find("http")]
    
    
    authors = str(soup.find_all("div", style="padding:10px 0;")[0].find("div", class_ = "bold j_text_size")).replace('<div class="bold j_text_size">', '').replace('</div>','').replace("and ",", ")
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    
    authors = authors.split(", ")
    
    corresp = []
    corresp_section = soup.find_all("div", style="padding:10px 0;")[1].text 
    
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    abstract = str(soup.find("div", class_ ="Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace('<br/>', ' ').replace("&lt;", "<").replace("&gt;", ">")
    
    abstract = abstract.split(". ")
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp
    
    keywords = str(soup.find("div", class_ ="Abstract").find_all("dd")[1]).replace('<dd class="j_text_size"><strong>Keywords</strong> : ',"").replace("</dd>","")
    keywords = preprocessed(keywords)
    keywords = keywords.replace(",", ";")
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_jop(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    article_info01 = soup.find("div", class_ = "article-info")
    article_info02 = soup.find("div", class_ = "article-info02")
    
    journal_title = "Journal of Pharmacopuncture"
    copyright = "© The Korean Pharmacopuncture Institute"
    
    article_title = str(article_info01.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>","").replace("</h2>", "")
    
    
    authors = str(article_info01.find("div", class_ = "authors"))
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    authors = authors.replace('<div class="authors">', "").replace('</div>', "")
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    authors = authors.replace("*", "")
    authors = authors.split(", ")
    
    corresp_section = article_info01.find("p", style="padding-top:15px;text-align:left;").text
    corresp = []
    
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ",""):
            corresp.append(auth)
            
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    publication = article_info02.find_all("p")[0].text
    published = article_info02.find_all("p")[1].text
    published = published[ : published.find("http")]
    doi = article_info02.find_all("p")[1].text
    doi = doi[doi.find("http") : ]
    
    abstract = str(soup.find("div", class_ = "article-info03 mb40", id="body00").find("div", class_ = "article-text mb40"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<div class="article-text mb40">', "").replace("</div>", "").replace("&lt;", "<").replace("&gt;", ">").replace("–", "-")
    abstract = abstract.replace("vs. ", "vs.").replace("<br/>"," ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ","")
        txt = txt + "."
        txt = txt.replace(".." , ".")
        
        tmp.append(txt)
    
    i = 0
    for abs in abstract:
        try:
            if abstract[i+1][0].islower():
                abstract[i] = abstract[i] + ". " + abstract[i+1]
                abstract.remove(abstract[i+1])
        except:
            pass
        i += 1

    abstract = tmp
    
    keywords = soup.find("div", class_ = "article-info03 mb40", id="body00").find_all("div", class_ = "article-text")[1].text
    keywords = keywords.replace(",", ";")
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer btn-file")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_kjcls(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Korean Journal of Clinical Laboratory Science"
    copyright = "© 2022 Korean Society for Clinical Laboratory Science"
    
    list_top = soup.find("div", class_ = "list_top")
    article_title = str(list_top.find("div", class_="tit j_text_size"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<div class="tit j_text_size">', '').replace('</div>', '')
    
    publication = list_top.find_all("div", class_="author j_text_size")[0].text
    publication = publication[:publication.find("http")]
    doi = list_top.find_all("div", class_="author j_text_size")[0].text
    doi = doi[doi.find("http") : ]
    published = list_top.find_all("div", class_="author j_text_size")[1].text
    
    authors = str(soup.find_all("div", style="padding:10px 0;")[0].find("div", class_ = "bold j_text_size")).replace('<div class="bold j_text_size">', '').replace('</div>','')
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    
    authors = authors.split(", ")
    
    corresp = []
    corresp_section = soup.find_all("div", style="padding:10px 0;")[1].text 
    
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    abstract = str(soup.find("div", class_ ="Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace('<br/>', ' ').replace("&lt;", "<").replace("&gt;", ">")
    
    abstract = abstract.split(". ")
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp
    
    keywords = str(soup.find("div", class_ ="Abstract").find_all("dd")[1]).replace('<dd class="j_text_size"><strong>Keywords</strong> : ',"").replace("</dd>","")
    keywords = preprocessed(keywords)
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_kjo(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    origin_section01 = soup.find("div", class_ = "origin_section01")
    origin_section02 = soup.find("div", class_ = "origin_section02")
    origin_section03 = soup.find("div", class_ = "origin_section03", id="body00")
    
    journal_title = "Korean Journal of Orthodontics"
    copyright = "© The Korean Association of Orthodontists"
    
    publication = origin_section01.find_all("p")[0].text 
    published = origin_section01.find_all("p")[1].text 
    published = published[ : published.find("Publication Date")]
    
    publication =  publication[ : publication.find("http")]
    doi = origin_section01.find_all("p")[0].text 
    doi = doi[doi.find("http") : ]
    
    article_title = str(origin_section02.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    
    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace('<p>', "").replace("</p>", "")
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")

    authors = authors.split(", ")

    corresp_section = str(origin_section02.find_all("p")[2]).replace("<p>", "").replace("</p>", "")
    if "<br/><br/>" in corresp_section:
        corresp_section = corresp_section[ : corresp_section.find("<br/><br/>")]
    
    corresp = []
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ",""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    abstract = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[0])
    abstract = preprocessed(abstract)
    
    abstract = abstract.replace("<p>","").replace("</p>", "").replace("<br/>", " ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt :
            txt = txt[txt.find("</b>") : ]
        txt = txt.replace("</b> ","").replace("<b>", "").replace("</br>" , "")
        tmp.append(txt)
    abstract = tmp
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
    
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    
    abstract = tmp
    
    keywords = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[1])
    keywords = preprocessed(keywords)
    keywords = keywords.replace("<p>","").replace("</p>", "")
    keywords = keywords.replace(",",";")
    keywords = keywords.replace("<strong>Keywords</strong>: ","")
    
    imgs = []
    try:
        graphic_abstract = soup.find("div", class_="origin_section03", id="body01").find("p").find("img")
        imgs.append(graphic_abstract['src'])
    except:
        pass
    
    figs = soup.find_all("img", class_ = "view_img pointer")
    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_kjpp(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    origin_section01 = soup.find("div", class_ = "origin_section01")
    origin_section02 = soup.find("div", class_ = "origin_section02")
    origin_section03 = soup.find("div", class_ = "origin_section03", id="body00")
    
    journal_title = "Korean Journal of Phsiology and Pharmacology"
    copyright = "© Korean J Physiol Pharmacol"
    
    publication = origin_section01.find_all("p")[0].text 
    published = origin_section01.find_all("p")[1].text 
    published = published[ : published.find("http")]
    
    publication =  publication[ : publication.find("http")]
    doi = origin_section01.find_all("p")[1].text 
    doi = doi[doi.find("http") : ]
    
    article_title = str(origin_section02.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    
    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace("<p>","").replace("</p>","")
    authors = authors.replace("and ",", ")
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace("and ", ", ").replace("*", "").replace("Md","")
    authors = re.sub(r'[0-9]+', '', authors)
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        
        tmp.append(auth.replace(".","").replace(",", ""))
    authors = tmp
    for auth in authors:
        if auth == "" or auth == " ":
            authors.remove(auth)
    corresp_section = str(origin_section02)
    corresp_section = corresp_section[corresp_section.find("Correspondence to") : ]
    corresp = []
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ", ""):
            corresp.append(auth)

    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    abstract = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[0])
    abstract = preprocessed(abstract)
    
    abstract = abstract.replace('<p style="margin:5px;">',"").replace("</p>", "").replace("<br/>", " ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt :
            txt = txt[txt.find("</b>") : ]
        txt = txt.replace("</b> ","").replace("<b>", "").replace("</br>" , "")
        tmp.append(txt)
    abstract = tmp
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    
    abstract = tmp
    
    keywords = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[1])
    keywords = preprocessed(keywords)
    keywords = keywords.replace("<p>","").replace("</p>", "")
    keywords = keywords.replace(",",";")
    keywords = keywords.replace("<strong>Keywords</strong>: ","")
    
    imgs = []
    try:
        graphic_abstract = soup.find("div", class_="origin_section03", id="body01").find("p").find("img")
        imgs.append(graphic_abstract['src'])
    except:
        pass
    
    figs = soup.find_all("img", class_ = "view_img pointer")
    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}
    
def metadata_type_vsijournal(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    article_info01 = soup.find("div", class_ = "article-info")
    article_info02 = soup.find("div", class_ = "article-info02")
    
    journal_title = "Vascular Specialist International"
    copyright = "© The Korean Society for Vascular Surgery"
    
    article_title = str(article_info01.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>","").replace("</h2>", "")
    
    authors = str(article_info01.find("div", class_ = "authors"))
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    authors = authors.replace('<div class="authors">', "").replace('</div>', "")
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    authors = authors.replace("*", "").replace("and ",", ")
    authors = authors.split(", ")
    
    tmp = []
    for auth in authors:
        if auth == "" or auth == " ":
            authors.remove(auth)
    
    corresp_section = article_info01.find("div", class_ = "corres-author").text
    corresp = []
    
    for auth in authors:
        if auth.replace(" ","") in corresp_section.replace(" ",""):
            corresp.append(auth)
            
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    publication = article_info02.find_all("p")[0].text
    published = article_info02.find_all("p")[1].text
    published = published[ : published.find("http")]
    doi = article_info02.find_all("p")[1].text
    doi = doi[doi.find("http") : ]
    
    
    abstract = str(soup.find("div", class_ = "article-info03 mb40", id="body00").find("div", class_ = "article-text mb40"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<div class="article-text mb40">', "").replace("</div>", "").replace("&lt;", "<").replace("&gt;", ">").replace("–", "-")
    abstract = abstract.replace("vs. ", "vs.").replace("<br/>"," ")
    abstract = abstract.split(". ")
    tmp = []
    for abs in abstract:
        txt = abs
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ","")
        txt = txt + "."
        txt = txt.replace(".." , ".")
        
        tmp.append(txt.replace("</br>", " "))
    while True:
        lower_exist = False
        i = 0
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        
        if lower_exist == False:
            break
        

    abstract = tmp
    try:
        keywords = soup.find("div", class_ = "article-info03 mb40", id="body00").find_all("div", class_ = "article-text")[1].text
        keywords = keywords.replace(",", ";")
    except:
        keywords = "No Keywords"

    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer btn_file")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp

    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_acb(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    origin_section01 = soup.find("div", class_ = "origin_section01")
    origin_section02 = soup.find("div", class_ = "origin_section02")
    origin_section03 = soup.find("div", class_ = "origin_section03", id="body00")
    
    journal_title = "Anatomy and Cell Biology"
    copyright = "© Korean Association of ANATOMISTS"
    
    publication = origin_section01.find_all("p")[0].text 
    published = origin_section01.find_all("p")[1].text 
    
    publication =  publication[ : publication.find("http")]
    doi = origin_section01.find_all("p")[2].text 
    doi = doi[doi.find("http") : ]
    
    article_title = str(origin_section02.find("h2"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace("<h2>", "").replace("</h2>", "")
    
    if article_title == "":
        origin_section02 = soup.find("div", class_ = "origin_section02  bt-none")
        article_title = str(origin_section02.find("h2"))
        article_title = preprocessed(article_title)
        article_title = article_title.replace("<h2>", "").replace("</h2>", "")

    authors = str(origin_section02.find_all("p")[0])
    authors = authors.replace("<p>","").replace("</p>","")
    authors = authors.replace("and ",", ")
    
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace("and ", ", ").replace("*", "").replace("Md","")
    authors = re.sub(r'[0-9]+', '', authors)
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    
    
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        
        tmp.append(auth.replace(".","").replace(",", ""))
    authors = tmp
    for auth in authors:
        if auth == "" or auth == " ":
            authors.remove(auth)
    
    
    corresp_section = str(origin_section02)
    
    corresp_section = corresp_section[corresp_section.find("Correspondence to") : ]
    if "<br/><br/>" in corresp_section:
        corresp_section = corresp_section[ : corresp_section.find("<br/><br/>")]

    corresp = []
    if len(authors) == 1:
        corresp.append(authors[0])
    else:
        for auth in authors:
            if auth.replace(" ","") in corresp_section.replace(" ", ""):
                corresp.append(auth)

        
        for cor in corresp:
            for auth in authors:
                if auth in cor:
                    authors.remove(auth)
        corresp = ", ".join(corresp)
    try:
        abstract = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[0])
        abstract = preprocessed(abstract)
        
        abstract = abstract.replace('<p style="margin:5px;">',"").replace("</p>", "").replace("<br/>", " ")
        abstract = abstract.split(". ")
        tmp = []
        for abs in abstract:
            txt = abs
            if "</b>" in txt :
                txt = txt[txt.find("</b>") : ]
            txt = txt.replace("</b> ","").replace("<b>", "").replace("</br>" , "")
            tmp.append(txt)
        abstract = tmp
        
        while True:
            i = 0
            lower_exist = False
            for abs in abstract:
                try:
                    if abstract[i + 1][0].islower():
                        abstract[i] = abstract[i] +". " + abstract[i+1]
                        abstract.remove(abstract[i+1])
                        
                except:
                    pass
                i += 1
            for abs in abstract:
                if abs[0].islower():
                    lower_exist = True
                else:
                    pass
            if lower_exist == False:
                break
            
            
        tmp = []
        for abs in abstract:
            txt = abs+"."
            txt = txt.replace("..", ".")
            tmp.append(txt)
        
        abstract = tmp
    except:
        abstract = []
    keywords = "No Keywords"
    
    try:
        keywords = str(origin_section03.find("div", class_ = "go_section", id="fulltext_Area").find_all("p")[1])
        keywords = preprocessed(keywords)
        keywords = keywords.replace("<p>","").replace("</p>", "")
        keywords = keywords.replace(",",";")
        keywords = keywords.replace("<strong>Keywords</strong>: ","")
    except:
        pass
    
    
    imgs = []
    try:
        graphic_abstract = soup.find("div", class_="origin_section03", id="body01").find("p").find("img")
        imgs.append(graphic_abstract['src'])
    except:
        pass
    
    figs = soup.find_all("img", class_ = "view_img pointer")
    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_wjmh(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "World Journal of Men's Health"
    copyright = "© 2022 Korean Society for Sexual Medicine and Andrology"
    
    article_title = str(soup.find("span", class_ ="tl-document"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<span class="tl-document"><left>','').replace('</left></span>','').replace("\n","")
    
    article_front_0 = soup.find("div", id="article-level-0-front")
    publication = article_front_0.find_all("table")[0].find_all("tr")[1].text
    publication = publication[ : publication.find("Published")]
    
    published = article_front_0.find_all("table")[0].find_all("tr")[1].text
    published = published[published.find("Published") : ]
    published = published[ : published.find("http")]
    published = published.replace("\xa0","")
    
    doi = article_front_0.find_all("table")[0].find_all("tr")[1].text
    doi = doi[doi.find("http") : ]
    doi = doi.replace("\n","")

    trs = article_front_0.find_all("table")[1].find_all("tr")
    authors = trs[2].text.replace('\n', ' ').replace(' and', ', ')
    authors = re.sub(r'[0-9]+', ' ', authors)
    
    authors = authors.split(", ")
    
    tmp = []
    for auth in authors:
        if auth == "" or auth == " ":
            pass
        else:
            tmp.append(auth.replace(",", ""))
    authors = tmp
    corresp = []
    
    for auth in authors:
        if "*" in auth:
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp).replace("*","")
    if corresp == "":
        corresp = []
        corresp_section = str(article_front_0.find_all("table")[1])
        corresp_section = corresp_section[corresp_section.find("Correspondence") : ]
        for auth in authors:
            if auth.replace(" ", "") in corresp_section.replace(" ", ""):
                corresp.append(auth)
        
        for cor in corresp:
            for auth in authors:
                if auth in cor:
                    authors.remove(auth)
                    
        corresp = ", ".join(corresp).replace("*","")
        
        
    trs = article_front_0.find_all("table")[1].find_all("tr")
    
    abstract = trs[len(trs) - 1].find_all("p")
    tmp = []
    for abs in abstract:
        tmp.append(str(abs).replace("<p>","").replace("</p>", ""))
        
    abstract = tmp
    abstract = " ".join(abstract)
    abstract = preprocessed(abstract)
    
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("div", id="article-level-0-end-metadata").find_all("span", class_ = "capture-id")
    tmp = []
    for keyword in keywords:
        txt = str(keyword).replace('<span class="capture-id">', '').replace('</span>','')
        txt = preprocessed(txt)
        tmp.append(txt)
    
    keywords = tmp
    keywords = "; ".join(keywords)
    
    figs = soup.find_all("img", border="1")
    imgs = []
    for fig in figs:
        if "wjmh" in fig['src']:
            txt = "https://wjmh.org" + fig['src']
            txt = txt.replace(".jpg","-l.jpg")
            
            imgs.append(txt)    
    figs = soup.find_all("img", border="0")
    for fig in figs:
        if "wjmh" in fig['src']:
            txt = "https://wjmh.org" + fig['src']
            txt = txt.replace(".jpg","-l.jpg")
            imgs.append(txt)    
        
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_aon(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')

    journal_title = "Asian Oncology Nursing"
    copyright = "© 2022 Korean Oncology Nursing Society"
    
    article_title = str(soup.find_all("span", class_ ="tl-document")[1])
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<span class="tl-document"><left>','').replace('</left></span>','').replace("\n","")
    
    article_front_0 = soup.find("div", id="article-level-0-front")
    publication = article_front_0.find_all("table")[0].find_all("tr")[1].text
    publication = publication[ : publication.find("Published")]
    
    published = article_front_0.find_all("table")[0].find_all("tr")[1].text
    published = published[published.find("Published") : ]
    published = published[ : published.find("http")]
    published = published.replace("\xa0","")
    
    doi = article_front_0.find_all("table")[0].find_all("tr")[1].text
    doi = doi[doi.find("http") : ]
    doi = doi.replace("\n","")
    
    trs = str(article_front_0.find_all("table")[1])
    authors = trs[trs.find(str(soup.find_all("span", class_ ="tl-document")[1])) : ].replace(str(soup.find_all("span", class_ ="tl-document")[1]), '')
    authors = authors[authors.find('<td align="left" colspan="2" valign="top">') : ].replace('<td align="left" colspan="2" valign="top">', '')
    authors = authors[ : authors.find('</td></tr>')]
    
    authors = authors.split('\n')
    
    for auth in authors:
        if auth == "" or auth == " ":
            authors.remove(auth)
    corresp = []
    for auth in authors:
        if "corresp" in auth:
            corresp.append(auth)
    for cor in corresp:
        for auth in authors:
            if auth in cor :
                authors.remove(auth)
    corresp = ", ".join(corresp)
    corresp = corresp.replace('</a>','').replace('</span>', '')
    corresp = corresp.replace('<span class="capture-id">', '')
    pattern = re.compile(u'<span.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    spans = re.findall(pattern, corresp)
    for span in spans:
        corresp = corresp.replace(span, "")
    
    pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, corresp)
    for a_tag in a_tags:
        corresp = corresp.replace(a_tag, "")

    pattern = re.compile(u'<img.*?"/>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, corresp)
    
    for img_tag in img_tags:
        corresp = corresp.replace(img_tag, "")
        
    corresp = corresp[ : corresp.find('<')]
    corresp = corresp.replace(' and', '')
    tmp = []
    for auth in authors:
        txt = auth
        pattern = re.compile(u'<span.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        spans = re.findall(pattern, txt)
        for span in spans:
            txt = txt.replace(span, "")
        
        pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        a_tags = re.findall(pattern, txt)
        for a_tag in a_tags:
            txt = txt.replace(a_tag, "")

        pattern = re.compile(u'<img.*?"/>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        img_tags = re.findall(pattern, txt)
        
        for img_tag in img_tags:
            txt = txt.replace(img_tag, "")
        txt = txt[ : txt.find("<")]
        tmp.append(txt)
    authors = tmp
    
    trs = article_front_0.find_all("table")[1].find_all("tr")
    abstract = trs[len(trs) - 1].find_all("p")
    tmp = []
    for abs in abstract:
        tmp.append(str(abs).replace("<p>","").replace("</p>", ""))
        
    abstract = tmp
    abstract = " ".join(abstract)
    abstract = preprocessed(abstract)
    
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    imgs = []
    figs = soup.find_all("img", border="0")
    for fig in figs:
        if "aon" in fig['src']:
            img_url = "https://aon.or.kr" + fig['src'].replace('.jpg', '-l.jpg')
            if img_url not in imgs:
                
                imgs.append(img_url)
                
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_algae(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    copyright = "© 2022 The Korean Society of Phycology"
    journal_title = "Algae"
    
    article_front = soup.find("div", id="article-front", class_ = "front")
    publication = article_front.find_all("p", class_ = "metadata-entry")[0].text
    published = article_front.find_all("p", class_ = "metadata-entry")[1].text
    doi = article_front.find_all("p", class_ = "metadata-entry")[2].text
    doi = doi.replace('DOI: ', '')
    
    article_title = str(soup.find("h3", class_ = "PubTitle"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '')
    
    authors = str(soup.find_all("div", class_ = "metadata-group author_layer")[1])
    authors = authors.replace('<div class="metadata-group author_layer" style="margin-bottom:10px; color: #000000;">', '').replace('</div>', '').replace("\n", "")
    
    pattern = re.compile(u'<a.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    authors = authors.replace('</a>', '').replace("<sup>*</sup>", "*")
    pattern = re.compile(u'<sup.*sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    authors = authors.split(", ")
    
    tmp = []
    for auth in authors:
        txt = auth
        sups = re.findall(pattern, txt)
        for sup in sups:
            txt = txt.replace(sup, "")
        tmp.append(txt)
    authors = tmp
    corresp = []
    for auth in authors:
        if "*" in auth:
            corresp.append(auth)
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)

    corresp = ", ".join(corresp)
    corresp = corresp.replace("*", "")
    
    abstract = soup.find("div", class_ ="abstract")
    
    abstract = str(abstract.find("div", class_ = "first"))
    abstract = preprocessed(abstract)
    
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, abstract)
    
    for a_tag in a_tags:
        abstract = abstract.replace(a_tag, "")
    
    abstract = abstract.replace("</div>", "").replace('vs. ','vs.')
    pattern = re.compile(u'<div.*>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    div_tags = re.findall(pattern, abstract)
    for div_tag in div_tags:
        abstract = abstract.replace(div_tag, "")
    
    abstract = abstract.split(". ")
    
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".").replace('vs.','vs. ')
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("div", class_ ="abstract").find("p", class_ = "metadata-entry").text
    keywords = keywords.replace("Key words: ", "")
    
    
    
    figs = soup.find_all("img", align="middle")
    imgs = []
    for fig in figs:
        if "algae" in fig['src']:
            img_url = "https://www.e-algae.org" + fig['src']
            img_url = img_url.replace('//thumbnails', '/thumbnails')
        if img_url not in imgs:
            imgs.append(img_url)
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}
    
def metadata_type_aair(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Allergy, Asthma & Immunology Research"
    copyright = "© The Korean Academy of Asthma, Allergy and Clinical Immunology"
    
    article_title = str(soup.find("span", class_ ="tl-document"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<span class="tl-document"><left>','').replace('</left></span>','').replace("\n","")
    
    article_front_0 = soup.find("div", id="article-level-0-front")
    publication = article_front_0.find_all("table")[0].find_all("tr")[1].text
    publication = publication[ : publication.find("Published")]
    
    published = article_front_0.find_all("table")[0].find_all("tr")[1].text
    published = published[published.find("Published") : ]
    published = published[ : published.find("http")]
    
    doi = article_front_0.find_all("table")[0].find_all("tr")[1].text
    doi = doi[doi.find("http") : ]
    doi = doi.replace("\n","")

    trs = article_front_0.find_all("table")[1].find_all("tr")
    authors = trs[2].find_all("span")
    tmp = []
    
    for auth in authors:
        txt = auth.find("a").text    
        if txt not in tmp:
            tmp.append(txt)
    
    authors = tmp
    
    corresp = []
    
    corresp_section = str(article_front_0.find_all("table")[1])
    corresp_section = corresp_section[corresp_section.find("Correspondence") : ].replace("\n","")
    corresp_section = corresp_section[ : corresp_section.find('<div class="fm-footnote"')]

    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ",""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    trs = article_front_0.find_all("table")[1].find_all("tr")
    
    abstract = trs[len(trs) - 1].find_all("p")
    tmp = []
    for abs in abstract:
        tmp.append(str(abs).replace("<p>","").replace("</p>", ""))
        
    abstract = tmp
    abstract = " ".join(abstract)
    abstract = preprocessed(abstract)
    
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("div", id="article-level-0-end-metadata").find_all("span", class_ = "capture-id")
    tmp = []
    for keyword in keywords:
        txt = str(keyword).replace('<span class="capture-id">', '').replace('</span>','')
        txt = preprocessed(txt)
        tmp.append(txt)
    
    keywords = tmp
    keywords = "; ".join(keywords)
    
    figs = soup.find_all("img", border="1")
    imgs = []
    for fig in figs:
        if "aair" in fig['src']:
            txt = "https://e-aair.org" + fig['src']
            txt = txt.replace(".jpg","-l.jpg")
            
            imgs.append(txt)    
    figs = soup.find_all("img", border="0")
    for fig in figs:
        if "aair" in fig['src']:
            txt = "https://e-aair.org" + fig['src']
            txt = txt.replace(".jpg","-l.jpg")
            imgs.append(txt)    
        
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_apm(doi: str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Anesthesia & Pain Medicine"
    copyright = "© Anesthesia and Pain Medicine"
    
    article_title = str(soup.find("h3", class_ = "PubTitle"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '')
    
    metadata_table = soup.find("div", class_ = "metadata two-column table")
    metadata_entry = metadata_table.find_all("p", class_="metadata-entry")
    publication = metadata_entry[0].text
    published = metadata_entry[1].text
    doi = metadata_entry[2].text.replace('DOI: ', '')
    
    authors = str(soup.find_all("div", class_ = "metadata-group author_layer")[1])
    authors = authors.replace('<div class="metadata-group author_layer" style="margin-bottom:10px; color: #000000;">', '').replace('</div>', '')
    authors = authors.replace('</a>', '')
    
    pattern = re.compile(u'<a.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
        
    pattern = re.compile(u'<img.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, authors)
    for img_tag in img_tags:
        authors = authors.replace(img_tag, "")
    authors = authors.replace('\n','')
    
    pattern = re.compile(u'<sup.*/sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        txt = auth
        sups = re.findall(pattern, txt)
        for sup in sups:
            txt = txt.replace(sup, "")
        if txt not in tmp:
            tmp.append(txt)
    authors = tmp    
    
    corresp_section = str(soup.find('div', class_ = "corresp"))
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)

    abstract = str(soup.find("div", class_ = "abstract").find('div', class_ = "first"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace("</div>", "")
    pattern = re.compile(u'<div.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    div_tags = re.findall(pattern, abstract)
    for div_tag in div_tags:
        abstract = abstract.replace(div_tag, "")
    
    if abstract == "None":
        abstract = ""
        abs_group = soup.find("div", class_ = "abstract").find_all("div", class_ = "section")
        
        for section in abs_group:
            abstract += " " + str(section.find("div")).replace("</div>", "")
        
        pattern = re.compile(u'<div.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        div_tags = re.findall(pattern, abstract)
        
        for div_tag in div_tags:
            abstract = abstract.replace(div_tag, "")
        abstract = preprocessed(abstract)
        
    
    abstract = abstract.split(". ")
    
    
    for abs in abstract:
        if abs == "" or abs == " ":
            abstract.remove(abs)
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("p", class_ = "metadata-entry_k").text
    keywords = keywords.replace("Keywords: ","")
    
    
    figs = soup.find_all("img")
    imgs = []
    for fig in figs:
        if "thumbnails/apm" in fig['src']:
            img_url = "https://www.anesth-pain-med.org" + fig['src'].replace("//thumbnails", "/thumbnails")
            if img_url not in imgs:
                imgs.append(img_url)
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_agmr(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Annals of Geriatiric Medicine and Research"
    copyright = "© Korean Geriatrics Society"
    
    article_title = str(soup.find("h3", class_ = "PubTitle"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '')
    
    metadata_table = soup.find("div", class_ = "metadata two-column table")
    metadata_entry = metadata_table.find_all("p", class_="metadata-entry")
    publication = metadata_entry[0].text
    published = metadata_entry[1].text
    doi = metadata_entry[2].text.replace('DOI: ', '')
    
    authors = str(soup.find_all("div", class_ = "metadata-group author_layer")[1])
    authors = authors.replace('<div class="metadata-group author_layer" style="margin-bottom:10px; color: #000000;">', '').replace('</div>', '')
    authors = authors.replace('</a>', '')
    
    pattern = re.compile(u'<a.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
        
    pattern = re.compile(u'<img.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, authors)
    for img_tag in img_tags:
        authors = authors.replace(img_tag, "")
    authors = authors.replace('\n','')
    
    pattern = re.compile(u'<sup.*/sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        txt = auth
        sups = re.findall(pattern, txt)
        for sup in sups:
            txt = txt.replace(sup, "")
        if txt not in tmp:
            tmp.append(txt)
    authors = tmp    
    
    corresp_section = str(soup.find('div', class_ = "corresp"))
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    abstract = str(soup.find("div", class_ = "abstract").find('div', class_ = "first"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace("</div>", "")
    pattern = re.compile(u'<div.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    div_tags = re.findall(pattern, abstract)
    for div_tag in div_tags:
        abstract = abstract.replace(div_tag, "")
    
    if abstract == "None":
        abstract = ""
        abs_group = soup.find("div", class_ = "abstract").find_all("div", class_ = "section")
        
        for section in abs_group:
            abstract += " " + str(section.find("div")).replace("</div>", "")
        
        pattern = re.compile(u'<div.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        div_tags = re.findall(pattern, abstract)
        
        for div_tag in div_tags:
            abstract = abstract.replace(div_tag, "")
        abstract = preprocessed(abstract)
        
    
    abstract = abstract.split(". ")
    
    
    for abs in abstract:
        if abs == "" or abs == " ":
            abstract.remove(abs)
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("p", class_ = "metadata-entry_k").text
    keywords = keywords.replace("Key words: ","").replace(",", ";")
    
    figs = soup.find_all("img")
    imgs = []
    for fig in figs:
        if "thumbnails/agmr" in fig['src']:
            img_url = "https://www.e-agmr.org" + fig['src'].replace("//thumbnails", "/thumbnails")
            if img_url not in imgs:
                imgs.append(img_url)
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_apem(doi: str): 
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Annals of Pediatric Endocrinology & Metabolism"
    copyright = "© Annals of Pediatric Endocrinology & Metabolism"
    
    article_title = str(soup.find("h3", class_ = "PubTitle"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '')
    
    metadata_table = soup.find("div", class_ = "metadata two-column table")
    metadata_entry = metadata_table.find_all("p", class_="metadata-entry")
    publication = metadata_entry[0].text
    published = metadata_entry[1].text
    doi = metadata_entry[2].text.replace('DOI: ', '')
    
    authors = str(soup.find_all("div", class_ = "metadata-group author_layer")[1])
    authors = authors.replace('<div class="metadata-group author_layer" style="margin-bottom:10px; color: #000000;">', '').replace('</div>', '')
    authors = authors.replace('</a>', '')
    
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.replace("M.D.", "").replace("Ph.D.", "").replace("B.S.", "").replace("Ph.D","").replace("M.D", "").replace("Md. ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace("and ", ",")
    
    pattern = re.compile(u'<a.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
        
    pattern = re.compile(u'<img.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, authors)
    for img_tag in img_tags:
        authors = authors.replace(img_tag, "")
    authors = authors.replace('\n','')
    
    pattern = re.compile(u'<sup.*/sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        txt = auth
        sups = re.findall(pattern, txt)
        for sup in sups:
            txt = txt.replace(sup, "")
        if txt not in tmp:
            tmp.append(txt)
    authors = tmp    
    
    corresp_section = str(soup.find('div', class_ = "corresp"))
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)

    abstract = soup.find("div", class_ = "abstract")
    if abstract == None:
        abstract = str(soup.find("div", id="article-body", class_ = "body").find("div", class_ = "first"))
        abstract = abstract.replace("</div>", "").replace("</a>", "")
        pattern = re.compile(u'<div.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        div_tags = re.findall(pattern, abstract)
        for div_tag in div_tags:
            abstract = abstract.replace(div_tag, "")
        pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        a_tags = re.findall(pattern, abstract)
        for a_tag in a_tags:
            abstract = abstract.replace(a_tag, "")
        abstract = abstract.replace("[]","").replace("()","")
        
    else:
        abstract = str(abstract.find('div', class_ = "first"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace("</div>", "")
    pattern = re.compile(u'<div.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    div_tags = re.findall(pattern, abstract)
    for div_tag in div_tags:
        abstract = abstract.replace(div_tag, "")
    
    if abstract == "None":
        abstract = ""
        abs_group = soup.find("div", class_ = "abstract").find_all("div", class_ = "section")
        
        for section in abs_group:
            abstract += " " + str(section.find("div")).replace("</div>", "")
        
        pattern = re.compile(u'<div.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        div_tags = re.findall(pattern, abstract)
        
        for div_tag in div_tags:
            abstract = abstract.replace(div_tag, "")
        abstract = preprocessed(abstract)
    
    abstract = abstract.split(". ")

    for abs in abstract:
        if abs == "" or abs == " ":
            abstract.remove(abs)
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break

    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp

    try:
        keywords = soup.find("p", class_ = "metadata-entry_k").text
        keywords = keywords.replace("Keywords: ","").replace(",", ";")
    except:
        keywords = "No Keywords"
    
    figs = soup.find_all("img")
    imgs = []
    for fig in figs:
        if "thumbnails/apem" in fig['src']:
            img_url = "https://e-apem.org" + fig['src'].replace("//thumbnails", "/thumbnails")
            if img_url not in imgs:
                imgs.append(img_url)
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_arm(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Annals of Rehabilitation Medicine"
    copyright = "© by Korean Academy of Rehabilitation Medicine"
    
    article_title = str(soup.find("h3", class_ = "PubTitle"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '')
    
    metadata_table = soup.find("div", class_ = "metadata two-column table")
    metadata_entry = metadata_table.find_all("p", class_="metadata-entry")
    publication = metadata_entry[0].text
    published = metadata_entry[1].text
    doi = metadata_entry[2].text.replace('DOI: ', '')
    
    authors = str(soup.find_all("div", class_ = "metadata-group author_layer")[1])
    authors = authors.replace('<div class="metadata-group author_layer" style="margin-bottom:10px; color: #000000;">', '').replace('</div>', '')
    authors = authors.replace('</a>', '')
    
    authors = authors.replace("PhD", "").replace("MSc","").replace("MD","").replace("BPharm","").replace("  "," ").replace("(HKU)", "")
    authors = authors.replace("Phoebe ","").replace("MBCHB (OTAGO)", "").replace("MRCS (EDIN)", "").replace("MSCPD (CARDIFF)", "").replace("MBBS", "")
    authors = authors.replace("DFM", "").replace("DPD", "").replace("(HK)", "").replace("MRCSED", "").replace("PGDIPCLINDERM", "").replace("(QMUL)", "")
    authors = authors.replace("MSc", "").replace("FCOHK", "").replace("MBChB", "").replace("(CUHK)", "").replace("DCH", "").replace("(Sydney)", "").replace("Dip Derm", "")
    authors = authors.replace("(Glasgow)", "").replace("Ms Clin Derm", "").replace("(Cardiff)", "").replace("Ms PD", "").replace("FHKAM","").replace("(MED)", "")
    authors = authors.replace("FHKCP", "").replace("MSc PD","").replace("MRCP", "").replace("(UK)", "").replace("(Wales)", "").replace("PG Dip Clin Derm", "").replace("(London)", "")
    authors = authors.replace("Grad Dip Derm", "").replace("(NUS)", "").replace("DDME", "").replace("FCSHK", "").replace("CPD (CARDIFF)", "").replace("PD", "").replace("Dip Med ", "")
    authors = authors.replace("M.D.", "").replace("Ph.D.", "").replace("B.S.", "").replace("Ph.D","").replace("M.D", "").replace("Md. ", "")
    authors = authors.encode("utf-8").decode("ascii", 'ignore').replace("and ", ",")
    
    pattern = re.compile(u'<a.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
        
    pattern = re.compile(u'<img.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, authors)
    for img_tag in img_tags:
        authors = authors.replace(img_tag, "")
    authors = authors.replace('\n','')
    
    pattern = re.compile(u'<sup.*/sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    authors = authors.split(", ")
    tmp = []
    for auth in authors:
        txt = auth
        sups = re.findall(pattern, txt)
        for sup in sups:
            txt = txt.replace(sup, "")
        if txt not in tmp:
            tmp.append(txt)
    authors = tmp    
    for auth in authors:
        if auth == "" or auth == " ":
            authors.remove(auth)
            
    corresp_section = str(soup.find('div', class_ = "corresp"))
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    abstract = soup.find("div", class_ = "abstract")
    if abstract == None:
        abstract = str(soup.find("div", id="article-body", class_ = "body").find("div", class_ = "first"))
        abstract = abstract.replace("</div>", "").replace("</a>", "")
        pattern = re.compile(u'<div.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        div_tags = re.findall(pattern, abstract)
        for div_tag in div_tags:
            abstract = abstract.replace(div_tag, "")
        pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        a_tags = re.findall(pattern, abstract)
        for a_tag in a_tags:
            abstract = abstract.replace(a_tag, "")
        abstract = abstract.replace("[]","").replace("()","")
        
    else:
        abstract = str(abstract.find('div', class_ = "first"))
    abstract = preprocessed(abstract)
    abstract = abstract.replace("</div>", "")
    pattern = re.compile(u'<div.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    div_tags = re.findall(pattern, abstract)
    for div_tag in div_tags:
        abstract = abstract.replace(div_tag, "")
    
    if abstract == "None":
        abstract = ""
        abs_group = soup.find("div", class_ = "abstract").find_all("div", class_ = "section")
        
        for section in abs_group:
            abstract += " " + str(section.find("div")).replace("</div>", "")
        
        pattern = re.compile(u'<div.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        div_tags = re.findall(pattern, abstract)
        
        for div_tag in div_tags:
            abstract = abstract.replace(div_tag, "")
        abstract = preprocessed(abstract)
    
    abstract = abstract.split(". ")

    for abs in abstract:
        if abs == "" or abs == " ":
            abstract.remove(abs)
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break

    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    try:
        keywords = soup.find("p", class_ = "metadata-entry_k").text
        keywords = keywords.replace("Keywords: ","").replace(",", ";")
    except:
        keywords = "No Keywords"
        
    
    figs = soup.find_all("img")
    imgs = []
    for fig in figs:
        if "thumbnails/arm" in fig['src']:
            img_url = "https://www.e-arm.org" + fig['src'].replace("//thumbnails", "/thumbnails")
            if img_url not in imgs:
                imgs.append(img_url)
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_astr(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Annals of Suergical Treatment and Research"
    copyright = "© the Korean Surgical Society"
    
    article_title = str(soup.find("span", class_ ="tl-document"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<span class="tl-document"><left>','').replace('</left></span>','').replace("\n","")
    
    article_front_0 = soup.find("div", id="article-level-0-front")
    publication = article_front_0.find_all("table")[0].find_all("tr")[1].text
    publication = publication[ : publication.find("Published")]
    
    published = article_front_0.find_all("table")[0].find_all("tr")[1].text
    published = published[published.find("Published") : ]
    published = published[ : published.find("http")]
    
    doi = article_front_0.find_all("table")[0].find_all("tr")[1].text
    doi = doi[doi.find("http") : ]
    doi = doi.replace("\n","")
    
    trs = article_front_0.find_all("table")[1].find_all("tr")
    authors =str(trs[2].find("td"))
    authors = authors.replace('<td align="left" colspan="2" valign="top">', '').replace('</td>', '')
    authors = authors.replace('<span class="capture-id">', '').replace('</span>', '').replace('</a>', '')
    
    pattern = re.compile(u'<span.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    span_tags = re.findall(pattern, authors)
    for span_tag in span_tags:
        authors = authors.replace(span_tag, '')
    pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, '')
    pattern = re.compile(u'<img.*?"/>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    img_tags = re.findall(pattern, authors)
    for img_tag in img_tags:
        authors = authors.replace(img_tag, '')
    authors = authors.split("\n")
    tmp = []
    for auth in authors:
        
        txt = auth[ : auth.find('<sup>')]
        txt = txt.replace(",","").replace(" and ","")
        tmp.append(txt)
    authors = tmp
    for auth in authors:
        if auth == "" or auth ==" ":
            authors.remove(auth)
    
    
    corresp_section = str(article_front_0.find_all("table")[1])
    corresp_section = corresp_section[corresp_section.find("Corresponding") : ]
    corresp_section = corresp_section[ : corresp_section.find("</span><br/>")]
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ",""):
            corresp.append(auth)
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    corresp = ", ".join(corresp)
    
    trs = article_front_0.find_all("table")[1].find_all("tr")
    
    abstract = trs[len(trs) - 1].find_all("p")
    tmp = []
    for abs in abstract:
        tmp.append(str(abs).replace("<p>","").replace("</p>", ""))
        
    abstract = tmp
    abstract = " ".join(abstract)
    abstract = preprocessed(abstract)
    abstract = abstract.replace('</span>','')
    pattern = re.compile(u'<span.*?"/>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    span_tags = re.findall(pattern, abstract)
    
    for span_tag in span_tags:
        abstract = abstract.replace(span_tag, '')
        
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i + 1][0].islower():
                    abstract[i] = abstract[i] +". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
                    
            except:
                pass
            i += 1
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
        if lower_exist == False:
            break
        
        
    tmp = []
    for abs in abstract:
        txt = abs+"."
        txt = txt.replace("..", ".")
        tmp.append(txt)
    abstract = tmp
    
    keywords = soup.find("div", id="article-level-0-end-metadata").find_all("span", class_ = "capture-id")
    tmp = []
    for keyword in keywords:
        txt = str(keyword).replace('<span class="capture-id">', '').replace('</span>','')
        txt = preprocessed(txt)
        tmp.append(txt)
    
    keywords = tmp
    keywords = "; ".join(keywords)
    
    figs = soup.find_all("img", border="1")
    imgs = []
    for fig in figs:
        if "astr" in fig['src']:
            txt = "https://astr.or.kr" + fig['src']
            txt = txt.replace(".jpg","-l.jpg")
            
            imgs.append(txt)    
    figs = soup.find_all("img", border="0")
    for fig in figs:
        if "astr" in fig['src']:
            txt = "https://astr.or.kr" + fig['src']
            txt = txt.replace(".jpg","-l.jpg")
            imgs.append(txt)    
        
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_appmicro(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Applied Microscopy"
    copyright = "© Korean Society of Microscopy"
    
    list_top = soup.find("div", class_ = "list_top")
    article_title = str(list_top.find("div", class_="tit j_text_size"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<div class="tit j_text_size">', '').replace('</div>', '')
    
    
    publication = list_top.find_all("div", class_="author j_text_size")[0].text
    publication = publication[:publication.find("http")]
    doi = list_top.find("div", style="padding-left: 10px").text
    published = list_top.find_all("div", class_="author j_text_size")[1].text
    
    authors = str(soup.find_all("div", style="padding:10px 0;")[0].find("div", class_ = "bold j_text_size")).replace('<div class="bold j_text_size">', '').replace('</div>','')
    authors = authors.replace(" and", ", ")
    
    authors = authors.split(", ")
    
    corresp = []
    if len(authors) == 1:
        corresp.append(authors[0])
        authors = []
    else:
        for auth in authors:
            if "*" in auth:
                corresp.append(auth)
        
        for cor in corresp:
            for auth in authors:
                if cor in auth:
                    authors.remove(cor)
    
    tmp = []
    for auth in authors:
        txt = auth
        pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        sups = re.findall(pattern, auth)
        for sup in sups:
            txt = txt.replace(sup, '').replace(",","")
        tmp.append(txt)
    authors = tmp
    
    tmp = []
    for cor in corresp:
        txt = cor
        pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        sups = re.findall(pattern, cor)
        for sup in sups:
            txt = txt.replace(sup, '').replace(",","")
        tmp.append(txt)
    corresp = tmp
    
    abstract = str(soup.find_all("div", class_ ="section")[0].find_all("dd")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<dd class="j_text_size">', '').replace('</dd>', '').replace('<p>','').replace('</p>','').replace("vs. ", 'vs.').replace('<br/>', ' ').replace("&lt;", "<").replace("&gt;", ">")
    
    abstract = abstract.split(". ")
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp    
    keywords = str(soup.find_all("div", class_ ="section")[0].find_all("dd")[1]).replace('<dd class="j_text_size">', '').replace('</dd>', '').replace('<p>','').replace('</p>','')
    keywords = preprocessed(keywords)
    keywords = keywords.replace('<strong>Keywords</strong> : ', "")
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_ajbc(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Asian Journal of Beauty & Cosmetology"
    copyright = "© Korea Institute of Dermatological Sciences"
    publication = soup.find_all("p", class_ = "metadata-entry")[1].text
    published = soup.find_all("p", class_ = "metadata-entry")[2].text
    doi = soup.find_all("p", class_ = "metadata-entry")[3].text
    doi = doi.replace('DOI: ', '')
    
    article_title = str(soup.find_all("h3", class_ = "PubTitle")[1])
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '').replace('\n','')
    
    authors = soup.find_all('div', class_ = "metadata-group author_layer")[1]
    authors = authors.find_all("a")
    tmp = []
    for auth in authors:
        tmp.append(auth.text)
    authors = tmp
    
    corresp_section = str(soup.find("div", class_ = "corresp"))
    corresp = []
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(' ', ''):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp).replace("*" ,"")
    
    sections = soup.find_all("div", class_ = "abstract")[1].find_all("div", class_ = "section")
    abstract = ""
    for section in sections:
        txt = str(section.find("div"))
        txt = txt.replace("</div>", "")
        txt = txt[txt.find('">') : ].replace('">', '').replace("&lt;", "<").replace("&gt;", ">").replace("’", "'")
        txt = preprocessed(txt)
        abstract += " " + txt
    
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp
    
    keywords = str(soup.find_all("div", class_ = "abstract")[1].find("p", class_ = "metadata-entry"))
    keywords = keywords.replace('<p class="metadata-entry">' , '').replace('</p>', '')
    keywords = keywords.replace('</a>', '')
    keywords = keywords.replace('<span class="generated">', '')
    keywords = keywords.replace('</span>', '').replace('<b>Keywords</b>: ', '').replace(',', ';')

    pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, keywords)
    for a_tag in a_tags:
        keywords = keywords.replace(a_tag, '')  
    
    figs = soup.find_all('div',  class_ ="fig panel")
    imgs = []
    for fig in figs:
        imgs.append("https://www.e-ajbc.org" + fig.find('img')['src'].replace('//thumbnails', '/thumbnails'))
    
        return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_eksss(doi : str):
    
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    
    journal_title = "Phonetics and Speech Sciences"
    copyright = "© Korean Society of Speech Sciences"
    
    published = soup.find("p", class_ = "epub-date").text
    article_metadata = soup.find("div", class_ = "article_meta_data")
    publication = article_metadata.find_all("p")[0].text 
    doi = article_metadata.find_all("p")[2].text.replace('DOI: ', '') 

    article_title = str(soup.find("div", class_ = "metadata main-top-title-trans"))

    if article_title == "None":
        article_title = str(soup.find("h1", class_ = "metadata main-top-title citation_title"))
    article_title = article_title.replace("                     ", " ").replace('     ', ' ').replace('     ', ' ')
    article_title = article_title.replace('<div class="metadata main-top-title-trans">', '').replace("</div>", '')
    
    article_title = article_title.replace('</h1>','')
    pattern = re.compile(u'<h1.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    h1_tags = re.findall(pattern, article_title)
    for h1_tag in h1_tags:
        article_title = article_title.replace(h1_tag, '') 
    
    
    article_title = article_title.replace('</a>','')
    pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, article_title)
    for a_tag in a_tags:
        article_title = article_title.replace(a_tag, '')    
    article_title = preprocessed(article_title)
    article_title = article_title.replace("*", "").replace('\n', '')
    contrib_group = soup.find_all("div", class_ = "contrib-group")
    if len(contrib_group) > 1:
        authors = str(soup.find_all("div", class_ = "contrib-group")[1])
    else:
        authors = str(soup.find_all("div", class_ = "contrib-group")[0])
    
    authors = authors.replace('<div class="contrib-group">', '').replace('</div>', '')
    authors = authors.replace('<span class="citation_author">', '').replace('</span>', '')
    authors = authors.replace('<sup>*</sup>', '*').replace('<sup>**</sup>', '*').replace('\n', '')
    authors = re.sub(r'[0-9]+', '', authors)

    authors = authors.split(", ")
    
    tmp = []
    for auth in authors:
        txt = auth
        pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        sups = re.findall(pattern, auth)
        for sup in sups:
            txt = txt.replace(sup, '').replace(",","").replace('<sup>', '').replace('</sup>', '')
        tmp.append(txt)
    authors = tmp
    
    corresp = []
    for auth in authors:
        if "*" in auth:
            corresp.append(auth)

    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(cor)
    corresp = ", ".join(corresp)
    corresp = corresp.replace('*' ,'')
    
    abstract_sections = soup.find_all("div", class_ = "abstract")
    if len(abstract_sections) > 1:
        abstract = str(soup.find_all("div", class_ = "abstract")[1].find("p"))
    else:    
        abstract = str(soup.find_all("div", class_ = "abstract")[0].find("p"))

    abstract = abstract.replace("</p>", '').replace('                     ', ' ').replace('     ', ' ')

    pattern = re.compile(u'<p.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, abstract)
    
    for a_tag in a_tags:
        abstract = abstract.replace(a_tag, '')  
    
    abstract = preprocessed(abstract).replace("\n", "").replace("\t","")
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp
    
    keywords = ""
    divs = soup.find_all("div")
    for div in divs:
        if "Keywords: " in str(div):
            keywords = str(div)
    keywords = keywords.replace('<div class="">', '').replace('</div>', '').replace('<span class="generated"><span class="keywords_title">Keywords: </span> </span>', "")
    keywords = preprocessed(keywords)
    
    figs = soup.find_all("img", class_ = "fig_img")
    imgs = []
    for fig in figs:
        imgs.append("https://www.eksss.org" + fig['src'])

    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_aspin(doi : str):
    html_req = proxy.get_requests(doi)
    soup = BeautifulSoup(html_req.content, 'html.parser')
    journal_title = "Asian Spine Journal"
    copyright = "© by Korean Society of Spine Surgery"
    
    publication = soup.find_all("p", class_ = "metadata-entry")[1].text
    published = soup.find_all("p", class_ = "metadata-entry")[2].text
    doi = soup.find_all("p", class_ = "metadata-entry")[3].text
    doi = doi.replace('DOI: ', '')
    
    article_title = str(soup.find("h3", class_ = "PubTitle"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<h3 class="PubTitle">', '').replace('</h3>', '').replace('\n','')
    
    authors = str(soup.find_all("div", class_ = "metadata-group author_layer")[1])
    authors = authors.replace('<div class="metadata-group author_layer" style="margin-bottom:10px; color: #000000;">', '').replace('</div>', '').replace("\n", "")
    
    pattern = re.compile(u'<a.*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    pattern = re.compile(u'<a.*?a>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, authors)
    for a_tag in a_tags:
        authors = authors.replace(a_tag, "")
    authors = authors.replace('</a>', '').replace("<sup>*</sup>", "*")
    pattern = re.compile(u'<sup.*sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    
    authors = authors.split(", ")
    
    tmp = []
    for auth in authors:
        txt = auth
        sups = re.findall(pattern, txt)
        for sup in sups:
            txt = txt.replace(sup, class_ = "corresp")
        tmp.append(txt)
    authors = tmp
    corresp = []
    corresp_section = str(soup.find('div', class_ ="corresp"))
    for auth in authors:
        if auth.replace(' ', '') in corresp_section.replace(' ', ''):
            corresp.append(auth)
    
    for cor in corresp :
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
                

    corresp = ", ".join(corresp)
    corresp = corresp.replace("*", "")
    
    sections = soup.find_all("div", class_ = "abstract")[0].find_all("div", class_ = "section")
    abstract = ""
    for section in sections:
        txt = str(section.find("div"))
        txt = txt.replace("</div>", "")
        txt = txt[txt.find('">') : ].replace('">', '').replace("&lt;", "<").replace("&gt;", ">").replace("’", "'")
        txt = preprocessed(txt)
        abstract += " " + txt
    
    abstract = abstract.split(". ")
    
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp
    
    keywords = str(soup.find_all("div", class_ = "abstract")[0].find("p", class_ = "metadata-entry_k"))
    keywords = keywords.replace('<p class="metadata-entry_k" style="margin-top:10px;">' , '').replace('</p>', '')
    keywords = keywords.replace('</a>', '')
    keywords = keywords.replace('<span class="generated">', '')
    keywords = keywords.replace('</span>', '').replace('<b>Keywords</b>: ', '').replace(',', ';')
    
    pattern = re.compile(u'<a.*?">', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    a_tags = re.findall(pattern, keywords)
    for a_tag in a_tags:
        keywords = keywords.replace(a_tag, '') 
        

    figs = soup.find_all("div", class_ = "fig panel")
    imgs = []
    for fig in figs:
        imgs.append("https://www.asianspinejournal.org" + fig.find('img')['src'].replace('//thumbnails', '/thumbnails'))
    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords, "correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}

def metadata_type_ijstemcell(doi : str):
    html_req = proxy.get_requests(doi)
    content = html_req.content   
    soup = BeautifulSoup(content, 'html.parser')
    copyright = "© Korean Society for Stem Cell Research"
    journal_title = "International Journal of Stem Cells"
    
    list_top = soup.find("div", class_ = "list_top")
    article_title = str(list_top.find("div", class_="tit j_text_size"))
    article_title = preprocessed(article_title)
    article_title = article_title.replace('<div class="tit j_text_size">', '').replace('</div>', '')
    publication = list_top.find_all("div", class_="author j_text_size")[0].text
    publication = publication[:publication.find("http")]
    doi = list_top.find_all("div", style="padding-top: 5px;")[0].find("a")['href']
    published = list_top.find_all("div", class_="author j_text_size")[1].text.replace('\xa0', '')
    
    authors = str(soup.find_all("div", style="padding:10px 0;")[0].find("div", class_ = "bold j_text_size")).replace('<div class="bold j_text_size">', '').replace('</div>','')
    pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    sups = re.findall(pattern, authors)
    
    for sup in sups:
        authors = authors.replace(sup, "")
    
    authors = authors.split(", ")
    
    corresp = []
    corresp_section = soup.find_all("div", style="padding:10px 0;")[1].text 
    
    for auth in authors:
        if auth.replace(" ", "") in corresp_section.replace(" ", ""):
            corresp.append(auth)
    
    for cor in corresp:
        for auth in authors:
            if auth in cor:
                authors.remove(auth)
    
    corresp = ", ".join(corresp)
    
    abstract = str(soup.find("div", class_ ="Abstract").find_all("dd")[0])
    abstract = preprocessed(abstract)
    abstract = abstract.replace('<dd class="j_text_size" style="text-align:justify;">', '').replace('</dd>', '').replace("vs. ", 'vs.').replace('<br/>', ' ').replace("&lt;", "<").replace("&gt;", ">")
    
    abstract = abstract.split(". ")
    while True:
        i = 0
        lower_exist = False
        for abs in abstract:
            try:
                if abstract[i+1][0].islower():
                    abstract[i] = abstract[i] + ". " + abstract[i+1]
                    abstract.remove(abstract[i+1])
            except:
                pass
            i += 1
        
        for abs in abstract:
            if abs[0].islower():
                lower_exist = True
            else:
                pass
            
        if lower_exist == False:
            break
        
    tmp = []
    for abs in abstract:
        txt = abs.replace("vs.", "vs. ")
        if "</b>" in txt:
            txt = txt[txt.find("</b> ") : ].replace("</b> ", "")
            
        
        txt = txt + "."
        
        txt = txt.replace("..", ".")
        tmp.append(txt)
        
    abstract = tmp
    
    keywords = str(soup.find("div", class_ ="Abstract").find_all("dd")[1]).replace('<dd class="j_text_size"><strong>Keywords</strong> : ',"").replace("</dd>","")
    keywords = preprocessed(keywords)
    
    imgs = []
    figs = soup.find_all("img", class_ = "view_img pointer")

    for fig in figs:
        imgs.append(fig['src'].replace("thumb/", ""))
        
    
    tmp = []
    for img in imgs:
        if img not in tmp:
            tmp.append(img)
    imgs = tmp

    
    return {"journal_title" : journal_title, "article_title" : article_title, "keywords" : keywords,"correspondence" : corresp, "copyright" : copyright, "doi" : doi, "authors" : authors, "abstract" : abstract, "images" : imgs, "published" : published, "publication" : publication}


    
    