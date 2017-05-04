import requests
import re

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

    # populate list of boards
    def populate_boards(self): # Clean board URLS from HTML code using regexes
        tmp_list = re.findall('viewforum.php\?.*', self.load_page('').text)
        # Finally, start cleaning
        for board_name in tmp_list:
            tmp_data = board_name.split("\"")
            tmp_string = re.search('>(.*)</a>', tmp_data[-1]).group(1)
            tmp_url = tmp_data[0]
            # Process topics
            tmp_board_object = ForumBoard(tmp_url, tmp_string)
            tmp_board_object.topic_list = self.populate_topics(tmp_url)
            self.board_list.append(tmp_board_object)

    def populate_topics(self, in_url):
        tmp_list = re.findall('viewtopic.php.*', self.load_page(in_url).text)
        final_list = []
        for topic in tmp_list:
            # Fix to search only string without start=0 and title only-check
            if "class=\"topictitle\"" in topic:
                tmp_url = re.search('viewtopic.php.*?"', topic).group(0).replace('amp', '').replace(';', '')[:-1]
                tmp_name = re.search('topictitle">(.*)</a>', topic).group(1)
                final_list.append(ForumTopic(tmp_url, tmp_name))
            else:
                pass
        return final_list

    def accept_rules(self): # Accept rules, if there is any front page
        self.session.post(self.url + 'enter.php', data = {'enter': 'enter'})

    def load_page(self, url_sub_page = ''): # Load page and return result
        return self.session.get(self.url + url_sub_page)

    def fix_url(self, forced_suffix = 'index.php'): # Fix forum url to match real URL, as it breaks login
        self.url = self.session.get(self.url + forced_suffix).url

    def login_forum(self, in_usr, in_passwd): # Login user
        tmp_sid = self.session.cookies.items()[1][1] # Prepare SessionID from session
        data_dict = {'username': in_usr, 'password': in_passwd,
                     'sid': tmp_sid, 'login': 'login', 'redirect': 'index.php'}
        self.session.post(self.url + 'ucp.php?mode=login', data = data_dict)

class ForumBoard(object):
    """
        docstring for ForumBoard.
    """
    def __init__(self, url, name):
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
        self.last_post = None
