import os
import itertools
import json
import api
import xmltodict,collections

class DataForEachMeshTerm():
    def __init__(self, mesh_terms, query):
        self.mesh_terms = mesh_terms
        self.query = query
        if self.mesh_terms and self.query:
            self.fetchMeshTermdata()

    def get_data_foldername(self,query):
        return "data_folder/" + query

    def get_search_term(self):
        return self.query

    def getMeshTermCombinations(self):
        # Preprocess terms
        terms = self.mesh_terms.split('OR')
        terms = [term.replace('(', '') for term in terms]
        terms = [term.replace(')', '') for term in terms]
        # Removing date from last term
        temp = terms[len(terms)-1].split('AND')
        terms[len(terms)-1] = temp[0] 
        terms = [term.strip() for term in terms]
        terms = ['('+term+')' if 'AND' in term else term for term in terms]

        combs = []

        for i in range(1, len(terms)+1):
            tmp = [list(x) for x in itertools.combinations(terms,i)]
            combs.extend(tmp)

        # print(combs)
        mesh_exps = []
        for comb in combs:
            s = ""
            # for x in range(0,len(comb)-1):
                # s+="("
            count = 0
            for term in comb:
                if count == 0:
                    s += term
                else:
                    s += " OR " + term
                count += 1
            mesh_exps.append(s)
        return mesh_exps

    def fetchMeshTermdata(self):
        _retmax = 400
        if self.mesh_terms:
            _terms = self.getMeshTermCombinations()
        else:
            print("No mesh term returned by PUBMED API..")
            return
        if _terms and self.query:
            print("Getting information for each mesh-term and create a json file...")
            if not os.path.exists(self.get_data_foldername(self.get_search_term())):
                os.mkdir(self.get_data_foldername(self.get_search_term()))
                count = 0
                for term in _terms:
                    count = count + 1
                    # Getting abstract here
                    _pmids, mtdummy = api.fetch_data(term,_retmax)
                    # Get abs for all ids together
                    ids = ""
                    for pmid in _pmids:
                        ids += str(pmid) + ","
                    data = api.get_abstract(ids)
                    lines = xmltodict.parse(data)
                    
                    id_list = []
                    title_list = []
                    abstract_list = []
                    meshterms = []

                    article = lines['PubmedArticleSet']['PubmedArticle']

                    for obj in article:
                        text = ""
                        title = ""
                        citation = obj['MedlineCitation']
                        pmid = citation['PMID']['#text']
                        mesh_heading = []
                        id_list.append(pmid)
                        # print(pmid)

                        # title extraction
                        if('ArticleTitle' in citation['Article']):
                            if(type(citation['Article']['ArticleTitle']) is list):
                                title = citation['Article']['ArticleTitle'][0]
                            elif(type(citation['Article']['ArticleTitle']) is str):
                                title = citation['Article']['ArticleTitle']
                            elif(type(citation['Article']['ArticleTitle']) is collections.OrderedDict):
                                title = citation['Article']['ArticleTitle']['#text']

                        # abstract extraction
                        if('Abstract' in citation['Article']):
                            abstracts = citation['Article']['Abstract']
                            if('AbstractText' in abstracts):
                                if(type(abstracts['AbstractText']) is list):
                                    for abs in abstracts['AbstractText']:
                                        if(type(abs) is collections.OrderedDict):
                                            if('#text' in abs):
                                                text += abs['#text']
                                        elif(abs is not None):
                                            text += abs
                                elif(type(abstracts['AbstractText']) is collections.OrderedDict):
                                    if('#text' in abstracts['AbstractText']):
                                        text += abstracts['AbstractText']['#text']
                                elif(type(abstracts['AbstractText']) is str):
                                    text += abstracts['AbstractText']

                        # Mesh terms associated with a pmid 
                        temp = ""
                        if('MeshHeadingList' in citation):
                            for ob in citation['MeshHeadingList']['MeshHeading']:
                                if('DescriptorName' in ob):
                                    temp = ob['DescriptorName']['#text']
                                if ('QualifierName' in ob):
                                    if(type(ob['QualifierName']) is list):
                                        for qualifier in ob['QualifierName']:
                                            mesh_heading.append(temp+'/'+qualifier['#text'])
                                    else:
                                        mesh_heading.append(temp+'/'+ob['QualifierName']['#text'])
                                else:
                                    mesh_heading.append(temp)
                        title_list.append(title)
                        abstract_list.append(text)
                        meshterms.append(mesh_heading)
                        
                    # build json object with relevent fields from abstract xml
                    jObject = {}
                    jObject['queryId'] = count
                    jObject['query'] = term
                    jObject['articleIds'] = id_list
                    jObject['titles'] = title_list
                    jObject['abstracts'] = abstract_list
                    jObject['meshterms'] = meshterms

                    with open(self.get_data_foldername(self.get_search_term())+"/"+str(count)+'.json', 'w') as outfile:
                        json.dump(jObject, outfile)

