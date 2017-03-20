
    form Variables
      sentence filename
      real timestep
    endform

    Read from file... 'filename$'
    To Intensity... 100 'timestep' yes

    frames = Get number of frames

    output$ = "time"+tab$+"Intensity"+newline$

    for f from 1 to frames
        t = Get time from frame number... 'f'
        t$ = fixed$(t, 3)
        v = Get value in frame... 'f'
        v$ = fixed$(v, 2)
        output$ = output$+t$+tab$+v$+newline$
    endfor

    echo 'output$'
