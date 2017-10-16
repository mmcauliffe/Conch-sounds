
form Variables
    sentence file
    positive numCC
    real windowLength
    real timeStep
    real maxMel
endform

Read from file... 'file$'

Rename... wavfile

To MFCC... numCC windowLength timeStep 100.0 100.0 maxMel

To TableOfReal... 1

output$ = "time" + tab$

numCols = Get number of columns

for j from 1 to numCols
    label$ = Get column label... j
    output$ = output$ +  label$
    if j != numCols
        output$ = output$ + tab$
    else
        output$ = output$ + newline$
    endif
endfor

numRows = Get number of rows

for i from 1 to numRows
    selectObject: "MFCC wavfile"
    time = Get time from frame number... i
    val$ = fixed$(time,3)
    output$ = output$ + val$ + tab$
    selectObject: "TableOfReal wavfile"
    for j from 1 to numCols
        val = Get value... i j
        val$ = fixed$(val,3)
        output$ = output$ + val$
        if j != numCols
            output$ = output$ + tab$
        endif
    endfor
    if i != numRows
        output$ = output$ + newline$
    endif
endfor

echo 'output$'
