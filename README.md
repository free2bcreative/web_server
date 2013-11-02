# Web Server

This is a basic web server program that only implements the GET request.  It uses non-blocking IO, timeouts, and caching.  It's pretty magical.

## Short Guide to My Code

### web.py

The main file that starts up the whole thing

### poller.py

This is where most of the server is located.

### HTMLParser.py

Class that parses a request.

### FileServer.py

Class that takes the HTMLParser and generates Response Codes (400, 404, etc) depending on what the client requests.

### WebServerConfig.py

Class that takes in web.conf and parses it and makes it usable to the poller.py and FileServer.py classes.

### ErrorResponseCodes.py

Class that generates Error Response Codes quickly.

### Debug.py

The Debug class made it a little easier to place debugging messages throughout my code.  It came in handy so many times.  

## Non-Blocking IO

I set each client that came in to be non-blocking in line 107 of "poller.py".

Most of the code for Non-Blocking IO was in the handleClient function in "poller.py".  I check for EAGAIN and EWOULDBLOCK on line 133.  If that happened, I broke from the loop and didn't wait for the client.

However, when sending the files back to a client, I tried sending again if EAGAIN or EWOULDBLOCK occured, as seen on lines 148 - 158 (for the HTTP response) and in the sendFile() function (lines 165 - 189). 

## Timeouts

I used "Mark and Sweep" to clear idle clients.  I set the sweepTime to 5.0 seconds on line 22.  

Most of the "Mark and Sweep" code was in the run() function starting on line 48, where I took the current time to know when I last swept.  

I then took the current time before a client connected (line 58) and placed it in a dictionary called last_used (line 71).  

On lines 78-90, I checked if it was "time" to sweep again.  If so, I iterated through all of the clients and checked to see if they were idle for too long and deleted them.

I then reset the lastChecked time to the current time.  That way, it would Sweep again in 5.0 seconds.


## Caching

In the case that a client send a little bit of a request at a time, I cached all of the little requests and added them together.

I created a cache of and empty string when the client first connected (line 108).

I then received the data from the client, and if the client DID send data, I added it to the request (line 124).  

If the request was complete, i.e. had a "\r\n\r\n" in it, I parsed it and handled the request.  But if it was NOT a complete message, I put the partial request into the cache dictionary (line 162) for use later in next loop.