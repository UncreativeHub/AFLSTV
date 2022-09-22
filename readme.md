STV All Australian Side
=======================

This is some quick and dirty python code to "elect" an AFL All Australian team using the [Single Tranferable Vote](https://en.wikipedia.org/wiki/Single_transferable_vote) method used in the Australian Senate.

For player data I used the "fryzigg" fetch_player_stats data source for the entire year (2022) via the excellent [FitzRoy](https://jimmyday12.github.io/fitzRoy/) R package, and saved it to a csv file.

Disclaimer
----------

This isn't a serious attempt to select the best players in the AFL. It's a bit of fun.

I haven't done much in the way of verifying the maths of my code. So there could be horrible errors. But it seems to be roughly around the mark.

Electing a Team
---------------

The selection algorithm briefly works by considering each match as a "Ballot" ranking players by their [AFL Player Rating score](https://twitter.com/aflplayerrating), and treating the best on ground (BOG) as the "first preference". It then works out a quota of BOG's necessary for election to the All-Australian side. (9 BOG's for the typical AFL season if you're including an injury sub, which I am.)

Any players who meet this quota are selected to the All-Australian side, eliminated from future consideration and have any surplus BOG value distributed to the next best on ground. If no players meet this quota, the player with the lowest BOGs (gross player rating value as tie-breaker) is eliminated and has their BOGs redistributed to the next best.

This repeats, electing or eliminating one player at a time, until there is a full All-Australian team selected. Or if the amount of unselected players is the same as the amount of spots remaining in the side, then all remaining players are selected.

Future Work
-----------

I'd originally planned to extend this to multiple different selection algorithms, and to sort the selected team into something approximating an actual AFL team with positions. But never got around to it.

It should be trivial to use a different stat than player rating, but I'd also like to add more elaborate metrics

Thanks, etc
------------

I am in infinite debt to the superb work of the developers of the [FitzRoy](https://jimmyday12.github.io/fitzRoy/) R package. And to [Fryzigg](https://twitter.com/fryzigg) who maintains the data source I used.
