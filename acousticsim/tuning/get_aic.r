
options(warn=-1)
load_lmer = suppressMessages(library(lme4, quietly=TRUE, warn.conflicts = FALSE,verbose=F,logical.return=T))

if(load_lmer){
  filenames = commandArgs(trailingOnly = TRUE)
  aics = numeric()
  for (f in 1:length(filenames)){
    data = read.delim(filenames[f])
    data$Shadower = factor(data$Shadower)
    data$Listener = factor(data$Listener)
    data$Word = factor(data$Word)
    if ('Model' %in% names(data)){
      data$Model = factor(data$Model)
      mod = lmer(Dependent ~ Independent + (1+Independent|Model) + (1+Independent|Shadower) + (1+Independent|Listener) + (1+Independent|Word),data = data)
    } else{
      mod = lmer(Dependent ~ Independent + (1+Independent|Shadower) + (1+Independent|Listener) + (1+Independent|Word),data = data)
    }
    cat(AIC(mod),'\n')
  }
} else{
  cat('LmerError')
}