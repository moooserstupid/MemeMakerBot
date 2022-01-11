"""Query cog module.

The query cog contains methods and attributes used to async query the
Bing Image Search API V7.0 for images based on a query string and some
defined parameters.  
"""

# Standard Library imports
import aiohttp
from io import BytesIO
import os
from dotenv import load_dotenv
# Discord and discord extension library imports
import discord
from discord.ext import commands


class Query(commands.Cog):
    """Class that defines an image request cog.

    Creates an image search request and async sends it to the Bing Image
    Search V7.0 API in response to user request. Must be loaded before
    the Editor cog in order to provide it with the selected image.
    """

    def __init__(
            self, bot, mkt='en-US', result_count=5, 
            moderation='Moderate', minDim=(120, 120), 
            maxDim=(1024, 1024)):
        """Init method for the Query cog"""
        self.bot = bot

        load_dotenv()
        self.api_key = os.getenv('BS_API_KEY')
        self.endpoint = os.getenv('END_POINT') + "v7.0/images/search"
        
        self.query = None
        self.market = mkt
        self.result_count = result_count
        self.offset = 0
        self.moderation = moderation
        self.minDim = minDim
        self.maxDim = maxDim

        self.params = {
            'q': self.query, 'mkt': self.market, 'count': self.result_count, 
            'offset': self.offset,'safeSearch': moderation,
            'minWidth': minDim[0], 'minHeight': minDim[1], 
            'maxWidth': maxDim[0], 'maxHeight': maxDim[1]
        }
        
        self.url_list = None
        self.img_list = None
        self.selected_image = None

    async def cog_check(self, ctx):
        """Cog level context checker.
        
        Is called and evaluated whenever a command is mentioned.
        Checks whether the command has been used in a dm channel.
        """
        if isinstance(ctx.channel, discord.DMChannel): return True
        else: return False

    @commands.group(name='find', 
        help="Finds and returns images based on a descriptive query.",
        invoke_without_command=True)
    async def find(self, ctx, *, arg: str):
        """ Finds images based on the query param """

        headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        self.query = arg
        self.update_params()
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
                                if image_bytes is not None:
                                    await ctx.send(file=discord.File(image_bytes, str(i + 1) + '.jpg'))
                                print(image_bytes)
                                self.img_list.append(image_bytes)
                            else:
                                self.img_list.append(None)
                                await ctx.send("An unexpected error occured while retrieving this image.")
                    await session.close()
   
    @find.command(name='more', 
        help="Command used to find more images for the same query.")
    async def find_more(self, ctx, *, arg):
        pass
    
    @commands.command(name='select', help="Command used to select one of the images for editing.")
    async def select(self, ctx, choice: int):
        if self.img_list is not None:
            if choice > 0 and choice <= self.result_count:
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
    
    @commands.command(name='upload', 
        help="Command that can be used to upload an image to be edited."
        " Please upload only a single image for editing."
        " If multiple images are uploaded, only the first image will be selected" 
        " for editing. Only .jpg, .jpeg and .png files are currently supported.")
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

    @commands.command(name='edit', 
        help="Command used to load the image editor. An image needs to be"
        " selected before using this command. You will be unable to use the" 
        " query and find commands once you use this command.")
    async def edit(self,ctx):
        if self.selected_image is not None:
            #self.bot.unload_extension(f'cogs.query')
            self.bot.load_extension(f'cogs.editor')
            await ctx.send("The editor has been loaded. You can use commands like !caption top or !whitespace top to edit your image.")
        else:
            await ctx.send("You need to select an image before you can edit it.")
    
    def update_params(self):
        """Updates the parameter string. 
        
        Checks the entered parameters for errors and updates the params
        attribute if none are found.
        """
        if len(self.query.strip()) > 100: return # We enforce a hard limit of 100 characters on search queries.
        if self.result_count > 5: return   # We enforce a 5 image limit on results 
                                    # to prevent one user from taking up too much bandwith
        self.params = {'q': self.query, 'mkt': self.market, 'count' : self.result_count, 'offset': self.offset,'safeSearch' : self.moderation,
        'minWidth' : self.minDim[0], 'minHeight' : self.minDim[1], 'maxWidth' : self.maxDim[0], 'maxHeight' : self.maxDim[1]}
    
    def get_selected_image(self):
        """Returns selected image attribute.

        Used by the Editor cog to retrieve the selected image from the
        Query cog. 
        """
        return self.selected_image


def setup(bot):
    bot.add_cog(Query(bot))