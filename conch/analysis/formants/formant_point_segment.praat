
form Variables
    sentence filename
	real begin
	real end
	integer channel
	real padding
    real timestep
    real windowlen
    real nformants
    real ceiling
    real percent_point
endform

Open long sound file... 'filename$'

duration = Get total duration

seg_begin = begin - padding
if seg_begin < 0
    seg_begin = 0
endif

seg_end = end + padding
if seg_end > duration
    seg_end = duration
endif

Extract part... seg_begin seg_end 1
channel = channel + 1
Extract one channel... channel

Rename... segment_of_interest


output$ = ""
for i from 1 to nformants
    formNum$ = string$(i)
    output$ = output$ + "F" + formNum$ + tab$ + "B" + formNum$
    if i <> nformants
        output$ = output$ + tab$
    endif
endfor
output$ = output$ + newline$

duration = end - begin
r = begin+ (duration * percent_point)


To Formant (burg)... 'timestep' 'nformants' 'ceiling' 'windowlen' 50

for i from 1 to nformants
    formant = Get value at time... 'i' 'r' Hertz Linear
    formant$ = fixed$(formant, 2)
    if formant = undefined
        #echo "error"
    endif
    bw = Get bandwidth at time... 'i' 'r' Hertz Linear
    bw$ = fixed$(bw, 2)
    output$ = output$ + formant$ + tab$ + bw$
    if i <> nformants
        output$ = output$ + tab$
    endif
endfor
output$ = output$ + newline$

echo 'output$'
