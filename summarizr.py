import cherrypy
import rpy2.robjects as robjects
import json, os

class RGraphs(object):

	def index(self):
		return """
        <html><body>
            <h2>Upload a file</h2>
            <form action="graph" method="post" enctype="multipart/form-data">
	    Enter a google docs csv export url:
		<input type="string" name="doc" /> <br/>
	    Enter aggregation column name:
		<input type="string" name="aggBy" /> <br/>
		<input type="radio" name="generate" value="False" checked /> Just display images. 
		<input type="radio" name="generate" value="True" /> Generate new images (takes a while). <br />
            <input type="submit" />
            </form>
        </body></html>
        """
	index.exposed = True

	def graph(self, doc, aggBy, generate):
		robjects.r("library(RCurl)")
		doc = doc or 'https://docs.google.com/spreadsheet/pub?hl=en_US&hl=en_US&key=0AqkhmY48RtzudFBxUjR3NHVQdUZyQjFkODRyWV9wNGc&output=csv'
		df = robjects.r("read.csv(textConnection(getURL('" + doc + "')))")
		#df = robjects.r("read.csv('tmpfile')")
		print doc
		if aggBy in robjects.r['names'](df):
			graphlist = self.graphs(df, aggBy, generate=="True")
		else:
			graphlist = self.graphs(df, None, generate=="True")
		return "<html><body><ul><li>" + "</li><li>".join(graphlist) + "</li></ul></body></html>"
	graph.exposed = True

	def graphs(self, df, aggBy=None, generate=False):
		#generate = True
		robjects.r['source']('summarizr.R')
		l = []
		if aggBy:
			l = robjects.r['ggraphs_with_agg'](df, aggBy)
		else:
			l = robjects.r['ggraphs'](df)
		if generate:
			old_d = robjects.r('getwd()')
			robjects.r('setwd("' + os.path.join(os.getcwd(), "static") + '")')
			filenames = robjects.r['oneplot'](l) 
			robjects.r['setwd'](old_d)
		else:
			filenames = robjects.r['oneplot'](l, generate=False)
		return map(lambda s:'<a href="static/' + s + '"><img src="static/' + s + '" / ></a>' + s + '<br/>', filenames)

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

