## ArtemisScannerTracker v0.1.3 dev
 An [EDMC](https://github.com/EDCD/EDMarketConnector) plugin that keeps track of the exobiology scanner of a CMDRs artemis suit in ED:Odyssey


## Installation

1. Find your EDMC _plugins_ folder (In EDMC settings under _plugins_ you can click the button _Open_ to open the _plugins_ folder)
2. Download the latest release.
3. Unpack the _.zip_ archive of the latest release and move the _ArtemisScannerTracker_ folder into said _plugins_ folder. (folder may have a version number)

You will need to re-start EDMC if EDMC was open while you installed the plugin. Otherwise just start EDMC


## Features

- The plugin keeps track of the Exobiology Scanner through a Cmdr's journal entries.
It tracks which species (Tussock, Fungoida, ...), and on which body the last exobiology scan occurred (Futes A 2, Moriosong A 1 a, ...) and also the state of the progress of the last exobiological scan. (1/3 found, 2/3 found...)

- It keeps track of unsold profits. Vista genomics prices in this plugin are at the state of U14 after the buff. _though not sure how long these will stay accurate :c_
 
- It also keeps track of your sold and scanned but unsold exobiology once it is installed and running, and show it when you're in the corresponding system.

- A handy Button in the preferences that'll let the plugin scan through your journal files to retroactively track exobiology scans you've done in the past.

*NEW*: Multi Commander Support. The plugin can handle you playing with many different CMDRs on the same machine with the same EDMC installation.


## Usage

- You have to do mostly _nothing_ (yay) apart from having to play Elite Dangerous while using this plugin with EDMC.

- For the sake of making it impossible for the exobiology data tracking to accitentially assume the wrong system as already sold please do sell your whole batch of data.

- When using the "Scan game journals for sold exobiology":
In the case of journals from your journal-limpet backup you can move them into the local journal folder inside the plugin folder
and press the "Scan local journal folder for sold exobiology"-button.

Make sure you're not missing a journal in between two other journal files as one of those missing _could_ mean that the sold exobiology scans are not getting tracked properly and please wait a good second or two when scanning through a lot of journal files.


## Motivation

Finally not having to look at the Scanner LEDs in game after returning to a session and wonder "Which goddamn plant was I scanning again?"
while being several thousand lightyears away from Sol. And you'll know which plants you've scanned too!
Sadly that type of information is impossible to get from the Exobiology scanner itself. 
The only thing that it can tell us even despite not telling us _what_ or on which _body_ we last scanned is that the last scan is _incomplete_. The horror. Damn you Supratech! You damn Scoudrels!

Anyway with this plugin those kind of problems are hopefully becoming a thing of the past for our all most favourite recreational activity of scanning space grass while binging Star Trek TNG I guess.

Thats the current extent of this little project. Maybe it'll be extended with more exobiology related features.
