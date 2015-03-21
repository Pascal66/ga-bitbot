# Quick Start Guide - In Development Version #

This version reflects the in development version available from the code repository.


## Introduction ##
ga-bitbot is a distributed genetic algorithm tuned trading system for Bitcoin which includes market data collection, gene client/server, reporting tool, and automated trading.

The intention of this project is to create a high frequency capable trade platform for the bitcoin p2p currency. Please note that this is a highly experimental project. The intention isn't to provide a profitable system 'out of the box', rather the goal is to provide a framework which can be reconfigured to optimize a users unique trade strategy.

Note that it will take a considerable amount of time for the system to search and populate the gene database with good solutions. Genetic algorithms are evolutionary; The strategies will evolve over time to converge on a good solution. In order to mitigate the long startup time, the system periodically saves the gene database to reduce the initial search times when the system is restarted.

If you don't already know what bitcoin visit http://bitcoin.org/ for more information.

This system is programmed for python version 2.7 and has been tested on Linux, OSX & Windows. It will not work on python 3.x. You can download python here: http://www.python.org


## PYPY (Required) ##
For increased performance (~250% faster), use the pypy JIT interpreter. I recommend the nightly builds as there are bugs with the latest released version.

Nightly builds of pypy can be found here:
http://buildbot.pypy.org/nightly/trunk/

## redis (Optional but highly recommended) ##
Enables data caching allowing for increased performance

http://www.redis.io/

Use of redis requires the python redis-py client available here:
https://github.com/andymccurdy/redis-py

Also, depending on how pypy is installed you may need to edit the sys path in cache.py so it can find the redis-py module.


## node.js (Optional but highly recommended) ##

http://www.nodejs.org

Enables server.js script to be run allowing for:
  * websocket bridge
  * streaming mtgox orders, trades & depth
  * streaming mtgox depth chart updates (initial population of depth currently disabled)
  * streaming ga-bitbot pid info
  * parallel coordinate visualization of the gene database

enter the /tools/nimbs folder and run: node server.js
open your browser to your local IP port 8088
(ie. 127.0.0.1:8088)

## OpenCL (Optional - on hold) ##

**Experimental - currently not in a working state**

This project also contains an optional OpenCL implementation which will utilize available host GPU resources for highly task parallelized computing ([[HPC](http://en.wikipedia.org/wiki/Parallel_computing)).

In addition to a base python installation the required packages are required:

For AMD/ATI based systems (Intel/NVIDIA systems are untested) the accelerated parallel processing SDK may be required**:
http://developer.amd.com/sdks/amdappsdk/pages/default.aspx**

**newer drivers include opencl implementations so this step may not be required.**

Access the Catalyst Control Panel and disable both VPU recover and the watchdog timer:

  * Select Advanced > Graphics Settings > VPU Recover

  * Unclick Enable VPU Recover

The following packages are required regardless:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#base

http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopencl

As far as performance is concerned: python < pypy < OpenCL

## Overview ##

ga-bitbot is a system comprised of many scripts which work together. This guide explains how to configure the system, what each component does and how to use them.

System launcher:

  * **gal.py** - ga launcher/monitor is the preferred way to start the system. It synchronizes the historical bitcoin data, launches the gene\_server, web based client, reporting script, bit coin data feed, and launches/monitors the each instance of the local gts scripts. It basically launches everything except for bcbookie (live trading) and the optional node.js websocket bridge/server

System components (no need to run directly):

  * **bcfeed.py** - connects to the http://bitcoincharts.com/ telnet interface to collect market trade data

  * **gene\_server.py** - implements an XMLRPC server which clients use to  store/retrieve genetic data. Now supports database collections stored in a single library file (/config/gene\_server\_db\_library.json)

  * **gene\_server\_config.py** - contains the IP and port configuration for the XMLRPC server

  * **genetic.py** - generic genetic algorithm implementation. This module is used by other scripts and isn't meant to be run directly.

  * **bct.py** -  the default trade simulator - implements the a strategy framework

  * **bct\_alt.py** -  the alternative trade simulator - implements a trade strategy framework

  * **gts.py** - genetic test sequencer. Requires a gene\_server to be running.

  * **report\_gen.py** - generates the html reports (charting) for the trade system and finds target buy/sell orders. Requires a gene\_server and gts instances running, one for each quartile (see below for what this means).

  * **wc\_server** - web based client for system monitoring and viewing reports. Open your browser to your local ip address using port 8080 to view. Example: 192.168.0.100:8080


Live automated trading (Requires PyCrypto python module installation. Currently under development - use at your own risk!!):

  * **encrypt\_api\_key.py** - this script creates an encrypted file containing your API key/secret key (generated on the MtGox website) to enable automated trading using the MtGox HMAC API authentication method. The local decryption password is salted and hashed (SHA512) to prevent dictionary attacks by an attacker in the case of a compromised filesystem.

  * **bcbookie.py** - implements a http://www.mtgox.com trading bot for live automated trading. Requires a gene\_server and gts instances running, one for each quartile (see below for what this means). Now that the gene server can host a collection of databases you can use the wc\_server interface to select the active database (just click on the db link on the status page). The default database is always set by the first client connection. If using the gal.py script, the fist client loaded always uses the gene\_def file found in the config folder.

Experimental code (not currently used in the system):

  * **mgws.py** - connects to the mtgox.com websocket interface to collect market trade data (in development currently not used for anything)

  * **ocl\_gts.py** - OpenCL implementation of gts.py. Executes the fitness function provided by gkernel.cl

Extra components (optional):

  * **encrypt\_aws\_key.py** - this script creates an encrypted file containing your Amazon AWS API key/secret key (generated on Amazons website). This will allow bcbookie to send messages (sms,email,etc - configured through Amazon AWS) to you in realtime as orders are completed. The local decryption password is salted and hashed (SHA512) to prevent dictionary attacks by an attacker in the case of a compromised filesystem.  The messaging service can be enabled/disabled in the global\_config.json file.

## Configuration ##

See [GlobalConfig](GlobalConfig.md) for details regarding global\_config.json


Before you use the system you will need to:
  * Configure the port the gene server will listen on and set your IP (IP only needed if you want to provide access to the gene server to other computers on a LAN or WAN). (see gene\_server\_config.py)

The system defaults to 127.0.0.1 (localhost) on port 9854 and so will only be available on your local machine. If you want to use multiple machines you must change the setting to the LAN or WAN IP.

**MtGox:**

Before the automated trade script (bcbookie) can be used, an advanced API HMAC access key/secret must be generated here:  https://mtgox.com/users/settings?page=api

Scroll to the bottom of the page to the 'Advanced API key creation', enter a name for the key and click the create key button. Once the key is created make sure to grant the key 'trade' and 'info' access.

Once the API key is created, run the encrypt\_api\_key script and follow the directions to generate a local encrypted copy of the API key data. This file will be used to enable automated trading.

**Amazon AWS SNS:**
To use the Amazon AWS simple notification service you will need to sign up for an account here:
http://aws.amazon.com/sns/

(The first 1,000 Amazon SNS Email/Email-JSON Notifications per month are free, with SMS I believe you get the first 100 text messages per month for free -- but check first!)

First you will need to generate security credentials. Click on your account name in the upper right hand corner and select 'Security Credentials'. Once the page loads, scroll down to 'Access Credentials' and click 'Create a New Access Key'. Once created save the access key and secret key for the last step.

Once an account is created and you have generated the security credentials you will need to create a new topic. To do this log into the AWS Management Console go to the SNS tab and click on 'Create a new topic'. You will also need to create a subscription to the topic. The subscription is where you define the protocol(s) and contact information (cell phone,email address,etc.) to receive the notifications.

With your security credentials and newly created topic ARN (It will look something like this: arn:aws:sns:us-east-1:123451234567:bcbookie) launch encrypt\_aws\_key.py and enter the information as it's requested.

Finally, to enable text messaging by editing the global\_config.json file and set 'enable\_text\_messaging' to 1.

If enabled, bcbookie will send a message upon startup and whenever a bid or ask order completes.

## Utilities ##
**bcfeed\_synch**

This script is used to bootstrap the system with the latest historic price data.

**The old way of using it:**
This script takes a datafeed downloaded from http://bitcoincharts.com/ (see http://bitcoincharts.com/about/markets-api/ ) and converts the data to a 1min weighted average format. Be sure to name the downloaded file 'download\_mtgoxUSD.csv' prior to running the script!

The script is setup for the mtgox data naming convention but any data feed can be processed - just be sure to rename the output file correctly!

After running the script you must then manually copy the output to the datafeed folder and overwrite the previous version.

**The new way:** Add a -d argument when running the script and it will automatically download the mtgox USD historic data, process the information and move the result into the datafeed folder.
Open a command shell and type: python bcfeed\_synch.py -d

**Here's the direct link to download all historic mtgoxUSD trades:
http://bitcoincharts.com/t/trades.csv?symbol=mtgoxUSD&start=0**


If your not using the system launcher (gal.py) or if you are developing your own system, in order to maintain the latest dataset run bcfeed.py located in the main project folder. This script connects to the bitcoincharts telnet interface to receive and store the latest (live) trade data. To prevent gaps in the dataset, only run bcfeed.py after running bcfeed\_synch.

**db\_admin\_util**

A database administration utility for managing the gene\_server\_db\_library.json file.


## Quick Start ##

The use of pypy is highly recommended for increased performance. See the introduction for direction on how to install pypy.

**When installing pypy on windows the executable should be renamed pypy or on posix systems create a symbolic link to the executable named pypy. For the really lazy just download the nightly pypy build and extract the archive into the same folder as ga-bitbot; Be sure to rename the executable to pypy.**

**Automated System Launch (Requires PYPY)**
  1. Open a terminal and type: python gal.py

This script supports three command line options: all, server & client. The server option will only launch the server components. The client option launches only the clients (used for distributed computing) . The default configuration is all.

**Manual System Launch**
  1. Optional: see the instructions in the utilities section above to download the latest bitcoin market data. Otherwise the system will run with the supplied non-current historic data.
  1. Optional: To maintain an active dataset, after the data is bootstrapped from step one, start the data feed script by opening a command shell within the project folder and type: python bcfeed.py
  1. Open a command shell and navigate to the project folder then start the gene server by typing: python gene\_server.py
  1. Open an additional shells as needed to execute each of the following scripts
  1. Start the gts scripts by typing the following (if not using pypy substitute with 'python' below):
    1. pypy gts.py 1 y v
    1. pypy gts.py 2 y v
    1. pypy gts.py 3 y v
    1. pypy gts.py 4 y v
  1. To run the OpenCL implementation substitute 'python' for 'pypy' and 'ocl\_gts.py' for 'gts.py'
  1. At least four instances of gts.py need to be running, one for each quartile (see the components section for an explanation of what this means), in order for the reporting script to work. Start the reporting script by typing: pypy report\_gen.py

The first argument to gts.py tells the script which quartile to test.

The second argument (y/n) tells the script to periodically download the best of the best genes from the gene server and retest. If set to y the script will constantly retest the best genes available from the server and use them as seed stock for mated/mutated genes. If set to n the script will begin with a random population in order to find a new local optima to be submitted as a best of the best gene to the server. Once a new local optima is found, the process repeats with a new random population.

The third option 'v' tells the script to run in verbose mode which will display the genes as they are being tested. Note that on windows you'll want to adjust the terminal width to about 140 characters wide so the data will fit on one line. This lets you see what's going on under the hood as the genes evolve. Verbose mode is optional.

Each gts script is an independent worker, you can run as many instances as you wish. Ideally you can run as many as your machine has cores available. At a minimum you'll want to run a set (quartiles 1-4) of gts scripts in best of the best mode (second argument set to y). Any additional instances should be run in standard search mode (second argument set to n).

The processing load of the gene\_server and bcfeed scripts is negligible.

You can view the constantly updated GA reports by entering the report folder and opening one of the html files in your browser. The files with the 'latest' suffix only contain the tail end of the market data which greatly reduces the file sizes (the full reports will be very large and can cause loading problems for your browser!!).

At this point the GA is optimizing the trade strategies and reporting data, but trade automation is not yet running... documentation of this final step is coming soon ;)

## Components ##
**gts.py**

This is the glue script which configures the trade system (bct) from the gene pool, feeds the historic data through the system, collects the score (fitness function built into bct) and sends the high scoring genes to the gene\_server.

The command line arguments are:
  1. 1-4 or all :  Selects the quartile. The 'all' option will cycle through each quartile.
  1. y or n : This seeds the client gene pool population from the high scoring genes retrieved from the gene server if set to y
  1. v : verbose mode. This optional argument tells the script to display each gene as it's tested along with the high score and current score
  1. run\_once : This optional argument tells the script to run only one local optima cycle then exit. Guards against potential memory leak issues with some pypy builds.

  1. get\_config : a random registered gene\_def will be downloaded from the gene\_server and used. If none are available the local gene\_def.json file will be used.

  1. get\_default\_config : get the actively selected gene\_def config from the gene server

  1. score\_only : only score the genes, used to refresh the scores on the gene server

  1. profile : runs a profiler on the fitness script. exits after a min score of 1000 is reached (be careful that the fitness gene can reach this score in a reasonable time). saves a dot plot png image in the report folder. requires the pycallgraph module to be installed.

Special case - when the 'all' option is paired with the best of the best ('y' option) all scores on the gene\_server will be updated but no new populations will be created.


**quartiles in bct**

The system is actually optimizing four trade strategies in parallel. The historic data is preprocessed and split into volatility quartiles using a modified average true pct range indicator:

http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_true_range_atr

This isn't backtest cheating but rather simply analyzing the historic data to define the quartile boundaries used in the trade system. These boundaries are constantly recalculated as new price data is collected which will effect the scores of previously calculated genes. This is also why the gene\_server maintains a best of the best population - for retesting genes over time, and also why the gene\_server has a moving window for reporting current high scores.

