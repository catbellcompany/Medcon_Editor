from webbrowser import get
from metadata.crawler import *

def get_Metadata_doi(doi : str):
    if "ijgii" in doi or "10.18528" in doi:
        return metadata_type_ijgii(doi)

    elif "e-jecoenv" in doi or "10.5141" in doi:
        return metadata_type_jee(doi)
    
    elif "jchestsurg" in doi or "10.5090" in doi:
        return metadata_type_jchestsurg(doi)
    
    elif "10.14348" in doi:
        return metadata_type_molcells(doi)
    
    elif "epain" in doi or "10.3344" in doi:
        return metadata_type_kjp(doi)

    elif "biomolther" in doi or "10.4062" in doi:
        return metadata_type_biomolther(doi)
    
    elif "bmbreports" in doi or "10.5483" in doi:
        return metadata_type_bmbreports(doi)
    
    elif "cpn.or.kr" in doi or "10.9758" in doi:
        return metadata_type_cpn(doi)
    
    elif "gutnliver" in doi or "10.5009" in doi:
        return metadata_type_gnl(doi)
    
    elif "10.51507" in doi:
        return metadata_type_jams(doi)
    
    elif "10.15430" in doi:
        return metadata_type_jcp(doi)
    
    elif "e-jmis" in doi or "10.7602" in doi:
        return metadata_type_jmis(doi)
    
    elif "10.3831" in doi:
        return metadata_type_jop(doi)
    
    elif "10.15324" in doi:
        return metadata_type_kjcls(doi)

    elif "10.4041" in doi or "e-kjo" in doi:
        return metadata_type_kjo(doi)
    
    elif "10.4196" in doi:
        return metadata_type_kjpp(doi)
    
    elif "10.5758" in doi:
        return metadata_type_vsijournal(doi)
    
    elif "10.11106" in doi:
        return metadata_type_ijthyroid(doi)
    
    elif "10.5115" in doi:
        return metadata_type_acb(doi)
    
    elif "10.5534" in doi or "wjmh" in doi:
        return metadata_type_wjmh(doi)
    
    elif "10.4490" in doi:
        return metadata_type_algae(doi)
    
    elif "10.4168" in doi:
        return metadata_type_aair(doi)
    
    elif "10.17085" in doi:
        return metadata_type_apm(doi)
    
    elif "10.4235" in doi:
        return metadata_type_agmr(doi)
    
    elif "10.6065" in doi:
        return metadata_type_apem(doi)
    
    elif "e-arm" in doi or "10.5535" in doi:
        return metadata_type_arm(doi)
    
    elif "10.4174" in doi:
        return metadata_type_astr(doi)
    
    elif "10.9729" in doi or "appmicro" in doi:
        return metadata_type_appmicro(doi)
    
    elif "jnmjournal" in doi or "10.5056" in doi:
        return metadata_type_jnm(doi)
    elif "ijstemcell" in doi or "10.15283" in doi:
        return metadata_type_ijstemcell(doi)