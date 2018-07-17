# encoding: utf-8
import os
import shutil
import time
import threading
import unittest
from multiprocessing.pool import ThreadPool

from file_search import FileSearch
from file_search import IFileSearch

class Test_file_search_unittest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create test folder
        test_dir = os.getcwd()
        test_dir = test_dir + '/' + 'Test'
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        new_dir = test_dir
        for dir_index in range(20):
            new_dir = new_dir + '/' + format(dir_index);
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            for file_index in range(100):
                fo = open(new_dir + '/' + 'Test' + format(file_index) + '.txt', 'w')
                fo.write('test')
                fo.close()

    @classmethod
    def tearDownClass(cls):
        test_dir = os.getcwdu()
        test_dir = test_dir + '/' + 'Test'
        shutil.rmtree(test_dir)

        #remove png files
        test_dir = os.getcwdu()
        items = os.listdir(test_dir)
        for item in items:
            if format(item).endswith('png'):
                os.remove(test_dir + u'/' + item)

    def test_constructor_should_pass(self):
        file_search = FileSearch('temp', 'somekeyword')
        self.assertIsNotNone(file_search)

    def test_search_sync_should_empty_result_with_wrong_root_dir(self):
        file_search = FileSearch('somedir', 'somekeyword')
        search_result = file_search.search()
        self.assertTrue(len(search_result) == 0)

    def test_search_current_directory_for_all_files_should_return_some_file(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, "");
        search_result = file_search.search()
        self.assertFalse(len(search_result) == 0)

    def test_search_current_directory_for_current_file_name_should_return_at_least_one_file(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, 'file_search.py');
        search_result = file_search.search()
        self.assertFalse(len(search_result) == 0)
        self.assertTrue(search_result['/'] >= 1)

    def test_search_for_all_files_should_return_more_than_two_files(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, '^[a-zA-Z]*');
        search_result = file_search.search()
        self.assertFalse(len(search_result) == 0)
        self.assertTrue(search_result['/'] >= 2)

    def test_search_sync_in_different_thread_twice_should_return_valid_result(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, '^[a-zA-Z]*')
        thread_pool = ThreadPool(processes=2)
        async_result1 = thread_pool.apply_async(file_search.search)
        async_result2 = thread_pool.apply_async(file_search.search)
        search_result1 = async_result1.get()
        search_result2 = async_result2.get().copy()
        self.assertTrue(search_result1 == search_result2)

    def test_search_async_and_then_cancel_should_return_incomplete_result(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, '^[a-zA-Z]*')
        async_thread = threading.Thread(target = file_search.search)
        async_thread.start()
        time.sleep(0.02); #sleep for a while to ensure thread is executing
        file_search.cancel()
        async_thread.join()
        search_result_async = file_search.get_search_result().copy()
        search_result_sync = file_search.search();
        self.assertFalse(search_result_sync == search_result_async)

    def test_cancel_before_search_should_not_affect_search_result(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, '^[a-zA-Z]*')
        file_search.cancel()
        search_result = file_search.search()
        self.assertTrue(len(search_result) > 0)

    def test_search_for_unicode_result_should_return_valid_result(self):
        test_dir = os.getcwd() + '/' + 'Test'
        fo = open(test_dir + '/' + u'测试' + '.txt', 'w')
        fo.write('test')
        fo.close()
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, u'测试.txt')
        search_result = file_search.search()
        self.assertTrue(len(search_result) > 0)

    def __handle_search_result_changed(self):
        self.callback_reached = True

    def test_subscribe_to_search_result_changed_event(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, 'file_search.py');
        self.callback_reached = False
        file_search.subscribe_search_result_changed_event(callback = self.__handle_search_result_changed)
        file_search.search()
        self.assertTrue(self.callback_reached)

    def test_subscribe_and_unsubscribe_to_search_result_changed_event(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, 'file_search.py');
        self.callback_reached = False
        file_search.subscribe_search_result_changed_event(callback = self.__handle_search_result_changed)
        file_search.unsubscribe_search_result_changed_event(callback = self.__handle_search_result_changed)
        file_search.search()
        self.assertFalse(self.callback_reached)

    def test_unsubscribe_to_search_result_changed_should_not_raise_exceptions(self):
        current_dir = os.getcwdu()
        file_search = FileSearch(current_dir, 'file_search.py');
        self.callback_reached = False
        file_search.unsubscribe_search_result_changed_event(callback = self.__handle_search_result_changed)
        file_search.search()
        self.assertFalse(self.callback_reached)

    def test_pass_an_invalid_dir_to_file_search_factory_should_throw_an_exception(self):
        self.assertRaises(ValueError, IFileSearch.factory, '.invalid_dir./', 'file_search.py')

    def test_pass_an_invalid_regex_to_file_search_factory_should_throw_an_exception(self):
        self.assertRaises(BaseException, IFileSearch.factory, os.getcwdu(), '*.*.')

    def test_pass_valid_params_to_file_search_factory_should_return_valid_object(self):
        current_dir = os.getcwdu()
        file_search = IFileSearch.factory(current_dir, 'file_search.py');
        self.assertIsNotNone(file_search)

    def test_factory_generated_instance_should_return_valid_search_result(self):
        current_dir = os.getcwdu()
        file_search = IFileSearch.factory(current_dir, 'file_search.py');
        search_result = file_search.search()
        self.assertTrue(len(search_result) > 0)

    def __find_png_file(self):
        items = os.listdir(os.getcwdu())
        for item in items:
            if format(item).endswith('png'):
                return True
        return False

    def test_plot_current_valid_result_should_generate_a_plot_in_workding_dir_and_remove_with_clear_plot(self):
        current_dir = os.getcwdu()
        file_search = IFileSearch.factory(current_dir, 'file_search.py');
        search_result = file_search.search()
        self.assertTrue(len(search_result) > 0)
        file_search.plot()
        self.assertTrue(self.__find_png_file())
        file_search.clear_plot()
        self.assertFalse(self.__find_png_file())

    def test_plot_before_valid_search_should_return_with_no_plot(self):
        current_dir = os.getcwdu()
        file_search = IFileSearch.factory(current_dir, 'this_file_does_not_exit.py');
        search_result = file_search.search()
        file_search.plot()
        self.assertFalse(self.__find_png_file())

    def test_plot_current_valid_result_and_show_should_do_protocol_launch_to_display_plot(self):
        current_dir = os.getcwdu()
        file_search = IFileSearch.factory(current_dir, 'file_search.py');
        search_result = file_search.search()
        self.assertTrue(len(search_result) > 0)
        file_search.plot()
        file_search.show_plot()
        time.sleep(2)
        file_search.clear_plot()
        self.assertFalse(self.__find_png_file())

if __name__ == '__main__':
    unittest.main()
