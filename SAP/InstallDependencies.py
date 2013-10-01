import zipfile, tempfile, sys, ftplib, urllib, re, os, getpass, tarfile, glob, time

from UtilityFunctions import findOnSystem


class Download:

    def __init__(self, minValue = 0, maxValue = 100, totalWidth=80, guiParent=None):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string
        self.guiParent = guiParent
        if self.guiParent is not None:
            import wx

    def updateAmount(self, newAmount = 0):
        """ Update the progress bar with the new amount (with min and max
            values set at initialization; if it is over or under, it takes the
            min or max value as a default. """
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = int(round(percentDone))

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if numHashes == 0:
            self.progBar = "[>%s]" % (' '*(allFull-1))
        elif numHashes == allFull:
            self.progBar = "[%s]" % ('='*allFull)
        else:
            self.progBar = "[%s>%s]" % ('='*(numHashes-1),
                                        ' '*(allFull-numHashes))

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone)) 
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = ''.join([self.progBar[0:percentPlace], percentString,
                                self.progBar[percentPlace+len(percentString):]
                                ])

    def __str__(self):
        return str(self.progBar)


    def progressHook(self, nrblocks, block, totalsize):
        """ Updates the amount, and writes to stdout. Prints a carriage return
            first, so it will overwrite the current line in stdout."""
        print '\r',

        total_nr_blocks = totalsize / block
        value = (nrblocks * 100) / total_nr_blocks

        if self.guiParent is None:
            self.updateAmount(value)
            sys.stdout.write(str(self))
            sys.stdout.flush()
        else:
            self.progressDialog.Update(value)


    def downloadURL(self, url):
        """
        Downloads package specified by URL to temporary file.
        """
        tmpDirName = tempfile.mkdtemp()
        tmpFile, tmpFileName = tempfile.mkstemp(dir=tmpDirName)
        tmpFileName += os.path.splitext(url)[1]
        success = True
        try:
            if self.guiParent is None:
                sys.stderr.write('Package download:\n')
                sys.stderr.flush()

                self.progressHook(0, 1, 1)
                urllib.urlretrieve('ftp://' + url, tmpFileName, self.progressHook)

                sys.stdout.write("\n")
                sys.stdout.flush()
            else:
                import wx
                self.progressDialog = wx.ProgressDialog("Download",
                                        "Fetching package from third party FTP site:",
                                        maximum = self.max,
                                        parent=self.guiParent)

                self.progressHook(0, 1, 1)
                urllib.urlretrieve('ftp://' + url, tmpFileName, self.progressHook)

                self.progressDialog.Destroy()
        except:
            success = False
        
        return tmpDirName, tmpFileName, success

def failiure(guiParent=None, errorNr=None):
    msg = 'You will need to install this dependency yourself. See the manual page for help.'
    header = 'Automatic installation failed.'
    if errorNr is not None:
        msg = "Install error: %d\n%s" % (errorNr, msg)
    if guiParent is None:
        print header, msg
        sys.exit()
    else:
        import wx
        dlg = wx.MessageDialog(guiParent, msg, header, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        sys.exit()

def prompt(msg):
    return raw_input(msg + ' ').strip().lower()

def assertClustalw2Installed(guiParent=None):
    """
    Checks if Clustalw2 is installed.
    """

    ftpURL = 'ftp.ebi.ac.uk'
    ftpDir = 'pub/software/clustalw2/2.0.8'

    found = False
    if os.name in ('nt', 'dos'):
        name = 'clustalw2.exe'        
    else:
        name = 'clustalw2'

    msg = "This program depends on %s for aligning homologues. If you have an internet connection SAP can download and install it for you. Do you  want to do this now?" % name
    if findOnSystem(name):
        return True
    else:
        if guiParent is None:
            reply = prompt(msg + ' Y/n:')
            if reply == 'n':
                sys.exit()
        else:
            import wx
            nResult = wx.MessageBox(msg, "Dependency missing from your system!", wx.YES_NO | wx.ICON_QUESTION, guiParent)
            if nResult == wx.NO:
                msg ="You can download %s yourself from:\nftp://%s/%s" % (name, ftpURL, ftpDir)
                dlg = wx.MessageDialog(guiParent, msg, 'Manual installation', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                sys.exit()

        packageRE = re.compile(r'clustalw-[\d.]+-([^.]+)')
        success = getPackage('clustalw2', packageRE, ftpURL, ftpDir, guiParent=guiParent)
        return success

def assertNetblastInstalled(guiParent=None):
    """
    Checks if Netblast is installed.
    """
    return assertBlastInstalled(guiParent=guiParent)
# 
#     ftpURL='ftp.ncbi.nlm.nih.gov'
#     ftpDir = 'blast/executables/release/2.2.19'
# 
#     found = False
#     if os.name in ('nt', 'dos'):
#         name = 'blastcl3.exe'        
#     else:
#         name = 'blastcl3'
# 
#     msg = "This program depends on %s for searching the GenBank database. If you have an internet connection SAP can\ndownload and install it for you. Do you  want to do this now?" % name
#     if findOnSystem(name):
#         return True
#     else:
#         if guiParent is None:
#             reply = prompt(msg + ' Y/n:')
#             if reply == 'n':
#                 sys.exit()
#         else:
#             import wx
#             nResult = wx.MessageBox(msg, "Depency missing from your system!", wx.YES_NO | wx.ICON_QUESTION, guiParent)
#             if nResult == wx.NO:
#                 msg ="You can download Netblast yourself from:\nftp://%s/%s" % (ftpURL, ftpDir)
#                 dlg = wx.MessageDialog(guiParent, msg, 'Manual installation', wx.OK | wx.ICON_INFORMATION)
#                 dlg.ShowModal()
#                 dlg.Destroy()
#                 sys.exit()
# 
#         packageRE = re.compile(r'netblast-[\d.]+-([^.]+)')
#         getPackage('netblast', packageRE, ftpURL, ftpDir, guiParent=guiParent)
# 
#         return True
    
def assertBlastInstalled(guiParent=None):
    """
    Checks if Blast is installed.
    """

#     # First check if the user has wu-blast installed:
#     if findOnSystem('blastn') and findOnSystem('xdformat'):
#         return True

    ftpURL='ftp://ftp.ncbi.nlm.nih.gov'
    ftpDir = '/blast/executables/blast+/LATEST'

    found = False
    if os.name in ('nt', 'dos'):
        name = 'blastn.exe'        
    else:
        name = 'blastn'

    msg = "This program depends on %s for searching a local database. If you have an internet connection SAP can download and install it for you.\nDo you  want to do this now?" % name
    if findOnSystem(name):
        return True
    else:
        if guiParent is None:
            reply = prompt(msg + ' Y/n:')
            if reply == 'n':
                sys.exit()
        else:
            import wx
            nResult = wx.MessageBox(msg, "Depency missing from your system!", wx.YES_NO | wx.ICON_QUESTION, guiParent)
            if nResult == wx.NO:
                msg ="You can download Blast yourself from:\nftp://%s/%s" % (ftpURL, ftpDir)
                dlg = wx.MessageDialog(guiParent, msg, 'Manual installation', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                sys.exit()

        packageRE = re.compile(r'blast-[\d.]+-([^.]+)')
        getPackage('blastn', packageRE, ftpURL, ftpDir, guiParent=guiParent)

        return True

def getPackage(name, packageRE, ftpURL=None, ftpDir=None, guiParent=None):
    """
    Checks if a program is installed and proceeds to interactive
    instalation if not.
    """

    # Get info on available packages:
    releases = getPackageDict(name, packageRE, ftpURL, ftpDir)
    platforms = releases.keys()
    platforms.sort()

    # Let user pick the approapriate package:
    platform = pickPlatform(platforms, guiParent=guiParent)
    if not platform:
        failiure(guiParent=guiParent, errorNr=1)

    # Download package:
    download = Download(maxValue=100, totalWidth=80, guiParent=guiParent)
    tmpDirName, tmpFileName, success = download.downloadURL(releases[platform])
    if not success:
        failiure(guiParent=guiParent, errorNr=2)

    # Install:
    install(name, tmpDirName, tmpFileName, guiParent=guiParent)
    
# Removal of tmp files fails: The process cannot access the file because it is being used by andother process
#     # Remove tmp files:
#     for d in os.walk(tmpDirName, topdown=False):
#         for f in d[2]:
#             os.unlink(os.path.join(d[0], f))
#         os.rmdir(d[0])

    if guiParent is not None:
        import wx
        msg = '%s is now installed on your system and program will start up if no further dependencies are missing.' %  name
        dlg = wx.MessageDialog(guiParent, msg, 'Installation complete.', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def rootAccess(guiParent=None):
    """
    Asks the user if he/she has root access.
    """
    if guiParent is not None:
        import wx
        nResult = wx.MessageBox("""Do you have root access on this computer? If you do you can
choose 'Yes' to install for all users. Otherwise choose 'No'
to install the dependency under your user account.""", "Where to install?", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, guiParent)
        if nResult == wx.YES:
            return True
        elif nResult == wx.NO:
            return False
    else:
        reply = prompt('Do you have root access on this computer? y/N: ')
        if reply == 'y':
            return True
        else:
            return False
    
def pickPlatform(platformList, guiParent=None):
    """
    Lets the users pick the platform of his computer.
    """
    
    if guiParent is not None:
        import wx

        msg = "Pick the version that correponds to the platform\nof your computer."

        if 'ia32-win32' in platformList:
            msg += '\nChoose ia32-win32 for standard Windows PC'
        if 'src' in platformList:
            msg += '\nChoose src for Linux/Unix'

        dlg = wx.SingleChoiceDialog(
                guiParent, msg, 'download',
                platformList, 
                wx.CHOICEDLG_STYLE
                )

        if dlg.ShowModal() == wx.ID_OK:
            platform = dlg.GetStringSelection()
        else:
            sys.exit()
        
        dlg.Destroy()
        
    else:
        sys.stdout.write('The dependency is available in the following versions:\n')
        for i, p in enumerate(platformList):
            if p == 'ia32-win32':
                p  += ' (standard windows PC)'
            if p == 'src':
                p += ' (Linux/Unix)'
            sys.stdout.write(" %-04d%s\n" % (i+1, p))

        reply = ''
        while not reply.isdigit():
            reply = prompt('Spcify package number (type 0 for no choice):')
        if reply != '0':
            platform = platformList[int(reply)-1]
        else:
            failiure(guiParent=guiParent, errorNr=3)

    return platform        

def getPackageDict(name, packageRE, ftpURL, ftpDir):
    """
    Creates a dictionary of download URLs keyed by platform name.
    """
    sys.stderr.write('Fetching %s package list...' % name)
    sys.stderr.flush()

    try:
        ftp = ftplib.FTP(ftpURL)
    except:
        raise AnalysisTerminated(1, "FTP connection failed. Make sure you are connected to the internet.")
    ftp.login()
    dirList = ftp.nlst(ftpDir)
    ftp.quit()

    packages = {}
    for packagePath in dirList:
        search = packageRE.search(packagePath)
        if search:
            platform = search.group(1)
            packages[platform] = "%s/%s" % (ftpURL, packagePath)
    sys.stderr.write("done\n")
    sys.stderr.flush()
    return packages

def passwDialog(guiParent):

    import wx
    dlg = wx.TextEntryDialog(guiParent, 'Enter root password:',
                             'Installation', '', wx.TE_PASSWORD | wx.OK)
    dlg.CenterOnScreen()

    if dlg.ShowModal() == wx.ID_OK:
        password = dlg.GetValue()
    else:
        password = None
    dlg.Destroy()
    return password

def install(name, tmpDirName, tmpFileName, guiParent=None):
    
    # Call the approapriate install function
    if os.name in ('posix', 'darwin'):
        if name == 'netblast':
            installNetblastOnPosix(tmpDirName, tmpFileName, guiParent=guiParent)
        if name == 'blast':
            installBlastOnPosix(tmpDirName, tmpFileName, guiParent=guiParent)
        elif name == 'clustalw2':
            installClustalw2OnPosix(tmpDirName, tmpFileName, guiParent=guiParent)
    elif os.name in ('nt', 'dos'):
        if name == 'netblast':
            installNetblastOnWindows(tmpDirName, tmpFileName, guiParent=guiParent)
        if name == 'blast':
            installNlastOnWindows(tmpDirName, tmpFileName, guiParent=guiParent)
        elif name == 'clustalw2':
            installClustalw2OnWindows(tmpDirName, tmpFileName, guiParent=guiParent)

def installNetblastOnWindows(tmpDirName, tmpFileName, guiParent=None):
    """
    Install downloaded package on a widows platform.
    """
    z = zipfile.ZipFile(tmpFileName, "r")
    for fileName in z.namelist():
        if fileName == 'blastcl3.exe':
            excecutable = z.read(fileName)
    z.close()
    installDir = 'C:\Program Files\Netblast'
    os.makedirs(installDir)

    fh = open(os.path.join(installDir, 'blastcl3.exe'), 'wb')
    fh.write(excecutable)
    fh.close()

    if not findOnSystem('blastcl3.exe'):
        failiure(guiParent=guiParent, errorNr=4)

def installBlastOnWindows(tmpDirName, tmpFileName, guiParent=None):
    """
    Install downloaded package on a widows platform.
    """
    z = zipfile.ZipFile(tmpFileName, "r")
    for fileName in z.namelist():
        if fileName == 'blastall.exe':
            excecutable = z.read(fileName)
    z.close()
    installDir = 'C:\Program Files\Blast'
    os.makedirs(installDir)

    fh = open(os.path.join(installDir, 'blastall.exe'), 'wb')
    fh.write(excecutable)
    fh.close()

    if not findOnSystem('blastall.exe'):
        failiure(guiParent=guiParent, errorNr=4)

def getPossixInstallDir(guiParent=None):

    # Dir to install in:
    installDir = None

    haveRootAccess = rootAccess(guiParent=guiParent)

    # See if we can find a sensible place to install:
    for path in ('/usr/local/bin', os.environ['HOME']+'/usr/local/bin'):
        if os.path.exists(path):
            if os.access(path, os.W_OK) or haveRootAccess:
                installDir = path
                break

    # If not, create a directory for installation:
    if not installDir:
        if haveRootAccess:
            path = '/usr/local/bin'
            os.system("echo '%s' | sudo -S mkdir -p %s" % (passwDialog(guiParent), path))
            #fail = os.system('sudo mkdir -p %s' % path)
        else:
            path = os.environ['HOME']+'/usr/local/bin'
            os.system('mkdir -p %s' % path)
        installDir = path
        if not os.path.exists(installDir):
            failiure(guiParent=guiParent, errorNr=5)

    return installDir

def installClustalw2OnWindows(tmpDirName, tmpFileName, guiParent=None):
    """
    Run the msi installer.
    """
    os.system(tmpFileName)

    if not findOnSystem('clustalw2.exe'):
        failiure(guiParent=guiParent, errorNr=6)

def installNetblastOnPosix(tmpDirName, tmpFileName, guiParent=None):
    """
    Install downloaded package on a posix platform.
    """

    # Unpack the tarball:
    tar = tarfile.open(tmpFileName, 'r:gz')

    for item in tar:
        tar.extract(item, tmpDirName)
    tar.close()    
    os.unlink(tmpFileName)

#     # Get content list:
#     packageContent = glob.glob(os.path.join(tmpDirName, '*'))
#     # Decend one dir level if tarball was unpacked to a dir:
#     if len(packageContent) == 1 and os.path.isdir(packageContent[0]):
#         packageContent = glob.glob(os.path.join(packageContent[0], '*'))
    packageContent = glob.glob(os.path.join(tmpDirName, 'netblast-*', '*'))

    installDir = getPossixInstallDir(guiParent=guiParent)

    # Chop off the bin dir from the install path becauce we copy the
    # bin dir and the data dir over when installing:
    installDir = os.path.split(installDir)[0]

    try:
        if not os.access(installDir, os.W_OK):
            if guiParent is None:                
                os.system("sudo cp -r %s %s" % (" ".join(packageContent), installDir))
            else:
                os.system("echo '%s' | sudo -S cp -r %s %s" % (passwDialog(guiParent), " ".join(packageContent), installDir))
        else:
            os.system("cp -r %s %s" % (" ".join(packageContent), installDir))
    except:
        pass

    if not findOnSystem('blastcl3'):
        failiure(guiParent=guiParent, errorNr=7)

def installBlastOnPosix(tmpDirName, tmpFileName, guiParent=None):
    """
    Install downloaded package on a posix platform.
    """

    # Unpack the tarball:
    tar = tarfile.open(tmpFileName, 'r:gz')

    for item in tar:
        tar.extract(item, tmpDirName)
    tar.close()    
    os.unlink(tmpFileName)

#     # Get content list:
#     packageContent = glob.glob(os.path.join(tmpDirName, '*'))
#     # Decend one dir level if tarball was unpacked to a dir:
#     if len(packageContent) == 1 and os.path.isdir(packageContent[0]):
#         packageContent = glob.glob(os.path.join(packageContent[0], '*'))
    packageContent = glob.glob(os.path.join(tmpDirName, 'blast-*', '*'))

    installDir = getPossixInstallDir(guiParent=guiParent)

    # Chop off the bin dir from the install path becauce we copy the
    # bin dir and the data dir over when installing:
    installDir = os.path.split(installDir)[0]

    try:
        if not os.access(installDir, os.W_OK):
            if guiParent is None:                
                os.system("sudo cp -r %s %s" % (" ".join(packageContent), installDir))
            else:
                os.system("echo '%s' | sudo -S cp -r %s %s" % (passwDialog(guiParent), " ".join(packageContent), installDir))
        else:
            os.system("cp -r %s %s" % (" ".join(packageContent), installDir))
    except:
        pass

    if not findOnSystem('blastcl3'):
        failiure(guiParent=guiParent, errorNr=7)

def installClustalw2OnPosix(tmpDirName, tmpFileName, guiParent=None):

    installDir = getPossixInstallDir(guiParent=guiParent)

    fail = False
        
    if sys.platform == 'darwin':
        # Unpack the disk image and move the executable to the install dir:
        fail = os.system('open -g -a DiskImageMounter %s' % tmpFileName)

        # Hack to for OSX 10.4 where open does not have the -g option:
        if fail == 256:
            fail = os.system('open -a DiskImageMounter %s' % tmpFileName)
                
        if fail:
            return False
        while not glob.glob('/Volumes/clustalw-*/clustalw-*/clustalw2'):
            time.sleep(1)            
        time.sleep(2)
        executable = glob.glob('/Volumes/clustalw-*/clustalw-*/clustalw2')[0]

        try:
            if not os.access(installDir, os.W_OK):
                if guiParent is None:                
                    os.system("sudo cp %s %s" % (executable, installDir))
                else:
                    os.system("echo '%s' | sudo -S cp %s %s" % (passwDialog(guiParent), executable, installDir))
            else:
                os.system("cp %s %s" % (executable, installDir))
        except:
            return False
    else:
        # Unpack the tarball:
        tar = tarfile.open(tmpFileName, 'r:gz')

        for item in tar:
            tar.extract(item, tmpDirName)
        tar.close()    
        os.unlink(tmpFileName)
            
        # Chop off the bin dir from the install path becauce we copy the
        # bin dir and the data dir over when installing:
        installDir = os.path.split(installDir)[0]

        oldCWD = os.getcwd()
        os.chdir(glob.glob(tmpDirName + '/clustalw-*')[0])

        if installDir == '/usr/local':
            if os.system("./configure"):
                return False
        else:
            if os.system("./configure --prefix %s" % installDir):
                return False

        if os.system("make"):
            return False            

        if not os.access(installDir, os.W_OK):
            if guiParent is None:                
                os.system("sudo make install")
            else:
                os.system("echo '%s' | sudo -S make install")            
        else:
            os.system("make install")

        os.chdir(oldCWD)

    if not findOnSystem('clustalw2'):
        failiure(guiParent=guiParent, errorNr=8)


if __name__ == '__main__':

    assertNetblastInstalled()
    assertClustalw2Installed()
