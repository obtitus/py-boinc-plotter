<%!
## python module-level code
import datetime
import pyBoincPlotter.boinccmd
def tag(name, attribute='', content=''):
    """There is probably a better way of doing this, but saves some typing.
    Returns <{name} {attribute}>{content}</{name}>"""
    return "<{name} {attribute}>{content}</{name}>\n".format(name=name, 
                                                             content=content,
                                                             attribute=attribute)
%>
<%
## python code block
def makeRow(task):
    ret = ''
    for item in task.toString():
        ret += tag('td', content=item)
    return tag('tr', content=ret)
def makeTable(app):
    ret = ''
    for task in app.tasks: # row
        ret += makeRow(task)
    return tag('table', 'cellpadding="4" style="border: 1px solid #000000; border-collapse: collapse;" border="1"', ret)
%>

<html><head></head><body>
<h1></h1>
% for key, project in sorted(pyBoincPlotter.boinccmd.get_state().items()):
    % if len(project) == 0:
        <% continue %>:
    % endif
    <h2>${project.name}</h2>
    <p>
    % for prop in [project.settings, project.statistics]:
        ${prop}
    </p>
    % endfor
    % for key, app in sorted(project.applications.items()):
        % if len(app) == 0:
            <% continue %>:
        % endif
        <h3>${app.name}</h3>
        ${str(app.statistics)}
        ${str(app.badge)}
        ${makeTable(app)}
    % endfor
% endfor
</body></html>
