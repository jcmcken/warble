# warble

A MIDI device driver for FFXIV. Let's you play your MIDI device and translate the notes in real(ish) time to FFXIV
Perform notes.

## Disclaimer

**Use at your own risk!**

Square Enix does not permit the use of third-party tools that negatively affect players or
any Square Enix service. Don't be an absolute idiot.

## Installation

First and foremost, you need Python 2. I would install Python 2.7 (the latest version).

Next, you need an appropriate ``libusb`` device driver. Default Windows USB device drivers
will not work. The easiest thing to do is to use [Zadig](http://zadig.akeo.ie/) and install
``libusb-win32``.

Next, install ``pywin32``. For some reason, installing this via ``setuptools`` is broken,
so you'll need to install it on your own. One way to do this is via ``pip``:

```console
> pip.exe install pywin32
```

Next, from the ``warble`` project root, just run:

```console
> python.exe setup.py install
```

## Usage

Log into FFXIV, obviously, and turn on Perform.

Next, plug in your device with a USB MIDI cable and turn it on.

Now launch a ``cmd.exe`` console as Administrator (this is necessary to
read the raw data coming from the USB device)

If you have a YAMAHA portable grand piano, then this will just work
(assuming your Python ``Scripts`` are in your ``PATH``)

```
> warble.exe
```

This will:

* Focus your FFXIV process.
* Launch a MIDI listener for your USB device that will translate played
notes to Perform key presses.

Play a few notes on your device to validate that it's working. ``warble``
will also print the notes to the console.

If you're using some other instrument, you'll need to grab the USB
vendor ID and product ID from the Windows Device Manager. Then you can
run:

```console
> warble.exe --vendor-id 0x0499 --product-id 0x1039
```

(Replacing the hex values with the appropriate codes)

## Notes

**All discussion below is based on FFXIV patch 4.2**

In FFXIV, Perform only covers 3 piano octaves (octaves 3,4, and 5) plus
octave 6 ``C``. If you hit a note outside of this range, it won't have
the right pitch in game.

Another thing to keep in mind is latency. When you hit a note on your
instrument, it needs to travel through your MIDI cable, into ``warble``,
down through the Win32 keyboard event API, and into your game process.
In practice, the game itself introduces the largest latency, because you
can only play notes so fast within the game.

As of patch 4.2, Perform can only play one note at a time. But you can
simulate chords by arpeggiating, as long as you keep latency in mind (
arpeggiating too quickly will result in lost notes).
