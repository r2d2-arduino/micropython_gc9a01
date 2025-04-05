"""
GC9A01FB_SPI v 0.1.3
Display controller driver for GC9A01 (with Framebuffer)

Display: GC9A01
Connection: 4-line SPI
Color: 16-bit
Controllers: Esp32-S3, Esp32-S2, RP2-family
 
Project path: https://github.com/r2d2-arduino/micropython_gc9a01
MIT License

Author: Arthur Derkach
"""

from machine import Pin
from time import sleep_ms
from framebuf import FrameBuffer, RGB565

class GC9A01FB_SPI( FrameBuffer ):
    
    def __init__( self, spi, cs_pin, dc_pin, rst_pin, width = 240, height = 240 ):
        """ Constructor
        Args
        spi  (object): SPI
        cs_pin   (int): CS pin number (Chip Select)
        dc_pin   (int): DC pin number (command/parameter mode)
        rst_pin  (int): RST pin number (Reset)
        width   (int): Screen width in pixels (less)
        height  (int): Screen height in pixels        
        """ 
        self.spi = spi
        self.rst = Pin( rst_pin, Pin.OUT, value = 0 )
        self.dc  = Pin( dc_pin,  Pin.OUT, value = 0 )
        self.cs  = Pin( cs_pin,  Pin.OUT, value = 1 )
        
        self._font = None
        self._rotation = 0
        
        self.width  = width
        self.height = height        
        
        # Buffer initialization
        self.buffsize = width * height * 2
        self.buffer = bytearray(self.buffsize)
        super().__init__(self.buffer, self.width, self.height, RGB565)        

        self.init()  
    
    def init( self ):
        self.reset()
        
        self.write_command( 0xFE ) # Inter Register Enable 1
        self.write_command( 0xEF ) # Inter Register Enable 2

        self.write_command_data(0xB6, bytearray([ 0x00, 0x00 ])) # Display Function Control
        self.write_command_data(0x3A, bytearray([ 0x55 ]))  # Pixel Format Set: 55 = 16-bit, 66 = 18-bit

        self.write_command_data(0xC3, bytearray([ 0x13 ])) # Vreg 1a voltage Control
        self.write_command_data(0xC4, bytearray([ 0x13 ])) # Vreg 1b voltage Control
        self.write_command_data(0xC9, bytearray([ 0x22 ])) # Vreg 2a voltage Control

        self.write_command_data(0xF0,
                bytearray([ 0x45, 0x09, 0x08, 0x08, 0x26, 0x2A ]) ) # Set Gamma 1
        self.write_command_data(0xF1,
                bytearray([ 0x43, 0x70, 0x72, 0x36, 0x37, 0x6F ]) ) # Set Gamma 2
        self.write_command_data(0xF2,
                bytearray([ 0x45, 0x09, 0x08, 0x08, 0x26, 0x2A ]) ) # Set Gamma 3
        self.write_command_data(0xF3,
                bytearray([ 0x43, 0x70, 0x72, 0x36, 0x37, 0x6F ]) ) # Set Gamma 4

        self.write_command_data(0xE8, bytearray([ 0x34 ])) # Frame Rate

        self.write_command_data(0x66,
                bytearray([ 0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00 ]) )
        self.write_command_data(0x67,
                bytearray([ 0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98 ]) )

        self.write_command( 0x34 ) # Tearing Effect Line Off
        self.write_command( 0x21 ) # Display Inversion On
        self.write_command( 0x11 ) # Sleep Out
        sleep_ms(5)

        self.set_rotation( 0 )
        
        self.write_command( 0x29 ) # Display On         
            
    def reset( self ):
        """ Display reset """
        self.rst.value( 0 )
        sleep_ms( 10 )
        self.rst.value( 1 )
        sleep_ms( 10 )
        
    def write_command( self, command ):
        """ Sending a command to the display
        Args
        cmd (int): Command number, example: 0x2E
        """
        self.cs.value( 0 )
        self.dc.value( 0 )        
        self.spi.write( bytearray( [ command ] ) )
        self.cs.value( 1 )

    def write_data( self, data ):
        """ Sending data to display
        Args
        data (int): Data byte, example: 0xF8
        """
        self.cs.value( 0 )
        self.dc.value( 1 )
        self.spi.write( data )
        self.cs.value( 1 )
        
    def read_data( self, num_bytes = 1 ):
        """ Reading data from display
        Return (bytes): Data bytes, example: 0xF8
        """
        self.cs.value( 0 )
        self.dc.value( 1 )
        response = self.spi.read( num_bytes )
        self.cs.value( 1 )
        return response
        
    def write_command_data( self, command, data ):
        self.cs.value( 0 )

        self.dc.value( 0 )
        self.spi.write( bytearray( [ command ] ) )

        self.dc.value( 1 )
        self.spi.write( data )

        self.cs.value( 1 )        
        
    def read_command( self, command, num_bytes = 1 ):
        """ Reading answer from display """
        self.write_command( command )
        sleep_ms(10)     
        return self.read_data( num_bytes )

    
    def set_rotation(self, rotation = 0):
        """
        Set orientation of Display
        Params
        rotation (int):  0 = 0 degree, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
        """
        if rotation > 3 or rotation < 0:
            print("Incorrect rotation value")
            return False
        
        old_rotation = self._rotation
        self._rotation = rotation

        if rotation == 0: # 0 deg
            self.memory_access_control(0, 1, 0, 0, 1, 0)
        elif rotation == 1: # 90 deg
            self.memory_access_control(0, 0, 1, 0, 1, 0)
        elif rotation == 2: # 180 deg
            self.memory_access_control(1, 0, 0, 0, 1, 0)
        elif rotation == 3: # 270 deg
            self.memory_access_control(1, 1, 1, 0, 1, 0)

        # Change height <-> width for 90 and 270 degrees
        if (( rotation & 1) and not (old_rotation & 1)
            or not ( rotation & 1) and (old_rotation & 1) ):
            height = self.height
            self.height = self.width
            self.width = height
            
            super().__init__(self.buffer, self.width, self.height, RGB565)
            
        self.set_window(0, 0, self.width - 1, self.height - 1)

    def memory_access_control(self, my = 0, mx = 0, mv = 0, ml = 0, bgr = 0, mh = 0):
        """ MADCTL. This command defines read/write scanning direction of frame memory. """
        self.write_command(0x36)
        data =  0
        data += mh << 2 # Display Data Latch Data Order
        data += bgr<< 3 # RGB-BGR Order: 0 - RGB, 1 - BGR
        data += ml << 4 # Line Address Order
        data += mv << 5 # Row/Column exchange
        data += mx << 6 # Column address order
        data += my << 7 # Row address order
        #print(data)
        self.write_data(bytearray([data]))

    def invert_display(self, on = True):
        """ Enables or disables color inversion on display.
        Args
        on (bool): True = Enable inversion, False = Disable inversion
        """
        if bool(on):
            self.write_command( 0x21 )  
        else:
            self.write_command( 0x20 )

    def tearing_effect(self, on = True):
        """ Activate "Tearing effect"
        Args
        on (bool): True = Enable effect, False = Disable effect
        """        
        if bool(on):
            self.write_command( 0x35 )
        else:
            self.write_command( 0x34 )

    def idle_mode(self, on = True):
        """ Enables or disables idle mode on display.
        Args
        on (bool): True = Enable idle mode, False = Disable idle mode
        """
        if bool(on):
            self.write_command( 0x39 )
        else:
            self.write_command( 0x38 )

    def set_brightness(self, value ):
        """ Set brightness value ( No effect )
        Args
        value (int): brightness 0..255
        """
        if 0 <= value < 256:
            self.write_command( 0x51 )
            self.write_data( bytearray([ value ]) )
        else:
            print('Error value in def set_brightness')
            print(value)
            
    def vert_scroll(self, top_fix: int, scroll_height: int, bot_fix: int):
        """ Vertical scroll settings
        Args
        top_fix (int): Top fixed rows
        scroll_height (int): Scrolling height rows
        bot_fix (int): Bottom fixed rows
        
        top_fix + bot_fix + scroll_height - must be  equal height of screen
        """
        screen_height = self.height
        if self._rotation & 1:
            screen_height = self.width
            
        sum = top_fix + bot_fix + scroll_height
        
        if sum == screen_height:
            self.write_command( 0x33 )
            #Top fixed rows
            self.write_data( bytearray([ (top_fix >> 8) & 0xFF, top_fix & 0xFF ]) )
            #Scrolling height rows
            self.write_data( bytearray([ (scroll_height >> 8) & 0xFF, scroll_height & 0xFF ]) )
            #Bottom fixed rows
            self.write_data( bytearray([ (bot_fix >> 8) & 0xFF, bot_fix & 0xFF ]) )
            
        else:
            print('Incorrect sum in vertical scroll ', sum, ' <> ', screen_height)
            
    def vert_scroll_start_address(self, start = 0):
        """ Set vertical scroll start address, and run scrolling
        Args
        start (int): start row        
        """
        self.write_command( 0x37 )
        self.write_data( bytearray([ (start >> 8) & 0xFF, start & 0xFF ]) )
        
    def scroll(self, delay = 5):
        """ Scrolling on the screen at a given speed.
        Args
        delay (int): Delay between scrolling actions
        """
        height = self.height
        if self._rotation & 1:
            height = self.width
            
        for y in range(height):
            self.vert_scroll_start_address(y + 1)
            sleep_ms(delay)        

    @micropython.viper
    def set_window(self, x0:int, y0:int, x1:int, y1:int):
        """ Sets the starting position and the area of drawing on display
        Args
        x0 (int): Start X position  ________
        y0 (int): Start Y position  |s---> |
        x1 (int): End X position    ||     |    
        y1 (int): End Y position    |v____e|  
        """        
        dc  = self.dc
        spi = self.spi
        
        dc.value(0) # command mode
        spi.write(b'\x2a')
        dc.value(1) # data mode
        spi.write(bytearray([(x0 >> 8) & 0xff, x0 & 0xff, (x1 >> 8) & 0xff, x1 & 0xff]))
        
        dc.value(0) # command mode
        spi.write(b'\x2b')
        dc.value(1) # data mode
        spi.write(bytearray([(y0 >> 8) & 0xff, y0 & 0xff, (y1 >> 8) & 0xff, y1 & 0xff]))
        
        #dc.value(0) # command mode
        #spi.write(b'\x2c')
        #dc.value(1)    


    """ IMAGE AREA """
    @micropython.viper
    def draw_raw_image(self, filename, x:int, y:int, width:int, height:int):
        """ Draw RAW image (RGB565 format) on display
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        width (int) : Width of raw image
        height (int) : Height of raw image
        """
        f = open(filename, 'rb')
        buffer = ptr16(self.buffer)
        row_width = width * 2
        screen_width = int(self.width)
        
        for row in range(height):
            image_data = f.read(row_width)
            image_buffer = ptr16(image_data)
            offset = x + (row + y) * screen_width

            col = 0
            while col < width:
                buffer[offset + col] = image_buffer[col]
                col += 1

        f.close()        
        
    def draw_bmp(self, filename, x = 0, y = 0):
        """ Draw BMP image on display
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        """
        f = open(filename, 'rb')
        
        if f.read(2) == b'BM':  #header
            dummy    = f.read(8) #file size(4), creator bytes(4)
            offset   = int.from_bytes(f.read(4), 'little')
            dummy    = f.read(4) #hdrsize
            width    = int.from_bytes(f.read(4), 'little')
            height   = int.from_bytes(f.read(4), 'little')
            planes   = int.from_bytes(f.read(2), 'little')
            depth    = int.from_bytes(f.read(2), 'little')
            compress = int.from_bytes(f.read(4), 'little')

            if planes == 1 and depth == 24 and compress == 0: #compress method == uncompressed
                rowsize = (width * 3 + 3) & ~3
                
                if height < 0:
                    height = -height

                frameWidth, frameHeight = width, height
                
                if x + frameWidth > self.width:
                    frameWidth = self.width - x
                    
                if y + frameHeight > self.height:
                    frameHeight = self.height - y

                f.seek(offset)
                
                self._send_bmp_to_framebuff(f, x, y, frameHeight, frameWidth, offset, rowsize)
                
        f.close()
            
    @micropython.viper           
    def _send_bmp_to_framebuff( self, f, x: int, y: int, frameHeight: int, frameWidth: int, offset: int, rowsize: int ):
        """ Send bmp-file to display
        Args
        f (object File) : Image file
        frameHeight (int): Height of image frame
        frameWidth (int): Width of image frame
        offset (int): Internal byte offset of image-file
        rowsize (int): Internal byte rowsize of image-file        
        """
        buffer = ptr8(self.buffer)
        screen_width = int(self.width) 
        main_offset = (y * screen_width + x) * 2
        buffsize = int(self.buffsize)
        
        for row in range(frameHeight):
            buff_offset = row * screen_width * 2 + main_offset
            
            # Start position of new row in image-file
            pos = offset + row * rowsize
                                    
            if int(f.tell()) != pos:
                f.seek(pos)
            
            # Reading one row from image-file
            bgr_row = f.read(3 * frameWidth)
            image_buffer = ptr8(bgr_row)
            
            for col in range(frameWidth):
                #Getting color bytes
                red   = image_buffer[ col * 3     ]
                green = image_buffer[ col * 3 + 1 ]
                blue  = image_buffer[ col * 3 + 2 ]
                
                # Sending new bit-masks directly to registers
                buff_i = buffsize - (frameWidth - col) * 2 - buff_offset
                buffer[buff_i] = (blue & 0xF8 ) | ( green & 0xFC ) >> 5  # color hi
                buffer[buff_i + 1] = (green & 0x1C ) << 3 | red >> 3  # color low
        
    """ TEXT AREA """
        
    def set_font(self, font):
        """ Set font for text
        Args
        font (module): Font module generated by font_to_py.py
        """
        self._font = font
    
    def draw_text( self, text, x, y, color ):
        """ Draw text on display
        Args
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        """
        screen_height = self.height
        screen_width = self.width
        x_start = x
        
        font = self._font        
        if font == None:
            print("Font not set")
            return False        
        
        for char in text:
            if char == "\n": # New line
                x = screen_width
                continue
            
            if char == "\t": #replace tab to space
                char = " "                
            
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width  = glyph[2]
            
            if x + glyph_width >= screen_width: # End of row
                break
            
            self.draw_bitmap(glyph, x, y, color)
            x += glyph_width
    
    def draw_text_wrap(self, text, x, y, color):
        """ Draw text on display (wrapped version)
        Args
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        """
        def is_point_in_screen( x, y, cx, cy, radius ):
            """ Check is point in visibled part of screen
            Args
            x (int) : X position of point
            y (int) : Y position of point
            Return (bool): is in screen        
            """            
            return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
        
        
        def find_left_x( y, cx, cy, radius ):
            #print( y, cx, cy, radius )
            return round( cx - (radius**2 - (y - cy)**2)**0.5 )
        
        def find_rigth_x( y, cx, cy, radius ):
            return round( cx + (radius**2 - (y - cy)**2)**0.5 )        

        screen_height = self.height
        screen_width = self.width
        radius = screen_width // 2
        cx = screen_width // 2
        cy = screen_height // 2
        x_start = x
        left_x = find_left_x( y, cx, cy, radius )
        if x_start < left_x:
            x_start = left_x
        
        font = self._font        
        if font == None:
            print("Font not set")
            return False
        
        corr = 0
        for char in text:
            if char == "\n": # New line
                x = screen_width
                continue
            
            if char == "\t": #replace tab to space
                char = " "                
            
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width  = glyph[2]
            
            if not is_point_in_screen( x + glyph_width, y + corr, cx, cy, radius):
                #x = x_start
                y += glyph_height
                if y + glyph_height >= screen_height: # End of screen
                    break
                #print(y, cx, cy)

                if y > radius:
                    corr = glyph_height
                    
                x = find_left_x( y + corr, cx, cy, radius )
            #print(y, x)
            self.draw_bitmap(glyph, x, y, color)
            x += glyph_width        
  
    @micropython.viper
    def draw_bitmap(self, bitmap, x:int, y:int, color:int):
        """ Draw one bitmap on display
        Args
        bitmap (tuple) : Bitmap data [data, height, width]
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB565 2-byte color, example 0xF81F
        """
        data   = ptr8(bitmap[0]) #memoryview to glyph
        height = int(bitmap[1])
        width  = int(bitmap[2])
        screen_width  = int(self.width)
        
        buffer = ptr8(self.buffer)
        color_hi  = color & 0xFF
        color_low = (color >> 8) & 0xFF
        
        i = 0
        for h in range(height):
            ypos = (h + y) * screen_width * 2
            bit_len = 0
            while bit_len < width:
                byte = data[i]
                pos = ypos + (bit_len + x) * 2
                #Drawing pixels when bit = 1
                if (byte >> 7) & 1:                    
                    buffer[ pos     ] = color_hi
                    buffer[ pos + 1 ] = color_low        
                if (byte >> 6) & 1:                   
                    buffer[ pos + 2 ] = color_hi
                    buffer[ pos + 3 ] = color_low                    
                if (byte >> 5) & 1:                    
                    buffer[ pos + 4 ] = color_hi
                    buffer[ pos + 5 ] = color_low                      
                if (byte >> 4) & 1:                    
                    buffer[ pos + 6 ] = color_hi
                    buffer[ pos + 7 ] = color_low                    
                if (byte >> 3) & 1:                    
                    buffer[ pos + 8 ] = color_hi
                    buffer[ pos + 9 ] = color_low                     
                if (byte >> 2) & 1:                    
                    buffer[ pos + 10 ] = color_hi
                    buffer[ pos + 11 ] = color_low                     
                if (byte >> 1) & 1:                    
                    buffer[ pos + 12 ] = color_hi
                    buffer[ pos + 13 ] = color_low                     
                if byte & 1:                    
                    buffer[ pos + 14 ] = color_hi
                    buffer[ pos + 15 ] = color_low                     
                
                bit_len += 8
                i += 1
        
    @staticmethod
    def rgb(red, green, blue):
        """ Convert 8,8,8 bits RGB to 16 bits  """
        #return ( (red << 11) & 0xF800 | (green << 5) & 0x07E0 | blue & 0x001F )
        return ((blue & 0xf8) << 5 | (green & 0x1c) << 11 | (green & 0xe0) >> 5 | (red & 0xf8))
    
    def show(self):
        ''' Displays the contents of the buffer on the screen '''
        self.cs.value(0)
        self.dc.value(0) # Command mode
        self.spi.write(b'\x2c') # Memory write
        self.dc.value(1) # Data mode    
        self.spi.write( self.buffer )
        self.cs.value(1)
