"""
GC9A01_SPI_BASE v 0.3.1
Display controller driver

Displays: GC9A01
Connection: 4-line SPI
Colors: 12, 16, 18 bits
Controllers: Esp32-family, RP2-family
 
Project path: https://github.com/r2d2-arduino/micropython_gc9a01
MIT License

Author: Arthur Derkach
"""

from machine import Pin
from time import sleep_ms

class GC9A01_SPI_BASE( ):
    
    def __init__( self, spi, cs_pin, dc_pin, rst_pin, blk_pin = None,
                  width = 240, height = 240, bgr = False ):
        """ Constructor
        Args
        spi  (object): SPI
        cs_pin  (int): Chip Select pin number
        dc_pin  (int): Data/Command pin number
        rst_pin (int): Reset pin number 
        blk_pin (int): Backlight pin number
        width   (int): Screen width in pixels (less)
        height  (int): Screen height in pixels
        bgr    (bool): Color order: False = RGB, True = BGR
        """ 
        self.spi = spi
        self.rst = Pin( rst_pin, Pin.OUT, value = 0 )
        self.dc  = Pin( dc_pin,  Pin.OUT, value = 0 )
        self.cs  = Pin( cs_pin,  Pin.OUT, value = 1 )
        self.blk = None
        
        self.controller_name = self.read_controller_name()

        if blk_pin is not None:
            self.blk = Pin(blk_pin, Pin.OUT, value = 1)
            
            self.blk_pwm = PWM(self.blk)
            self.blk_pwm.freq( 2000 )
            
            if self.controller_name == 'RP2':
                self.blk_pwm.duty_u16( 65535 )
            else:
                self.blk_pwm.duty( 1023 )
            
        self._rotation = 0
        
        self.width  = width
        self.height = height        
        
        self.bgr = 0
        if bgr:
            self.bgr = 1
    
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
        sleep_ms( 120 )
        
    def write_command( self, command ):
        """ Sending a command to the display
        Args
        cmd (int): Command number, example: 0x2E
        """
        self.cs.value( 0 )
        self.dc.value( 0 )        
        self.spi.write( bytes( [ command ] ) )
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
        self.spi.write( bytes( [ command ] ) )

        self.dc.value( 1 )
        self.spi.write( data )

        self.cs.value( 1 )        
        
    def read_command( self, command, num_bytes = 1 ):
        """ Reading answer from display """
        self.write_command( command )
        sleep_ms(10)     
        return self.read_data( num_bytes )

    def set_rotation( self, rotation = 0 ):
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
            self.memory_access_control(0, 1, 0, 0, self.bgr, 0)
        elif rotation == 1: # 90 deg
            self.memory_access_control(0, 0, 1, 0, self.bgr, 0)
        elif rotation == 2: # 180 deg
            self.memory_access_control(1, 0, 0, 0, self.bgr, 0)
        elif rotation == 3: # 270 deg
            self.memory_access_control(1, 1, 1, 0, self.bgr, 0)

        # Change height <-> width for 90 and 270 degrees
        if ( ((rotation & 1) and not (old_rotation & 1))
            or ((not (rotation & 1)) and (old_rotation & 1)) ):
            
            self.swap_dimensions()

    def memory_access_control( self, my = 0, mx = 0, mv = 0, ml = 0, bgr = 0, mh = 0 ):
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

    def invert_display( self, on = True ):
        """ Enables or disables color inversion on the display.
        Args
        on (bool): True = Enable inversion, False = Disable inversion
        """
        if bool(on):
            self.write_command( 0x21 )  
        else:
            self.write_command( 0x20 )

    def tearing_effect( self, on = True ):
        """ Activate "Tearing effect"
        Args
        on (bool): True = Enable effect, False = Disable effect
        """        
        if bool( on ):
            self.write_command( 0x35 )
        else:
            self.write_command( 0x34 )

    def idle_mode( self, on = True ):
        """ Enables or disables idle mode on the display.
        Args
        on (bool): True = Enable idle mode, False = Disable idle mode
        """
        if bool( on ):
            self.write_command( 0x39 )
        else:
            self.write_command( 0x38 )

    def set_brightness( self, value ):
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
            
    def vert_scroll( self, top_fix: int, scroll_height: int, bot_fix: int ):
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
            
    def vert_scroll_start_address( self, start = 0 ):
        """ Set vertical scroll start address, and run scrolling
        Args
        start (int): start row        
        """
        self.write_command( 0x37 )
        self.write_data( bytearray([ (start >> 8) & 0xFF, start & 0xFF ]) )
        
    def scroll( self, delay = 5 ):
        """ Scrolling on the screen at a given speed.
        Args
        delay (int): Delay between scrolling actions
        """
        height = self.height
        if self._rotation & 1:
            height = self.width
            
        for y in range( height ):
            self.vert_scroll_start_address(y + 1)
            sleep_ms(delay)  
    
    @staticmethod
    def read_controller_name():
        from os import uname
        
        """ Reading controller name """
        info = uname()
        sysname = info.sysname

        controller = 'Undefined'
        if sysname == 'esp32':
            if 'ESP32S3' in info.machine:
                controller = 'ESP32-S3'
            elif 'ESP32C3' in info.machine:
                controller = 'ESP32-C3'
            else:
                controller = 'ESP32'
        elif sysname == 'rp2':
            controller = 'RP2'

        return controller
    
    def set_backlight ( self, duty = 1023 ):
        """ Set Backlight PWM Pin
        Args
        duty (int): Duty value: 0..1023
        """
        if self.blk is not None:
            if 0 <= duty < 1024:
                if self.controller_name == 'RP2':
                    self.blk_pwm.duty_u16( duty * 64 )
                else:
                    self.blk_pwm.duty( duty )
            else:
                print("Duty value out of range: 0..1023")
        
