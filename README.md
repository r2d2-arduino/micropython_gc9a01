# micropython_gc9a01
Display controller driver for gc9a01 using SPI connection.

![Photo of gc9a01 display](/../main/photo/gc9a01.jpg)

## File Structure:
* **examples/** - a set of examples for using the library GC9A01_SPI.
* **examples_fb/** - a set of examples for using the library GC9A01_SPI_FB.
* **examples_dma/** - a set of examples for using the library GC9A01_SPI_FB with DMA.
* **resources/** - files related to examples.
* **gc9a01_spi_base.py** - Base library for GC9A01_SPI and GC9A01_SPI_FB.
* **gc9a01_spi.py** - Main library GC9A01_SPI.
* **gc9a01_spi_fb.py** - Main library GC9A01_SPI_FB. Framebuffer and DMA version.

## Dependencies:
The main libraries inherit from the graphics libraries tft_draw:
https://github.com/r2d2-arduino/tft_draw

## Minimum code to run:
```python
from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin

# Set your pins here
CS_PIN   = 4
DC_PIN   = 5
RST_PIN  = 3

spi = SPI( 0, baudrate = 40_000_000, sck = Pin(6), mosi = Pin(7) ) # Option for pico

tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN )

tft.fill( tft.color565( 255, 0, 0 ) ) # Fills the entire screen with red
```

## Display functions:
* **set_rotation ( rotation = 0 )** - Set orientation of Display, 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees.
* **invert_display ( on = True )** - Enables or disables color inversion on display.
* **tearing_effect ( on = True )** - Activate "Tearing effect".
* **idle_mode ( on = True )** - Enables or disables idle mode on display.
* **scroll ( delay = 5 )** - Scrolling on the screen at a given speed.
* **show ( )** - Displays the contents of the buffer on the screen ( gc9a01_spi_fb only ).
