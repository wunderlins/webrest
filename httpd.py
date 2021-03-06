#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

REST example with json/xml/txt and html output. The output is controlled 
by the http Accept request header

Example:
curl -iH "Accept: application/json" localhost:8082/a/b/c
curl -iH "Accept: text/xml" localhost:8082/a/b/c
curl -iH "Accept: text/html" localhost:8082/a/b/c
curl -iH "Accept: text/plain" localhost:8082/a/b/c

Using a different method:
curl -XDELETE  -iH "Accept: text/xml" localhost:8082/a/b/c

if the Accept header is missing, json is the default.

"""

try:
	import simplejson as json
except ImportError:
	import json
import sys, os

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'web.py-0.37'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'python-mimeparse-1.5.1'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'mimerender-master', 'src'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'dicttoxml-1.6.6'))

import pprint
import mimerender
import web
import dicttoxml
from xml.dom.minidom import parseString

mimerender = mimerender.WebPyMimeRender()

urls = (
	'/rest/(.*)', 'rest',
	'/test', 'posttest'
)

class wsgiapp(web.application):
	def run(self, port=8080, ip='127.0.0.1', *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, (ip, port))

class renderer(object):
	
	@staticmethod
	def dict2xml(d):
		return parseString(dicttoxml.dicttoxml(d, \
		                   custom_root="root")).toprettyxml()
	
	@staticmethod
	def dict2json(d):
		return json.dumps(d)
	
	@staticmethod
	def dict2txt(d):
		pp = pprint.PrettyPrinter(indent=4, width=1)
		return pp.pformat(d)
	
	@staticmethod
	def dict2html(d):
		buffer = '<table border="1" style="border-collapse: collapse;"><tbody>'
		for e in d:
			buffer += "<tr><td>" + str(e) + "</td><td>"
			if type(d[e]) is dict: # or type(d[e]) is list:
				buffer += renderer.dict2html(d[e])
			else:
				buffer += str(d[e])
			buffer += "</td></tr>"
		buffer += '</tbody></table>'
	
		return buffer

class posttest:
	def POST(self):
		print web.data()
		
		return "It works!!!1!!1"
	
	def GET(self):
		web.header("Content-type", "text/html")
		return """
		
<script>
function send_form() {
	var r = new XMLHttpRequest();
	r.open("POST", "/rest/aaaaaaaaa", true);
	r.setRequestHeader("Content-Type","application/json; charset=utf-8");
	r.onreadystatechange = function () {
		if (r.readyState==4 && r.status==200) {
			//console.log(data)
			data = JSON.parse(r.responseText);
			alert(data)
			return
		} else if (r.readystate == 4) {
			alert("shit happened");
		}
	};
	r.send(JSON.stringify(
		{a: 1, b: 2, c: [0,1,2]}
	));
}
</script>		
		
<form method="POST" action="/test">
	<input type="text" name="aaaaa" value="asd fasfd adsf asdf asfd af" />
	<button type="submit">hit me!</button>
</form>

<button type="button" onclick="send_form()">Send json</button>

"""

class rest:
	render_xml  = lambda **args: renderer.dict2xml(args)
	render_json = lambda **args: renderer.dict2json(args)
	render_html = lambda **args: '<!DOCTYPE html>\n<html>\n<body>\n' + \
	                             renderer.dict2html(args) + "\n</body>\n</html>"
	render_txt  = lambda **args: renderer.dict2txt(args)
	
	@mimerender(
		default = 'json',
		#html = render_html,
		json = render_json,
		xml  = render_xml,
		txt  = render_txt
	)
	def GET (self, name):
		if not name: 
			name = 'world'
		data = {
			'message': 'Hello, ' + name + '!', 
			"sub": {
				"array": [1,2,3], 
				"list": {"a": 1, "b": 2}
			}
		}
		return data
		
	@mimerender(
		default = 'json',
		json = render_json
	)
	def POST(self, name):
		print json.loads(web.data())
		pprint.pprint(web.data())
		return json.loads(web.data())

if __name__ == "__main__":
	web.config.debug = True
	app = wsgiapp(urls, globals())
	app.run(port=8082)
	
