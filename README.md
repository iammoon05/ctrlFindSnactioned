Make sure you have Python 3.12 installed. It might run with lower versions, but 3.12 is what the script was written on. <br>
Once you are in the directory, you can run the command `pip install -r requirements.txt` to install the requirements. <br>
<br>
To run the program: <br>
&emsp; `python ctrlFind.py --keyword Whatever You Want To Search For` <br>
you might have to run <br>
&emsp; `python3 ctrlFind.py --keyword Whatever You Want To Search For` <br>
if that's how your system is set up. <br>
<br>
Currently the search is default based on substring-ing on various names of all the chunks found from the html page. <br>
If  a command like the following is passed then it will only search for the keyword in the beginning of the name: <br>
`python3 ctrlFind.py --keyword Whatever You Want To Search For --searchType beginning` <br>
<br>
Note: A **chunk** here is everything found from appearance of a `Unique ID` til the next appearance of the same tag
