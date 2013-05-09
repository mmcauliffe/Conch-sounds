form Variables
    sentence firstfile
    sentence secondfile
endform

Read from file... 'firstfile$'
first = selected()

Read from file... 'secondfile$'
second = selected()

select first
To Spectrogram... 0.005 5000 0.002 20 Gaussian
first_spec = selected()

select second
To Spectrogram... 0.005 5000 0.002 20 Gaussian
second_spec = selected()

select first_spec
plus second_spec
To DTW... 1 1 no restriction
spec_dist = Get distance (weighted)

select first
To MFCC... 12 0.015 0.005 100.0 100.0 0.0
first_mfcc = selected()

select second
To MFCC... 12 0.015 0.005 100.0 100.0 0.0
second_mfcc = selected()

select first_mfcc
plus second_mfcc
To DTW... 1.0 0.0 0.0 0.0 0.056 1 1 no restriction
mfcc_dist = Get distance (weighted)

echo 'spec_dist' 'mfcc_dist'
