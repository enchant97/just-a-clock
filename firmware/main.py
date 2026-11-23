from machine import I2C

from justaclock.main import DisplayWiring, main

if __name__ == "__main__":
    display_wiring = DisplayWiring(I2C(0), 0x70)
    main(display_wiring)
