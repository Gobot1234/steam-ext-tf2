steam-ext-tf2
==============

An extension to interact with the Team Fortress 2 Game Coordinator for 
[steam.py](https://github.com/Gobot1234/steam.py). `tf.Client` and `tf.Bot` are `steam.Client` and `commands.Bot` 
subclasses respectively, so whatever you did with `steam.-` you can do with `tf.-`


Example Auto-crafting metal
===========================

```py
import steam
from steam.ext import tf2

bot = tf2.Bot(command_prefix="!")

@bot.event
async def on_gc_ready():
    print("GC is ready")

@bot.event
async def on_trade_accept(trade: steam.TradeOffer):
    refined_crafted = 0
    backpack = await bot.user.inventory(steam.TF2)
    scrap = backpack.filter_items("Scrap Metal")
    for scrap_triplet in steam.utils.chunk(scrap, 3):
        if len(scrap_triplet) != 3:
            break
        await bot.craft(scrap_triplet)
        await bot.wait_for("crafting_complete")

    backpack = await bot.user.inventory(steam.TF2)
    reclaimed = backpack.filter_items("Reclaimed Metal")
    for reclaimed_triplet in steam.utils.chunk(reclaimed, 3):
        if len(reclaimed_triplet) != 3:
            break
        await bot.craft(reclaimed_triplet)
        await bot.wait_for("crafting_complete")
        refined_crafted += 1

    print(f"Crafted {refined_crafted} Refined Metal")

bot.run("username", "password")
```