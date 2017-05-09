import requests
import re

# Define general functions, that are not tied to any instance / class
def find_pager(in_data, split_type = 'viewforum'): #
    page_list = []
    # Read the regex, split it by recognizable information
    try:
        tmp_cache_list = re.search('onclick=\"jumpto.*', in_data.text).group(0).split(split_type +'.php')
    except:
        return (0, 0)
    # If the board has more pages
    for cache in tmp_cache_list:
        tmp_data = re.search('start=(\d*)', cache)
        if tmp_data and tmp_data.group(1) not in page_list:
            page_list.append(tmp_data.group(1))
    # first index: size and 'second' page, last index: last page reachable
    return (int(page_list[0]), int(page_list[-1]))

def auto_pager(in_page_size, in_last_page, url, in_session): # Autopage
    # Check, if we have any length
    if in_page_size != 0 and in_last_page != 0:
        real_range = int(in_last_page / in_page_size) + 1
    else: # We need to fix zero-length
        real_range = 1

    page_responses = []
    for page_num in range(real_range): # we know that we can start on page one
        # Convert it to 'page' size
        page_responses.append(in_session.get(url + '&start=%s' % (page_num * in_page_size)))
    return page_responses

def populate(in_html_data, par_obj, in_obj, method = 'viewforum'): # Unified populator
    parse_string = {'viewforum': '(viewforum.php\?f=\d*).*>(.*)</a>.*', 'viewtopic': '[^unread].*(viewtopic.php\?f=.*)\" class=\"topictitle">(.*)<'}
    # Get the data
    tmp_list = re.findall(parse_string.get(method), in_html_data)
    # Start 'assigning'
    for data in tmp_list:
        tmp_obj = in_obj(par_obj, data[0].replace('amp;', ''), data[1])
        par_obj.append(tmp_obj)

class Forum(object):
    """
        docstring for Forum.
    """
    def __init__(self, name = None, url = None):
        super(Forum, self).__init__()
        self.name = name
        self.url = url
        self.session = requests.Session() # Cookies related data
        # Board related functions
        self.board_list = []

    def __repr__(self):
        return 'Forum named %s:\n\tURL:\t\t\t%s\n\tNumber of boards:\t%s\n\tBoards:\t\t%s' %(self.name, self.url, len(self.board_list), [x.name for x in self.board_list])

    def accept_rules(self): # Accept rules, if there is any front page. May be obsolete
        self.session.post(self.url + 'enter.php', data = {'enter': 'enter'})

    def load_page(self, url_sub_page = ''): # Load page and return result
        return self.session.get(self.url + url_sub_page)

    def login_forum(self, in_usr, in_passwd): # Login user
        self.load_page('')
        tmp_sid = self.session.cookies.items()[1][1] # Prepare SessionID from session
        data_dict = {'username': in_usr, 'password': in_passwd,
                     'sid': tmp_sid, 'login': 'login', 'redirect': 'index.php'}
        self.session.post(self.url + 'ucp.php?mode=login', data = data_dict)

    def append(self, in_obj): # We need this function to universally connect to populator
        self.board_list.append(in_obj)
        self.board_list[-1].get_page_num()

    def populate_boards(self): # Clean board URLS from HTML code using regexes
        html_data = self.load_page('').text
        # Populate boards
        populate(html_data, self, ForumBoard)

class ForumBoard(object):
    """
        docstring for ForumBoard.
    """
    def __init__(self, parent, url, name):
        self.parent = parent
        self.url = url
        self.name = name
        self.topic_list = []
        # Size related vars
        self.page_size = None
        self.last_page = None

    def get_page_num(self):
        self.page_size, self.last_page = find_pager(self.parent.session.get(self.parent.url + self.url))

    def populate_topics(self):
        page_responses = auto_pager(self.page_size, self.last_page, self.parent.url + self.url, self.parent.session)
        # Start to populate
        for response in page_responses:
            populate(response.text, self, ForumTopic, method = 'viewtopic')

    def append(self, in_obj): # We need this function to universally connect to populator
        self.topic_list.append(in_obj)

class ForumTopic(object):
    """
        Docstring
    """
    def __init__(self, parent, url, name):
        self.parent_board = parent
        self.url = url
        self.name = name
        self.page_size = None
        self.last_page = None
        self.content = None
