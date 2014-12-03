
        form Variables
            sentence file
            positive numCC
            real windowLength
            real timeStep
            real maxMel
        endform

        Read from file... 'file$'

        To MFCC... numCC windowLength timeStep 100.0 100.0 maxMel

        To TableOfReal... 0
        
        output$ = ""
        
        numRows = Get number of rows
        
        for i from 1 to numRows
            for j from 1 to numCC
                val = Get value... i j
                val$ = fixed$(val,3)
                output$ = output$ + val$
                if j != numCC
                    output$ = output$ + tab$
                endif
            endfor
            if i != numRows
                output$ = output$ + newline$
            endif
        endfor

        echo 'output$'