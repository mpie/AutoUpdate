import re, urllib2, urllib, json, threading, os, zipfile, shutil
import xbmcaddon, xbmcplugin, xbmcgui, xbmc

ADDON = xbmcaddon.Addon(id='plugin.video.doofree')
PATH = 'doofree'
VERSION = '1.1.6'
#djsalkjdaljadskl
base_url = ''
addon_handle = ''

master_json = "https://raw.githubusercontent.com/mpie/doofree/REV-1.1.5/json/master.json"
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
            print "MU-Openurl = " + url
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

def addLink(name, url, mode, image):
    url = build_url({'mode': mode, 'name': name, 'url': url, 'image': image})
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
            for item in data['list']:
                addDir(item['title'].encode("utf-8"), item['location'], 1, item['thumbnail'], item['id'])
        else:
            for item in data['list']:
                addLink(item['title'].encode("utf-8"), item['location'], 4, item['thumbnail'])
            
    else:
        link = getContent(url)
        link=''.join(link.splitlines()).replace('\'','"')
        limatch=re.compile('<figure>(.+?)</a><figcaption>').findall(link)
        for licontent in limatch:
            show=re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)">').findall(licontent)
            title = show[0][2].decode('tis-620')
            addThaiDir(title, seesantv + show[0][0], 2, show[0][1], cat_id)

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

def play(name, vidurl, image):
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
    item.setInfo(type="Video", infoLabels={ "Title": name })
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
    play(name, url, image)

xbmcplugin.endOfDirectory(addon_handle)
