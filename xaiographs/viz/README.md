<h1># REQUIREMENTS</h1>
<p>In order to launch the Explainability web portal (XAIoWeb) it is necessary to have Nodejs installed and configured.</p>

<p>If you do not have it, you can access the address https://nodejs.org/en/ and download the installer of the LTS version</p>

<br><br>

<h1># EXECUTION</h1>

<p>To run and launch the Explainability web portal (XAIoWeb) it is necessary to run the file launcher.py</p>

It receives as parameters the port in which you want to start the web server and the path where the CSV's with the data to be analyzed are located.

    -- port (-p) Web Port - If none is specified, 8080 will be taken by default.
    -- path (-w) Absolute path where the csv are located

Therefore the complete command would be, for example:

    python launcher.py --port=8080 --path='tmp/csv'

<p>Before getting up, it will be verified that the necessary requirements are met and that the necessary packages are available for its correct operation.
If they are not available, the command itself will generate them.</p>
