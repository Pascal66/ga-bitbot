#frequently asked questions

# Notes #


**The configuration files: global\_config.json and gene\_def.json regularly change on the repository. If you have a running system make sure to back up these configuration files before downloading new releases or pulling new versions from the repository.**

**Editing the gene\_def.json file will result in a new db being created in the gene db library. A MD5 hash of the gene\_def.json file is used to generate the db name, so any changes to this file at all will result in a new db.**


# FAQ #


## Q: I can't do anything else on my computer while the program is running. Can I reduce the load on the CPU? ##
A: You can lower the CPU load by increasing the variable 'load\_throttle\_sleep\_interval' in global\_config.json

Another option is to run the system in vmware player using a linux image. The vmware player can be configured to set a hard limit to the number of CPU cores used.

vmware player is free and can be downloaded here: http://www.vmware.com/products/player/

## Q: Why do the charts show a net loss? ##
1) The system may not have stabilized yet.


It takes time for a GA system to find good solutions. The longer the system runs the greater potential becomes to find the best strategy. I would recommend letting the system run for an hour or two before considering the output legitimate.


2) The fitness function utilizes a non-linear scoring factor weighted towards the latest trades.


This allows the system to more easily adapt to market changes while still taking past performance into consideration.

Consider that the system will constantly evolve in the future as it would have in the past. Therefore, it's not possible through the current gts configuration to produce evidence of the overall success of the system.

When reviewing a report, it's more important that the latest/current trades are producing positive results. As far as live trading goes, orders are gated by overall win/loss ratios to prevent poor trade strategies from going active.

### Q: Why do the clients testing the lower quartiles expire at a higher rate, or why does the gene visualizer show less genes in the lower quartile ###

This is normal. The reason you're seeing this behavior is that the fitness function can not find suitable genes in the lower two quartiles and the gene\_server filters out any submitted genes that did not result in a trade.

In the gts.py script, each time the population is fully scored, the local optima buffer captures the highest score. Local optima is detected when the buffer is filled with the same score. This indicates that no further progress is likely with the test population. And with the run\_once option set when launching gts.py, the script will 'expire' when this condition is reached.

So one reason your seeing greater expiration rates for the lower two quartiles is that the local optima condition is triggered with the absolute minimum number of population cycles required due to no advancement in fitness scores.

The second contributor is that the fitness function runs faster when no trade positions are generated. This is because the fitness function code to manage trade positions is never executed.

The reason the gene visualization for the first two quartiles are of differing lengths is that the gene\_server wont accept submissions for the lowest score: if d['score'] != -987654321.12346:

Differences in performance between commits can probably be attributed to changes in the gene\_def config. I regularly change it for testing purposes.