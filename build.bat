python -c "import nice_update"
python setup.py build
copy config.txt build\exe.win-amd64-3.3 /y
copy update.bat build\exe.win-amd64-3.3 /y
python "update prepare.py"
pause