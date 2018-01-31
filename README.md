# MessengerDataOrganizer
Organise and analyse Messenger data from Facebook Data Copy

1. Extracts messages from *.html files (given in Facebook Data Copy)
2. Saves messages to SQLite database (as `*.db` file) on your computer
3. Provides some basic analysis functions. Saves results as `*.csv` which can be than used to draw charts in Excel.

There are currently two separate versions of this application
* `python_implementation` - recommended, supports newests changes in facebook data strucutre as of `30/1/2018`
* `old_js_implementation` - not recommended, may not work with newest facebook data downloads, needs update

Go to dedicated folders (`python_implementation` or `old_js_implementation`) for details.
