import cherrypy
import rpy2.robjects as robjects
import json, os
robjects.r['source']('summarizr.R')

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


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
		if doc=="":
			df = robjects.r("read.csv('tmpfile')")
		else:
			df = robjects.r("read.csv(textConnection(getURL('" + doc + "')))")
		if aggBy in robjects.r['names'](df):
			graphlist = self.graphs(df, aggBy, generate=="True")
		else:
			graphlist = self.graphs(df, None, generate=="True")
		template = env.get_template("graph.html")
		rawlist = map(lambda s:s.split('.')[0], graphlist)
		return template.render(graphlist=rawlist, ext='svg')

        graph.exposed = True

	def graphs(self, df, aggBy=None, generate=False):
		#generate = True
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
		return filenames
		#return map(lambda s:'<a href="static/' + s + '"><img src="static/' + s + '" / ></a>' + s + '<br/>', filenames)

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

