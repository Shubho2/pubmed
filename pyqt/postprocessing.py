import os
import json
from mesh_explosion import DataForEachMeshTerm
import operator
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class PostProcessing():

    def __init__(self):
        pass

    def getTitleAbs(self,index,json_no,query):
        # open json
        dfet = DataForEachMeshTerm(None,None)
        data_folder_name = dfet.get_data_foldername(query)
        f = open(data_folder_name+"/"+str(json_no)+".json", 'r')
        json_object = json.load(f)
        f.close()
        abstracts = json_object["abstracts"]
        titles = json_object["titles"]
        mesh_terms = json_object["meshterms"]
        toptitles,topabs, sameabs = self.split_abstracts(index,abstracts,titles)
        return toptitles, topabs, sameabs


    def split_abstracts(self,index,abstracts,titles):
        count = 0
        allabs = []
        sameabs = [] # nedded for Gene tagging
        alltitles = []
        while(count < 4 and index < len(abstracts)):
            allabs.append(self.getProcessedAbs(abstracts[index]))
            alltitles.append(self.getProcessedTitle(titles[index]))
            sameabs.append(abstracts[index])
            index += 1
            count += 1
        return alltitles,allabs,sameabs


    def getProcessedAbs(self, abstract):
        abs = ""
        i = 0
        c = 0
        divide = 0
        while(c < 2 and i < len(abstract)):
            if(abstract[i] == '\n'):
                i += 1
                continue
            abs += abstract[i]
            divide += 1
            if((divide >= 80 and abstract[i] == ' ') or divide >= 93):
                if(c == 0):
                    abs += '\n'
                c += 1
                divide = 0
            i += 1
        return abs

    def getProcessedTitle(self, title):
        data = ""
        i = 0
        divide = 0
        while(i < len(title)):
            if(title[i] == '\n'):
                i += 1
                continue
            data += title[i]
            divide += 1
            if(divide >= 80 and title[i] == ' ' or divide >= 93):
                data += '\n'
                divide = 0
            i += 1
        return data

    def term_tagging(self,optimized_terms):
       
        term_dict = {}
        for terms in optimized_terms:
            for term in terms:
                i = 0
                count=0
                st = ""
                while i<len(term):
                    if term[i] == '"':
                        count += 1
                        if count%2==0:
                            self.countoccurrences(term_dict,st) 
                        st = ""
                    else:
                        st += term[i]
                    i += 1

        print(term_dict)

        sorted_dict = sorted(term_dict.items(), key=operator.itemgetter(1),reverse=True)

        print(sorted_dict)

        return sorted_dict


    def countoccurrences(self,store,value):
        try:
            store[value] = store[value] + 1
        except KeyError as e:
            store[value] = 1
        return


    def gene_cloud(self,term_id,gene_file_name,search_term):
        print("Gene cloud called..")
        file_name = "data_folder/"+search_term+"/"+str(term_id)+'.json'
        f = open(file_name, 'r')
        json_object = json.load(f)
        f.close()

        data_abstract = json_object["abstracts"]
        data_title = json_object["titles"]

        abstracts = ""
        for i in range(0,len(data_abstract)):
            abstracts = abstracts+data_title[i]+data_abstract[i]

        content = abstracts.replace('\n', ' ')
        content = content.replace('.', ' ')
        content = content.replace(',', ' ')
        content = content.lower()
        # print(content)

        data = content.split()

        filepointer = open(gene_file_name,'r')
        genefile = filepointer.read().lower().split('\n')

        gene_dict = {} 

        for gene in genefile:
            if gene:
                gene_dict[gene] = data.count(gene)+1.0

        
        wordcloud = WordCloud(width = 1000, height = 500).fit_words(gene_dict)
        
        # plot the WordCloud image                       
        fig = plt.figure(figsize=(15,8))
        plt.imshow(wordcloud)
        plt.tight_layout(pad = 0)
        plt.axis("off")
        fig.canvas.set_window_title("Gene cloud")
        plt.show()
        plt.close()

    def mesh_cloud(self,term_id,search_term):
        print("Mesh cloud called..")
        file_name = "data_folder/"+search_term+"/"+str(term_id)+'.json'
        f = open(file_name, 'r')
        json_object = json.load(f)
        f.close()

        mesh_terms_matrix = json_object["meshterms"]
        mesh_array = []
        for arr in mesh_terms_matrix:
            for word in arr:
                mesh_array.append(word)
        unique_string=(" ").join(mesh_array)
        if(len(unique_string) > 0):
            wordcloud = WordCloud(width = 1000, height = 500).generate(unique_string)
        else:
            regexp=r"\w[\w' ]+"
            my_list=["No mesh terms found"]
            wordcloud = WordCloud(width=1000, height=500, regexp=r"\w[\w' ]+").generate("+".join(my_list))
        mesh = plt.figure(figsize=(15,8))
        plt.imshow(wordcloud)
        plt.tight_layout(pad = 0)
        plt.axis("off")
        mesh.canvas.set_window_title("Mesh cloud")
        plt.show()
        plt.close()