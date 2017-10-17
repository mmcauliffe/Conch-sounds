
form Variables
    sentence filename
    real timestep
    real windowlen
    real nformants
    real ceiling
    real percent_point
endform

Read from file... 'filename$'

duration = Get total duration
r = duration * percent_point


To Formant (burg)... 'timestep' 'nformants' 'ceiling' 'windowlen' 50
frames = Get number of frames

output$ = ""
for i from 1 to nformants
    formNum$ = string$(i)
    output$ = output$ + "F" + formNum$ + tab$ + "B" + formNum$
    if i <> nformants
        output$ = output$ + tab$
    endif
endfor
output$ = output$ + newline$


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
