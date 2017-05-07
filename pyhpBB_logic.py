import requests
import re

# Define general functions, that are not tied to any instance / class
def find_pager(in_data, split_type = 'viewforum'): #
    page_list = []
    # Read the regex, split it by recognizable information
    tmp_cache_list = re.search('onclick=\"jumpto.*', in_data.text).group(0).split(split_type +'.php')
    for cache in tmp_cache_list:
        tmp_data = re.search('start=(\d*)', cache)
        if tmp_data and tmp_data.group(1) not in page_list:
            page_list.append(tmp_data.group(1))
    # first index: size and 'second' page, last index: last page reachable
    return (int(page_list[0]), int(page_list[-1]))

def auto_pager(in_page_size, in_last_page, url):
    pass
    

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
        # Size related vars
        self.page_size = None
        self.last_page = None

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

    def populate_boards(self): # Clean board URLS from HTML code using regexes
        html_data = self.load_page('').text
        tmp_list = re.findall('viewforum.php\?.*', html_data)
        # Finally, start cleaning
        for board_name in tmp_list:
            tmp_data = board_name.split("\"")
            tmp_string = re.search('>(.*)</a>', tmp_data[-1]).group(1)
            tmp_url = tmp_data[0]
            # Process topics
            tmp_board_object = ForumBoard(tmp_url, tmp_string)
            tmp_board_object.topic_list = self.populate_topics(tmp_url)
            self.board_list.append(tmp_board_object)

class ForumBoard(object):
    """
        docstring for ForumBoard.
    """
    def __init__(self, forum_url, url, name):
        self.forum_url = forum_url
        self.url = url
        self.name = name
        self.topic_list = []

class ForumTopic(object):
    """
        Docstring
    """
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.page_size = None
        self.last_page = None
        self.content = None
