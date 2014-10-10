
from collections import OrderedDict

from numpy import zeros, array, abs
from numpy.random import RandomState

from sklearn import metrics

from networkx import Graph, empty_graph
from sklearn import manifold
from sklearn.decomposition import PCA

from .affinity import affinity_cluster

class ClusterNetwork(object):
    def __init__(self, reps):
        self.g = Graph()
        self.N = len(reps.keys())
        nodes = []
        self.lookup = {}
        self.attributes = None
        for i,r in enumerate(sorted(reps.keys())):
            self.lookup[r] = i
            if self.attributes is None:
                print(reps[r]._attributes)
                self.attributes = list(reps[r]._attributes.keys())
            nodes.append((i,{'rep':reps[r]}))
        self.g.add_nodes_from(nodes)
        self.clusters = None

    def __iter__(self):
        for i,d in self.g.nodes_iter(data=True):
            yield d

    def __len__(self):
        return self.N

    def __getitem__(self, key):
        if isinstance(key,str):
            return self.g.node[self.lookup[key]]
        return self.g.node[key]

    def cluster(self,scores,cluster_method,oneCluster):
        #Clear any edges
        self.g.remove_edges_from(list(self.g.edges_iter(data=False)))

        if cluster_method is None:
            return
        if scores is not None:
            self.simMat = zeros((self.N,self.N))
            for k,v in scores.items():
                indOne = self.lookup[k[0]]
                indTwo = self.lookup[k[1]]
                self.simMat[indOne,indTwo] = v
                self.simMat[indTwo,indOne] = v
            self.simMat = -1 * self.simMat
        if cluster_method == 'affinity':
            true_labels = array([ self[i]['rep']._true_label for i in range(self.N)])
            self.clusters = affinity_cluster(self.simMat,true_labels,oneCluster)
            edges = []
            for k,v in self.clusters.items():
                for v2 in v:
                    if v2[0] == k:
                        continue
                    edges.append((k,v2[0],v2[1]))
        elif cluster_method == 'complete':
            edges = []
            for i in range(self.N):
                for j in range(i+1,self.N):
                    edges.append((i,j,self.simMat[i,j]))
        self.g.add_weighted_edges_from(edges)
        seed = RandomState(seed=3)
        mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-9, random_state=seed,
                   dissimilarity="precomputed", n_jobs=4)
        pos = mds.fit(-1 * self.simMat).embedding_
        clf = PCA(n_components=2)
        pos = clf.fit_transform(pos)
        for i,p in enumerate(pos):
            self.g.node[i]['pos'] = p

    def calc_reduction(self):
        if self.clusters is None:
            return
        means = {}
        reverse_mapping = {}
        for k,v in self.clusters.items():
            s = 0
            for ind in v:
                reverse_mapping[ind[0]] = k
                s += ind[1]
            means[k] = s/len(v)
        for i in self.g.nodes_iter():
            clust_center = reverse_mapping[i]
            if i == clust_center:
                self.g.node[i]['HyperHypoMeasure'] = 0
                continue
            dist = self.g[i][clust_center]['weight']
            norm_dist = abs(dist - means[clust_center])
            len_diff = self[clust_center]['representation'].shape[0]-self[i]['representation'].shape[0]
            if len_diff < 0:
                norm_dist *= -1
            self.g.node[i]['HyperHypoMeasure'] = norm_dist
        if 'HyperHypoMeasure' not in self.attributes:
            self.attributes.append('HyperHypoMeasure')

    def get_edges(self):
        return array(self.g.edges(data=False))

    def labels(self):
        labels = list(range(len(self.g)))
        for k,v in self.clusters.items():
            for v2 in v:
                labels[v2[0]] = k
        true_labels = list()
        for i in range(len(labels)):
            true_labels.append(self[i]['rep']._true_label)
        levels = {x:i for i,x in enumerate(set(true_labels))}
        for i in range(len(true_labels)):
            true_labels[i] = levels[true_labels[i]]
        return array(labels),array(true_labels)

    def silhouette_coefficient(self):
        labels,true_labels = self.labels()
        return metrics.silhouette_score(self.simMat, labels, metric = 'precomputed')

    def homogeneity(self):
        labels,true_labels = self.labels()
        return metrics.homogeneity_score(true_labels, labels)

    def completeness(self):
        labels,true_labels = self.labels()
        return metrics.completeness_score(true_labels, labels)

    def v_score(self):
        labels,true_labels = self.labels()
        return metrics.v_measure_score(true_labels, labels)

    def adjusted_mutual_information(self):
        labels,true_labels = self.labels()
        return metrics.adjusted_mutual_info_score(true_labels, labels)

    def adjusted_rand_score(self):
        labels,true_labels = self.labels()
        return metrics.adjusted_rand_score(true_labels, labels)
