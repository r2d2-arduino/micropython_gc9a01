"""
GC9A01_SPI v 0.1.3
Display controller driver for GC9A01

Display: GC9A01
Connection: 4-line SPI
Color: 16-bit
Controllers: Esp32-family, RP2-family
 
Project path: https://github.com/r2d2-arduino/micropython_gc9a01
MIT License

Author: Arthur Derkach
"""

from machine import Pin
from time import sleep_ms

class GC9A01_SPI():
    
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
        
        self.init()   
    
    def init( self ):
        """ Initial display settings """
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
        
    def write_command_data( self, command, data ):
        self.cs.value( 0 )

        self.dc.value( 0 )
        self.spi.write( bytearray( [ command ] ) )

        self.dc.value( 1 )
        self.spi.write( data )

        self.cs.value( 1 )        
        
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

        if   rotation == 0: # 0 deg
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
        
        dc.value(0) # command mode
        spi.write(b'\x2c')
        dc.value(1)
    
    def fill_rect( self, x, y, width, height, color ):
        """ Draw filled rectangle
        Args
        x (int): Start X position          xy----->
        y (int): Start Y position          |   w  .
        width (int): Width of rectangle  h |      .
        height (int): Height of rectangle   v.......
        color (int): RGB color
        """        
        color_bytes = [color & 0xff, (color >> 8) & 0xff]
        
        buffer = bytearray( color_bytes * width )
        
        self.cs.value(0)        
        self.set_window(x, y, x + width - 1, y + height - 1)
        
        for _ in range( height ):
            self.spi.write( buffer )
            
        self.cs.value(1)
        
    def fill(self, color):
        """ Fill whole screen
        Args
        color (int): RGB color
        """        
        self.fill_rect( 0, 0, self.width, self.height, color )
        
    
    def draw_vline(self, x, y, height, color, thickness = 1):
        """ Draw vertical line
        Args
        x (int): Start X position      xy
        y (int): Start Y position     h |   
        height (int): Height of line    v   
        color (int): RGB color
        thickness (int): thickness of line
        """        
        self.fill_rect(x, y, thickness, height, color)

    def draw_hline(self, x, y, width, color, thickness = 1):
        """ Draw horizontal line 
        Args
        x (int): Start X position          xy----->
        y (int): Start Y position              w
        width (int): Width of line            
        color (int): RGB color
        thickness (int): thickness of line
        """         
        self.fill_rect(x, y, width, thickness, color)
    
    def draw_rect(self, x, y, width, height, color, thickness = 1):
        """ Draw rectangle 
        Args  
        x (int): Start X position          xy----->
        y (int): Start Y position          |   w  .
        height (int): Height of line    h  |      .
        width (int): Width of square       v.......  
        thickness (int): thickness of line   
        color (int): RGB color
        """         
        self.fill_rect(x, y, width, thickness, color)
        self.fill_rect(x , y + thickness, thickness, height, color)
        self.fill_rect(x + thickness, y + height, width, thickness, color)        
        self.fill_rect(x + width, y, thickness, height, color)
        
    def draw_line(self, x0, y0, x1, y1, color):
        """ Draw line using Bresenham's Algorithm
        Args
        x0 (int): Start X position   s
        y0 (int): Start Y position    \
        x1 (int): End X position       \ 
        y1 (int): End Y position        e
        color (int): RGB color
        """
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        dc = self.dc
        spi = self.spi
        
        self.cs.value(0)
        
        color_bytes = bytearray([color & 0xff, (color >> 8) & 0xff])
        
        x0_bytes = bytearray([(x0 >> 8) & 0xff, x0 & 0xff, (x0 >> 8) & 0xff, x0 & 0xff])
        y0_bytes = bytearray([(y0 >> 8) & 0xff, y0 & 0xff, (y0 >> 8) & 0xff, y0 & 0xff])
        
        while True:
            #pixel(x0, y0, color)
            dc.value(0) # command mode
            spi.write(b'\x2a')
            dc.value(1) # data mode
            spi.write( x0_bytes )
            
            dc.value(0) # command mode
            spi.write(b'\x2b')
            dc.value(1) # data mode
            spi.write( y0_bytes )
            
            dc.value(0) # command mode
            spi.write(b'\x2c')
            dc.value(1) # data mode
            spi.write( color_bytes )
        
            if x0 == x1 and y0 == y1:
                break            
            
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
                x0_bytes = bytearray([(x0 >> 8) & 0xff, x0 & 0xff, (x0 >> 8) & 0xff, x0 & 0xff])
                
            if e2 < dx:
                err += dx
                y0 += sy
                y0_bytes = bytearray([(y0 >> 8) & 0xff, y0 & 0xff, (y0 >> 8) & 0xff, y0 & 0xff])
        

        self.cs.value(1)

    def draw_circle(self, x, y, radius, color, border = 1):
        """ Draw circle
        Args
        x (int): Start X position          
        y (int): Start Y position              
        radius (int): Radius of circle         
        border (int): border of circle   
        color (int): RGB color
        """
        if (x < 0 or y < 0 or x >= self.width or y >= self.height):
            print("Invalid params in draw_circle")
            return
        
        pixel = self.draw_pixel
        
        for r in range(radius - border, radius):
            # Bresenham algorithm
            x_pos = 0 - r
            y_pos = 0
            err = 2 - 2 * r
            while 1:
                pixel(x - x_pos, y + y_pos, color)
                pixel(x + x_pos, y + y_pos, color)
                pixel(x + x_pos, y - y_pos, color)
                pixel(x - x_pos, y - y_pos, color)
                
                e2 = err
                if (e2 <= y_pos):
                    y_pos += 1
                    err += y_pos * 2 + 1
                    if(0-x_pos == y_pos and e2 <= x_pos):
                        e2 = 0
                if (e2 > x_pos):
                    x_pos += 1
                    err += x_pos * 2 + 1
                if x_pos > 0:
                    break    
    
    def fill_circle(self, x, y, radius, color):
        """ Draw filled circle
        Args
        x (int): Start X position          
        y (int): Start Y position              
        radius (int): Radius of circle
        color (int): RGB color
        """
        color_bytes = [color & 0xff, (color >> 8) & 0xff]
        self.cs.value(0) 
        for p in range(-radius, radius + 1):
            # Calculating the horizontal line
            dx = round( (radius**2 - p**2)**0.5 )
            if dx > 0:                       
                self.set_window(x - dx, y + p, x + dx - 1, y + p)                
                self.spi.write( bytearray( color_bytes * 2 * dx ) )
                    
        self.cs.value(1)       
    
    @micropython.viper
    def draw_pixel(self, x:int, y:int, color:int):
        """ Draw one pixel on display
        Args
        x (int): X position on dispaly, example 100
        y (int): Y position on dispaly, example 200
        color (int): RGB color
        """        
        dc = self.dc
        spi = self.spi
        
        self.cs.value(0)
        dc.value(0) # command mode
        spi.write(b'\x2a')
        dc.value(1) # data mode
        spi.write(bytearray([(x >> 8) & 0xff, x & 0xff, (x >> 8) & 0xff, x & 0xff]))
        
        dc.value(0) # command mode
        spi.write(b'\x2b')
        dc.value(1) # data mode
        spi.write(bytearray([(y >> 8) & 0xff, y & 0xff, (y >> 8) & 0xff, y & 0xff]))
        
        dc.value(0) # command mode
        spi.write(b'\x2c')
        dc.value(1) # data mode
        spi.write(bytearray([color & 0xff, (color >> 8) & 0xff]))
        self.cs.value(1)

    """ IMAGE AREA """
    
    def draw_raw_image(self, filename, x, y, width, height):
        """ Draw RAW image (RGB565 format) on display
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        width (int) : Width of raw image
        height (int) : Height of raw image
        """
        f = open(filename, 'rb')

        self.cs.value(0)      
        self.set_window(x, y, x + width - 1, y + height - 1) # Set start position

        byte_width = width * 2
    
        for _ in range(height):
            self.spi.write( f.read(byte_width) )
                     
        self.cs.value(1)  # Chip disabled
        
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
                
                self.cs.value(0)
                self.set_window(x, y, x + frameWidth - 1, y + frameHeight - 1)
                
                self._send_bmp_to_display(f, frameHeight, frameWidth, offset, rowsize)
         
                self.cs.value(1)
                    
                    
    @micropython.viper           
    def _send_bmp_to_display( self, f, frameHeight: int, frameWidth: int, offset: int, rowsize: int ):
        """ Send bmp-file to display
        Args
        f (object File) : Image file
        frameHeight (int): Height of image frame
        frameWidth (int): Width of image frame
        offset (int): Internal byte offset of image-file
        rowsize (int): Internal byte rowsize of image-file        
        """
        spi_buffer = bytearray( frameWidth * 2 )
        row_buffer = ptr8( spi_buffer )
        
        for row in range( frameHeight ):
            # Start position of new row in image-file
            pos = offset + ( frameHeight - row ) * rowsize
                                    
            if int( f.tell() ) != pos:
                f.seek( pos )
            
            # Reading one row from image-file
            bgr_row = f.read( frameWidth * 3 )
            image_buffer = ptr8( bgr_row )
            
            for col in range( frameWidth ):             
                #Getting color bytes
                red   = image_buffer[ col * 3     ]
                green = image_buffer[ col * 3 + 1 ]
                blue  = image_buffer[ col * 3 + 2 ]
                
                row_buffer[ col * 2     ] = ( blue & 0xF8 ) | ( green & 0xFC ) >> 5
                row_buffer[ col * 2 + 1 ] = ( green & 0x1C ) << 3 | red >> 3
                
            self.spi.write( spi_buffer )
        
    @staticmethod
    def rgb(red, green, blue):
        """ Convert 8,8,8 bits RGB to 16 bits  """
        #return ( (red << 11) & 0xF800 | (green << 5) & 0x07E0 | blue & 0x001F )
        return ((blue & 0xf8) << 5 | (green & 0x1c) << 11 | (green & 0xe0) >> 5 | (red & 0xf8))
    
    """ TEXT AREA """
        
    def set_font(self, font):
        """ Set font for text
        Args
        font (module): Font module generated by font_to_py.py
        """
        self._font = font
        
    def draw_text( self, text, x, y, color, bg ):
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
            
            self.draw_bitmap(glyph, x, y, color, bg)
            x += glyph_width
    
    def draw_text_wrap(self, text, x, y, color, bg):
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
            self.draw_bitmap(glyph, x, y, color, bg)
            x += glyph_width 
        
  
    @micropython.viper
    def draw_bitmap(self, bitmap, x:int, y:int, color:int, bg: int):
        """ Draw one bitmap on display
        Args
        bitmap (tuple) : Bitmap data [data, height, width]
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        bg (int) : Bacground, RGB color
        """
        data  = ptr8(bitmap[0]) #memoryview to bitmap
        height = int(bitmap[1]) 
        width  = int(bitmap[2])
        
        self.cs.value(0)
        self.set_window(x, y, x + width - 1, y + height - 1)
        
        spi_buffer = bytearray( height * width * 2 )
        bitmap_buffer = ptr16( spi_buffer )
        
        # Sending Color data        
        i = 0
        for row in range(height):
            dots_sum = 0                    
            while dots_sum < width:
                byte = data[i]
                i += 1
                dot = 0
                offset = (row * width + dots_sum)
                
                while dot < 8 and dot + dots_sum < width:
                    if (byte >> (7 - dot)) & 1: # main color
                        bitmap_buffer[ dot + offset ] = color
                    else: # background
                        bitmap_buffer[ dot + offset ] = bg
                    dot += 1                         
                dots_sum += 8
                
        self.spi.write(spi_buffer)     
        self.cs.value(1)
