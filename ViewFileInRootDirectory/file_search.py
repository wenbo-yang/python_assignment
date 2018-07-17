# encoding: utf-8
#from file_search_interface import IFileSearch
import abc
import enum
import matplotlib.pyplot as plt
import threading
import numpy as np
import os
import re
import uuid
import webbrowser

class IFileSearch(object):
    """abstract base class for factory pattern"""
    def factory(root_dir, keyword):
        if not os.path.exists(root_dir):
            raise ValueError('Root_dir does not exist: ' + root_dir)

        regex = re.compile(keyword) 
        if regex == None:
            raise ValueError('Keyword is not a regular expression, ' + keyword)

        return FileSearch(root_dir, regex)
    factory = staticmethod(factory)

    @abc.abstractmethod
    def search():
        return

    @abc.abstractmethod
    def get_search_result():
        return

    @abc.abstractmethod
    def cancel():
        return

    @abc.abstractmethod
    def subscribe_search_result_changed_event(callback = None):
        return

    @abc.abstractmethod
    def plot():
        return

    @abc.abstractmethod
    def clear_plot():
        return

class FileSearchStatus(enum.Enum):
    ready = 1
    searching = 2
    cancelled = 3

# search for file with regular expression in a root dir
class FileSearch(IFileSearch):
    __CONST_ROOT_DIR_SYMBOL = u'/'
    __CONST_SUBDIR_DISPLAY_LENGTH = 5
    __CONST_SUBDIR_DISPLAY_HINT_LENGTH = 2
    __CONST_SUBDIR_DISPLAY_REPLACEMENT = u'...'
    __CONST_WEBBROWSER_PROTOCOL_LAUNCH_FILE = u'file://'

    def __init__(self, root_dir, keyword):
        root_dir = root_dir.replace(u'\\', FileSearch.__CONST_ROOT_DIR_SYMBOL); # adjust for windows platform
        if not root_dir.endswith(FileSearch.__CONST_ROOT_DIR_SYMBOL):
            root_dir += FileSearch.__CONST_ROOT_DIR_SYMBOL
        self.root_dir = root_dir
        self.keyword = keyword
        self.matched_files= dict()
        self.figure = None
        self.search_lock = threading.Lock()
        self.plot_lock = threading.Lock()
        self.search_status = FileSearchStatus.ready
        self.search_result_changed = list()
        self.plot_file_name = os.getcwdu() + u'/' + format(uuid.uuid4()) + u'.png'
        self.plot_viewer_webbrowser = webbrowser.get()

    # let garbage collector do the work
    def __del__(self):
        return

    # search for file in the root_dir assigned in constructor
    # returns dictionary of sub_dir and number of files matching that keyword
    def search(self):
        with self.search_lock:
            self.search_status = FileSearchStatus.searching
            self.matched_files.clear()
            self.__on_search_result_changed()
            self.__search_file_recursive(self.root_dir) 
            self.search_status = FileSearchStatus.ready
            return self.matched_files;

    def get_search_result(self):
        return self.matched_files;

    def subscribe_search_result_changed_event(self, callback):
        try:
            if self.search_result_changed.index(callback) > 0 :
                print 'This callback is already in subscribed'
        except:
            self.search_result_changed.append(callback)

    def unsubscribe_search_result_changed_event(self, callback):
        try:
            self.search_result_changed.remove(callback)
        except StandardError as standard_err:
            print 'Try to remove callback from result changed event has raise an exception ' + format(standard_err)

    def cancel(self):
        if self.search_status == FileSearchStatus.searching:
            self.search_status = FileSearchStatus.cancelled

    # close the existing plot 
    def clear_plot(self):
        try:
            if self.plot_file_name:
                os.remove(self.plot_file_name)
        except BaseException as generic_err:
            print 'Clear file failed with exception, ' + format(generic_err)

    # plot the current set of matched results
    def plot(self):
        if not self.search_status == FileSearchStatus.ready:
            return

        count = len(self.matched_files)
        if count == 0:
            return

        x_data = xrange(0, count)
        x_ticks = list();
        y_data = list();

        for key, value in sorted(self.matched_files.iteritems()):
            x_ticks.append(FileSearch.__plot_format_xrange_ticks(key))
            y_data.append(value)

        self.__save_figure_to_root_dir(x_data, y_data, x_ticks)

    def show_plot(self):
        if os.path.exists(self.plot_file_name):
            webbrowser.open_new_tab(FileSearch.__CONST_WEBBROWSER_PROTOCOL_LAUNCH_FILE + self.plot_file_name)

    # helper method to save figure into the root dir
    def __save_figure_to_root_dir(self, x_data, y_data, x_ticks):
        with self.plot_lock:
            figure = plt.figure()
            plt.title('Search for files in ' + self.root_dir)
            plt.stem(x_data, y_data)
            plt.xticks(x_data, x_ticks)
            figure.savefig(self.plot_file_name)

    # helper method to make the directory names a little smaller
    # sometimes the directories are really long, we don't want that 
    def __plot_format_xrange_ticks(value):
        reformatted = value
        if len(value) > FileSearch.__CONST_SUBDIR_DISPLAY_LENGTH:
            reformatted = value[0:FileSearch.__CONST_SUBDIR_DISPLAY_HINT_LENGTH - 1]
            reformatted += FileSearch.__CONST_SUBDIR_DISPLAY_REPLACEMENT
            reformatted += value[len(value) - FileSearch.__CONST_SUBDIR_DISPLAY_HINT_LENGTH:]
        return reformatted
    __plot_format_xrange_ticks = staticmethod(__plot_format_xrange_ticks)

    # helper function that finds all the files and directories
    # if an item is an file then try to see if it matches the pattern
    # if an item is an directory, then push it to a list and recurse latter
    def __search_file_recursive(self, target_dir):
        try:
            if self.search_status == FileSearchStatus.cancelled:
                return

            items = os.listdir(target_dir)
            sub_dirs = list()
            for item in items: 
                if os.path.isdir(target_dir + FileSearch.__CONST_ROOT_DIR_SYMBOL + item): 
                    sub_dirs.append(item)
                else:
                    self.__evaluate_file_and_add_to_matched_file(item, target_dir)
            for sub_dir in sub_dirs:
                self.__search_file_recursive(target_dir + FileSearch.__CONST_ROOT_DIR_SYMBOL + sub_dir)
        except WindowsError as win_err:
            print 'Windows error occured ' + format(win_err)
        except IOError as io_err:
            print 'IO error occured ' + format(io_err)
        except StandardError as unexpected_err:
            print 'Unexpected error occurred ' + format(unexpected_err)
        finally:
            print 'Exception thrown when searching for file in directory ' + target_dir

    # helper function to see if a particular file fits the search criteria
    # if yes add it to matched file list
    def __evaluate_file_and_add_to_matched_file(self, item, target_dir):
        matched = re.search(self.keyword, item)
        if matched :
            dir_key = target_dir.replace(self.root_dir, "");
            if not dir_key:
                dir_key = FileSearch.__CONST_ROOT_DIR_SYMBOL
            self.matched_files[dir_key] = self.matched_files[dir_key] + 1 if self.matched_files.has_key(dir_key) else 1
            self.__on_search_result_changed()

    # helper method to call on all registered callbacks
    def __on_search_result_changed(self):
        for callback in self.search_result_changed:
            if callback:
                callback()