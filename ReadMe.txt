------------------ Assignment ------------------

Requirements:

- Please use Python language v2.7.x
- Please implement a stand-alone script that does the following:

 
Input:
Taking an argument “root_dir” as a root directory to start traversing.
Taking an argument “keyword” as a regular expression for example ( “^[a-zA-Z]+_TESTResult.*” ) to detect that a file contains a string

 

Functionality:
The script should recursively walk the “root_dir” and detect all the files under that dir contains “keywords” and count the number of files for that sub dir. All results should be saved in a key:value array with key being subdir string, and value being counts of file contains the key line

 
Output:
A output array of all the data, for example {’a/b’: 6, ’a/b/c’: 7, ‘/a/b/c/d’:0}
Stretch goal:- An output graph with a plot with X as subdir name string, Y as count values.
Tests: Please design a set of tests for the above routine you just wrote, how many ways can break the routine above and how many ways can you test the routine. Send these tests in a text file. 

 
-------------------- Answer ---------------------

Style: 
I am using PEP 8 coding convention here: 
https://www.python.org/dev/peps/pep-0008/
As of data structures, I used built in data structures, list, dictionary, enum, etc

Algorithm:
The core algorithm is quite simple, genereate a regex patter and match it with everything in the the target folder, if a match is found, push it to a dictionary if not already in or increment if such element is already in. If the item is a folder, then push it to a list and recursively going into these sub folders and repeat the process.

Design:

I am following the existing Windows Explore search design and generated the following functional requirements:
1. User should be able to search for a file in a given directory
2. User should be able to cancel search if it takes too long
3. User should be able to get notified of search result update
4. User should be able to initiate multiple searches the same directory, at the same time
5. User should be able to initiate multiple searches in different directories, at the same time
6. User should be able to plot the result


In order to fullfil above functional requirements:
1. I've used a factory pattern to ensure that the caller is getting a new object to perform searches. 
2. In the factory, basic parameter validation is performed to ensure valid parameters are passed to object constructor. 
3. In the search object, write subscribe and unsubscibe update event functions to register and inform other layers that results are available
4. Added a public getter to get the current search results
5. Plot function is added to save the figure to a file. NOTE: I've decided to save the figure on disk rather than using plot.show() function. Plot.show() function is consuming a lot of memory. Since user is not expected to interact with the figure (this is my assumption), figures can be viewed / launched through protocol activation (see 7)
6. Clear plot function is added to clear the figure if needed
7. Show plot is added to display the figure using protocol launch

Tests: 
I've added the following tests: 
1. Constructor 
2. Search for wrong item in wrong directory should return nothing
3. Sunny day scenario, search for some file should return some item
4. Sunny day scenario, search for particular file should return that file
5. Sunny day scenario, search with a regular expression should return those files
6. Core search function should be thread safe, (guarded with lock)
7. Cancel the search should return incomplete result
8. Cancel before search should not affect anything, test for robustness, and make sure internal states are not messed up
9. Test search with international characters
10-12. Test callbacks are called when search results are updated. Test unsubscribe before subscribe does not break the function, making sure code is robust with invalid usage
13-16. test factory parameter validation code path and make sure a valid object is generated with correct parameters
17. Test plot saves to current working directory and clear_plot delete the plot
18. Test trying to plot before a valid search, does not plot anything
19. Test protocol launch should show user the plot

Portability: 
No OS specific APIs are used. 

Scalablility:
As already mentioned above. The core algorithms are multi-threaded safe. And factory pattern ensures that unique objects are given to the caller, so that it can be used in parallel. Also, plotting part is optimized for memory, so that hundreds of objects can be running at the same time. 

Reliablity: 
Tested for bad usage cases. 