# ArtemisScannerTracker v0.2.1
 An [EDMC](https://github.com/EDCD/EDMarketConnector) plugin that keeps track of the exobiology scanner of a CMDRs artemis suit in ED:Odyssey


## Installation

1. Find your EDMC _plugins_ folder (In EDMC settings under _plugins_ you can click the button _Open_ to open the _plugins_ folder)
2. Download the latest release.
3. Unpack the _.zip_ archive of the latest release and move the _ArtemisScannerTracker_ folder into said _plugins_ folder. (folder may have a version number)
4. Overwrite anything if there was an old version installed.

You will need to re-start EDMC if EDMC was open while you installed the plugin. Otherwise just start EDMC


## Features

- The plugin keeps track of the Exobiology Scanner through a Cmdr's journal entries.
It tracks which species (Tussock, Fungoida, ...), and on which body the last exobiology scan occurred (Futes A 2, Moriosong A 1 a, ...) and also the state of the progress of the last exobiological scan. (1/3 found, 2/3 found...)

- It keeps track of unsold profits. Vista genomics prices in this plugin are at the state of U14.01
 
- It also keeps track of your sold and scanned but unsold exobiology once it is installed and running, and show it when you're in the corresponding system.

- Handy buttons in the preferences that'll let the plugin scan through your journal files to retroactively track exobiology scans you've done in the past.

- Multi Commander Support. The plugin can handle you playing with many different CMDRs on the same machine with the same EDMC installation.

- Shows the Clonal Colony Range of the last scanned exobiology scan, and your current distance to up to two previous scan locations with corresponding bearing.

- A button that copies the value of your currently unsold scans to your clipboard

*NEW*: Additional feature to automatically hide values with a through a few new preference settings.


## Usage

- You have to do mostly _nothing_ (yay) apart from having to play Elite Dangerous while using this plugin with EDMC.

- For the sake of making it impossible for the exobiology data tracking to accitentially assume the wrong system as already sold please do sell your whole batch of data.

### Main UI
![AST UI](https://i.imgur.com/nemRFxj.png "main plugin ui pic annotated")

- #1 Update link, only appears if the currently installed version of the plugin is not the same as the newest release.
    - Will lead the user to the newest release.
- #2 Full Status display. Includes Info about species, scan progress and the body it was scanned on.
    - Can be automatically hidden after selling all exobiology or fully finishing a scan.
- #3 Species and Scan Progress display.
    - Can be automatically hidden after selling all exobiology or fully finishing a scan.
- #4 System/Body of last Scan display.
    - Can be automatically hidden after selling all exobiology or fully finishing a scan, if any of these options are activated they will also hide if they are the same as the current system or body.
- #5 Unsold Scan value display. Shows the amount of all unsold exobiology data is worth.
    - The button copies the value shown to your clipboard. Can be automatically hidden when the unsold value is 0 Cr.
- #6 Current System and Body display.
- #7 Clonal Colonial Range display. Will only show up when near a planet.
    - Shows the Current position on a planet (lat, long, heading) and the distance, colonial range and bearing to the scan location to any of the last 2 scans of the currently conducted sampling.
- #8 Finished Scan display. Shows how many Scans are in the current system.
    - Lists them by Planet names assigned to their respective species. Button expands and collapses the list of finished scans. Scans with "*" around the Planet name have not been sold yet and will be lost upon death.

### Settings
![Preferences](https://i.imgur.com/e9kaSED.png "preferences ui")

- All tickbox "Hide X" options will just hide the respective information regardless of what happens in the game.
    - Note that when you are not close to a planets surface the option "Hide clonal colonial distances" may seem to not do anything. If activated the Clonal Colonial Range display will just not pop up when approaching a planets' surface.
- "Autom. hide values after selling all": Will automatically hide the full status, species, scan progress, system/body of last scan after all unsold exobiology was sold. The mentioned information will show up upon the next exobiology scan unless they are manually hidden with a option further up in the settings.
- "Autom. hide values after finished scan": Will automatically hide the full status, species, scan progress, system/body of last scan after a Scan is completely finished after scanning the third. The mentioned information will show up upon the next exobiology scan unless they are manually hidden with a option further up in the settings.
- "Autom. hide unsold value when 0 Cr.": Will hide the unsold value together with the button to copy the value to clipboard when the unsold value reaches 0 Cr.
- "Force hide/show autom. hidden": Will force to hide or show the full status, species, scan progress, system/body of last scan unless a display is manually hidden by an option further up in the settings.
- "Scan game journals for sold exobiology": Will update the plugins' soldbiodata.json by crawling through all journals in the folder specified in the EDMC Configuration.
- "Scan local journal folder for sold exobiology": Will update the plugins' soldbiodata.json by crawling through all journals placed in the journals folder 
    -  Make sure you're not missing a journal in between two other journal files as one of those missing _could_ mean that the sold exobiology scans are not getting tracked properly and please wait a good second or two when scanning through a lot of journal files.

## Motivation

Finally not having to look at the Scanner LEDs in game after returning to a session and wonder "Which goddamn plant was I scanning again?"
while being several thousand lightyears away from Sol. And you'll know which plants you've scanned too!
Sadly that type of information is impossible to get from the Exobiology scanner itself. 
The only thing that it can tell us even despite not telling us _what_ or on which _body_ we last scanned is that the last scan is _incomplete_. The horror. Damn you Supratech! You damn Scoudrels!

Anyway with this plugin those kind of problems are hopefully becoming a thing of the past for our all most favourite recreational activity of scanning space grass while binging Star Trek TNG I guess.

Thats the current extent of this little project. Maybe it'll be extended with more exobiology related features.
