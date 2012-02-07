# You know, returns a "saner" data frame. I'm not gonna define what that is right now.

# Used because R treats all characters as factors. A 28-row column with a 28-level factor is a bit ridiculous, no?
# Stringify all factors with # of levels > (1/x) number of rows (x = max_row_levels_ratio)) and levels > most_levels (a constant)
# TODO: do this based on form-type
sanify_data_frame <- function(df, max_row_to_levels_ratio=2, most_levels=20) {
	# Drop all only-n/a factors
	df <- df[sapply(df, function(col) { !(is.factor(col) && (length(levels(col)) == 1) && (levels(col)[[1]] =="n/a" ))})]
	f <- function(x) { is.factor(x) && (length(x) / length(levels(x)) < 2) || length(levels(x)) > most_levels }
	data.frame(lapply(df, function(x) { if(f(x)) {as.character(x)} else {x}}), stringsAsFactors=FALSE)
}

# Stringifies too many factors; drops only one-level factors
# TODO: stringify instead of drop?
only_plotworthy_columns <- function(df, most_levels=20) {
	df <- sanify_data_frame(df)
	df[sapply(df, function(col) { !(is.factor(col) && (length(levels(col)) == 1)) })]
}

# returns all the column names if the column type is a factor
factor_col_names <- function(df) {
	names(which(sapply(only_plotworthy_columns(df), is.factor)))
}

