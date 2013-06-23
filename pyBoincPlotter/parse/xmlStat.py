# TODO: convert to beautiful-soup
def parse(page):
    tree = xml.etree.ElementTree.fromstring(page)

    e = tree.find('Error')
    if e:
        print e.text
        return None, None

    try:
        member = tree.iter('MemberStat').next()
    except StopIteration:
        print 'Something is wrong with xml statisics, correct username and code?'
        return None, None
    lastResult = member.find('LastResult').text
    lastResult = lastResult.replace('T', ' ')

    stat = list()
    for s in ['RunTime', 'RunTimeRank', 'RunTimePerDay',
              'Points', 'PointsRank', 'PointsPerDay',
              'Results', 'ResultsRank', 'ResultsPerDay']:
        i = member.iter(s).next()
        stat.append(i.text)
    statistics = Statistics_worldcommunitygrid(lastResult, *stat)
    
    projects = dict()
    for project in tree.iter('Project'):
        short = project.find('ProjectShortName').text
        name = project.find('ProjectName').text
        runtime = project.find('RunTime').text
        points = project.find('Points').text
        results = project.find('Results').text
        projects[name] = Project(short, name, runtime, points, results)

    for badge in tree.iter('Badge'):
        name = badge.find('ProjectName').text
        badgeURL = badge.iter('Url').next().text        
        t = badge.iter('Description').next().text
        projects[name].badge = t
        projects[name].badgeURL = badgeURL
#         for key in projects:
#             if projects[key].name == name:
#                 projects[key].badge += badge
                
    return statistics, projects
