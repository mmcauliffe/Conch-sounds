
from sklearn.cluster import AffinityPropagation

def affinity_cluster(simMat,oneCluster):
    if oneCluster:
        pref = simMat.min() * 3
    else:
        pref = None
    af = AffinityPropagation(
                affinity = 'precomputed',
                preference=pref
                ).fit(simMat)

    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    labels = af.labels_

    clusters = dict()

    for k in range(n_clusters_):
        clust = cluster_centers_indices[k]
        class_members = labels == k
        clusters[clust] = list()
        for i, x in enumerate(class_members):
            if not x:
                continue
            clusters[clust].append((i,simMat[i,clust]))
    return clusters

