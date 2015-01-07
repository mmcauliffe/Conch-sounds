
from numpy import arange, array, zeros
from sklearn.cluster import AffinityPropagation

def affinity_cluster(simMat, true_labels, oneCluster):

    if oneCluster:
        levels = set(true_labels)
        clusters = dict()
        for w in levels:
            label_mapping = arange(len(true_labels))[true_labels == w]
            #subSimMat = simMat[true_labels == w, true_labels == w]
            subSimMat = zeros((len(label_mapping),len(label_mapping)))
            for ix,x in enumerate(label_mapping):
                for iy,y in enumerate(label_mapping):
                    subSimMat[ix,iy] = simMat[x,y]
            pref = subSimMat.min() * 2.5
            af = AffinityPropagation(
                affinity = 'precomputed',
                preference=pref
                ).fit(subSimMat)
            cluster_centers_indices = af.cluster_centers_indices_
            n_clusters_ = len(cluster_centers_indices)
            labels = af.labels_


            for k in range(n_clusters_):
                clust = cluster_centers_indices[k]
                class_members = labels == k
                clusters[label_mapping[clust]] = list()
                for i, x in enumerate(class_members):
                    if not x:
                        continue
                    #print(clust)
                    #print(i)
                    #print(label_mapping[clust])
                    #print(label_mapping[i])
                    clusters[label_mapping[clust]].append((label_mapping[i],subSimMat[i,clust]))
        return clusters
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

