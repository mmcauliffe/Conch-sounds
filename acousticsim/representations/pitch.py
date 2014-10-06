
from .gammatone import to_gammatone



def to_pitch_zcd(gt):
    import matplotlib.pyplot as plt
    print(gt.shape)
    nsamps = gt.shape[0]
    nbands = get.shape[1]
    for i in range(1,nsamps-1):
        pass
    plt.plot(gt)
    plt.show()
