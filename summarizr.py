import cherrypy
import rpy2.robjects as robjects
import json, os
robjects.r['source']('summarizr.R')

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


class RGraphs(object):

	def index(self):
		return env.get_template('index.html').render()
	index.exposed = True

	def graph(self, doc="", splitBy="", generate="False", whole='Yes'):
		if whole=='Yes': template = 'graph.html'
		else: template = 'tabs.html'
		if doc=="": df = robjects.r("read.csv('static/example.csv')")
		else: df = robjects.r("read.csv(textConnection(getURL('" + doc + "')))")
		factorNames = robjects.r['names'](df)
		colNames = robjects.r['factor_col_names'](df)
		if splitBy in colNames:  graphlist = self.graphs(df, splitBy, generate=="True")
		else: graphlist = self.graphs(df, None, generate=="True")
		rawlist = map(lambda s:s.split('.')[0], graphlist)
		template = env.get_template(template)
		return template.render(graphlist=rawlist, colNames=colNames, ext='svg')
        graph.exposed = True
	

	def graphs(self, df, splitBy=None, generate=False):
		l = []
		if splitBy:
			l = robjects.r['ggraphs_with_agg'](df, splitBy)
		else:
			l = robjects.r['ggraphs'](df)
		if generate:
			old_d = robjects.r('getwd()')
			robjects.r('setwd("' + os.path.join(os.getcwd(), "static") + '")')
			filenames = robjects.r['oneplot'](l) 
			robjects.r['setwd'](old_d)
		else:
			filenames = robjects.r['oneplot'](l, generate=False)
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

