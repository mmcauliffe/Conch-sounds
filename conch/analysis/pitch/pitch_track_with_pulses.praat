
form Variables
    sentence filename
    real timestep
    real minpitch
    real maxpitch
    real silence_threshold
    real voicing_threshold
    real octave_cost
    real octave_jump_cost
    real voiced_unvoiced_cost
endform

Read from file... 'filename$'

To Pitch (ac)... 'timestep' 'minpitch' 15 yes 'silence_threshold' 'voicing_threshold' 'octave_cost' 'octave_jump_cost' 'voiced_unvoiced_cost' 'maxpitch'
frames = Get number of frames

output$ = "time"+tab$+"F0"+newline$

for f from 1 to frames
    t = Get time from frame number... 'f'
    t$ = fixed$(t, 3)
    v = Get value in frame... 'f' Hertz
    v$ = fixed$(v, 2)
    output$ = output$+t$+tab$+v$+newline$
endfor

output$ = output$+newline$+newline$

To PointProcess

num_points = Get number of points

for p from 1 to num_points
    t = Get time from index... 'p'
    t$ = fixed$(t, 3)
    output$ = output$ + t$ + newline$
endfor

echo 'output$'
