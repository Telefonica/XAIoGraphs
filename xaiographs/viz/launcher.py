import http.server
import os
import pathlib
import shutil
import subprocess
import socketserver
import webbrowser

from absl import app, flags

# CONSTANTS
BACKEND_NODE_PACKAGE = 'Backend node package'
BACKEND_PUBLIC_FOLDER = 'backend/public'
COL_HEIGHT_LEFT = 50
COL_HEIGHT_RIGHT = 20
FRONTEND_NODE_PACKAGE = 'Frontend node package'
MY_PROTOCOL = 'http://'
MY_HOST_NAME = 'localhost'
MY_HTML_FOLDER_PATH = 'XAIoWeb/'
MY_HOME_PAGE_FILE_PATH = 'index.html'
NODE_BACKEND = 'backend'
NODE_FRONTEND = 'frontend'
NODE_MODULES_BACKEND = 'backend/node_modules'
NODE_MODULES_FRONTEND = 'frontend/node_modules'
TEXT_COLOR_WHITE = '\033[0m'
TEXT_COLOR_RED = '\033[91m'
TEXT_COLOR_GREEN = '\033[92m'
XAIOWEB_DISTRIBUTION = 'XAIoWeb distribution'

CSV_FILES = ["global_explainability.csv",
             "global_target_distribution.csv",
             "global_graph_nodes.csv",
             "global_graph_edges.csv",
             "local_dataset_reliability.csv",
             "local_reason_why.csv",
             "local_graph_nodes.csv",
             "local_graph_edges.csv",
             "data_correlation_matrix_dataset.csv",
             "input_dataset.csv",
             "input_dataset_discretized.csv",
             "global_target_explainability[DEPRECATED].csv",
             "local_explainability[DEPRECATED].csv",
             ]

# Parameters definition
flags.DEFINE_integer(name='port', default=8080, help='Web server port', required=False)
flags.DEFINE_string(name='path', default=None, help='CSV files path', required=True)
FLAGS = flags.FLAGS


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = os.path.join(MY_HTML_FOLDER_PATH, MY_HOME_PAGE_FILE_PATH)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def print_upper_line():
    """
    This function print the upper line of the requirements validatons table.
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
    This function print the middle line of the requirements validatons table.
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
    This function print a message line of the requirements validatons table.
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


def check_npm_requirements() -> bool:
    """
    This function check the NodeJS installation requirements and print the results.

    :return: Boolean value to continue with the publishing process.
    """
    print_upper_line()
    npm_status = subprocess.run('node --version', shell=True, capture_output=True, text=True)
    if len(npm_status.stdout) > 10:
        print_message_line('NPM Installed', 'FAILED', TEXT_COLOR_RED)
        print_bottom_line()
        return False
    else:
        print_message_line('NPM Installed', npm_status.stdout.strip(), TEXT_COLOR_GREEN)
        print_bottom_line()
        return True


def check_node_backend() -> bool:
    """
    This function check Node packages used to deploy the backend.
    In case of node_modules folder doesn't exist, execute a packages installations.

    :return: Boolean value to continue with the publishing process.
    """
    print_upper_line()
    if not os.path.exists(os.path.join(os.getcwd(), NODE_MODULES_BACKEND)):
        print_message_line(BACKEND_NODE_PACKAGE, 'MISSING', TEXT_COLOR_WHITE)
        print_message_line(BACKEND_NODE_PACKAGE, 'INSTALLING...', TEXT_COLOR_WHITE)

        os.chdir(os.path.join(os.getcwd(), NODE_BACKEND))
        back_process = subprocess.run('npm install', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(os.path.join(os.getcwd(), '..'))

        if back_process.stderr is None:
            print_message_line(BACKEND_NODE_PACKAGE, 'AVAILABLE', TEXT_COLOR_GREEN)
            return True
        else:
            print_message_line(BACKEND_NODE_PACKAGE, 'ERROR', TEXT_COLOR_RED)
            return False
    else:
        print_message_line(BACKEND_NODE_PACKAGE, 'AVAILABLE', TEXT_COLOR_GREEN)
        return True


def check_node_frontend() -> bool:
    """
    This function check Node packages used to deploy the frontend.
    In case of node_modules folder doesn't exist, execute a packages installations.

    :return: Boolean value to continue with the publishing process.
    """
    print_middle_line()
    if not os.path.exists(os.path.join(os.getcwd(), NODE_MODULES_FRONTEND)):
        print_message_line(FRONTEND_NODE_PACKAGE, 'MISSING', TEXT_COLOR_WHITE)
        print_message_line(FRONTEND_NODE_PACKAGE, 'INSTALLING...', TEXT_COLOR_WHITE)

        os.chdir(os.path.join(os.getcwd(), NODE_FRONTEND))
        front_process = subprocess.run('npm install', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(os.path.join(os.getcwd(), '..'))

        if front_process.stderr is None:
            print_message_line(FRONTEND_NODE_PACKAGE, 'AVAILABLE', TEXT_COLOR_GREEN)
            return True
        else:
            print_message_line(FRONTEND_NODE_PACKAGE, 'ERROR', TEXT_COLOR_RED)
            return False
    else:
        print_message_line(FRONTEND_NODE_PACKAGE, 'AVAILABLE', TEXT_COLOR_GREEN)
        return True


def check_deploy_web() -> bool:
    """
    This function check build of the frontend.
    In case of build folder doesn't exist, execute a build process.

    :return: Boolean value to continue with the publishing process.
    """
    print_middle_line()

    if not os.path.exists(os.path.join(os.getcwd(), MY_HTML_FOLDER_PATH, MY_HOME_PAGE_FILE_PATH)):
        print_message_line(XAIOWEB_DISTRIBUTION, 'MISSING', TEXT_COLOR_WHITE)
        print_message_line(XAIOWEB_DISTRIBUTION, 'INSTALLING...', TEXT_COLOR_WHITE)
        build_process = subprocess.run('npm run build-xai --prefix frontend', shell=True, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)

        if build_process.stderr is None:
            print_message_line(XAIOWEB_DISTRIBUTION, 'AVAILABLE', TEXT_COLOR_GREEN)
            print_bottom_line()
            return True
        else:
            print_message_line(XAIOWEB_DISTRIBUTION, 'ERROR', TEXT_COLOR_RED)
            print_bottom_line()
            return False
    else:
        print_message_line(XAIOWEB_DISTRIBUTION, 'AVAILABLE', TEXT_COLOR_GREEN)
        print_bottom_line()
        return True


def clean_csv_public_folder():
    """
    This function remove all csv files used previously
    """
    pathlib.Path(BACKEND_PUBLIC_FOLDER).mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(BACKEND_PUBLIC_FOLDER):
        file_path = os.path.join(BACKEND_PUBLIC_FOLDER, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def process_csv_files(path: str):
    """
    This function prepare the backend publish folder used to store and read the csv files.
    Once the folder is clean, copy all the files from the location indicated in the path parameter to the public folder.
    """
    clean_csv_public_folder()

    print_upper_line()

    for csv in CSV_FILES:
        csv_source_file = os.path.join(path, csv)
        if os.path.exists(csv_source_file):
            shutil.copy(csv_source_file, BACKEND_PUBLIC_FOLDER)
            print_message_line(csv, 'AVAILABLE', TEXT_COLOR_GREEN)
            if csv != CSV_FILES[-1]:
                print_middle_line()
            else:
                print_bottom_line()
        else:
            print_message_line(csv, 'File Not Found', TEXT_COLOR_RED)


def main(argv: list):
    """
    Function with main program

    :param argv: List non-empty of the command line arguments including program name, sys.argv is used if None.
    """
    del (argv)

    my_handler = MyHttpRequestHandler

    if check_npm_requirements():
        if check_node_backend() * check_node_frontend() * check_deploy_web():
            process_csv_files(path=FLAGS.path)

            with socketserver.TCPServer(("", FLAGS.port), my_handler) as httpd:
                subprocess.run('pm2 start pm2-XAIoWeb.json', shell=True)

                print("Http Server Serving at port", FLAGS.port)
                url_domain = '{}{}:{}'.format(MY_PROTOCOL, MY_HOST_NAME, str(FLAGS.port))
                webbrowser.open('{}/{}'.format(url_domain, MY_HTML_FOLDER_PATH), new=2)

                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    pass

                subprocess.run('pm2 stop XAIoWeb', shell=True)
                subprocess.run('pm2 flush', shell=True)
                subprocess.run('pm2 kill', shell=True)
                httpd.server_close()
                print("Server stopped")


if __name__ == '__main__':
    app.run(main=main)
