steam-ext-tf2
==============

An extension to interact with the Team Fortress 2 Game Coordinator for [steam.py](https://github.com/Gobot1234/steam.py).
`tf.Client` and `tf.Bot` are `steam.Client` and `commands.Bot` subclasses respectively, so whatever you did with
`steam.-` you can do with `tf.-`


Proposed example code
======================
(This won't work *yet*)

```py
import steam
from steam.ext import tf

bot = tf.Bot(command_prefix="!")

@bot.event
async def on_gc_ready():
    print("GC is ready")

@bot.event
async def on_trade_accept(trade):
    if [item.name for item in trade.items_to_receive].count("Scrap Metal") > 3:
        await bot.craft(trade.)
        await bot.wait_for("crafting_complete")
        print(f"Crafted {amount} Refined Metal")
```