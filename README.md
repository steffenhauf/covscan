# CovScan

A RPI hack for creating a Covid Scanner

## Introduction

This project was born out of a not too serious discussion on how to
cope with more stringend Covid-restrictions in Germany. Namely, on how
to automate scanning the European Covid Passport as a door entry system.
After a few iterations, it's reached a level of maturity, where it might
actually be useful to others.

## Hard- & Software

The hardware was determined mostly by what was available already. To
reproduce the project you'll need

* a Raspberry PI Zero
* a wide-angle PI camera module, e.g. https://www.amazon.de/gp/product/B07XL3YVYY/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1
* an adapter camera cable for the PI zero, e.g. https://www.amazon.de/AZDelivery-Flexkabel-Raspberry-Zero-Display/dp/B07CMZ9DV2/ref=sr_1_1_sspa?__mk_de_DE=ÅMÅŽÕÑ&keywords=pi+zero+camera+cable
* three 5 mm LEDs, blue, red and green might be appropriate colors
* six 220Ω resistors
* two 8 pin sockets
* one 4 pin bent pin connector
* a small buzzer
* a HC-SR04  ultra-sonic distance sensor, https://www.amazon.de/gp/product/B091BW1MM3/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1
* a 5 x 7cm prototype PCB board

The software consists of a single python script, which can be found in this
repository. Additional dependencies are required and installation is
detailed below.

## Tools

To follow the instructions you'll need a soldering iron and lead, access to a
3d printer, some cutter pliers, and a selection of jumper wires.

## Preparing the Hardware

I'm a software developer (and recovering physicist), so please don't judge
my soldering skills :) However, the following does work, and you are very
welcome to make comments for improvement.

We will need to solder components on both sides of the PCB board. The
following sketches are for indication only. How you do the actual routing
is a bit up to you. However, to fit the case, you shoudl make sure that
the PI zero, the SR04 and the pin connector for the LEDs are positioned in
the right place on the PCB.

![Top view of PCB](./images/pcb_top.png)

Start off by soldering the 2 8-pin sockets 8 rows from the top edge (so
start in row 9) and 2 columns from the right edge (start in column 3).
This is where the PI will connect to. Then solder the 4-pin connector 2 rows
and to columns away from the lower left edge. Both of these go on the same
side of the PCB.

Next, solder the SR04 7 rows from the top and 5 columns from the left edge
onto the same side as the pin connector. Your buzzer should now go somewhere
in the top right corner.

Now we need to do the actual connection routing. We'll start with implementing
a voltage divider for the output of the SR04. Solder three of the resistors
in sequence originating from the "echo" pin of the SR04. I still did this
on the same side as the previous components, allowing me to route on the
other side then.

![SR04 installed](./sketches/sonic_only.png)

Connect the far side of the first resistor to GPIO pin 27 of the PI, which
corresponds to the second pin from the left of the lower row of the 8 pin
connector.

Connect the far end of the last resistor to ground, e.g. to 4th pin from the
left of the lower connector row.

Connect the trigger pin of the SR04 to GPIO 17, which is the third pin from
the left of the lower row.

Finally, connect VCC to a 5V output of the PI, which is e.g. the right-most
pin in the top connector row.

With the SR04 connected we now wire the buzzer. It's ground should be
connected to the ground we used for the SR04. The other pin connects to
GPIO 2, which is the second pin from the right in the lower connector.

Next we connect the power button, which we solder onto the opposite side of
the PCB. It connects to GPIO3 and to ground. It's important to use GPIO3 here
as otherwise the wake functionality of the PI will not work.

![Button installed](./sketches/push_button.png)

![Button installed](./images/pcb_bottom.png)


Finally, we connect the LED pins. The top-most pin should be connected to
ground. Going down from top to bottom we then connect to GPIO pins 18, 15,
14 respectively, which are the 5th, 4th and 3rd pin from the left,
in the top connector row.

The complete PCB should look like this

![Full circuit sketch](./sketches/circuit_sketch.png)