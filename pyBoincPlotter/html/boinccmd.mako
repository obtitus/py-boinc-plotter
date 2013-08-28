<%!
## python module-level code
import datetime
import pyBoincPlotter.boinccmd
def tag(name, attribute='', content=''):
    """There is probably a better way of doing this, but saves some typing.
    Returns <{name} {attribute}>{content}</{name}>"""
    return "<{name} {attribute}>{content}</{name}>".format(name=name, 
                                                           content=content,
                                                           attribute=attribute)
%>
<%
## python code block
def makeRow(task):
    ret = ''
    for item in task.toString():
        ret += tag('td', content=item)
    # for name in range(row):
    #     ret += tag('td', datetime.datetime.now(), 'bgcolor="red"') #'<td>{}</td>'.format(name)
    return tag('tr', ret)
def makeTable(app):
    ret = ''
    for task in app.tasks: # row
        ret += makeRow(task)
    return tag('table', 'cellpadding="4" style="border: 1px solid #000000; border-collapse: collapse;" border="1"', ret)
%>

<html><head></head><body>
<h1></h1>
% for key, project in sorted(pyBoincPlotter.boinccmd.get_state().items()):
    % for key, app in sorted(project.applications.items()):
        ${makeTable(app)}
    % endfor
% endfor
</body></html>
