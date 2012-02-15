library(plyr)
library(RJSONIO)

onedf <- function(df, df_name) {
    l = llply(df, function(x) { count(as.data.frame(x))})
    toJSON(setNames(list(l), list(df_name)))
}
aggdf <- function(df, splitBy) toJSON(dlply(df, splitBy, onedf)) 
