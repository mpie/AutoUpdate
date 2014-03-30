import re, urllib2, urllib, json, threading, os, zipfile, shutil
import xbmcaddon, xbmcplugin, xbmcgui, xbmc
from t0mm0.common.net import Net as net

ADDON = xbmcaddon.Addon(id='plugin.video.doofree')
PATH = 'doofree'
VERSION = '1.1.6'
base_url = ''
addon_handle = ''

master_json = "https://raw.githubusercontent.com/mpie/doofree/master/json/master.json"
seesantv = "http://www.seesantv.com/seesantv_2014/"
asia=["http://as11.seesantv.com/"]
uk=["http://uk23.seesantv.com/", "http://uk24.seesantv.com/", "http://uk12.seesantv.com/", "http://uk13.seesantv.com/", "http://uk25.seesantv.com/", "http://uk1.seesantv.com/", "http://uk27.seesantv.com/"]
us=["http://us14.seesantv.com/"]
thaiChannels=[4,5,6,7,8,9]
chMovies=[10,11]
logo = xbmc.translatePath('special://home/addons/plugin.video.doofree/icon.png')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
UpdatePath=os.path.join(datapath,'Update')

try: os.makedirs(UpdatePath)
except: pass

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

def unzipAndMove(_in, _out , src):
    try:
        zin = zipfile.ZipFile(_in, 'r')
        zin.extractall(_out)
        if src:
            moveFiles(src, _out)
            shutil.rmtree(src)
    except Exception, e:
        print str(e)
        return False
    return True

def moveFiles(root_src_dir,root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)
            
def getUpdateFile(path,default = 0):
    if os.path.exists(path):
        try:
            f = open(path, 'r')
            return f.read()
        except: pass
    return default

def saveUpdateFile(path,value):
    try:
        open(path,'w+').write(value)
    except: pass

def OPENURL(url, mobile = False, q = False, verbose = True, timeout = 10, cookie = None, data = None, cookiejar = False, log = True, headers = [], type = ''):
    UserAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
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
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
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

def resolve_vk(name, url):
    try:
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving %s Link...' % name)
        dialog.update(0)
        print 'VK - Requesting GET URL: %s' % url
        useragent='Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7'
        link2 = net(user_agent=useragent).http_GET(url).content
        if re.search('This video has been removed', link2, re.I):
            xbmc.executebuiltin("XBMC.Notification(This video has been removed,VK,2000)")
            return False
        match = re.search('(?i)<source src="(.+?\.1080.mp4.+?)"',link2)
        if not match:
            match = re.search('(?i)<source src="(.+?\.720.mp4.+?)"',link2)
            if not match:
                match = re.search('(?i)<source src="(.+?\.480.mp4.+?)"',link2)
                if not match:
                    match = re.search('(?i)<source src="(.+?\.360.mp4.+?)"',link2)
                    if not match:
                        match = re.search('(?i)<source src="(.+?\.240.mp4.+?)"',link2)
        if match:
            return match.group(1).replace("\/",'/')
    except Exception, e:
        xbmc.executebuiltin('[B][COLOR white]DooFree[/COLOR][/B]','[COLOR red]%s[/COLOR]' % e, 5000, logo)

def resolve_mbox(name, url):
    try:
        r = re.findall('h=(\d+?)&u=(\d+?)&y=(\d+)',url,re.I)
        if r: r = int(r[0][0]) + int(r[0][1]) + int(r[0][2])
        else: r = 537 + int(re.findall('id=(\d+)',url,re.I)[0])
        link=OPENURL(url,verbose=False)
        q = re.findall('"lang":"en","apple":([-\d]+?),"google":([-\d]+?),"microsoft":"([^"]+?)"',link,re.I)
        vklink = "https://vk.com/video_ext.php?oid="+str(r + int(q[0][0]))+"&id="+str(r + int(q[0][1]))+"&hash="+q[0][2]
    except:
        vklink=url
    vklink=vklink.replace("\/",'/')
    stream_url = resolve_vk(name, vklink)
    if stream_url == False: return
    stream_url=stream_url.replace(' ','%20')
    return stream_url

def resolve_movreel(name, url):
    try:
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving %s Link...' % name)
        dialog.update(0)

        print 'Movreel - Requesting GET URL: %s' % url
        html = net().http_GET(url).content

        dialog.update(33)

        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            logerror('***** DooFree - Site reported maintenance mode')
            xbmc.executebuiltin("XBMC.Notification(File is currently unavailable on the host,DooFree in maintenance,2000)")

        #Set POST data values
        op = re.search('<input type="hidden" name="op" value="(.+?)">', html).group(1)
        postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
        method_free = re.search('<input type="(submit|hidden)" name="method_free" (style=".*?" )*value="(.*?)">', html).group(3)
        method_premium = re.search('<input type="(hidden|submit)" name="method_premium" (style=".*?" )*value="(.*?)">', html).group(3)


        rand = re.search('<input type="hidden" name="rand" value="(.+?)">', html).group(1)
        data = {'op': op, 'id': postid, 'referer': url, 'rand': rand, 'method_premium': method_premium}

        print 'Movreel - Requesting POST URL: %s DATA: %s' % (url, data)
        html = net().http_POST(url, data).content

        #Only do next post if Free account, skip to last page for download link if Premium
        if method_free:
            #Check for download limit error msg
            if re.search('<p class="err">.+?</p>', html):
                errortxt = re.search('<p class="err">(.+?)</p>', html).group(1)
                xbmc.executebuiltin("XBMC.Notification("+errortxt+",Movreel,2000)")

            dialog.update(66)

            #Set POST data values
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)

            if r:
                for name, value in r:
                    data[name] = value
            else:
                xbmc.executebuiltin("XBMC.Notification(Unable to resolve Movreel Link,Movreel,2000)")

            print 'Movreel - Requesting POST URL: %s DATA: %s' % (url, data)
            html = net().http_POST(url, data).content

        #Get download link
        dialog.update(100)
        link = re.search('<a href="(.+)">Download Link</a>', html)
        if link:
	    return link.group(1)
        else:
            xbmc.executebuiltin("XBMC.Notification(Unable to find final link,Movreel,2000)")

    except Exception, e:
        raise ResolverError(str(e),"Movreel")
    finally:
        dialog.close()

def resolve_yify(name, url):
    try:
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving %s video...' % name)
        dialog.update(0)
        print 'Yify - Requesting GET URL: %s' % url
        html = net().http_GET(url).content
        url = re.compile('showPkPlayer[(]"(.+?)"[)]').findall(html)[0]
        url = 'http://yify.tv/reproductor2/pk/pk/plugins/player_p.php?url=https%3A//picasaweb.google.com/' + url
        html = net().http_GET(url).content
        html = re.compile('{(.+?)}').findall(html)[-1]
        stream_url = re.compile('"url":"(.+?)"').findall(html)[0]
        return stream_url
    except Exception, e:
        print('**** Yify Error occured: %s' % e, ' url: %s' % url)

def setFile(path,content,force=False):
    if os.path.exists(path) and not force:
        return False
    else:
        try:
            open(path,'w+').write(content)
            return True
        except: pass
    return False

def CheckForAutoUpdate(force = False):
    GitHubRepo    = 'AutoUpdate'
    GitHubUser    = 'mpie'
    GitHubBranch  = 'master'
    GitHubPath    = 'tree/master/plugin.video.doofree'
    UpdateVerFile = 'update'
    RunningFile   = 'running'
    verCheck=True #main.CheckVersion()#Checks If Plugin Version is up to date
    if verCheck == True:
        try:
            print "DooFree auto update - started"
            html=OPENURL('https://github.com/'+GitHubUser+'/'+GitHubRepo+'?files=1', mobile=True, verbose=False)
        except: html=''
        m = re.search("View (\d+) commit",html,re.I)
        if m: gitver = int(m.group(1))
        else: gitver = 0
        UpdateVerPath = os.path.join(UpdatePath,UpdateVerFile)
        try: locver = int(getUpdateFile(UpdateVerPath))
        except: locver = 0
        RunningFilePath = os.path.join(UpdatePath, RunningFile)
        if locver < gitver and (not os.path.exists(RunningFilePath) or os.stat(RunningFilePath).st_mtime + 120 < time.time()) or force:
            UpdateUrl = 'https://github.com/'+GitHubUser+'/'+GitHubRepo+'/archive/'+GitHubBranch+'.zip'
            UpdateLocalName = GitHubRepo+'.zip'
            UpdateDirName   = GitHubRepo+'-'+GitHubBranch
            UpdateLocalFile = xbmc.translatePath(os.path.join(UpdatePath, UpdateLocalName))
            setFile(RunningFilePath,'')
            print "auto update - new update available ("+str(gitver)+")"
            xbmc.executebuiltin("XBMC.Notification(DooFree Update,New Update detected,3000,"+logo+")")
            xbmc.executebuiltin("XBMC.Notification(DooFree Update,Updating...,3000,"+logo+")")
            try:os.remove(UpdateLocalFile)
            except:pass
            try: urllib.urlretrieve(UpdateUrl,UpdateLocalFile)
            except:pass
            if os.path.isfile(UpdateLocalFile):
                extractFolder = xbmc.translatePath('special://home/addons')
                pluginsrc =  xbmc.translatePath(os.path.join(extractFolder,UpdateDirName))
                if unzipAndMove(UpdateLocalFile,extractFolder,pluginsrc):
                    saveUpdateFile(UpdateVerPath,str(gitver))
                    print "DooFree auto update - update install successful ("+str(gitver)+")"
                    xbmc.executebuiltin("XBMC.Notification(DooFree Update,Successful,5000,"+logo+")")
                    xbmc.executebuiltin("XBMC.Container.Refresh")
                else:
                    print "DooFree auto update - update install failed ("+str(gitver)+")"
                    xbmc.executebuiltin("XBMC.Notification(DooFree Update,Failed,3000,"+logo+")")
            else:
                print "DooFree auto update - cannot find downloaded update ("+str(gitver)+")"
                xbmc.executebuiltin("XBMC.Notification(DooFree Update,Failed,3000,"+logo+")")
            try:os.remove(RunningFilePath)
            except:pass
        else:
            if force: xbmc.executebuiltin("XBMC.Notification(DooFree Update,DooFree is up-to-date,3000,"+logo+")")
            print "DooFree auto update - DooFree is up-to-date ("+str(locver)+")"
        return
    
def getContent(url):
    content = urllib2.urlopen(url).read()
    return content

def parseJson(url):
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    data = json.loads(f.read())
    return data

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def addDirItem(url, name, image):
    item = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=image)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=item, isFolder=True)
    
def addDir(name, url, mode, image, cat_id):
    url = build_url({'mode': mode, 'name': name, 'url': url, 'cat_id': cat_id})
    ok = addDirItem(url, name, image)
    return ok

def addThaiDir(name, url, mode, image, cat_id):
    url = build_url({'mode': mode, 'url': url, 'cat_id': cat_id})
    ok = addDirItem(url, name, image)
    return ok

def addMboxTVDir(name, seasons, mode, cat_id):
    for s in reversed(range(int(seasons))):
        url = build_url({'url': 'video', 'mode': mode, 'name': name, 'season': str(s+1), 'cat_id': cat_id})
        addDirItem(url, name.strip()+' Season '+str(s+1), '')
    return True

def addLink(name, url, mode, image, resolver):
    url = build_url({'mode': mode, 'name': name, 'url': url, 'image': image, 'resolver': resolver})
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
    item.setInfo(type="Video", infoLabels={ "Title": name })
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=item, isFolder=False)
    return ok

def addThaiLink(name, url, mode, image, channel):
    url = build_url({'mode': mode, 'name': name.encode('tis-620'), 'url': url, 'channel': channel, 'image': image})
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
    item.setInfo(type="Video", infoLabels={ "Title": name })
    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=item, isFolder=False)
    return ok

def discoverPagination(link, url):
    paginator=re.compile('<div class="page_list"  align="center">(.+?)</ul>').findall(link)[0]
    pages=re.compile('>(\d+)</a>').findall(paginator)
    if (len(pages) > 1):
        for page in pages:
            pag = int (page[0]) - 1
            pageUrl = url + '&vdo_type=.mp4&page=' + str (pag)
            addThaiDir('page ' + page[0], pageUrl, 2, image, '')
            
def exists(url):
    try:
        r = urllib2.urlopen(url, timeout=1)
        if r.getcode() == 200:
            return True
    except urllib2.URLError, e:
        return False

def HOME():
    url = ''
    data = parseJson(master_json)
    for item in data['Home']:
        if (exists(item['location'])):
            url = item['location']
        else:
            if 'page' in item:
                url = item['page']
        addDir(item['title'].encode("utf-8"), url, 1, '', item['id'])
        url = ''
    xbmcplugin.endOfDirectory(addon_handle)

def INDEX(name, url, cat_id):
    if (url.endswith('.json') and exists(url)):
        data = parseJson(url)
        if (data['isFolder']):
            if 'resolver' in data:
                if data['resolver'] == 'mbox':
                    addMboxTVDir(name, data['seasons'], 5, data['id'])
            else:
                for item in data['list']:
                    addDir(item['title'].encode("utf-8"), item['location'], 1, item['thumbnail'], item['id'])
        else:
            for item in data['list']:
                addLink(item['title'].encode("utf-8"), item['location'], 4, item['thumbnail'], item['resolver'])            
    else:
        link = getContent(url)
        link=''.join(link.splitlines()).replace('\'','"')
        limatch=re.compile('<figure>(.+?)</a><figcaption>').findall(link)
        for licontent in limatch:
            show=re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)">').findall(licontent)
            title = show[0][2].decode('tis-620')
            addThaiDir(title, seesantv + show[0][0], 2, show[0][1], cat_id)

def getMboxEpisodes(name, cat_id, season):
    getepi='http://mobapps.cc/api/serials/es/?id='+str(cat_id)+'&season='+str(season)
    link=OPENURL(getepi)
    match=re.findall('"(\d+)":"([^"]+?)"',link,re.DOTALL)
    dialogWait = xbmcgui.DialogProgress()
    ret = dialogWait.create('Please wait until Episodes list is cached.')
    totalLinks = len(match)
    loadedLinks = 0
    remaining_display = 'Episodes Cached :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B].'
    dialogWait.update(0,'[B]Will load instantly from now on[/B]',remaining_display)
    xbmc.executebuiltin("XBMC.Dialog.Close(busydialog,true)")
    for epinum,thumb in match:
        addLink(name+' Episode '+epinum, 'http://mobapps.cc/api/serials/e/?h='+str(cat_id)+'&u='+str(season)+'&y='+epinum, 4, thumb.replace('\/','/'), 'mbox')
        loadedLinks = loadedLinks + 1
        percent = (loadedLinks * 100)/totalLinks
        remaining_display = 'Episodes Cached :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B].'
        dialogWait.update(percent,'[B]Will load instantly from now on[/B]',remaining_display)
        if dialogWait.iscanceled():
            return False

def getEpisodes(url, cat_id):
    link = getContent(url + '&vdo_type=.mp4')
    link = ''.join(link.splitlines()).replace('\'','"')
    link=''.join(link.splitlines()).replace('<i class="icon-new"></i>','')

    episodematch = re.compile('<table class="program-archive">(.+?)</table>').findall(link)
    episodes = re.compile('<a href="(.+?)" >(.+?)</a> </td>                           \t\t\t\t\t\t\t<td>\t\t\t\t\t\t\t\t<a href="(.+?)" ><img').findall(episodematch[0])

    programMeta = re.compile('<div class="program-meta">(.+?)</div>').findall(link)
    image = re.compile('<img src="(.+?)" alt').findall(programMeta[0])[0]

    topInfo = re.compile('<div class="top-info">(.+?)</div>').findall(link)
    if (cat_id in thaiChannels):
        channel = re.compile('<img src="(.+?)" width').findall(topInfo[0])
        if (len(channel) > 0):
            channel = 'ch' + channel[0][-5]
            if (channel == 'chv'):
                channel = 'chthaipbs'
        else:
            channel = 'chall'
    elif (cat_id in chMovies):
        channel = 'chmovie'
    else:
        channel = 'chserie'

    for episode in episodes:
        addThaiLink(episode[1].decode('tis-620'), seesantv + episode[0], 3, image, channel)
    # paginator
    discoverPagination(link, url)

def getVideoUrl(name, url, channel):
    trySD = True
    programId = re.compile('program_id=(\d+)').findall(url)[0]
    if (len(programId) < 5):
        programId = '0' + programId
    fullDate = re.compile('(\d+-\d+-\d+) ').findall(name)[0]
    date = ''.join(fullDate.splitlines()).replace('-','')
    hd = channel + '/' + programId + '/' + date + '1-' + programId + '.mp4'
    sd = channel + '/' + programId + '/' + date + '-' + programId + '.mp4'
    #for host in xrange(1, 31):
    for host in uk:
        #fullurl = "http://uk" + str (host) + ".seesantv.com/" + path
        fullurl = host + hd
        found = exists(fullurl)
        if (found):
            xbmc.Player().play(fullurl)
            trySD = False
            break
    if (trySD):
        for host in uk:
            fullurl = host + sd
            found = exists(fullurl)
            if (found):
                xbmc.Player().play(fullurl)
                break

def play(name, vidurl, image, resolver):
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
    item.setInfo(type="Video", infoLabels={ "Title": name })
    if resolver == 'yify':
        vidurl = resolve_yify(name, vidurl)
    if resolver == 'movreel':
	    vidurl = resolve_movreel(name, vidurl)
    if resolver == 'mbox':
        vidurl = resolve_mbox(name, vidurl)
    xbmc.Player().play(vidurl, item)
    
def getParams():
    param = []
    paramstring = sys.argv[2]
    if (len(paramstring)>= 2):
        params = sys.argv[2]
        cleanedparams = params.replace('?','')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams) == 2):
                param[splitparams[0]] = splitparams[1]
    return param

params=getParams()
url=None
name=None
mode=None
serverurl=None
channel=None
playpath=None
image=None
cat_id=None
resolver=None
try:
    url=urllib.unquote_plus(params['url'])
except:
    pass
try:
    name=urllib.unquote_plus(params['name'])
except:
    pass
try:
    mode=int(params['mode'])
except:
    pass
try:
    serverurl=urllib.unquote_plus(params['serverurl'])
except:
    pass
try:
    channel=urllib.unquote_plus(params['channel'])
except:
    pass
try:
    playpath=urllib.unquote_plus(params['playpath'])
except:
    pass
try:
    image=urllib.unquote_plus(params['image'])
except:
    pass
try:
    cat_id=int(params['cat_id'])
except:
    pass
try:
    resolver=params['resolver']
except:
    pass
try:
    season=params['season']
except:
    pass

sysarg=str(sys.argv[1])
if mode==None or url==None or len(url)<1:
    threading.Thread(target=CheckForAutoUpdate).start()
    #INDEX("Test", "https://raw.githubusercontent.com/mpie/doofree/REV-1.1.5/json/new_movies.json?4")
    HOME()
elif mode==1:
    INDEX(name, url, cat_id)
elif mode==2:
    getEpisodes(url, cat_id)
elif mode==3:
    getVideoUrl(name, url, channel)
elif mode==4:
    play(name, url, image, resolver)
elif mode==5:
    getMboxEpisodes(name, cat_id, season)
xbmcplugin.endOfDirectory(addon_handle)
