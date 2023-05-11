# Overheard_Downloder
To Download the script, audio and picture about Overheard at National Geographic.

There are 5 Python scripts.

In log_overheard.py, Using the logging module and colorlog module to save the log to a log file and to output on the Pycharm control platform.

By running the get_all_basic_natgeo.py, you can get the all issue's title and url. Then running the get_all_specific_natgeo.py, you can download the script, picture and audio of every issue one by one.

The save_natgeo_data.py could write the title and url about every issue into the database. In the script, I use the Mysql 8.0.

The last one download_natgeo.py just combine those 4 scripts to complete the download task.

If you had download all the issues before, and after several days there are some new issues are updated on the homepage. You can download those latest contents only by runing this scrpit.

This trick will be save your lots of time.
