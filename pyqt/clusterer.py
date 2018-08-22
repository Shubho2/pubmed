import os
import json
import sys
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
from scipy.spatial import distance
from time import time
from sklearn.cluster import DBSCAN
from collections import OrderedDict
import collections
import random

class Clusterer:
	def __init__(self, relDocsSet, dataFolder, kmeans, hyper):
		raw_data = []
		data_folder_name = dataFolder+"/"
		for filename in os.listdir(data_folder_name):
		    f = open(data_folder_name+filename, 'r')
		    json_object = json.load(f)
		    f.close()
		    raw_data.append(json_object)
		    
		print ('Number of Cluster Points -------> ')
		print (len(raw_data))

		self.cluster_data = raw_data
		self.kmeans = kmeans
		self.related_docs = relDocsSet
		self.hyper = hyper

	# def get_final_set(self):
	# 	return self.final_set

	def cluster(self):
		data_abstract = [clusterpoint["abstracts"] for clusterpoint in self.cluster_data]
		data_query_label = [clusterpoint["query"] for clusterpoint in self.cluster_data]
		data_query_id = [clusterpoint["queryId"] for clusterpoint in self.cluster_data]

		# Perform an IDF normalization on the output of HashingVectorizer
		hasher = HashingVectorizer(n_features=1000, stop_words='english', norm=None, binary=False)
		vectorizer = make_pipeline(hasher, TfidfTransformer())
		X = vectorizer.fit_transform(data_abstract)
		print ("n_samples: %d, n_features: %d" % X.shape)
		# print(data_query_label)
		# print(X)

		# K-Means or DBSCAN
		if self.kmeans:
			num_clusters = int(self.hyper)
			km = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=100, n_init=1, verbose=True)
			t0 = time()
			km.fit(X)
			print("done in %0.3fs" % (time() - t0))
			# print(len(set(km.labels_)))
		else:
			km = DBSCAN(eps=float(self.hyper), min_samples=10).fit(X)
			num_clusters = len(set(km.labels_))

		cluster_labels = km.labels_
		cluster_centers = km.cluster_centers_
		print("cluster centers: ",cluster_centers)
		query_clusters = []
		query_clusters_pmids = []

		for i in range(0,num_clusters):
		    temp = []
		    tempset = set()
		    query_clusters_pmids.append(tempset)
		    query_clusters.append(temp)
		# Each row(cluster 0 to 8) will contain its corresponding MeshTerm nos
		for i in range(0,len(cluster_labels)):
			query_clusters[cluster_labels[i]].append(i+1)

			pmids = self.cluster_data[i]["articleIds"].split(',')
			# print("pmids: ", pmids)
			for pmid in pmids:
				if pmid:
					query_clusters_pmids[cluster_labels[i]].add(int(pmid))

		print ("cluster_id\tnum_queries\tnum_pmids")
		print ("-------------------------------------------------------------")
		for i in range(0,num_clusters):
		    print (str(i) + "\t\t" + str(len(query_clusters[i])) + "\t\t" + str(len(query_clusters_pmids[i])))

		relevant_docs = self.related_docs

		# random.shuffle(relevant_docs)

		# learning vs testing split

		training_cnt = int(len(relevant_docs))
		relevant_known = set(relevant_docs[:training_cnt])
		
		cluster_score = [float(len(relevant_known.intersection(cluster_pmids)))/float(len(cluster_pmids)) for cluster_pmids in query_clusters_pmids]
		
		print(cluster_score)
		cluster_score_relative = [score/max(cluster_score) for score in cluster_score]
		
		print ("Cluster ID\tRelevance Score")
		for i in range(0,num_clusters):
		    print (str(i) + "\t\t" + str(cluster_score_relative[i]))

		clus_dict = OrderedDict()
		final_corpus = set()
		for i in range(0,num_clusters):
			if cluster_score_relative[i] > 0.5:
				clus_dict[cluster_score_relative[i]] = i

		sortedscore = sorted(clus_dict.items(), reverse=True)
		# print(sortedscore)
		optimized_query = []
		for i in range(0,num_clusters):
			optimized_query.append([])
		optimized_query_ids = []
		for i in range(0,num_clusters):
		    optimized_query_ids.append([])
		done = 0
		min = sys.float_info.max
		for _score , _clus_no in sortedscore:
			for _k in query_clusters[_clus_no]:
				if not done:
					dist = distance.euclidean(cluster_centers[_clus_no], X[_k - 1].toarray())
					if dist < min:
						min = dist
						representative = data_query_label[_k-1]
						representative_id = _k
						print("----------------------------------------",_k)
				optimized_query_ids[_clus_no].append(_k)
				optimized_query[_clus_no].append(data_query_label[_k-1])
			done = 1
		
		# print(optimized_query)
		# print(optimized_query_ids)
		print(representative)
		return representative_id,representative,optimized_query_ids, optimized_query