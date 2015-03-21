This page describes how to generate the API key on MtGox and create the encrypted API/Secret key file which is required by the MtGoxHMAC.py module to enable trading with bcbookie.py.


## Step 1: Generate the Advanced API Key on MtGox ##

  1. Log into MtGox
  1. Go to the security center link
  1. Select advanced API key creation
  1. Enter a key name and select the permissions: trade & get info
  1. Click on create key; MtGox will generate the API key and Secret key

## Step 2: Generate the encrypted API key file ##
Run the encrypt\_api\_key.py script. It will prompt you to enter the API Key and Secret Key along with a password. This password is used to encrypt the API/Secret key file on your computer.

## Step 3: Running bcbookie.py ##
When you run bcbookie.py you will be prompted for the password used in step 2 to decrypt/load the API/Secret key data.

It's important to know, in case that that the user is looking to use ga-bitbot as a foundation to implement their own bot, that this prompt is actually coming from the MtGoxHMAC.py module which implements the python interface to the MtGox API.