# "SHARED\_SECTION" : 1 #


**"max\_length" : 100000**

Defines how many historic periods are used for the analysis. 1 period ~= 1 min

**"enable\_flash\_crash\_protection" : 1**

Enable/Disable flash crash protection

Flash crash protection is triggered when a stop loss order is triggered while the volatility is in the fourth quartile (most volatile). In this case the sell order is canceled and instead the order's max\_hold is set to expire after the defined flash\_crash\_protection\_delay.

**"flash\_crash\_protection\_delay" : 240**

Defines how long a stop loss sell order is to be halted (minutes)

**"price\_format" : "%.5f"**  (in repo / will be included in version 0.3)

Sets the decimal precision for prices within the system.

Example:

"%.5f" = $0.00000

"%.2f" = $0.00


# "GTS\_SECTION" : 1 #


**"load\_throttle" : 1**

Enable CPU load throttling.

**"load\_throttle\_sleep\_interval" : 0.15**

Load throttling interval (seconds) between testing each gene.

**"calibrate" : 1**

Automatic population size calibration. Will resize the population to be tested within the defined cycle time.

**"cycle\_time" : 60**

Time in seconds the calibration routine will target to test the entire population.

**"min\_cycle\_time" : 40**

Minimum cycle time (seconds)

**"cycle\_time\_step" : 2**

Cycle time step size. Set to zero to disable variable cycle times.

**"pid\_update\_rate" : 15**

The rate at which gts will send the watchdog keep alive message to the gene server.

# "BCBOOKIE\_SECTION" : 1 #


**"monitor\_mode" : 0**

0 = Enables full functionality (bid & ask)
1 = Disables the generation of bid orders.

**"bid\_counter" : 0**

the initial bid counter

**"bid\_counter\_trip" : 1**

number of cycles between each potential bid. Once tripped will reset to zero

**"order\_qty" : 1.0**

Ask order size

**"commit\_pct\_to\_target" : 0.75**

The percentage to target which pending sell orders much reach before sell orders goes active

**"sleep\_state\_seconds" : 60**

sleep delay between cycles

**"buy\_order\_wait" : 90**

time in seconds a buy order will remain active

**"min\_bid\_price" : 1.0**

Minimum buy price per BTC in dollars.

**"max\_bid\_price" : 20.00**

Maximum buy price per BTC in dollars

**"enable\_underbids" : 1**

Enable/disable underbid orders.

Enabling underbid orders will generate multiple bid orders below the target price at an increasing discount with increasing qtys. Target sell prices remain at the initial bid order price.

Here's an example:

buy: order confirmed : 1.00000000 BTC @ $4.58000 < - original order

buy: order confirmed : 2.00000000 BTC @ $4.54000 < - start of underbid orders

buy: order confirmed : 4.00000000 BTC @ $4.51000

buy: order confirmed : 6.00000000 BTC @ $4.47000

buy: order confirmed : 8.00000000 BTC @ $4.43000



**"enable\_text\_messaging":1**

Enable / disable Amazon AWS SNS

# "REPORTGEN\_SECTION" : 1 #


**"chart\_zoom\_periods" : 1500**

Number of historic periods to chart for the 'zoom' chart

**"chart\_now\_periods" : 200**

Number of historic periods to chart for the 'now' chart

**"win\_loss\_gate\_pct" : 0.80**

The win loss threshold required before the target price result may enter live trading.


# "GAL\_SECTION" : 1 (in repo / will be included in version 0.3) #


**"WATCHDOG\_TIMEOUT" : 60**

Timeout in seconds for monitored processes to send a keep alive message

**"MONITORED\_PROCESS\_LAUNCH\_TIMEOUT" : 20**

Timeout in seconds for launching new processes

**"GENE\_SERVER\_STDERR\_FILE" : "./report/gene\_server\_error\_log.txt"**

**"BCFEED\_STDERR\_FILE" : "/dev/null"**

**"WC\_SERVER\_STDERR\_FILE" : "/dev/null"**

**"REPORT\_GEN\_STDERR\_FILE" : "/dev/null"**

**"GTS\_STDERR\_FILE" : "./report/gts\_error\_log.txt"**

Error log file paths.
Redirecting to /dev/null will not capture any data (works cross-platform)


# Finally #
**"config\_loaded" : 1**

Flag used by scripts to detect if external configuration loaded successfully.