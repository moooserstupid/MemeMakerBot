from PIL import Image, ImageDraw, ImageFont
from enum import Enum

#suggestions: 
#1: institute a max character limit
#2: wrap this file in a function
#3: add a file not found return message
#4: Add the option to justify left or right
#5: Add the option to change the colour of the image
#6: Add the option to justify text left or right instead of always being in the center
#7: Add the option to change the text colour.
class WhiteSpace(Enum):
    TOP = 1
    BOT = 2
    TOPBOT = 3
    NONE = 4

def add_caption(img, toptext, bottext, fonttype, text_align = 'center', outline_size = 2, fontsize = 42, 
                whitespace = WhiteSpace.BOT, whitespace_ratio = 0.25):
    def add_whitespace():
        """ Adds a whitespace to the top of the image object and then returns it """
        new_image_layer = None
        whitespace_height = int(img.height * whitespace_ratio)
        if whitespace == WhiteSpace.TOPBOT:
            new_image_size = (img.width, img.height + 2 * whitespace_height)
            new_image_layer = Image.new('RGB', new_image_size, (255,255,255))
            new_image_layer.paste(img, (0, whitespace_height))
        elif whitespace == WhiteSpace.BOT:
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
            draw.multiline_text((x, y), text, (255,255,255), font=font, align=text_align, stroke_width=outline_size, stroke_fill='black')
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
        print("y" + str(y))
        drawTextWithOutline(text_multiline, x, y)
        print(text_multiline)
        lastY = y
        return
    print(img)
    #if whitespace != WhiteSpace.NONE: img = add_whitespace()
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(fonttype, fontsize)
    drawText(toptext, "t")
    drawText(bottext, "b")
    return img
if __name__=='__main__':
    with Image.open('images/1.jpg') as img:
        img = add_caption(img, "Something", "something else", "fonts/arial.ttf", fontsize=42, whitespace=WhiteSpace.TOPBOT)
        img.save("out.jpg")
    