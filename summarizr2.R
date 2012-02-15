library(plyr)
library(RJSONIO)

countdf <- function(df) { llply(df, function(x) { count(as.data.frame(x))}) }
df_to_json_counts <- function(df, df_name) {
    toJSON(setNames(list(countdf(df)), list(df_name)))
}
df_to_json_counts_with_split <- function(df, splitBy) toJSON(dlply(df, splitBy, countdf)) 
