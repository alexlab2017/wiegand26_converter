#!/usr/bin/env python3

"""wiegand26_converter.py

    An utility to deal with RFID over Wiegand 26 protocol.

    (c) 2019 Alessandro Labate
"""

import argparse
import sys
import tkinter as tk

# Set this to `True` to get a file that, double clicked on Windows, or
#     otherwise executed directly, opens the Graphical User Interface.
_GRAPHICS = False


class CustomValErr(ValueError):
    """CustomValErr(ValueError)

       This class has been defined to raise and catch errors that are
           specific to this applicatin.
    """


def get_integer(number):
    """get_integer(number)
        number : string (actually a string, float or integer)
        returns : integer
    """
    if number == '':
        raise CustomValErr(f'ERROR: please provide a number')
    try:
        # I prefer to convert `number` to string because if by mistake a float
        #     gets passed to the function it *will* be converted to integer,
        #     not raising the exception.
        number = int(str(number))
    except ValueError:
        raise CustomValErr(f'ERROR: "{number}" is not an integer.')
    return number


def card_2_wiegand(number):
    """card_2_wiegand(number)
        number : integer
        returns : string
    """
    number = get_integer(number)
    min_ = 65537    # facility 1 and user 1, encoded
    max_ = 16777215 # facility 255 and user 65535, encoded
    if not min_ <= number <= max_:
        raise CustomValErr(f'ERROR: {number} is not between {min_} and {max_}')
    # First convert entire number to binary with padding up to 24 chars (bits)
    number_bin = format(number, '024b')
    # Then split it and convert to integers to get the two needed numbers
    facility_code = int(number_bin[:8], 2)
    user_code = int(number_bin[8:], 2)
    # Return a string with two numbers side by side
    return f'{facility_code}{user_code}'


def wiegand_2_card(number):
    """wiegand_2_card(number)
        number : integer
        returns list of strings [str, ...]
    """
    number = get_integer(number)
    min_ = 11       # facility 1 and user 1 with no padding
    max_ = 25565535 # facility 255 and user 65535 with no padding
    if not min_ <= number <= max_:
        raise CustomValErr(f'ERROR: {number} is not between {min_} and {max_}')
    number = str(number)
    candidates = []
    res = []
    ##########
    # NOTE: to test `facility_code` and `user_code` separately may be more
    #     efficient because if one is wrong there's no need to test the other,
    #     anyway the `if ... and` seem more explicit.
    #
    # NOTE: another note on efficiency. Here all three possible combinations
    #     are checked, even if we know in avance that the third combination is
    #     impossible. i.e. with number 31155 we have two possibilities:
    #     facility 3 user 1155, facility 31 user 155. There is no need to test
    #     more because adding one digit to 31 would exceed max facility 255.
    #     Anyway, I do not have to process a million records, for my purpose
    #     this code is just fine.
    #
    # NOTE: `min(len(number), 4)` this is needed because facility_code is max
    #     3 digits long but on shorter numbers like 11 an IndexError would be
    #     raised.
    ##########
    #
    # Loop over the first three digits (or less if number is shorter)
    for i in range(1, min(len(number), 4)):
        # Convert the possible facility and user to integers
        facility_code = int(number[:i])
        user_code = int(number[i:])
        # check if they are in the standard range
        if 1 <= facility_code <= 255 and 1 <= user_code <= 65535:
            # Append to a list of candidates
            candidates.append((facility_code, user_code))
    if len(candidates) < 1:
        raise CustomValErr(
            f'ERROR: {number} does not map to a valid "facilityuser" scheme.'
        )
    # For each candidate, convert to binary, join two numbers and convert
    #     back to an integer, returning it as a string.
    for i in candidates:
        facility_code_bin = format(i[0], '08b') # padding here may be useless
        user_code_bin = format(i[1], '016b')    # padding here is necessary
        res.append(str(int(f'{facility_code_bin}{user_code_bin}', 2)))
    return res


class WiegandConverterGui():
    """Wiegand_converter_gui():
    """
    def __init__(self):
        self.root = tk.Tk()
        # following 6 variables are needed just for window size and positioning
        #    at the center of the screen. No need to save them in the class.
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_width = int(screen_width/4)   # NOTE: edit to adjust window width
        win_height = int(screen_height/2) # NOTE: edit to adjust window height
        win_x_pos = (screen_width//2) - (win_width//2)
        win_y_pos = (screen_height//2) - (win_height//2)
        self.root.geometry(f'{win_width}x{win_height}+{win_x_pos}+{win_y_pos}')
        self.root_bg = self.root.cget('bg')
        self.root.option_add('*Font', ('', 14))
        self.root.title('Wiegand converter')
        self.main_label = tk.Label(self.root, height=2, bg='grey')
        self.main_label.pack(fill=tk.X)
        tk.Label(self.root).pack() # spacing
        # No need to save buttons as will not be modified across the program.
        tk.Button(
            self.root, text='card2wiegand', bg='green',
            command=self.card_2_wiegand_graphics
        ).pack()
        tk.Button(
            self.root, text='wiegand2card', bg='orange',
            command=self.wiegand_2_card_graphics
        ).pack()
        tk.Label(self.root).pack() # spacing
        self.number_entry = tk.Entry(self.root)
        self.number_entry.pack()
        self.error_label = tk.Label(self.root,
                                    wraplength=win_width, justify='center')
        # Some error messages may be longer than the window, I want text wrap
        self.error_label.bind(
            '<Configure>',
            lambda x: self.error_label.config(wraplength=self.root.winfo_width())
        )
        self.error_label.pack()
        self.results_label = tk.Label(self.root)
        self.results_label.pack()
        tk.Label(self.root).pack() # spacing
        self.res_frame = tk.Frame()
        self.res_frame.pack()

        self.number_entry.focus()


    def clear_errors_and_results(self):
        """clear_errors_and_results(self)
        """
        self.error_label.configure(text='', bg=self.root_bg)
        for i in self.res_frame.winfo_children():
            i.pack_forget()


    def graphics_error(self, message):
        """graphics_error(self, message)
        """
        self.error_label.configure(text=f'{message}',
                                   bg='red',
                                   font='TkDefaultFont')
        self.results_label.configure(text='')


    def copy_to_clipboard(self, number):
        """copy_to_clipboard(self, number)
            Function needed to "personalize" a function that gets assigned to
                a button, without calling it at the time of assignment.
            number : a string, in this application actually a number
            returns : a function
        """
        def copy_to_clipboard():
            """copy_to_clipboard()
            """
            self.root.clipboard_clear()
            self.root.clipboard_append(number)
            self.root.update()
        return copy_to_clipboard


    def show_results(self, res):
        """show_results(self, res)
        """
        self.results_label.configure(text='Click to copy to the clipboard',
                                     font='TkDefaultFont')
        for i in res:
            tk.Button(
                self.res_frame, text=i, command=self.copy_to_clipboard(i)
            ).pack()


    def card_2_wiegand_graphics(self):
        """card_2_wiegand_graphics(self)
        """
        self.main_label.configure(text='Card --> Wiegand', bg='green')
        self.clear_errors_and_results()
        number = self.number_entry.get()
        try:
            res = card_2_wiegand(number)
        except CustomValErr as err:
            self.graphics_error(err)
        else:
            self.show_results([res])


    def wiegand_2_card_graphics(self):
        """wiegand_2_card_graphics(self)
        """
        self.main_label.configure(text='Wiegand --> Card', bg='orange')
        self.clear_errors_and_results()
        number = self.number_entry.get()
        try:
            res = wiegand_2_card(number)
        except CustomValErr as err:
            self.graphics_error(err)
        else:
            self.show_results(res)


def main_console(parsed_args):
    """main_console()
    """
    separators = {
        'space' : ' ',
        'comma' : ',',
        'tab' : '\t',
        'semicolon' : ';',
        'colon' : ':'
    }
    sep = separators.get(parsed_args.sep)
    if parsed_args.c2w:
        function = card_2_wiegand
    elif parsed_args.w2c:
        function = wiegand_2_card
    for number in parsed_args.numbers:
        try:
            converted = function(number)
        except CustomValErr as err:
            print(err, file=sys.stderr)
        else:
            if isinstance(converted, list):
                converted = [int(i) for i in converted]
            if parsed_args.keep_original:
                print(f'{number}{sep}{converted}')
            else:
                print(converted)


def main():
    """main()
    """
    if _GRAPHICS:
        WiegandConverterGui().root.mainloop()
    else:
        parser = argparse.ArgumentParser(
            description='Convert an RFID tag transmitted over a ' \
                        'Wiegand26 interface and vice-versa.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-c2w',
            help='Convert from a card to Wiegand26.',
            action='store_true',
        )
        group.add_argument(
            '-w2c',
            help='Convert from Wiegand26 to card.',
            action='store_true'
        )
        parser.add_argument(
            'numbers',
            metavar='N',
            type=int,
            nargs='+',
            help='Provide numbre(s) to be converted.'
        )
        parser.add_argument(
            '-k', '--keep-original',
            help='Print original number before the converted one.',
            action='store_true',
            default=False
        )
        parser.add_argument(
            '-s', '--sep',
            help='Choose the separator between original and converted number.',
            default='space',
            choices=['space', 'comma', 'tab', 'semicolon', 'colon']
        )
        parsed_args = parser.parse_args()
        main_console(parsed_args)

if __name__ == '__main__':
    main()
