#!/usr/bin/env python
"""Example server for displaying local boinc status. 
Run: python example_server.py
and the point your web browser to: http://localhost:8080/boinccmd.mako
The heavy lifting is done by wsgiref which is a standard python module and mako, see also boinccmd.mako"""
from wsgiref.simple_server import make_server
from mako.template import Template

def renderTemplate(file):
    template = Template(filename = file, output_encoding = 'ascii')
    return template.render()

def app(environ, start_response):
    start_response('200 OK', [])
    path = environ['PATH_INFO'][1:]     # strip the leading slash
    return '' if path == 'favicon.ico' else [renderTemplate(path)]  # ignore request for favicon

if __name__ == '__main__':
    server = make_server('127.0.0.1', 8080, app)
    server.serve_forever()
