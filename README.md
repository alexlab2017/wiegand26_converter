# wiegand26_converter

A simple utility to convert an RFID card/tag number as if it was transmitted
following the Wiegand 26 standard.

## The problem

I have an RFID card/tag reader placed remotely, used for access control. This
only reads the cards and sends data (using Wiegand 26 protocol) to a controller
relay board that is network connected. Installed on a PC, there is a software
used to manage users, time schedules and so on.

I noticed that the card number is not the same that I see in the software. Ii
seems that the number gets changed between the reader and controller board.

## More data

Doing a bit of research I found online some documentation on Wiegand 26
protocol, without repeating here what it's easy to find on the web, here is a
brief summary.

26 stand for 26 bits, two of which (first and last) are parity bits used for
data integrity validation, flow control or such tasks. Remaining 24 bits are
actual information, divided in two groups, first 8 bits stands for "facility
code" and can be anything between 1 and 255, last 16 bits stand for "user code"
and can be anything between 1 and 65535.

The reason for this is that with only "user code" would be easy for a card
belonging to company "A", let's say card number 1, to grant access also to
other companies "B" and "C" that use cards for access control. Adding a
facility code diminishes the probability of coincidence.

Examining my card number and the number appearing in the access control
software I could detect a pattern, I can see that there are "facility code" and
"user code" one next to the other, forming an integer number.

Per the tests that I did there is no padding between two numbers or before the
"facility code", so there is no precise way to split them. NOTE: as a side
note, this can lead to a bug because number "111" could be "facility 1 user 11"
but also "facility 11 and use 1".

Anyway what I was trying to accomplish is read RFID cards/tags on my desk and
register them into the software without having to go to the reader itself, read
the card and check how the number is "converted".

This task must be easy and usable also by non skilled personnel.

## The solution

I wrote this nice little utility to convert a number to the format used by my
software and vice-versa.

## Notes on the code

I tried to make code as clear as possible in order to be easily modifiable for
someone else needs. There are lots of comments trying to explain the logic.

There is a custom error class inheriting from `ValueError` to be able to handle
errors specific to the conversion.

There are two main functions responsible for the conversions: `card_2_wiegand`
and `wiegand_2_card` with an helper function to ensure that a valid string (one
that can be converted to integer) is passed to the main functions.

There is a class for the GUI. I decided not to inherit from `tkinter.Frame` as
I saw quite often in the documentation. I opted also to initialize my root
element `tkinter.Tk` inside the class without inheriting from it or defining it
outside the class. In this way I have a clean and Namespace to deal with my
variables and all the GUI stuff "all in one" but within separated variables.
This may be an issue if you want to implement this GUI inside an existing
application, anyway, having just one window, makes this setup ok for me and is
also quite easy to re-arrange the code in case of need.

Inside GUI class there are some functions for user experience and graphical
functioning of the window, as well as error handling.

### *IMPORTANT NOTE*

The `main` function runs accordingly to a variable: if `_GRAPHICS` is set to
`True` runs the GUI, otherwise parses command line parameters and runs a
function for command line use. If you are on Windows and you want a nice GUI,
just set the variable to `True` and with a double click you will get the
graphics. This has been tested on linux and on Windows.

## TODO and contributions

### Command line use

-   Accept a file as input
-   Read from stdin
-   Output to file


Beside this points, every other improvement to the GUI or to the logic of the
code is welcome.
