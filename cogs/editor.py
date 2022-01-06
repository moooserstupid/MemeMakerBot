import discord
from discord.ext import commands
import asyncio
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import copy 
import io

class WhiteSpace(Enum):
    TOP = 1
    BOT = 2
    TOPBOT = 3
    NONE = 4

from discord.ext.commands.core import command
class Editor(commands.Cog):
    """Class that defines an image editor object
    The user can call the create command directly. However they need to add the 
    image_object(using the choose parameter) and thetop_text bottom_text paramters 
    at least to change the image. We have default values for all other parameters but
    the user has the option to change all of them or to reset their changes using commands.
    Also add the ability for the user to undo and redo the changes they have made to the image.
    """
    def __init__(self, bot):
        self.bot = bot
        #with Image.open('images/1.jpg') as img:
        query_instance = bot.get_cog('Query')
        if query_instance is not None: 
            self.original_image_object = query_instance.get_selected_image()
            #bot.unload_extension(f'cogs.query')
        self.new_image_object = None
        self.image_object_edit_history = None

        self.top_text = ""
        self.bottom_text = ""
        self.align_type = 'center'
        self.font_type = 'impact'
        self.text_size = 42
        self.text_color = 'white'
        self.text_outline_color = 'black'
        self.text_ouline_size = 2

        self.whitespace = WhiteSpace.NONE
        self.whitespace_ratio = 0.25

    # @commands.group(invoke_without_command=True)
    # async def add(self, ctx):
    #     await ctx.send("Works!")

    @commands.group(name='caption', invoke_without_command=True)
    async def add_caption(self, ctx):
        await ctx.send("Double Works!")
    @add_caption.command(name='top', help="""Command used to add a text caption to the bottom of a selected image.
                      If the text format settings have not been changed the default formatting will be used.""")
    async def add_caption_top(self, ctx, *, arg):
        if len(arg) < 100:
            self.top_text = arg
            #await ctx.send("It worked")
            await self.edit_image()
            await self.show_modified_image(ctx)
        else:
            await ctx.send("The text you entered was too long. The bot has a limit of 100 characters for captions.")
    @add_caption.command(name='bot', help="""Command used to add a text caption to the bottom of a selected image.
                      If the text format settings have not been changed the default formatting will be used.""")
    async def add_caption_bottom(self, ctx, *, arg):
        if len(arg) < 100:
            self.bottom_text = arg
            await self.edit_image()
            await self.show_modified_image(ctx)
        else:
            await ctx.send("The text you entered was too long. The bot has a limit of 100 characters for captions.")
    
    @commands.group(name='whitespace', invoke_without_command=True)
    async def add_whitespace(self, ctx):
        pass
    @add_whitespace.command(name='top', help="""Command used to add whitespace to the top of a selected image. You can also define the ratio of the whitespace to the image when using this command.""")
    async def add_whitespace_top(self, ctx, *ratio: float):
        if len(ratio) > 1:
            await ctx.send("Incorrect parameter. Please try again.")
            return
        elif len(ratio) == 1:
            if ratio[0] < 1:
                self.whitespace_ratio = ratio[0] 
                await ctx.send("Whitespace ratio set to " + str(ratio[0]))
            else:
                await ctx.send("Incorrect parameter. Please try again.")
        if self.whitespace == WhiteSpace.NONE:
            self.whitespace = WhiteSpace.TOP
        elif self.whitespace == WhiteSpace.BOT:
            self.whitespace = WhiteSpace.TOPBOT 
        await self.edit_image()
        await self.show_modified_image(ctx)   
    @add_whitespace.command(name='bot',
                      help="""Command used to add whitespace to the bottom of a selected image.
                      You can also define the size of the whitespace as an optional parameter
                      when using this command. The default ratio of the image with whitespace
                      to the original image is 0.25""")
    async def add_whitespace_bot(self, ctx, *ratio: float):
        if len(ratio) > 1:
            await ctx.send("Incorrect paramter. Please try again.")
            return
        elif len(ratio) == 1:
            if ratio[0] < 1:
                self.whitespace_ratio = ratio[0] 
                await ctx.send("Whitespace ratio set to " + str(ratio[0]))
            else:
                await ctx.send("Incorrect parameter. Please try again.")
                
        if self.whitespace == WhiteSpace.NONE:
            self.whitespace = WhiteSpace.BOT
        elif self.whitespace == WhiteSpace.TOP:
            self.whitespace = WhiteSpace.TOPBOT 
        print(self.whitespace)
        await self.edit_image()
        await self.show_modified_image(ctx) 
    
    @commands.group(name='text', invoke_without_command=True)
    async def change_text(self, ctx):
        pass
    @change_text.command(name='font', 
                      help="""Command used to change the font used in the captions. 
                      The default font is impact. Use the show_font_examples command to check out the other
                      available fonts.""")
    async def change_text_font(self, ctx, arg):
        pass
    @change_text.command(name='size',
                      help="""Command used to define the size of the caption text. 
                        The default size is 42. The max size is 60.""")
    async def change_text_size(self, ctx, size: int):
        if size <= 60:
            self.text_size = size
            await ctx.send("Text size changed to " + str(self.text_size) + ".")
            await self.edit_image()
            await self.show_modified_image(ctx)
    @change_text.command(name='color',
                      help="""Command used to change the color of the caption text. Use the !show colors command to get the list of all available colors.""")
    async def change_text_color(self, ctx, arg: str):
        accepted_colors = ['white', 'black', 'red', 'green', 'blue', 'orange', 'purple']
        if arg in accepted_colors:
            self.text_color = arg
            await ctx.send("Text color changed to " + arg + ".")
            await self.edit_image()
            await self.show_modified_image(ctx)
        else:
            await ctx.send("Invalid color enter. Use the !show colors command to get a list of the supported colours.")
    @change_text.group(name='outline', invoke_without_command=True)
    async def change_text_outline(self, ctx):
        pass
    @change_text_outline.command(name='color', help="""Command used to change the color of the text outline. The default color is black. You can use or !text outline none !text outline color none to have no outline. Use the !show colors command to get the list of all available colors.""")
    async def change_text_outline_color(self, ctx, arg: str):
        accepted_colors = ['white', 'black', 'red', 'green', 'blue', 'orange', 'purple']
        if arg in accepted_colors:
            self.text_color = arg
            await ctx.send("Text color changed to " + arg + ".")
            await self.edit_image()
            await self.show_modified_image(ctx)
        else:
            await ctx.send("Invalid color enter. Use the !show colors command to get a list of the supported colours.")
    @change_text_outline.command(name='size', help="""Command used to change the size of the text oultine.
                                        The default value is 2. The max value is 10""")
    async def change_text_outline_size(self, ctx, size: int):
        if size <= 10:
            self.text_ouline_size = size
            await self.edit_image()
            await self.show_modified_image(ctx)
        else:
            await ctx.send("Invalid size value entered. The maximum value you can enter is 10.")
    @change_text.command(name='align', help="""Command used to change the type of the align used. Example: !text align left""")
    async def change_text_align_type(self, ctx, arg):
        align_type_list = ['left', 'center', 'right']
        if arg in align_type_list:
            self.align_type = arg
            await self.edit_image()
            await self.show_modified_image(ctx)
        else:
            await ctx.send("Incorrect parameter. Text can be aligned left, center, or right.")
    #@commands.group(name='whitespace' ,invoke_without_command=True)
    # async def change_whitespace(self, ctx):
    #     pass
    # @change_whitespace.group(name='size')
    # async def change_whitespace_size(self, ctx):
    #     pass
    # @change_whitespace_size.command(name='top', help="""Command used to change the size of the top whitespace.""")
    # async def change_whitespace_size_top(self, ctx, *, args):
    #     await ctx.send("change_whitespace_size_top")
    # @change_whitespace_size.command(name='bot', help="""Command used to change the size of the bot whitespace.""")
    # async def change_whitespace_size_bot(self, ctx, *, args):
    #     await ctx.send("change_whitespace_size_bot")
    # @commands.command()
    # async def undo(self):
    #     pass
    # @commands.command()
    # async def redo(self):
    #     pass
    # @commands.command()
    # async def change_image(self):
    #     pass
    @commands.group(invoke_without_command=True)
    async def reset(self, ctx):
        self.top_text = ""
        self.bottom_text = ""
        self.align_type = 'center'
        self.font_type = 'arial'
        self.text_size = 42
        self.text_color = 'white'
        self.text_outline_color = 'black'
        self.text_ouline_size = 2
        self.whitespace = WhiteSpace.NONE
        self.whitespace_ratio = 0.25
        self.new_image_object = None
    @reset.command()
    async def format(self, ctx):
        self.top_text = ""
        self.bottom_text = ""
        self.align_type = 'center'
        self.font_type = 'impact'
        self.text_size = 42
        self.text_color = 'white'
        self.text_outline_color = 'black'
        self.text_ouline_size = 2
        self.whitespace = WhiteSpace.NONE
        self.whitespace_ratio = 0.25
    @reset.command()
    async def image(self,ctx):
        self.original_image_object = None
    @commands.group(invoke_without_command=True)
    async def show_image(self, ctx):
        pass
    @show_image.command(name='original')
    async def show_original_image(self, ctx):
        self.original_image_object.seek(0)
        await ctx.send(file=discord.File(self.original_image_object, 'original_image.jpg'))

    @show_image.command(name='new')
    async def show_modified_image(self, ctx):
        if self.new_image_object is not None:
            self.new_image_object.seek(0)
            await ctx.send(file=discord.File(self.new_image_object, 'new_image.jpg'))
        else:
            await ctx.send("The image has not been modified. Use !show original to display the image.")
    
    async def edit_image(self):
        """Function used to edit the images. Takes the original image and applies edits according to the given parameters."""
        def add_whitespace_func():
            """ Adds a whitespace to the top of the image object and then returns it """
            new_image_layer = None
            whitespace_height = int(img.height * self.whitespace_ratio)
            if self.whitespace == WhiteSpace.TOPBOT:
                new_image_size = (img.width, img.height + 2 * whitespace_height)
                new_image_layer = Image.new('RGB', new_image_size, (255,255,255))
                new_image_layer.paste(img, (0, whitespace_height))
            elif self.whitespace == WhiteSpace.BOT:
                new_image_size = (img.width, img.height + whitespace_height)
                new_image_layer = Image.new('RGB', new_image_size, (255,255,255))
                new_image_layer.paste(img, (0, 0))
            else:
                new_image_size = (img.width, img.height + whitespace_height)
                new_image_layer = Image.new('RGB', new_image_size, (255,255,255))
                new_image_layer.paste(img, (0, whitespace_height))
            return new_image_layer
        def drawText(text, pos):
            def findTextSlices(text):
                """ If the input text is too long, it could go over the sides of the image. This function slices the 
                    text into managable chunks at the spaces b/w words """
                
                # The text is first split at spaces
                wordsInText = text.split()
                list = []
                sliceList = []
                for word in wordsInText:
                    # Then the text is recreated one by one 
                    # (draw returns a tuple of length 2) 
                    widthOfUpdatedSlice = draw.textsize((' '.join(list)) + word, font)[0]
                    if  widthOfUpdatedSlice < img.width:
                        # If this recreated text does not go over image width
                        # add it to the current slice
                        list.append(word)
                    else:
                        # If it does go over, we know where to cut
                        
                        # Create a new slice
                        sliceList.append(list[:])  # list[:] creates a shallow copy
                        # Clear the list to create new current slice
                        list.clear() 
                        list.append(word)
                sliceList.append(list)
                return sliceList
            
            def drawTextWithOutline(text, x, y):
                draw.multiline_text((x, y), text, self.text_color, font=font, align=self.align_type, 
                                    stroke_width=self.text_ouline_size, stroke_fill='black')
                return

            w, h = draw.textsize(text, font)

            # If the given text does not fit in the width of the image
            textList = []
            if w > img.width:
                #Find the slices of the text
                textList.extend(findTextSlices(text))
                
            else:
                textList.append(text)
            #print(textList)
            lastY = -h
            if pos == "b":
                lastY = img.height - h * (len(textList) + 1) - 10
            textSlice = []
            text_multiline = None
            for i in range(0, len(textList)):
                # The findTextSlices function returns a word list. We have to append it
                # to get the text back and we add a "\n" at the slices.
                if len(textList) > 1 : textSlice.append(str(' '.join(textList[i])))
                else: text_multiline = textList[i]
            if text_multiline is None: text_multiline = '\n'.join(textSlice)
            w, h = draw.textsize(text_multiline, font)
            x = img.width/2 - w/2
            y = lastY + h
            drawTextWithOutline(text_multiline, x, y)
            lastY = y
            return
        img_bytes = copy.copy(self.original_image_object)
        img_bytes.read()
        img = Image.open(img_bytes)
        if self.whitespace != WhiteSpace.NONE: img = add_whitespace_func()
        
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_type, self.text_size)
        drawText(self.top_text, "t")
        drawText(self.bottom_text, "b")
        bytes_object = io.BytesIO()
        img.save(bytes_object, format='jpeg')
        self.new_image_object = bytes_object
    
def setup(bot):
    bot.add_cog(Editor(bot))
