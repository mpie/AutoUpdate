import urllib,re,string,sys,os
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import time,threading

addon_id = 'plugin.video.doofree'
selfAddon = xbmcaddon.Addon(id=addon_id)
doofreepath = selfAddon.getAddonInfo('path')
grab = None
fav = False
hostlist = None
Dir = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.doofree', ''))
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
hosts = 'putlocker,sockshare,billionuploads,hugefiles,mightyupload,movreel,lemuploads,180upload,megarelease,filenuke,flashx,gorillavid,bayfiles,veehd,vidto,mailru,videomega,epicshare,bayfiles,2gbhosting,alldebrid,allmyvideos,vidspot,castamp,cheesestream,clicktoview,crunchyroll,cyberlocker,daclips,dailymotion,divxstage,donevideo,ecostream,entroupload,facebook,filebox,hostingbulk,hostingcup,jumbofiles,limevideo,movdivx,movpod,movshare,movzap,muchshare,nolimitvideo,nosvideo,novamov,nowvideo,ovfile,play44_net,played,playwire,premiumize_me,primeshare,promptfile,purevid,rapidvideo,realdebrid,rpnet,seeon,sharefiles,sharerepo,sharesix,skyload,stagevu,stream2k,streamcloud,thefile,tubeplus,tunepk,ufliq,upbulk,uploadc,uploadcrazynet,veoh,vidbull,vidcrazynet,video44,videobb,videofun,videotanker,videoweed,videozed,videozer,vidhog,vidpe,vidplay,vidstream,vidup,vidx,vidxden,vidzur,vimeo,vureel,watchfreeinhd,xvidstage,yourupload,youtube,youwatch,zalaa,zooupload,zshare'
art = ''
fanartimage = ''
VERSION = str(selfAddon.getAddonInfo('version'))

def OPENURL(url, mobile = False, q = False, verbose = True, timeout = 10, cookie = None, data = None, cookiejar = False, log = True, headers = [], type = '',ua = False):
    import urllib2
    UserAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
    if ua: UserAgent = ua
    try:
        if log:
            print "Openurl = " + url
        if cookie and not cookiejar:
            import cookielib
            cookie_file = os.path.join(os.path.join(datapath,'Cookies'), cookie+'.cookies')
            cj = cookielib.LWPCookieJar()
            if os.path.exists(cookie_file):
                try: cj.load(cookie_file,True)
                except: cj.save(cookie_file,True)
            else: cj.save(cookie_file,True)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        elif cookiejar:
            import cookielib
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = urllib2.build_opener()
        if mobile:
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')]
        else:
            opener.addheaders = [('User-Agent', UserAgent)]
        for header in headers:
            opener.addheaders.append(header)
        if data:
            if type == 'json':
                import json
                data = json.dumps(data)
                opener.addheaders.append(('Content-Type', 'application/json'))
            else: data = urllib.urlencode(data)
            response = opener.open(url, data, timeout)
        else:
            response = opener.open(url, timeout=timeout)
        if cookie and not cookiejar:
            cj.save(cookie_file,True)
        link=response.read()
        response.close()
        opener.close()
        #link = net(UserAgent).http_GET(url).content
        link=link.replace('&#39;',"'").replace('&quot;','"').replace('&amp;',"&").replace("&#39;","'").replace('&lt;i&gt;','').replace("#8211;","-").replace('&lt;/i&gt;','').replace("&#8217;","'").replace('&amp;quot;','"').replace('&#215;','x').replace('&#038;','&').replace('&#8216;','').replace('&#8211;','').replace('&#8220;','').replace('&#8221;','').replace('&#8212;','')
        link=link.replace('%3A',':').replace('%2F','/')
        if q: q.put(link)
        return link
    except Exception as e:
        if verbose:
            xbmc.executebuiltin("XBMC.Notification(Sorry!,Source Website is Down,3000,"+elogo+")")
        xbmc.log('***********Website Error: '+str(e)+'**************', xbmc.LOGERROR)
        import traceback
        traceback.print_exc()
        link ='website down'
        if q: q.put(link)
        return link

def setGrab():
    global grab
    if grab is None:
        from metahandler import metahandlers
        grab = metahandlers.MetaData()

def getFav():
    global fav
    if not fav:
        from resources.universal import favorites
        fav = favorites.Favorites(addon_id, sys.argv)
    return fav
################################################################################ Movies Metahandler ##########################################################################################################

def formatCast(cast):
    roles = "\n\n"
    for role in cast:
        roles =  roles + "[COLOR blue]" + role[0] + "[/COLOR] as " + role[1] + " | "
    return roles

def GETMETAT(mname,genre,fan,thumb,plot='',imdb='',tmdb=''):
    originalName=mname
    #print 'metaView:' + selfAddon.getSetting("meta-view")
    if selfAddon.getSetting("meta-view") == "true":
        setGrab()
        mname = re.sub(r'\[COLOR red\]\(?(\d{4})\)?\[/COLOR\]',r'\1',mname)
        mname = removeColoredText(mname)
        mname = mname.replace(' EXTENDED and UNRATED','').replace('Webrip','').replace('MaxPowers','').replace('720p','').replace('1080p','').replace('TS','').replace('HD','').replace('R6','').replace('H.M.','').replace('HackerMil','').replace('(','').replace(')','').replace('[','').replace(']','')
        mname = mname.replace(' Extended Cut','').replace('Awards Screener','')
        mname = re.sub('Cam(?![A-Za-z])','',mname)
        mname = re.sub('(?i)3-?d h-?sbs','',mname)
        mname = mname.strip()
        if re.findall('\s\d{4}',mname):
            r = re.split('\s\d{4}',mname,re.DOTALL)
            name = r[0]
            year = re.findall('\s(\d{4})\s',mname + " ")
            if year: year = year[0]
            else: year=''
        else:
            name=mname
            year=''
        name = name.decode("ascii", "ignore")
        meta = grab.get_meta('movie',name,imdb,tmdb,year)# first is Type/movie or tvshow, name of show,tvdb id,imdb id,string of year,unwatched = 6/watched  = 7
        if not meta['year']:
            name  = re.sub(':.*','',name)
            meta = grab.get_meta('movie',name,imdb,tmdb,year)
        print "Movie mode: %s"%name
        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
          'plot': meta['plot'],'metaName': mname, 'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],'overlay':meta['overlay'],
          'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url'],'tmdb_id': meta['tmdb_id'],'year': meta['year'],
          'imdb_id' : meta['imdb_id']}
        if infoLabels['genre']=='':
            infoLabels['genre']=genre
        if infoLabels['cover_url']=='':
            infoLabels['cover_url']=thumb
        if infoLabels['backdrop_url']=='':
            if fan=='': fan=fanartimage
            else: fan=fan
            infoLabels['backdrop_url']=fan
        if meta['overlay'] == 7: infoLabels['playcount'] = 1
        else: infoLabels['playcount'] = 0
        if infoLabels['cover_url']=='':
            thumb=art+'/vidicon.png'
            infoLabels['cover_url']=thumb
        #if int(year+'0'):
        #    infoLabels['year']=year
        infoLabels['title']=originalName
        if infoLabels['plot']=='': infoLabels['plot']=plot
        else: infoLabels['plot'] = infoLabels['plot'] + formatCast(infoLabels['cast'])
    else:
        if thumb=='': thumb=art+'/vidicon.png'
        if fan=='': fan=fanartimage
        else: fan=fan
        infoLabels = {'title': mname,'metaName': mname,'cover_url': thumb,'backdrop_url': fan,'season': '','episode': '','year': '','plot': '','genre': genre,'imdb_id': '','tmdb_id':''}
    return infoLabels

def ErrorReport(e):
    elogo = xbmc.translatePath('special://home/addons/plugin.video.movie25/resources/art/bigx.png')
    xbmc.executebuiltin("XBMC.Notification([COLOR=FF67cc33]Mash Up Error[/COLOR],"+str(e)+",10000,"+elogo+")")
    xbmc.log('***********Bampi Error: '+str(e)+'**************', xbmc.LOGERROR)
################################################################################ TV Shows Metahandler ##########################################################################################################

def GETMETAEpiT(mname,thumb,desc):
        originalName=mname
        mname = removeColoredText(mname)
        if selfAddon.getSetting("meta-view-tv") == "true":
                setGrab()
                mname = mname.replace('New Episode','').replace('Main Event','').replace('New Episodes','')
                mname = mname.strip()
                r = re.findall('(.+?)\ss(\d+)e(\d+)\s',mname + " ",re.I)
                if not r: r = re.findall('(.+?)\sseason\s(\d+)\sepisode\s(\d+)\s',mname + " ",re.I)
                if not r: r = re.findall('(.+?)\s(\d+)x(\d+)\s',mname + " ",re.I)
                if r:
                    for name,sea,epi in r:
                        year=''
                        name=name.replace(' US','').replace(' (US)','').replace(' (us)','').replace(' (uk Series)','').replace(' (UK)','').replace(' UK',' (UK)').replace(' AU','').replace(' AND',' &').replace(' And',' &').replace(' and',' &').replace(' 2013','').replace(' 2011','').replace(' 2012','').replace(' 2010','')
                        if re.findall('twisted',name,re.I):
                            year='2013'
                        if re.findall('the newsroom',name,re.I):
                            year='2012'
                        metaq = grab.get_meta('tvshow',name,None,None,year)
                        imdb=metaq['imdb_id']
                        tit=metaq['title']
                        year=metaq['year']
                        epiname=''
                else:
                    metaq=''
                    name=mname
                    epiname=''
                    sea=0
                    epi=0
                    imdb=''
                    tit=''
                    year=''
                meta = grab.get_episode_meta(str(name),imdb, int(sea), int(epi))
                print "Episode Mode: Name %s Season %s - Episode %s"%(str(name),str(sea),str(epi))
                infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'premiered':meta['premiered'],
                      'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'overlay':meta['overlay'],'episode': meta['episode'],
                              'season': meta['season'],'backdrop_url': meta['backdrop_url']}

                if infoLabels['cover_url']=='':
                        if metaq!='':
                            thumb=metaq['cover_url']
                            infoLabels['cover_url']=thumb

                if infoLabels['backdrop_url']=='':
                        fan=fanartimage
                        infoLabels['backdrop_url']=fan
                if infoLabels['cover_url']=='':
                    if thumb=='':
                        thumb=art+'/vidicon.png'
                        infoLabels['cover_url']=thumb
                    else:
                        infoLabels['cover_url']=thumb
                infoLabels['imdb_id']=imdb
                if meta['overlay'] == 7:
                   infoLabels['playcount'] = 1
                else:
                   infoLabels['playcount'] = 0

                infoLabels['showtitle']=tit
                infoLabels['year']=year
                infoLabels['metaName']=infoLabels['title']
                infoLabels['title']=originalName

        else:
                fan=fanartimage
                infoLabels = {'title': originalName,'metaName': mname,'cover_url': thumb,'backdrop_url': fan,'season': '','episode': '','year': '','plot': desc,'genre': '','imdb_id': ''}

        return infoLabels
############################################################################### Playback resume/ mark as watched #################################################################################

def WatchedCallback():
        xbmc.log('%s: %s' % (selfAddon.addon.getAddonInfo('name'), 'Video completely watched.'), xbmc.LOGNOTICE)
        videotype='movies'
        setGrab()
        grab.change_watched(videotype, name, iconimage, season='', episode='', year='', watched=7)
        xbmc.executebuiltin("XBMC.Container.Refresh")

def WatchedCallbackwithParams(video_type, title, imdb_id, season, episode, year):
    print "worked"
    setGrab()
    grab.change_watched(video_type, title, imdb_id, season=season, episode=episode, year=year, watched=7)
    xbmc.executebuiltin("XBMC.Container.Refresh")

def ChangeWatched(imdb_id, videoType, name, season, episode, year='', watched='', refresh=False):
        setGrab()
        grab.change_watched(videoType, name, imdb_id, season=season, episode=episode, year=year, watched=watched)
        xbmc.executebuiltin("XBMC.Container.Refresh")

def refresh_movie(vidtitle,imdb, year=''):

    #global metaget
    #if not metaget:
    #    metaget=metahandlers.MetaData()
    vidtitle = vidtitle.decode("ascii", "ignore")
    if re.search("^\d+", vidtitle):
        m = re.search('^(\d+)(.*)', vidtitle)
        vidtitle = m.group(1) + m.group(2)
    else: vidtitle = re.sub("\d+", "", vidtitle)
    vidtitle=vidtitle.replace('  ','')
    setGrab()
    search_meta = grab.search_movies(vidtitle)

    if search_meta:
        movie_list = []
        for movie in search_meta:
            movie_list.append(movie['title'] + ' (' + str(movie['year']) + ')')
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose', movie_list)

        if index > -1:
            new_imdb_id = search_meta[index]['imdb_id']
            new_tmdb_id = search_meta[index]['tmdb_id']
            year=search_meta[index]['year']

            meta=grab.update_meta('movie', vidtitle, imdb, '',new_imdb_id,new_tmdb_id,year)



            xbmc.executebuiltin("Container.Refresh")
    else:
        xbmcgui.Dialog().ok('Refresh Results','No matches found')

def episode_refresh(vidname, imdb, season_num, episode_num):
    setGrab()
    grab.update_episode_meta(vidname, imdb, season_num, episode_num)
    xbmc.executebuiltin("XBMC.Container.Refresh")

################################################################################ Types of Directories ##########################################################################################################
def getFile(path):
    content = None
    if os.path.exists(path):
        try: content = open(path).read()
        except: pass
    return content

def setFile(path,content,force=False):
    if os.path.exists(path) and not force:
        return False
    else:
        try:
            open(path,'w+').write(content)
            return True
        except: pass
    return False

def addDirX(name,url,mode,iconimage,plot='',fanart='',dur=0,genre='',year='',imdb='',tmdb='',isFolder=True,searchMeta=False,addToFavs=True,
            id=None,fav_t='',fav_addon_t='',fav_sub_t='',metaType='Movies',menuItemPos=None,menuItems=None,down=False,replaceItems=True):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&plot="+urllib.quote_plus(plot)+"&fanart="+urllib.quote_plus(fanart)+"&genre="+urllib.quote_plus(genre)
    if 'http://api.video.mail.ru/videos/embed/' in url or mode==364:
        name=name.decode('windows-1251')
        plot=plot.decode('windows-1251')
    print 'searchMeta:' + str(searchMeta)
    print 'metaType:' + metaType
    if searchMeta:
        if metaType == 'TV':
            infoLabels = GETMETAEpiT(name,iconimage,plot)
        else:
            '''
            print 'name:' + name
            print 'genre:' + genre
            print 'fanart:' + fanart
            print 'iconimage:' + iconimage
            print 'plot:' + plot
            print 'imdb:' + imdb
            print 'tmdb:' + tmdb
            '''
            infoLabels = GETMETAT(name,genre,fanart,iconimage,plot,imdb,tmdb)
        iconimage = infoLabels['cover_url']
        fanart = infoLabels['backdrop_url']
        plot = infoLabels['plot']
    if not fanart: fanart=fanartimage
    if not iconimage: iconimage=art+'/vidicon.png'
    if not plot: plot='Sorry description not available'
    plot=plot.replace(",",'.')
    Commands = []
    if addToFavs:
        fav = getFav()
        fname = name.replace(",",'')
        if isFolder:
            Commands.append(("[B][COLOR blue]Add[/COLOR][/B] to My Fav's",fav.add_directory(fname, u, section_title=fav_t, section_addon_title=fav_addon_t+" Fav's", sub_section_title=fav_sub_t, img=iconimage, fanart=fanart, infolabels={'item_mode':mode, 'item_url':url, 'plot':plot,'duration':dur,'genre':genre,'year':year})))
        else:
            Commands.append(("[B][COLOR blue]Add[/COLOR][/B] to My Fav's",fav.add_video_item(fname, u, section_title=fav_t, section_addon_title=fav_addon_t+" Fav's", sub_section_title=fav_sub_t, img=iconimage, fanart=fanart, infolabels={'item_mode':mode, 'item_url':url, 'plot':plot,'duration':dur,'genre':genre,'year':year})))
        Commands.append(("[B][COLOR red]Remove[/COLOR][/B] from My Fav's",fav.delete_item(fname, section_title=fav_t, section_addon_title=fav_addon_t+" Fav's", sub_section_title=fav_sub_t)))
    if down:
        sysurl = urllib.quote_plus(url)
        sysname= urllib.quote_plus(name)
        Commands.append(('Direct Download', 'XBMC.RunPlugin(%s?mode=190&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
        Commands.append(('Download with jDownloader', 'XBMC.RunPlugin(%s?mode=776&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
    if searchMeta:
        if metaType == 'TV' and selfAddon.getSetting("meta-view-tv") == "true":
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            cname = infoLabels['title']
            cname = cname.decode('ascii', 'ignore')
            cname = urllib.quote_plus(cname)
            sea = infoLabels['season']
            epi = infoLabels['episode']
            imdb_id = infoLabels['imdb_id']
            if imdb_id != '':
                if infoLabels['overlay'] == 6: watched_mark = 'Mark as Watched'
                else: watched_mark = 'Mark as Unwatched'
                Commands.append((watched_mark, 'XBMC.RunPlugin(%s?mode=779&name=%s&url=%s&iconimage=%s&season=%s&episode=%s)' % (sys.argv[0], cname, 'episode', imdb_id,sea,epi)))
            Commands.append(('Refresh Metadata', 'XBMC.RunPlugin(%s?mode=780&name=%s&url=%s&iconimage=%s&season=%s&episode=%s)' % (sys.argv[0], cname, 'episode',imdb_id,sea,epi)))
        elif metaType == 'Movies' and selfAddon.getSetting("meta-view") == "true":
            xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
            if id != None: xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PLAYLIST_ORDER )
            else: xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )
            cname=urllib.quote_plus(infoLabels['metaName'])
            imdb_id = infoLabels['imdb_id']
            if infoLabels['overlay'] == 6: watched_mark = 'Mark as Watched'
            else: watched_mark = 'Mark as Unwatched'
            Commands.append((watched_mark, 'XBMC.RunPlugin(%s?mode=777&name=%s&url=%s&iconimage=%s)' % (sys.argv[0], cname, 'movie',imdb_id)))
            Commands.append(('Play Trailer','XBMC.RunPlugin(%s?mode=782&name=%s&url=%s&iconimage=%s)'% (sys.argv[0],cname,'_',imdb_id)))
            Commands.append(('Refresh Metadata', 'XBMC.RunPlugin(%s?mode=778&name=%s&url=%s&iconimage=%s)' % (sys.argv[0], cname, 'movie',imdb_id)))
    else:
        infoLabels={ "Title": name, "Plot": plot, "Duration": dur, "Year": year ,"Genre": genre,"OriginalTitle" : removeColoredText(name) }
    if id != None:
        infoLabels["count"] = id
    Commands.append(('Watch History','XBMC.Container.Update(%s?name=None&mode=222&url=None&iconimage=None)'% (sys.argv[0])))
    Commands.append(("My Fav's",'XBMC.Container.Update(%s?name=None&mode=639&url=None&iconimage=None)'% (sys.argv[0])))
    Commands.append(('[B][COLOR=FF67cc33]Doofree[/COLOR] Settings[/B]','XBMC.RunScript('+xbmc.translatePath(doofreepath + '/resources/libs/settings.py')+')'))
    if menuItemPos != None:
        for mi in reversed(menuItems):
            Commands.insert(menuItemPos,mi)
    liz=xbmcgui.ListItem(name, iconImage=art+'/vidicon.png', thumbnailImage=iconimage)
    liz.addContextMenuItems( Commands, replaceItems=False)
    liz.setInfo( type="Video", infoLabels=infoLabels )
    liz.setProperty('fanart_image', fanart)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)

def addDir(name,url,mode,iconimage,plot=''):
    return addDirX(name,url,mode,iconimage,plot,addToFavs=0,replaceItems=False)

def addDirHome(name,url,mode,iconimage):
    return addDirX(name,url,mode,iconimage,addToFavs=0)

def addPlayc(name,url,mode,iconimage,plot,fanart,dur,genre,year):
    return addDirX(name,url,mode,iconimage,plot,fanart,dur,genre,year,isFolder=0,addToFavs=0)

def addSpecial(name,url,mode,iconimage):
    liz=xbmcgui.ListItem(name,iconImage="",thumbnailImage = iconimage)
    liz.setProperty('fanart_image', fanartimage)
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)

def removeColorTags(text):
    return re.sub('\[COLOR[^\]]{,15}\]','',text.replace("[/COLOR]", ""),re.I|re.DOTALL).strip()

def removeColoredText(text):
    return re.sub('\[COLOR.*?\[/COLOR\]','',text,re.I|re.DOTALL).strip()

def downloadFile(url,dest,silent = False,cookie = None):
    try:
        import urllib2
        file_name = url.split('/')[-1]
        print "Downloading: %s" % (file_name)
        if cookie:
            import cookielib
            cookie_file = os.path.join(os.path.join(datapath,'Cookies'), cookie+'.cookies')
            cj = cookielib.LWPCookieJar()
            if os.path.exists(cookie_file):
                try: cj.load(cookie_file,True)
                except: cj.save(cookie_file,True)
            else: cj.save(cookie_file,True)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
        u = opener.open(url)
        f = open(dest, 'wb')
        meta = u.info()
        if meta.getheaders("Content-Length"):
            file_size = int(meta.getheaders("Content-Length")[0])
        else: file_size = 'Unknown'
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer: break
            file_size_dl += len(buffer)
            f.write(buffer)
#             status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
#             status = status + chr(8)*(len(status)+1)
#             print status,
        print "Downloaded: %s %s Bytes" % (file_name, file_size)
        f.close()
        return True
    except Exception, e:
        print 'Error downloading file ' + url.split('/')[-1]
        main.ErrorReport(e)
        if not silent:
            dialog = xbmcgui.Dialog()
            dialog.ok("Doofree", "Report the error below to your supplier ", str(e), "We will try our best to help you")
        return False

#MBox movies/series
def addDown4(name,url,mode,iconimage,plot,fanart,dur,genre,year):
    '''
    print "addDown4 Name: "+str(name) + '<------'
    print "addDown4 Url: "+str(url) + '<------'
    print "addDown4 Mode: "+str(mode) + '<------'
    print "addDown4 iconimage: "+str(iconimage) + '<------'
    print "addDown4 plot: "+str(plot) + '<------'
    '''
    f = '</sublink>' in url
    if re.search('(?i)\ss(\d+)e(\d+)',name) or re.search('(?i)Season(.+?)Episode',name):
        return addDirX(name,url,mode,iconimage,plot,fanart,dur,genre,year,isFolder=f,searchMeta=1,metaType='TV',
                       fav_t='TV',fav_addon_t='TV Episode',fav_sub_t='Episodes',down=not f)
    else:
        return addDirX(name,url,mode,iconimage,plot,fanart,dur,genre,year,isFolder=f,searchMeta=1,metaType='Movies',
                       fav_t='Movies',fav_addon_t='Movie',down=not f)

#Music
def addDirMs(name,url,mode,iconimage,plot,fanart,dur,genre,year):
    print "Music Mode: "+str(mode) + '<------'
    return addDirX(name,url,mode,iconimage,plot,fanart,dur,genre,year,fav_t='Misc.',fav_addon_t='Misc.')

#TV
def addDirT(name,url,mode,iconimage,plot,fanart,dur,genre,year):
    return addDirX(name,url,mode,iconimage,plot,fanart,dur,genre,year,fav_t='TV',fav_addon_t='TV Show',fav_sub_t='Shows')
############################################################################### Resolvers ############################################################################################
def resolve_url(url,filename = False):
    import resolvers
    return resolvers.resolve_url(url,filename)

