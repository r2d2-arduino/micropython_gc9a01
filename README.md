# micropython_gc9a01
Display controller driver for gc9a01 using SPI connection.

## File Structure:
* **examples/** - a set of examples for using the library GC9A01_SPI.
* **examples_fb/** - a set of examples for using the library GC9A01FB_SPI.
* **for_examples/** - files related to examples.
* **gc9a01_spi.py** - Main library GC9A01_SPI. 
* **gc9a01fb_spi.py** - Main library GC9A01FB_SPI. Framebuffer version, see details here: https://docs.micropython.org/en/latest/library/framebuf.html . This option is much faster, but requires more RAM ( 110kB+ ).

## Minimum code to run:
```python
SPI_NUM = 1
SCK_PIN  = 14 # SCL
MOSI_PIN = 15 # SDA, for Esp32 = 13
DC_PIN   = 5
CS_PIN   = 4
RST_PIN  = 3

from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )

tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN )

tft.fill( tft.rgb( 255, 0, 0 ) ) # Fills the entire screen with red
```

## Display functions:
* **set_rotation ( rotation = 0 )** - Set orientation of Display, 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
* **invert_display ( on = True )** - Enables or disables color inversion on display
* **tearing_effect ( on = True )** - Activate "Tearing effect"
* **idle_mode ( on = True )** - Enables or disables idle mode on display.
* **scroll ( delay = 5 )** - Scrolling on the screen at a given speed.
* **show ( )** - Displays the contents of the buffer on the screen

## Image functions:
* **draw_raw_image ( filename, x, y, width, height )** - Draw RAW image (RGB565 format) on display
* **draw_bmp ( filename, x = 0, y = 0 )** - Draw BMP image on display
* **rgb ( red, green, blue )** - Convert 8,8,8 bits RGB to 16 bits

## Text functions:
* **set_font ( font )** - Set font for text
* **draw_text ( text, x, y, color )** - Draw text on display
* **draw_text_wrap ( text, x, y, color )** - Draw text on display (wrapped version)
* **draw_bitmap ( bitmap, x, y, color )** - Draw one bitmap on display

## Draw functions ( for gc9a01_spi only ):
* **fill ( color )** - Fill whole screen
* **fill_rect ( x, y, width, height, color )** - Draw filled rectangle
* **draw_vline ( x, y, height, color, thickness = 1 )** - Draw vertical line
* **draw_hline ( x, y, width, color, thickness = 1 )** - Draw horizontal line
* **draw_rect ( x, y, width, height, color, thickness = 1 )** - Draw rectangle 
* **draw_line ( x0, y0, x1, y1, color )** - Draw line using Bresenham's Algorithm
* **draw_circle ( x, y, radius, color, border = 1 )** - Draw circle
* **fill_circle ( x, y, radius, color )** - Draw filled circle
* **draw_pixel ( x, y, color )** - Draw one pixel on display
