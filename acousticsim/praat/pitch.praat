
    form Variables
      sentence filename
      real timestep
      real minpitch
      real maxpitch
    endform

    Read from file... 'filename$'

    To Pitch (ac)... 'timestep' 'minpitch' 15 yes 0.03 0.45 0.01 0.35 0.14 'maxpitch'
    frames = Get number of frames

    output$ = "Time"+tab$+"Pitch"+newline$

    for f from 1 to frames
        t = Get time from frame number... 'f'
        t$ = fixed$(t, 3)
        v = Get value in frame... 'f' Hertz
        v$ = fixed$(v, 2)
        output$ = output$+t$+tab$+v$+newline$
    endfor

    echo 'output$'
