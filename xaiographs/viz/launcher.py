from xaiographs.common.constants import WEB_ENTRY_POINT

import argparse
import http.server
import os
import pathlib
import shutil
import socketserver
import webbrowser

from copy import deepcopy

MY_PROTOCOL = 'http://'
MY_HOST_NAME = '127.0.0.1'
MY_HTML_FOLDER_PATH = 'frontpiled'
MY_HOME_PAGE_FILE_PATH = 'index.html'
COL_HEIGHT_LEFT = 50
COL_HEIGHT_RIGHT = 20
TEXT_COLOR_WHITE = '\033[0m'
TEXT_COLOR_RED = '\033[91m'
TEXT_COLOR_GREEN = '\033[92m'
XAIOWEB_DISTRIBUTION = 'XAIoWeb distribution'
HIDDEN_DIR = '.{}'.format(WEB_ENTRY_POINT)
SRC_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), MY_HTML_FOLDER_PATH)
JSON_PUBLIC_FOLDER = os.path.join(HIDDEN_DIR, 'assets/public')

JSON_FILES = ["global_explainability.json",
              "global_target_distribution.json",
              "global_graph_description.json",
              "global_graph_nodes.json",
              "global_graph_edges.json",
              "global_heatmap_feat_val.json",
              "global_target_explainability.json",
              "local_dataset_reliability.json",
              "local_reason_why.json",
              "local_graph_nodes.json",
              "local_graph_edges.json",
              "fairness_confusion_matrix.json",
              "fairness_highest_correlation.json",
              "fairness_independence.json",
              "fairness_separation.json",
              "fairness_sufficiency.json",
              "fairness_sumarize_criterias.json"
              ]


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or HIDDEN_DIR not in self.path:
            self.path = os.path.join(HIDDEN_DIR, MY_HOME_PAGE_FILE_PATH).replace("\\", "/")

        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def print_upper_line():
    """
    This function print the upper line of the requirements validations table.
    The only functionality it has is when viewing the fulfillment of requirements
    """
    print(u"\u2554", end='')
    for _ in range(COL_HEIGHT_LEFT):
        print(u"\u2550", end='')
    print(u"\u2566", end='')
    for _ in range(COL_HEIGHT_RIGHT):
        print(u"\u2550", end='')
    print(u"\u2557")


def print_middle_line():
    """
    This function print the middle line of the requirements validations table.
    The only functionality it has is when viewing the fulfillment of requirements
    """
    print(u"\u2560", end='')
    for _ in range(COL_HEIGHT_LEFT):
        print(u"\u2550", end='')
    print(u"\u256C", end='')
    for _ in range(COL_HEIGHT_RIGHT):
        print(u"\u2550", end='')
    print(u"\u2563")


def print_message_line(message: str, status: str, style: str):
    """
    This function print a message line of the requirements validations table.
    The only functionality it has is when viewing the fulfillment of requirements
    The message shows the status of compliance with some of the requirements.

    :param message: name of the requirement to validate
    :param status: status of the requirement
    :param style: color text of the status value (green= Ok, red= alert)
    """
    print(u"\u2551", end=' ')
    print(message.ljust(COL_HEIGHT_LEFT - 1), end='')
    print(u"\u2551", end=' ')
    print(style + status.ljust(COL_HEIGHT_RIGHT - 1) + TEXT_COLOR_WHITE, end='')
    print(u"\u2551")


def print_bottom_line():
    """
    This function print the bottom line of the requirements validatons table.
    The only functionality it has is when viewing the fulfillment of requirements
    """
    print(u"\u255A", end='')
    for _ in range(COL_HEIGHT_LEFT):
        print(u"\u2550", end='')
    print(u"\u2569", end='')
    for _ in range(COL_HEIGHT_RIGHT):
        print(u"\u2550", end='')
    print(u"\u255D")


def check_deploy_web(force: bool = False) -> None:
    """
    This function check build of the frontend.
    In case of build folder doesn't exist, execute a build process.
    :return: Boolean value to continue with the publishing process.
    """
    print_upper_line()

    if not os.path.exists(os.path.join(os.getcwd(), HIDDEN_DIR)):
        print_message_line(XAIOWEB_DISTRIBUTION, 'MISSING', TEXT_COLOR_WHITE)
        print_message_line(XAIOWEB_DISTRIBUTION, 'INSTALLING...', TEXT_COLOR_WHITE)
        shutil.copytree(SRC_DIR, HIDDEN_DIR)
    else:
        if force:
            print_message_line(XAIOWEB_DISTRIBUTION, 'UPDATING...', TEXT_COLOR_WHITE)
            if os.path.exists(HIDDEN_DIR):
                shutil.rmtree(HIDDEN_DIR)
            shutil.copytree(SRC_DIR, HIDDEN_DIR)

    print_message_line(XAIOWEB_DISTRIBUTION, 'AVAILABLE', TEXT_COLOR_GREEN)
    print_bottom_line()


def clean_json_public_folder():
    """
    This function remove all JSON files used previously.
    """
    pathlib.Path(JSON_PUBLIC_FOLDER).mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(JSON_PUBLIC_FOLDER):
        file_path = os.path.join(JSON_PUBLIC_FOLDER, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def process_json_files(path: str):
    """
    This function prepare the backend publish folder used to store and read the JSON files.
    Once the folder is clean, copy all the files from the location indicated in the path parameter to the public folder.

    :param path: Path where the JSON files are stored
    """
    clean_json_public_folder()

    print_upper_line()

    for json in JSON_FILES:
        json_source_file = os.path.join(path, json)
        if os.path.exists(json_source_file):
            shutil.copy(json_source_file, JSON_PUBLIC_FOLDER)
            print_message_line(json, 'AVAILABLE', TEXT_COLOR_GREEN)
            if json != JSON_FILES[-1]:
                print_middle_line()
            else:
                print_bottom_line()
        else:
            print_message_line(json, 'File Not Found', TEXT_COLOR_RED)
            print_middle_line()


def main():
    parser = argparse.ArgumentParser(description='XAIoGraphs')
    parser.add_argument('-d', '--data', default=None, help='JSON files path', type=str, required=False)
    parser.add_argument('-p', '--port', default=8080, help='Web server port', type=int, required=False)
    parser.add_argument('-o', '--open', action='store_true', help='Open web in browser', required=False)
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force building the web from scratch, overwriting the existing one', required=False)
    args = deepcopy(parser.parse_args().__dict__)

    check_deploy_web(force=args.get('force'))
    process_json_files(path=args.get('data'))

    my_handler = MyHttpRequestHandler
    with socketserver.TCPServer((MY_HOST_NAME, args.get('port')), my_handler) as httpd:

        httpd.server_bind = MY_HOST_NAME
        print("Http Server Serving at port", args.get('port'))
        url_domain = '{}{}:{}'.format(MY_PROTOCOL, MY_HOST_NAME, str(args.get('port')))
        if args.get('open'):
            webbrowser.open(url_domain, new=2)
        else:
            print("Web published in URL {}".format(url_domain))

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

        httpd.server_close()


if __name__ == '__main__':
    main()
