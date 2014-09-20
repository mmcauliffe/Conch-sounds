
from collections import OrderedDict

from numpy import zeros, array, abs
from numpy.random import RandomState

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
            node_dict = OrderedDict({'label':r})
            for k,v in reps[r].items():
                node_dict[k] = v
            if self.attributes is None:
                self.attributes = [x for x in node_dict.keys() if x != 'representation']
            nodes.append((i,node_dict))
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
            self.clusters = affinity_cluster(self.simMat,oneCluster)
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
