# You know, returns a "saner" data frame. I'm not gonna define what that is right now.

sanify_data_frame <- function(df, max_row_to_levels_ratio=2) {
	# Drop all only-n/a factors
	df <- df[sapply(df, function(col) { !(is.factor(col) && (length(levels(col)) == 1) && (levels(col)[[1]] =="n/a" ))})]
	
	# Drop all factors with # of levels > (1/2) number of rows (well, except, its (1/max_row_levels_ratio))
	# Used because R treats all characters as factors. A 28-row column with a 28-level factor is a bit ridiculous, no?
	f <- function(x) { is.factor(x) && (length(x) / length(levels(x)) < 2) }
	data.frame(lapply(df, function(x) { if(f(x)) {as.character(x)} else {x}}), stringsAsFactors=FALSE)
}

only_plotworthy_columns <- function(df) {
	df <- sanify_data_frame(df)
	df[sapply(df, function(col) { !(is.factor(col) && (length(levels(col)) == 1)) })]
}

# returns all the column names if the column type is a factor
factor_col_names <- function(df) {
	names(which(sapply(only_plotworthy_columns(df), is.factor)))
}

