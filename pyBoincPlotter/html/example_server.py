#!/usr/bin/env python
"""Example server for displaying local boinc status. 
Run: python example_server.py
and the point your web browser to: http://localhost:8080/boinccmd.mako
The heavy lifting is done by wsgiref which is a standard python module and mako, see also boinccmd.mako

I found the following introductions helpefull:
* http://www.pixelmonkey.org/2012/06/14/web-app introduces 'View', 'Template', 'Database', 'Web server'
* http://baltazaar.wordpress.com/2011/09/09/easy-way-to-get-apache-and-mod_wsgi-working-on-os-x/ Step by step for apache osx server
"""
from wsgiref.simple_server import make_server
from mako.template import Template

def renderTemplate(file):
    template = Template(filename = file, output_encoding = 'ascii')
    return template.render()

def app(environ, start_response):
    """This is used by the wsgiref.simple_server and is usefull for local generation 
    (ie. http://localhost:8080/boinccmd.mako)"""
    start_response('200 OK', [])
    path = environ['PATH_INFO'][1:]     # strip the leading slash
    return '' if path == 'favicon.ico' else [renderTemplate(path)]  # ignore request for favicon

def application(environ, start_response):
    """This is used by the mod_wsgi to sit on a apache server,
    use something like: http://10.0.1.5/boinccmd.py
    VOPS: note the hardcoded path to boinccmd.mako!"""
    status = '200 OK'
    print 'STATUS', status
    output = renderTemplate('/Library/WebServer/Documents/boinccmd.mako')

    response_headers = [('Content-type', 'text/html'),
    ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

if __name__ == '__main__':
    server = make_server('127.0.0.1', 8080, app)
    server.serve_forever()
