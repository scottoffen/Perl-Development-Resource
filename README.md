Perl Development Resource
=========================

A simple CGI script that provides information about the Perl environment. While there are lots of these already out there, my host requires every perl script to run in taint mode. I couldn't find a version worked consistently in taint mode, so I made one based on perldiver 1.x, and made sure it worked on Windows and Linux. Tested with Perl 5.8.8 (Linux) and 5.16.3 (Windows 7).

Lists information about the system Perl is working on as well as all the Perl environment variables (so it make a great test script to GET/POST data to). Additionally lists out all installed Perl modules. Click on a module to see the installed version.

>Uses jQuery and Bootstrap; both are loaded via CDNs, so you don't need to worry about any dependencies.
