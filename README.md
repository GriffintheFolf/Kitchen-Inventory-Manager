# Kitchen Pantry Inventory Management

This is a program for managing stock in a kitchen pantry that I created for my final project in Computing Science 2.0.

This is likely the first programming project of any kind that I have ever finished, and as such I am publishing it here.

## How to run
All that is needed is Python 3 and [Flask](https://flask.palletsprojects.com/en/2.0.x/). Presumably, this program
needs at least Python 3.2 due to its use of the [`html`](https://docs.python.org/3/library/html.html) module,
but it most likely contains other functions that require later versions; I programmed with Python 3.7.

To install Flask, use pip, for example:
```
$ python3 -m pip install flask
```

After installation, run `main.py` to start the program, and connect to `127.0.0.1:5000` in your browser.

## Warning: may contain trace amounts of bugs
There may be some bugs or security vulnerabilities here, which I may or may not fix on my own time.

## Code conventions
This typing style is not what I would typically use, even for a Python program. For some reason, the class
required that all variable names be UPPERCASE, even if they were _not_ constant. Not only is this annoying
by virtue of having to continously hold the Shift key, but it also makes the code look awful as well,
since the function names of classes, etc. are lowercase to begin with.

## Licensing
This project is under the MIT Licence, so do whatever you want with it, providing you stick by the licence
of course.
