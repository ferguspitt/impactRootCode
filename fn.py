def fn(topicURL):
    topicData=BeautifulSoup(getPage(topicURL,header1Type,header1Value),'html5lib')
    Footnotes=[]
    citations=topicData.findAll('span',{'class': re.compile('^citation')})
    # check for archiving sites:
    for citation in citations:
        if len(citation.findAll('a',{'class': re.compile('^external')})) ==1:
            Footnotes.append(citation.findAll('a',{'class':re.compile('^external')})[0])
        else:
            if len(citation.findAll('a',{'class': re.compile('^external')})) >1:
                for link in citation.findAll('a',{'class': re.compile('^external')}):
                    if 'webcitation.org' in link.get('href'):
                        webcitationLog=open(filesLocation+'webcitationLog.log','a')
                        problemcite=str(citation)
                        webcitationLog.write(problemcite)
                        webcitationLog.write('\n\n')
                        webcitationLog.close()
                        print 'citation fail'
                    if 'web.archive.org' in link.get('href'):
                        archivedLog=open(filesLocation+'webarchivedLog.log','a')
                        problemcite=str(citation)
                        archivedLog.write(problemcite)
                        archivedLog.write('\n\n')
                        archivedLog.close()
                        # later: compare the two links in the citation, get rid of the preceder, then choose
                        print 'slightly less fail'
                    if 'webcitation.org' not in link.get('href') and 'web.archive.org' not in link.get('href'):
                        Footnotes.append(link)
                    else:
                        print 'dunno'
    return Footnotes

