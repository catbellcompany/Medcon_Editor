from fileinput import filename
import textwrap
from tkinter.messagebox import NO

from database.schemas import Scene_Rscs
from PIL import Image, ImageDraw, ImageFont
import os 
import textwrap
import re
import random
from nltk import word_tokenize
from PIL import Image
import string

class scene_Creator:
    def __init__(self, scene_info : Scene_Rscs, path : str):
        self.user_key  = scene_info.user_key
        self.project_name = scene_info.project_name
        self.project_key = scene_info.project_key
        self.correspond = scene_info.correspond.replace(",", ",\n")
        self.authors = scene_info.authors
        self.doi = scene_info.doi
        self.copyright = scene_info.copyright
        self.image_url_list = scene_info.image_url_list
        self.article_title = scene_info.article_title
        self.abstract = scene_info.abstract
        self.save_path = path + "/"
        self.temp_type = scene_info.template_type
        self.keywords = scene_info.keywords
        self.author_img = scene_info.author_img
        #sans_semibold = os.getcwd().replace("\\", "/") + "/sources/" + "fonts/" + "NotoSans/" + "NotoSans-SemiBold.ttf"
        #sans_semibold_italic = os.getcwd().replace("\\", "/") + "/sources/" + "fonts/" + "NotoSans/" + "NotoSans-SemiBoldItalic.ttf"
        sans_bold = os.getcwd().replace("\\", "/") + "/sources/" + "fonts/" + "NotoSans/" + "NotoSans-Bold.ttf"
        #sans_bold_italic = os.getcwd().replace("\\", "/") + "/sources/" + "fonts/" + "NotoSans/" + "NotoSansMedium-RegularItalic.ttf"
        sans_medium = os.getcwd().replace("\\", "/") + "/sources/" + "fonts/" + "NotoSans/" + "NotoSans-Medium.ttf"
        
        self.font_article_title = ImageFont.truetype(sans_bold, size = 40)
        
        #self.font_article_title_l = ImageFont.truetype(sans_bold_italic, size = 40)
        #self.font_subtitle = ImageFont.truetype(NotoSans-Medium.ttf, size = 30)
        #self.font_subtitle_l = ImageFont.truetype(sans_semibold_italic, size = 30)

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

    def preprocessing(self, text : str):
        pattern = re.compile(u'<sup.*?sup>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        sups = re.findall(pattern, text)
        if sups != []:
            for sup in sups:
                text =text.replace(sup, self.get_super(sup))
        text = text.replace("<ˢᵘᵖ>", "").replace("</ˢᵘᵖ>", "")
        pattern = re.compile(u'<sub.*?sub>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
        subs = re.findall(pattern, text)
        if subs != []:
            for sub in subs:
                text = text.replace(sub, self.get_sub(sub))
        text = text.replace("<ₛᵤ♭>", "").replace("</ₛᵤ♭>", "")
        text = text.replace("<i>", "<italic>").replace("</i>", "</italic>")
        return text

    def get_cover_name(self):
        if "10.14348" in self.doi:
            cover_name = "molcells.png"
        elif "10.5090" in self.doi or "jchestsurg" in self.doi:
            cover_name = "jchestsurg.png"
        
        elif "cpn" in self.doi or "10.9758" in self.doi:
            cover_name ="cpn.png"
            
        elif "10.18528" in self.doi or "ijgii" in self.doi:
            cover_name = "ijgii.png"
        elif "epain" in self.doi or "10.3344" in self.doi:
            cover_name = "pain.png"
        elif "e-jecoenv" in self.doi or "10.5141" in self.doi:
            cover_name = "jecoenv.png"
        elif "biomolther" in self.doi or "10.4062" in self.doi:
            cover_name = "biomolther.png"
        elif "bmbreports" in self.doi or "10.5483" in self.doi:
            cover_name = "bmbreports.png"
        elif "10.5009" in self.doi:
            cover_name = "gutnliver.png"
        elif "10.51507" in self.doi:
            cover_name = "journal-jams.png"
        elif "10.15430" in self.doi:
            cover_name = "jcpjournal.png"
        elif "e-jmis" in self.doi or "10.7602" in self.doi:
            cover_name = "jmis.png"
        elif "ijstemcell" in self.doi or "10.15283" in self.doi:
            cover_name = "ijstemcell.png"
        elif "10.5056" in self.doi:
            cover_name = "jnmjournal.png"
        elif "10.3831" in self.doi:
            cover_name = "jop.png"
        elif "10.15324" in self.doi:
            cover_name = "kjcls.png"
        elif "10.4041" in self.doi:
            cover_name = "kjo.png"
        elif "10.4196" in self.doi:
            cover_name = "kjpp.png"
        elif "10.5758" in self.doi:
            cover_name = "vsijournal.png"
        elif "10.11106" in self.doi:
            cover_name = "ijthyroid.png"
        elif "10.5115" in self.doi:
            cover_name = "acb.png"
        elif "10.5534" in self.doi:
            cover_name = "wjmh.PNG"
        elif "10.4490" in self.doi:
            cover_name = "algae.png"
        elif "10.4168" in self.doi:
            cover_name = "aair.png"
        elif "10.17085" in self.doi:
            cover_name = "apm.png"
        elif "10.4235" in self.doi:
            cover_name ="agmr.png"
        elif "10.6065" in self.doi:
            cover_name = "apem.png"
        elif "e-arm" in self.doi or "10.5535" in self.doi:
            cover_name = "arm.png"
        elif "10.4174" in self.doi:
            cover_name = "astr.png"
        elif "10.9729" in self.doi or "appmicro" in self.doi :
            cover_name = "appmicro.png"
        
        
        return cover_name

    def get_logo_img(self):
        logo_list = []
        
        if "10.14348" in self.doi:
            logo_list = ["SCIE.png", "Scopus.png", "PMC.png", "kci.png"]
            
        elif "10.5090" in self.doi or "jchestsurg" in self.doi:
            logo_list = ["PMC.png", "Scopus.png", "kci.png"]
            
        elif "10.18528" in self.doi:
            logo_list = ["ESCI_logo_t.png", "Scopus.png", "kci.png"]
        
        elif "epain" in self.doi or "10.3344" in self.doi:
            logo_list = ["SCIE.png", "Scopus.png", "PMC.png", "kci.png"]
        
        elif "e-jecoenv" in self.doi or "10.5141" in self.doi:
            logo_list = ["Scopus.png","kci.png"]
        
        elif "10.4062" in self.doi:  
            logo_list = ["Scopus.png", "kci.png", "SCIE.png", "PMC.png"]
        
        elif "bmbreports" in self.doi or "10.5483" in self.doi:
            logo_list = ["SCIE.png", "kci.png", "Medline.png", "PMC.png", "Scopus.png"]
        
        elif "10.5009" in self.doi:
            logo_list = ["Scopus.png", "PMC.png", "kci.png", "Medline.png", "SCIE.png"]
        
        elif "10.51507" in self.doi:
            logo_list = ["ESCI_logo_t.png", "Scopus.png", "kci.png", "Medline.png" ]
        
        elif "10.15430" in self.doi:
            logo_list = ["ESCI_logo_t.png", "PMC.png", "kci.png"]
            
        elif "e-jmis" in self.doi or "10.7602" in self.doi:
            logo_list = ["PMC.png"]

        elif "cpn" in self.doi or "10.9758" in self.doi:
            logo_list = ["kci.png", "SCIE.png", "PMC.png", "Scopus.png"]
            
        elif "10.5056" in self.doi:
            logo_list = ["Scopus.png", "SCIE.png", "kci.png", "PMC.png"]
            
        elif "10.3831" in self.doi:
            logo_list = ["ESCI_logo_t.png", "kci.png", "Scopus.png", "PMC.png"]
        
        elif "10.15324" in self.doi:
            logo_list = ["kci.png"]
        
        elif "10.4041" in self.doi:
            logo_list = ["kci.png", "PMC.png", "Scopus.png", "SCIE.png"]
        
        elif "10.4196" in self.doi:
            logo_list = ["Scopus.png", "SCIE.png", "PMC.png", "kci.png"]
            
        elif "10.5758" in self.doi:
            logo_list = ["PMC.png", "Scopus.png", "kci.png"]
            
        elif "10.11106" in self.doi:
            logo_list = ["kci.png"]
            
        elif "10.5115" in self.doi:
            logo_list = ["Scopus.png", "ESCI_logo_t.png", "PMC.png"]
            
        elif "10.5534" in self.doi: 
            logo_list = ["SCIE.png", "Scopus.png", "PMC.png", "kci.png"]
        
        elif "10.4490" in self.doi:
            logo_list = ["SCIE.png", "Scopus.png"]
            
        elif "10.4168" in self.doi:
            logo_list = ["PMC.png", "SCIE.png"]
        
        elif "10.17085" in self.doi:
            logo_list = ["PMC.png"]
        
        elif "10.4235" in self.doi:
            logo_list = ["PMC.png"]
        
        elif "10.6065" in self.doi:
            logo_list = ["ESCI_logo_t.png", "PMC.png", "Scopus.png"]
            
        elif "e-arm" in self.doi or "10.5535" in self.doi:
            logo_list = ["ESCI_logo_t.png", "PMC.png", "Scopus.png"]
        elif "10.4174" in self.doi:
            logo_list = ["SCIE.png", "PMC.png", "Scopus.png"]
        elif "10.4174" in self.doi:
            logo_list = ["SCIE.png", "PMC.png", "Scopus.png"]
        elif "10.9729" in self.doi or "appmicro" in self.doi :
            logo_list = ["kci.png"]
        elif "biomolther" in self.doi or "10.4062" in self.doi:
            logo_list = ["kci.png", ]
        left = 1920
        logo_dict_list = []
        i = 0
        for logo_name in logo_list:
            image = Image.open(os.getcwd().replace("\\", "/") + "/sources/images/logo/" + logo_name)
            left -= image.width
            image.close()
            logo_dict = {
                            "id": "StaticImage_logo_" + str(i),
                            "name": "logo_" + str(i),
                            "stroke": None,
                            "strokeWidth": 0,
                            #계산 후 들어감
                            "left": left,
                            "top": 1000,
                            "width": image.width,
                            "height": 50,
                            "opacity": 1,
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticImage",
                            
                            "visible": True,
                            "src": "http://218.52.115.188:7000/LogoImage/{}".format(logo_name) + "/",
                            "cropX": 0,
                            "cropY": 0,
                            "metadata": {}
                        }
            i += 1
            logo_dict_list.append(logo_dict)
        return logo_dict_list

    def creat_json(self):
        #생성된 자막 이미지 수 만큼 생성
        final_json = {}

        if self.temp_type == 0:
            scenes  = []
            
            index = 0
            img_ind = 0
            tokens = word_tokenize(self.article_title)
            lines = 1
            w = 0
            
            for token in tokens:
                width, height = self.font_article_title.getsize(token + " ")
                w += width
                if w > 1440:
                    w = 0 
                    lines += 1
                    
                
            print(lines)
            if lines == 1:
                text_top = 65.9
            elif lines == 2:
                text_top = 40
            elif lines == 3:
                text_top = 18.4
            elif lines == 4:
                text_top = 0
            print(text_top)
            
            for abs in self.abstract:
                if img_ind > len(self.image_url_list) - 1:
                    img_ind = 0
                    
                if self.image_url_list == []:
                    img_url = ""
                    img_width = 1560
                else:
                    img_url = self.image_url_list[img_ind][0]
                    img_width = self.image_url_list[img_ind][1]

                scene = {
                    "id": self.project_key + "-" + str(index),
                    "name": self.project_name + "-" + str(index),
                    "duration": 5000,
                    "layers": [
                            { ## 백그라운드 영역
                                "id": "background",
                                "name": "background",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 0,
                                "top": 0,
                                "width": 1920,
                                "height": 1080,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "Background",
                                
                                "visible": True,
                                "fill": "#ffffff",
                                "metadata": {}
                            },
                            {
                            "id": "StaticPath_articleTitle",
                            "name": "articleTitle",
                            "left": 360,
                            "top": 0,
                            "width": 1560,
                            "height": 180,
                            "type": "StaticPath",
                            "path": [
                                ["M", 1560, 0],
                                ["L", 0, 0],
                                ["L", 0, 180],
                                ["L", 1560, 180],
                                ["L", 1560, 0],
                                ["Z"]
                            ],
                            "fill": "#0B9281",
                            },
                            
                            #저자 배경 영역 Blugray
                            {
                                "id": "StaticPath_authors",
                                "name": "authors",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 0,
                                "top": 0,
                                "width": 360,
                                "height": 980,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticPath",

                                
                                "visible": True,
                                
                                "path": [
                                    ["M", 360, 0],
                                    ["L", 0, 0],
                                    ["L", 0, 980],
                                    ["L", 360, 980],
                                    ["L", 360, 0],
                                    ["Z"]
                                ],
                                "fill": "#4f6575",
                                "metadata": {}
                            },
                            #자막 배경 영역
                            {
                                "id": "StaticPath_abstract",
                                "name": "abstract",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 360,
                                #Edited
                                "top": 790,
                                "width": 1560,
                                #Edited
                                "height": 130,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticPath",

                                
                                "visible": True,
                                
                                "path": [
                                            ["M", 1560, 0],
                                            ["L", 0, 0],
                                            ["L", 0, 130],
                                            ["L", 1560, 130],
                                            ["L", 1560, 0],
                                            ["Z"]
                                        ],
                                "fill": "#ededed",
                                "metadata": {}
                            },
                            
                            { ## 키워드 배경 레이어
                                "id": "StaticPath_keyword",
                                "name": "keyword",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 360,
                                "top": 920,
                                "width": 1560,
                                "height": 60,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticPath",

                                
                                "visible": True,
                                
                                "path": [
                                    ["M", 1560, 0],
                                    ["L", 0, 0],
                                    ["L", 0, 60],
                                    ["L", 1560, 60],
                                    ["L", 1560, 0],
                                    ["Z"]
                                ],
                                "fill": "#dbdbdb",
                                "metadata": {}
                            },

                            { ## 저작권 배경 레이어
                                "id": "StaticPath_copyright",
                                "name": "copyright",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 0,
                                "top": 980,
                                "width": 1920,
                                "height": 100,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticPath",
                                
                                "visible": True,
                                
                                "path": [
                                    ["M", 1920, 0],
                                    ["L", 0, 0],
                                    ["L", 0, 100],
                                    ["L", 1920, 100],
                                    ["L", 1920, 0],
                                    ["Z"]
                                ],
                                "fill": "#000000",
                                "metadata": {}
                            },

                            
                            {   ##커버 이미지 레이어
                                "id": "StaticImage_cover",
                                "name": "cover",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 60,
                                "top": 40,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticImage",
                                
                                "visible": True,
                                
                                # 커버 URL
                                "src": 'http://218.52.115.188:7000/CoverImage/' + self.get_cover_name() + "/",
                                
                                "cropX": 0,
                                "cropY": 0,
                                "metadata": {}
                            },

                            {   ## 교신저자 레이어
                                "id": "StaticText_correspondence",
                                "name": "correspondence",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 30,
                                "top": 600,
                                "width": 300,
                                "height": 45,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",
                                
                                "visible": True,
                                
                                "charSpacing": 0,
                                "fill": "#ffffff",
                                "fontFamily": "NotoSans-Medium",
                                "fontSize": 33,
                                "lineHeight": 1.16,
                                ## 교신저자 텍스트
                                "text": self.correspond,
                                "textAlign": "center",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                            },

                            {   ## 공동저자 레이어
                                "id": "StaticText_authors",
                                "name": "authors",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 30,
                                "top": 680,
                                "width": 300,
                                "height": 53.7,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",
                                "visible": True,
                                
                                "charSpacing": 0,
                                "fill": "#ffffff",
                                "fontFamily": "NotoSans-Regular",
                                "fontSize": 22,
                                "lineHeight": 1.16,
                                #공동저자 텍스트
                                "text": self.authors.replace(";", ","),
                                "textAlign": "center",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                            },

                            {   ##타이틀 텍스트
                                "id": "StaticText_articleTitle",
                                "name": "articleTitle",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                ##Edited
                                "left": 420,
                                "top": text_top,
                                "width": 1440,
                                "height": 100,
                                #Edited
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",

                                "visible": True,
                                
                                #Edited
                                "charSpacing": 0,
                                "fill": "#ffffff",
                                "fontFamily": "NotoSans-Bold",
                                "fontSize": 40,
                                "lineHeight": 1.16,
                                #텍스트 영역
                                "text" : self.article_title,
                                "textAlign": "center",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Bold.woff2"
                            },

                            {   ##센터 이미지 레이어
                                "id": "StaticImage_centerImg",
                                "name": "centerImg",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": ((1560 - img_width) / 2) + 360,
                                "top": 210,
                                "width": img_width,
                                ## Edited
                                "height": 580,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticImage",
                                
                                
                                
                                
                                "visible": True,
                                
                                #이미지 URL
                                "src": img_url,
                                "cropX": 0,
                                "cropY": 0,
                                "metadata": {}
                            },

                            {   ##자막 텍스트 레이어
                                "id": "StaticText_abstract",
                                "name": "abstract",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                #Edited
                                "left": 420,
                                "top": 790,
                                #Edited
                                "width": 1440,
                                "height": 130,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",

                                "visible": True,
                                
                                
                                #Edited
                                "fill": "#000000",
                                "fontFamily": "NotoSans-Medium",
                                "fontSize": 30,
                                "lineHeight": 1.16,
                                #Edited
                                
                                "charSpacing": 0,
                                #자막 이미지 URL
                                "text": abs.replace("'", "’"),
                                "textAlign": "left",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                            },

                            { ## 키워드 타이틀 레이어
                                "id": "StaticText_keywordTitle",
                                "name": "keywordTitle",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 417,
                                "top": 934,
                                "width": 125,
                                "height": 31,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",

                                "visible": True,
                                
                                "charSpacing": 0,
                                "fill": "#444444",
                                "fontFamily": "NotoSans-Bold",
                                "fontSize": 25,
                                "lineHeight": 1,
                                "text": "KEYWORD",
                                "textAlign": "left",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Bold.woff2"
                            },

                            { ## 키워드 텍스트 레이어
                                "id": "StaticText_keyword",
                                "name": "keyword",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 588,
                                "top": 934,
                                "width": 1275,
                                "height": 31,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",

                                "visible": True,
                                
                                "charSpacing": 0,
                                "fill": "#444444",
                                "fontFamily": "NotoSans-Medium",
                                "fontSize": 25,
                                "lineHeight": 1,
                                "text": self.keywords.replace("'", "’"),
                                "textAlign": "left",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                            },
                            
                            {   ##저자 이미지 레이어
                                "id": "StaticImage_authors",
                                "name": "authors",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 108,
                                "top": 427,
                                "width": 144,
                                "height": 144,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticImage",

                                "visible": True,
                                
                                "src": self.author_img,
                                "cropX": 0,
                                "cropY": 0,
                                "metadata": {}
                            },
                    
                            {   ## DOI 주소 레이어
                                "id": "StaticText_doi",
                                "name": "doi",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 30,
                                "top": 1005,
                                "width": 800,
                                "height": 22.6,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",

                                "visible": True,
                                
                                "charSpacing": 0,
                                "fill": "#ffffff",
                                "fontFamily": "NotoSans-Regular",
                                "fontSize": 20,
                                "lineHeight": 1.16,
                                "text": self.doi,
                                "textAlign": "left",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                            },
                    
                            {   ##저작권 정보 레이어
                                "id": "StaticText_copyright",
                                "name": "copyright",
                                
                                "stroke": None,
                                "strokeWidth": 0,
                                "left": 30,
                                "top": 1030,
                                "width": 800,
                                "height": 22.6,
                                "opacity": 1,
                                
                                "originY": "top",
                                "scaleX": 1,
                                "scaleY": 1,
                                "type": "StaticText",

                                "visible": True,
                                
                                "charSpacing": 0,
                                "fill": "#ffffff",
                                "fontFamily": "NotoSans-Regular",
                                "fontSize": 20,
                                "lineHeight": 1.16,
                                "text": self.copyright,
                                "textAlign": "left",
                                "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                            }
                    
                            ## 로고레이어
                            
                    ] + self.get_logo_img()
                    
                }

                scenes.append(scene)
                index += 1
                img_ind += 1

            final_json = {
                "id": self.project_key,
                "name": self.project_name,
                "frame": { "width": 1920, "height": 1080 },
                "scenes": scenes,
                "metadata": {},
                "preview": ""
            }
            
        elif self.temp_type == 1:
            scenes  = []
            index = 0
            img_ind = 0
            cover_scene = {
                    "id": self.project_key + "_cover",
                    "name": self.project_name + "_cover",
                    "duration": 5000,
                    "layers": [
                        { ## 배경 레이어
                            "id": "background",
                            "name": "background",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 0,
                            "top": 0,
                            "width": 1920,
                            "height": 1080,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "Background",

                            "visible": True,
                            "fill": "#ffffff",
                            "metadata": {}
                            },
                
                    
                        { ## 타이틀 텍스트 레이어
                            "id": "StaticText_articleTitle",
                            "name": "articleTitle",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 900,
                            "top": 101,
                            "width": 970,
                            "height": 168,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#222222",
                            "fontFamily": "NotoSans-Bold",
                            "fontSize": 45,
                            "lineHeight": 1.16,
                            "text": self.article_title,
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Bold.woff2"
                        },
                        
                        
                        { ## 교신저자 텍스트 레이어
                            "id": "StaticText_correspondence",
                            "name": "correspondence",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 1095,
                            "top": 424,
                            "width": 610,
                            "height": 50,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#444444",
                            "fontFamily": "NotoSans-Medium",
                            "fontSize": 40,
                            "lineHeight": 1.16,
                            "text": self.correspond,
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                        },
                        
                        { ## 공동저자 텍스트 레이어
                            "id": "StaticText_authors",
                            "name": "authors",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 1095,
                            "top": 520,
                            "width": 610,
                            "height": 50,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#222222",
                            "fontFamily": "NotoSans-Regular",
                            "fontSize": 30,
                            "lineHeight": 1.16,
                            "text": self.authors.replace(";", ","),
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                        },
                        
                        { ## 키워드 타이틀 레이어
                            "id": "StaticText_keywordTitle",
                            "name": "keywordTitle",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 900,
                            "top": 917,
                            "width": 125,
                            "height": 62,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            "shadow": True,
                            "charSpacing": 0,
                            "fill": "#999999",
                            "fontFamily": "NotoSans-Bold",
                            "fontSize": 22,
                            "lineHeight": 1.16,
                            "text": "KEYWORDS",
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Bold.woff2"
                        },
                        
                        { ## 키워드 텍스트 레이어
                            "id": "StaticText_keyword",
                            "name": "keyword",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 1071,
                            "top": 917,
                            "width": 700,
                            "height": 62,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#444444",
                            "fontFamily": "NotoSans-Medium",
                            "fontSize": 22,
                            "lineHeight": 1.16,
                            "text": self.keywords.replace("'", "’"),
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                        },
                        
                        { ## 커버 이미지 레이어
                            "id": "StaticImage_cover",
                            "name": "cover",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 100,
                            "top": 101,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 2.74,
                            "scaleY": 2.74,
                            "type": "StaticImage",

                            "visible": True,
                            
                            "src": 'http://218.52.115.188:7000/CoverImage/' + self.get_cover_name() + "/",
                            "cropX": 0,
                            "cropY": 0,
                            "metadata": {}
                        },
                        
                        { ## 저자 이미지 레이어
                            "id": "StaticImage_authors",
                            "name": "authors",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 900,
                            "top": 374,
                            "width": 150,
                            "height": 150,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticImage",

                            "visible": False,
                            "shadow": False,
                            "src": self.author_img,
                            "cropX": 0,
                            "cropY": 0,
                            "metadata": {}
                        }
                    ]
                }
            scenes.append(cover_scene)
            
            tokens = word_tokenize(self.article_title)
            lines = 1
            w = 0
            
            for token in tokens:
                width, height = self.font_article_title.getsize(token + " ")
                w += width
                if w > 1560:
                    w = 0 
                    lines += 1

            
            if lines == 1:
                text_top = 65.9
            elif lines == 2:
                text_top = 40
            elif lines == 3:
                text_top = 18.4
            elif lines == 4:
                text_top = 0
                
            print(text_top)
            for abs in self.abstract:
                if img_ind > len(self.image_url_list) - 1:
                    img_ind = 0
                    
                if self.image_url_list == []:
                    img_url = ""
                    img_width = 900
                else:
                    img_url = self.image_url_list[img_ind][0]
                    img_width = self.image_url_list[img_ind][1]
                scene = {
                    "id": self.project_key + "-" + str(index),
                    "name": self.project_name + "-" + str(index),
                    "duration": 5000,
                    "layers": [
                        
                        { ## 배경 레이어
                            "id": "background",
                            "name": "background",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 0,
                            "top": 0,
                            "width": 1920,
                            "height": 1080,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "Background",

                            "visible": True,
                            "fill": "#ffffff",
                            "metadata": {}
                        },
                        
                        { ## 자막 배경 레이어
                            "id": "StaticPath_abstract",
                            "name": "abstract",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 0,
                            "top": 830,
                            "width": 1920,
                            "height": 150,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticPath",

                            "visible": True,
                            
                            "path": [
                                ["M", 1920, 0],
                                ["L", 0, 0],
                                ["L", 0, 150],
                                ["L", 1920, 150],
                                ["L", 1920, 0],
                                ["Z"]
                            ],
                            "fill": "#ededed",
                            "metadata": {}
                        },
                    
                        { ## 저작권 배경 레이어
                            "id": "StaticPath_copyright",
                            "name": "copyright",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 0,
                            "top": 980,
                            "width": 1920,
                            "height": 100,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticPath",

                            "visible": True,
                            
                            "path": [
                                ["M", 1920, 0],
                                ["L", 0, 0],
                                ["L", 0, 100],
                                ["L", 1920, 100],
                                ["L", 1920, 0],
                                ["Z"]
                            ],
                            "fill": "#000000",
                            "metadata": {}
                        },

                    
                        { ## 센터 이미지 레이어
                            "id": "StaticImage_centerImg",
                            "name": "centerImg",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": (1920- img_width) / 2,
                            "top": 210,
                            "width": img_width,
                            "height": 620,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticImage",

                            "visible": True,
                            
                            "src": img_url,
                            "cropX": 0,
                            "cropY": 0,
                            "metadata": {}
                        },
                        {
                            "id": "StaticText_articleTitle",
                            "name": "articleTitle",
                            "left": 180,
                            "top": 40,
                            "width": 1560,
                            "type": "StaticText",
                            "fill": "#ffffff",
                            "fontFamily": "NotoSans-Bold",
                            "fontSize": 40,
                            "lineHeight": 1.16,
                            "text": self.article_title,
                            "textAlign": "center",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Bold.woff2"
                        },
                        {
                            "id": "StaticPath_articleTitle",
                            "name": "articleTitle",
                            "left": 0,
                            "top": 0,
                            "width": 1920,
                            "height": 180,
                            "type": "StaticPath",
                            "path": [
                                ["M", 1920, 0],
                                ["L", 0, 0],
                                ["L", 0, 180],
                                ["L", 1920, 180],
                                ["L", 1920, 0],
                                ["Z"]
                            ],
                            "fill": "#0B9281"
                        },

                        { ## 자막 텍스트 레이어
                            "id": "StaticText_abstract",
                            "name": "abstract",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 180,
                            "top": 850,
                            "width": 1560,
                            "height": 88,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#000000",
                            "fontFamily": "NotoSans-Medium",
                            "fontSize": 30,
                            "lineHeight": 1.16,
                            "text": abs.replace("'", "’"),
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                        },
                    
                        { ## DOI 주소 레이어
                            "id": "StaticText_doi",
                            "name": "doi",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 30,
                            "top": 1005,
                            "width": 800,
                            "height": 25,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#ffffff",
                            "fontFamily": "NotoSans-Regular",
                            "fontSize": 20,
                            "lineHeight": 1.16,
                            "text": self.doi,
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                        },
                    
                        { ## 저작권 텍스트 레이어
                            "id": "StaticText_copyright",
                            "name": "copyright",
                            
                            "stroke": None,
                            "strokeWidth": 0,
                            "left": 30,
                            "top": 1030,
                            "width": 800,
                            "height": 25,
                            "opacity": 1,
                            
                            "originY": "top",
                            "scaleX": 1,
                            "scaleY": 1,
                            "type": "StaticText",

                            "visible": True,
                            
                            "charSpacing": 0,
                            "fill": "#ffffff",
                            "fontFamily": "NotoSans-Regular",
                            "fontSize": 20,
                            "lineHeight": 1.16,
                            "text": self.copyright,
                            "textAlign": "left",
                            "fontURL": "https://cdn.jsdelivr.net/npm/notosans@5.0.0/NotoSans-Regular.woff2"
                        }
                        
                        ## 로고 이미지 레이어
                    ] + self.get_logo_img()
                }
                
                scenes.append(scene)
                index += 1
                img_ind += 1
                
            final_json = {
                "id": self.project_key,
                "name": self.project_name,
                "frame": { "width": 1920, "height": 1080 },
                "scenes": scenes,
                "metadata": {},
                "preview": ""
            }
        
        final_json_text = str(final_json).replace('{"id": "StaticImage_centerImg", "name": "centerImg", "stroke": null, "strokeWidth": 0, "left": 510.0, "top": 210, "width": 900, "height": 620, "opacity": 1, "originY": "top", "scaleX": 1, "scaleY": 1, "type": "StaticImage", "visible": true, "src": "", "cropX": 0, "cropY": 0, "metadata": {}},', '')
        final_json_text = final_json_text.replace("False", "false").replace("True", "true").replace("None", "null")
        
        return final_json_text

