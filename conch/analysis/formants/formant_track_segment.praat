
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

To Formant (burg)... 'timestep' 'nformants' 'ceiling' 'windowlen' 50
frames = Get number of frames

output$ = "time"
for i from 1 to nformants
    formNum$ = string$(i)
    output$ = output$ +tab$+ "F"+formNum$ + tab$ + "B" + formNum$
endfor
output$ = output$ + newline$

for f from 1 to frames
    t = Get time from frame number... 'f'
    if t >= begin
        if t <= end
            t$ = fixed$(t, 3)
            output$ = output$ + t$
            for i from 1 to nformants
                formant = Get value at time... 'i' 't' Hertz Linear
                formant$ = fixed$(formant, 2)
                bw = Get bandwidth at time... 'i' 't' Hertz Linear
                bw$ = fixed$(bw, 2)
                output$ = output$ + tab$ + formant$ + tab$ + bw$
            endfor
            output$ = output$ + newline$
        endif
    endif
endfor

echo 'output$'
