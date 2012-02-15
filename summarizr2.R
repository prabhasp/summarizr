library(plyr)
library(RJSONIO)

onedf <- function(df) cat(toJSON(llply(df, function(x) { count(as.data.frame(x))})))
aggdf <- function(df, splitBy) ddply(df, splitBy, onedf) 
