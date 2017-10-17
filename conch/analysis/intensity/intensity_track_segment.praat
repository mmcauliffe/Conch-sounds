
form Variables
    sentence filename
	real begin
	real end
	integer channel
	real padding
  real timestep
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

To Intensity... 100 'timestep' yes

frames = Get number of frames

output$ = "time"+tab$+"Intensity"+newline$

for f from 1 to frames
    t = Get time from frame number... 'f'
    if t >= begin
        if t <= end
            t$ = fixed$(t, 3)
            v = Get value in frame... 'f'
            v$ = fixed$(v, 2)
            output$ = output$+t$+tab$+v$+newline$
        endif
    endif
endfor

echo 'output$'
