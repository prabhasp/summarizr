source("utils.R")
library(gridExtra)
library(ggplot2)
library(RCurl) # keep this loaded, this is used by a python object using this code

########### PLOT UTILS ############
# Tested filetypes, so far, are pdf and svg
vecplot <- function(name_plot_prefix, filetype='svg') {
	name = name_plot_prefix[[1]]
	plot = name_plot_prefix[[2]]
	prefix = name_plot_prefix[[3]]
	fname = paste(prefix, name, filetype, sep='.')
	ggsave(fname, plot=plot, height=2)
	fname
}
noplot <- function(name_plot_prefix, filename_prefix='', suffix='') {
	paste(name_plot_prefix[[3]], name_plot_prefix[[1]], suffix, sep='.')
}

oneplot <- function(name_plot_prefix_list_list, fname='output', filetype='svg', generate=TRUE) {
	filenamestubs <- names(name_plot_prefix_list_list)
	if (is.null(filenamestubs)) #unnamed list
		filenamestubs <- c(1:length(name_plot_prefix_list_list))
	file_fn = if(filetype=='svg') {svg} else {pdf}
	if (generate) {
	    lapply(filenamestubs, function(fname) {
	        plots_only = lapply(name_plot_prefix_list_list[[fname]], function(x) {x$plot})
		fname = paste(fname, filetype, sep='.') # prefix.svg / prefix.pdf
		file_fn(fname, height=(2*length(plots_only)))
		do.call(grid.arrange, c(plots_only, ncol = 1))
		dev.off()
	     })
	}
	#todo: do this and earlier op together
	unlist(lapply(filenamestubs, function(fname) paste(fname, filetype, sep='.')))
}
	

############# CORE STUFF -- just use this with plot utils ##################
# take a one-column data frame, and plot it
# returns NA if doesn't know how to plot, (name, plot) if it does
ggraph_one <- function (one_column_df, prefix='') {
	col_type <- class(one_column_df[[1]])
	if(col_type=="integer") {
		list(name = names(one_column_df)[[1]],
			 plot = ggplot(data=one_column_df) + aes_string(x=names(one_column_df)[1]) + geom_histogram() + opts(axis.title.y=theme_blank()),
			 prefix = prefix)
	} else if(col_type=="factor") {
		list(name = names(one_column_df)[[1]],
			plot = ggplot(data=one_column_df) + aes_string(fill=names(one_column_df)[1]) + aes(x=1)  + geom_bar(position="fill") + coord_flip() + opts(legend.position="bottom", legend.direction="horizontal", axis.title.x = theme_blank(), axis.title.y=theme_blank(), axis.text.y=theme_blank(), axis.ticks=theme_blank(), panel.grid.major=theme_blank(), panel.grid.minor=theme_blank()),
			prefix = prefix)
	} else {
	    NA
	}
}
# apply ggraph_one to a dataframe of many columns after sanification; drop NAs before returning; finally, return a one-element list
ggraphs <- function(df, prefix='') {
	df <- sanify_data_frame(df)	
	temp_list <- lapply(names(df), function(colname) { ggraph_one(df[colname], prefix=prefix)	})
	temp_list <- temp_list[which(!is.na(temp_list))]
	names(temp_list) <- lapply(temp_list, function(x) {x$name})
	list(temp_list)
}
ggraphs_fname <- function(csvname, prefix='') { ggraphs(read.csv(csvname), prefix=prefix) }
# apply graph to a dataframe, and aggreagate by factor_names
ggraphs_with_agg <- function(df, factor_names) {
	list_of_split_dfs = dlply(df, factor_names, function(x) {x[,!(names(x) %in% factor_names)]})
	res_list <- lapply(names(list_of_split_dfs), function(name) {
		unlist(ggraphs(list_of_split_dfs[[name]], prefix=name), recursive=FALSE)
	})
	names(res_list) <- names(list_of_split_dfs)
	res_list
}
# same, except now this takes a filename rather than a dataframe
ggraphs_with_agg_fname <- function(csvname, factor_names) {
	ggraph_with_agg(read.csv(csvname), factor_names)
}
