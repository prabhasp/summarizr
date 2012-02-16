import cherrypy
import rpy2.robjects as robjects
import json, os
robjects.r['source']('summarizr.R')
robjects.r['source']('summarizr2.R')

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


class RGraphs(object):

    def index(self):
        return env.get_template('index.html').render()
    index.exposed = True

    def graph(self, doc="", splitBy="", generate="False", whole='Yes'):
        # given a document name, give back a data frame
        if doc=='': doc = 'static/example.csv'
        if 'http://' in doc or 'https://' in doc:
            df =  robjects.r("read.csv(textConnection(getURL('" + doc + "')))")
        else: 
            df = robjects.r("read.csv('" + doc + "')")

        colNames = robjects.r['splittable_col_names'](df)
        if splitBy not in colNames: splitBy = None

        sanitized_doc_name = filter(str.isalnum, doc)
        graph_filenames = self.graphs(df, sanitized_doc_name, splitBy, generate=(generate=="True"))
        graph_filenamestubs = map(lambda s:s.split('.')[0], graph_filenames)

        template = 'graph.html' if whole=='Yes' else 'tabs.html'
        template = env.get_template(template)

        return template.render(graph_filenamestubs=graph_filenamestubs, dirname=os.path.join('static',sanitized_doc_name), colNames=colNames, ext='svg')
    graph.exposed = True

    def bin(self, doc="", splitBy=""):
        # given a document name, give back a data frame
        if doc=='': doc = 'static/example.csv'
        if 'http://' in doc or 'https://' in doc:
            df =  robjects.r("read.csv(textConnection(getURL('" + doc + "')))")
        else: 
            df = robjects.r("read.csv('" + doc + "')")
        
        colNames = robjects.r['splittable_col_names'](df)
        if splitBy not in colNames: 
            s = robjects.r('onedf')(df, "default")[0]
        else:
            s = robjects.r('aggdf')(df,splitBy)[0]

        return str(s)
    bin.exposed = True
    
    def d3_summary(self):
        return env.get_template('d3_test.html').render()
    d3_summary.exposed = True
    
    def graphs(self, df, dataname, splitBy=None, generate=False):
        if splitBy: l = robjects.r['ggraphs_with_agg'](df, splitBy)
        else: l = robjects.r['ggraphs'](df, dfname=dataname)
        
        # Generate images if they don't exist; even if generate=False 
        # TODO: put some end_time based logic here, or in R
        filenames = robjects.r['one_plot'](l, generate=False)
        file_exists = map(lambda x: os.path.exists(os.path.join('static',dataname,x)), filenames)
        if False in file_exists: generate = True

        if generate:
            print 'generating: ' + ' '.join(filenames)
            old_d = robjects.r('getwd()')
            new_d = os.path.join(os.getcwd(), 'static', dataname)
            if not os.path.exists(new_d): os.makedirs(new_d)
            robjects.r('setwd("' + new_d +  '")')
            filenames = robjects.r['one_plot'](l) 
            robjects.r['setwd'](old_d)
        else:
            filenames = robjects.r['one_plot'](l, generate=False)
        return filenames 

cherrypy.quickstart(RGraphs(), config=os.path.join(os.getcwd(), 'prod.conf'))

# convert formhub json format to {"name" : "label"} dictionary
def convert_to_name_label_dict(jsons):
    # now we have a complicated list and dd architecture. What I want to do is keep delving in, and anytime
    # we see a dict with name and label keys, we add to our dictionary
    def f(arg, acc):
        if (type(arg) == dict):
            keys = arg.keys()
            if "name" in keys and "label" in keys:
                acc[arg["name"]] = arg["label"]
            if "children" in keys:
                return f(arg["children"], acc)
            return acc
        elif (type(arg) == list):
            if len(arg)==0:
                return acc
            if type(arg[0])=="dict" or type(arg[0]=="list"):
                acc = f(arg[0], acc)
            return f(arg[1:], acc)
    return f(json.loads(jsons), {})

