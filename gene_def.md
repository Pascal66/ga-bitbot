This page outlines the editable configuration options available in the /config/gene\_def.conf file.

# Introduction #

The system uses a JSON formatted configuration file, /config/gene\_def.conf, to load the internal genetic class variables and to define the genetic content.



## Gene Definition ##
In order to minimize the gene length a non-standard data type is used.

The descriptions below use the genetic.py add\_numvar function to define the names, range and resolution for the gene variables used in the system.

**add\_numvar function**

"VARIABLE NAME",bits,decimal,offset

Name - Variable name

bits - Bit resolution of the number (2^n)

decimal - Shifts the decimal point n places

offset - optional constant value offset

**example #1: "anumber",8,2**

creates a variable called anumber which can contain values from 0-

2.55 with 8 bits of resolution (2.55/255 = 0.01 step size)

**example #2: "anumber",8,2,1.5**

same as above but with a constant offset of 1.5 which changes the range to 1.5 - 4.05 with a resolution of 0.01.



## Genetic Class Configuration ##
**Pruning**

"prune\_threshold" : 0.30

"max\_prune\_threshold" : 0.20

"min\_prune\_threshold" : 0.03

"step\_prune\_threshold\_rate" : 0.03

  * Configuration for variable pruning.


**Mutation**

"mutate" : 0.10

"max\_mutate" : 0.20

"min\_mutate" : 0.00

"step\_mutate\_rate" : 0.0001

  * Configuration for variable mutation rates

**Mating**

"multiple\_parent" : 0.05

"max\_multiple\_parents" : 7

  * Probability and max number for multiple parent mating.

**Filters**

"niche\_trigger" : 3

"niche\_min\_iteration" : 7

  * Filter for removing similar genes to maintain genetic diversity.


**Searches**

"bit\_sweep\_rate" : 0.99

"bit\_sweep\_min\_iteration" : 3

  * The rate and hold off for the bit sweep hill climbing algorithm

**Population**

"pool\_size" : 500

  * Initial pool size only. When the system is running the population sizes will adapt to guarantee a set iteration cycle time.

"pool\_family\_ratio" : 0.99

"pool\_max\_survivor\_ratio" : 0.3

"kill\_score" : -10000

  * Score threshold where a gene will always be removed from the gene pool.

"max\_iteration" : 60000

  * Maximum number of population iterations before the entire population is automatically killed off and reseeded with new genes.

**Limits**

"local\_optima\_trigger" : 10

  * Defines the number of population iterations where no increase in score will set the local\_optima flag. The local optima flag lets the host script know when a particular gene pool is no longer producing higher scoring genes.