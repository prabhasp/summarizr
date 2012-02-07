source("utils.R")
library(gridExtra)
library(ggplot2)
library(RCurl) # keep this loaded, this is used by a python object using this code

########### PLOT UTILS ############
# Tested filetypes, so far, are pdf and svg
one_plot <- function(named_plot_list, fname='output', ftype='svg', generate=TRUE) {
    filenamestubs <- names(named_plot_list)
    if (is.null(filenamestubs)) #unnamed list
        filenamestubs <- c(1:length(name_plot_prefix_list_list))
    file_fn = if(ftype=='svg') {svg} else {pdf}
   
    filenames = sapply(names(named_plot_list), function(plotname) paste(plotname, ftype, sep='.'))
    if (generate) {
        lapply(names(named_plot_list), function(plotname) {
            fname = filenames[[plotname]]
            plots = named_plot_list[[plotname]]

            file_fn(fname, height=(2*length(plots)))
            do.call(grid.arrange, c(plots, ncol = 1))
            dev.off()
         })
    }
    filenames
}

############# CORE STUFF -- just use this with plot utils ##################
# take a one-column data frame, and plot it
# returns NA if doesn't know how to plot, one-element [name=plot] list if it can.
ggraph_one <- function (one_column_df) {
    col_type <- class(one_column_df[[1]])
    if(col_type=="integer") {
        setNames(list(ggplot(data=one_column_df) + 
                            aes_string(x=names(one_column_df)[1]) + 
                            geom_histogram() + 
                            opts(axis.title.y=theme_blank())),
                names(one_column_df)[[1]])
    } else if(col_type=="factor") {
        b = theme_blank()
        setNames(list(ggplot(data=one_column_df) + 
                        aes_string(fill=names(one_column_df)[1]) + aes(x=1) + 
                        geom_bar(psition="fill") + coord_flip() + 
                        opts(legend.position="bottom", legend.direction="horizontal", 
                            axis.title.x = b, axis.title.y=b, axis.text.y=b, 
                            axis.ticks=b, panel.grid.major=b, panel.grid.minor=b)),
                names(one_column_df)[[1]])
    } else {
        NA
    }
}

# Returns a list of [name=plot] elements 
ggraphs <- function(df, dfname='') {
    df <- sanify_data_frame(df)    
    temp_list <- unlist(llply(names(df), function(colname) { ggraph_one(df[colname]) }), recursive = FALSE)
    temp_list <- temp_list[which(!is.na(temp_list))]   #remove all the NAs
    setNames(list(temp_list), dfname)
}

# apply graph to a dataframe, and aggreagate by factor_names
ggraphs_with_agg <- function(df, factor_names) {
    list_of_split_dfs = dlply(df, factor_names, function(x) {x[,!(names(x) %in% factor_names)]})
    res_list <- lapply(names(list_of_split_dfs), function(name) {
        unlist(ggraphs(list_of_split_dfs[[name]]), recursive=FALSE)
    })
    setNames(res_list, names(list_of_split_dfs))
}
