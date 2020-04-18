import requests
from getpass import getpass
from pathlib import Path
from bs4 import BeautifulSoup

PARSER = 'lxml'

try:
    import lxml
    del lxml
except ImportError:
    PARSER = 'html.parser'

CURRENT_DIRECTORY = Path(__file__).parent

BASE_URL = 'https://read.mi.hs-rm.de/'

LOGIN_URL = 'https://read.mi.hs-rm.de/ilias.php'\
            '?lang=de'\
            '&client_id=readmi'\
            '&cmd=post'\
            '&cmdClass=ilstartupgui'\
            '&cmdNode=sx'\
            '&baseClass=ilStartUpGUI'\
            '&rtoken='

COURSE_URL = 'https://read.mi.hs-rm.de/ilias.php'\
             '?baseClass=ilPersonalDesktopGUI'\
             '&cmd=jumpToMemberships'

CONTENT_TYPES = {
    'application/java-archive': '.jar',
    'application/octet-stream': '.dtd',
    'application/pdf': '.pdf',
    'application/postscript': '.eps',
    'application/xml': '.xml',
    'application/x-tex': '.tex',
    'application/zip': '.zip',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'image/svg+xml': '.svg',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'text/html': '.html',
    'text/html; charset=UTF-8': '.html',
    'text/plain': '.txt',
    'text/plain;charset=UTF-8': '.txt',
    'text/xml': '.xml',
    'text/xml;charset=UTF-8': '.xml',
    'video/mp4': '.mp4'
}


def tryToConnect(session, url, maxTries=5):
    """
    Args:
        session (Session): Valid readmi session
        url (string): Url to connect to
        maxTries (int): Maximum number of tries in case of failure
    Returns:
        Session: Session of readmi
    """
    tryCount = 0
    statusCode = 0
    response = None
    while tryCount < maxTries and statusCode != 200:
        tryCount += 1
        response = session.get(url)
        statusCode = response.status_code
    return response if statusCode == 200 else None


def getSession(username, password):
    """
    Args:
        username (string): HDS username
        password (string): HDS password
    Returns:
        Session: Login session of readmi
    """

    session = requests.Session()

    # Data for POST request
    formData = {
        'username': username,
        'password': password,
        'cmd[doStandardAuthentication]': 'Anmelden'
    }

    # Perform POST request and process response
    postResponse = session.post(
        LOGIN_URL, 
        data=formData, 
        allow_redirects=True
    )
    if postResponse.status_code != 200 or 'login' in postResponse.url:
        raise requests.exceptions.RequestException('Login failed!')
    return session


def getContainerItems(session, url=COURSE_URL):
    """
    Args:
        session (Session): Valid readmi session
    Returns:
        [(string, string)]: List containing item name and url
    """

    # Check for valid session and url
    response = tryToConnect(session, url)
    if not response:
        print('ERROR: Could not connect to ' + url)
        return
    
    # Get list of container items
    soup = BeautifulSoup(response.text, PARSER)
    return [(item.text, item.get('href') if item.get('href').startswith(BASE_URL) else BASE_URL + item.get('href')) 
                for item in soup.find_all('a', class_ = 'il_ContainerItemTitle')]


def crawl(session, url=COURSE_URL, path=CURRENT_DIRECTORY):
    """
    Args:
        session (Session): Valid readmi session
        url (string): Url to search for files
        path (Path): Directory to save files to
    """

    toCrawl = getContainerItems(session, url)

    for item in toCrawl:
        itemName, itemUrl = item[0], item[1]

        # Process files
        if 'download' in itemUrl:
            downloadFile(session, item, path)

        # Process links
        elif any(keyword in itemUrl for keyword in ['directlink', 'Wiki', 'showThreads', 'ExerciseHandler']):
            forwardedUrl = getForwardedLink(session, itemUrl)
            createLink(itemName, forwardedUrl, path)

        # Process directories
        else:
            newPath = path / itemName
            createDirectory(newPath)
            print(f'Checking {itemName}')
            crawl(session, itemUrl, newPath)


def downloadFile(session, item, path):
    """
    Args:
        session (Session): Valid readmi session
        item ((string, string)): Name and url of file to download
        path (Path): Location where file should be downloaded 
    """
    fileName, fileUrl = item[0], item[1]
    newFile = path / (fileName + getExtension(session, fileUrl))
    if not newFile.exists(): 
        print(f'Downloding: {newFile}')
        response = tryToConnect(session, fileUrl)
        file = open(newFile, 'wb')
        file.write(response.content)
        file.close()


def getForwardedLink(session, url):
    """
    Args:
        session (Session): Valid readmi session
        url (string): Forwarding url
    Returns:
        (string) Target url
    """
    response = tryToConnect(session, url)
    return response.url



def createLink(name, url, path):
    """
    Args:
        name (string): Name of the file
        url (string): Url that will be written in file
        path (Path): Location where file will be created
    """
    newFile = path / (name + '.html')
    if not newFile.exists():
        print(f'Creating: {newFile}')
        file = open(newFile, 'w')
        file.write(f'<html><body><script type="text/javascript">window.location.href="{url}"</script></body></html>')
        file.close()


def createDirectory(path):
    """
    Args:
        path (Path): Location of directory to create
    """
    if not path.exists():
        print(f'Creating directory: {path}')
        Path(path).mkdir(parents=True, exist_ok=True)


def getExtension(session, url):
    """
    Args:
        session (Session): Valid readmi session
        url (string): Url to file that's extension shall be found
    Returns:
        (string) File extension of content-type
    """
    response = session.head(url)
    contentType = response.headers['content-type']
    return CONTENT_TYPES.get(contentType, '')
       

def console():
    """
    Use console to get login credentials and start downloading.
    """

    # Get credentials
    print('Enter Username and password')
    username = input('Username: ')
    password = getpass()

    # Start crawling
    readmiSession = getSession(username, password)
    crawl(readmiSession)


if __name__ == "__main__":
    console()
