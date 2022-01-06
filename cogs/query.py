import discord
from discord import client
from discord.ext import commands
import aiohttp
import asyncio
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
class QuertExceptions(Exception):
    pass
class Query(commands.Cog):
    """Class that defines an image request object.
    Contains methods for changing various parameters used to find the result images.
    Also functions as a cog and contains commands related to sending image results to discord.
    """
    def __init__(self, bot, mkt='en-US', result_count=5, moderation='Moderate', 
                minDim = (120, 120), maxDim = (1024, 1024)):
        self.bot = bot
        load_dotenv()
        self.api_key = os.getenv('BS_API_KEY')
        self.endpoint = os.getenv('END_POINT') + "v7.0/images/search" #dont mess with this it will fuck everything up
        self.query = None
        self.mkt = mkt
        self.result_count = result_count
        self.offset = 0
        self.moderation = moderation
        self.params = {'q': self.query, 'mkt': mkt, 'count' : result_count, 'offset': self.offset,'safeSearch' : moderation,
        'minWidth' : minDim[0], 'minHeight' : minDim[1], 'maxWidth' : maxDim[0], 'maxHeight' : maxDim[1]}
        self.url_list = None
        self.img_list = None
        self.selected_image = None
    async def cog_check(self, ctx):
        async def check(ctx):
            if isinstance(ctx.channel, discord.DMChannel): return True
            else: return False
        return commands.check(check)
    @commands.group(name='find', help='Finds and returns images based on a descriptive query.', invoke_without_command=True)
    async def find(self, ctx, *, arg):
        """ Finds images based on the query param """
        headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        self.set_query(arg)
        if self.query is not None:
            await ctx.send("Finding image results for " + arg + ". Please wait...")
        # Calls the API
            async with aiohttp.ClientSession() as session:
                async with session.get(self.endpoint, headers=headers, params=self.params) as response:
                    #image_urls = []
                    if response.status == 200:
                        search_results = await response.json()
                        self.url_list = [img["contentUrl"] for img in search_results["value"][:self.result_count]]
                    else:
                        self.url_list = None
                await session.close()
            if self.url_list is not None:
                self.img_list = []
                async with aiohttp.ClientSession() as session:
                    for i in range(self.result_count):
                        async with session.get(self.url_list[i]) as image_data:
                            if image_data.status == 200:
                                image_bytes = BytesIO(await image_data.read())
                                    # Some image objects might use a different colour mode and need to be 
                                    # converted to rgb to prevent errors on previewing in the channel.
                                if image_bytes is not None:
                                    #if image_bytes.mode != 'RGB': image_bytes.convert('RGB') 
                                    await ctx.send(file=discord.File(image_bytes, str(i + 1) + '.jpg'))
                                print(image_bytes)
                                self.img_list.append(image_bytes)
                            else:
                                self.img_list.append(None)
                                await ctx.send("An unexpected error occured while retrieving this image.")
                    await session.close()
    @find.command(name='more', help="Command used to find more images for the same query.")
    async def find_more(self, ctx, *, arg):
        pass
    @commands.command(name='select', help="Command used to select one of the images for editing.")
    async def select(self, ctx, choice: int):
        if self.img_list is not None:
            if choice > 0 and choice + 1 <= self.result_count:
                # +1 and -1 are used in this section of the code to account for the fact that users are
                # likely to enter numbers from 1 to 5 rather than 0 to 4 (max list range)
                if self.img_list[choice - 1] is not None: 
                    self.selected_image = self.img_list[choice - 1]
                    self.selected_image.seek(0) #The seek method is used in case the file was sent before. This would mess with the seek position of the file object
                    await ctx.send("Image number " + str(choice) + " was successfully selected.")
                else: 
                    await ctx.send("An unexpected error occured while retrieving this image. Please select another.")
            else:
                await ctx.send("Please enter a valid choice from between 1 to " + str(self.result_count) + ".")
        else:
            await ctx.send("You need to use the !find command to search for a list of images before you can use this command.")
    @commands.command(name='upload', help="""Command that can be used to upload an image to be edited.
                                            Please upload only a single image for editing.
                                            If multiple images are uploaded, only the first image is selected 
                                            for editing. Only .jpg, .jpeg and .png files are currently supported.""")
    async def upload(self, ctx):
        attachment = None
        accepted_extension_list = ['.jpg', '.jpeg', '.png']
        if len(ctx.message.attachments) > 0:
            attachment = ctx.message.attachments[0]
            print("done")
        else:
            await ctx.send("You need to upload an attachment when using this command")
            return
        for extension in accepted_extension_list:
            if attachment.filename.endswith(extension):
                image_bytes = BytesIO()
                await attachment.save(image_bytes)
                self.selected_image = image_bytes
                print(self.selected_image)
                await ctx.send("Image upload successful.")
                return
        await ctx.send("This filename extension is not supported.")
    @commands.command(name='show', help="Command used to show the currently selected image.")
    async def show(self, ctx):
        if self.selected_image is not None:
            print(self.selected_image)
            await ctx.send(file=discord.File(self.selected_image, 'selected_image.jpg'))
            self.selected_image.seek(0)
        else:
            await ctx.send("You need to select an image before using this command.")

    @commands.command(name='edit', help="""Command used to load the image editor. An image needs to be
                                        selected before using this command. You will be unable to use the 
                                        query and find commands once you use this command.""")
    async def edit(self,ctx):
        if self.selected_image is not None:
            #self.bot.unload_extension(f'cogs.query')
            self.bot.load_extension(f'cogs.editor')
            await ctx.send("""The editor has been loaded. You can use commands !add caption top or !add whitespace top to edit your image.""")
        else:
            await ctx.send("You need to select an image before you can edit it.")
    def set_query(self, query):
        """ Checks the entered query paramater for errors and for whether it is identical
        to the current parameter"""
        if len(query.strip()) > 100: pass # We enforce a hard limit of 100 characters on search queries.
        elif self.query == query:
            pass
        else:
            self.query = query
            self.params['q'] = self.query
    def set_result_count(self, result_count):
        if result_count > 5: pass   # We enforce a 5 image limit on results 
                                    # to prevent one user from taking up too much bandwith
        else: self.result_count = result_count 
    def get_selected_image(self):
        return self.selected_image
def setup(bot):
    bot.add_cog(Query(bot))