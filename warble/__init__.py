import usb.core
import usb.util
import win32com.client
import time
import win32api
import win32con
import optparse

# USB product and vendor IDs
VENDOR_YAMAHA = 0x0499
PRODUCT_YAMAHA_PORTABLE_GRAND = 0x1039

class Device(object):
    def __init__(self, vendor_id, product_id):
        self._reader = self._setup_reader(vendor_id, product_id)

    def _setup_reader(self, vendor_id, product_id):
        device = usb.core.find(
            idVendor=vendor_id,
            idProduct=product_id,
        )
        device.set_configuration()
        cfg = device.get_active_configuration()
        intf = cfg[(0,0)]

        endpoint = usb.util.find_descriptor(
            intf,
            custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN,
        )
        return lambda: device.read(
            endpoint.bEndpointAddress,
            endpoint.wMaxPacketSize,
        )

    def read(self):
        while True:
            try:
                yield self._reader()
            except usb.core.USBError as e:
                if e.args == ('Operation timed out',):
                    continue

class Note(object):
    scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, note):
        self.number = note
        self.letter = self.scale[self.number % 12]
        self.octave = self.number / 12 - 1

    def __repr__(self):
        return "%s (octave %d)" % (self.letter, self.octave)

class MIDIFilter(object):
    NOTE_UP = 0x90 # can also represent NOTE_DOWN if velocity is zero

    def filter(self, data):
        channel, command, note, velocity = data[0:4]

        # for our purposes, we don't care about the channel or volume
        if command == self.NOTE_UP and velocity != 0:
            return Note(note)

class FFXIVNoteConverter(object):
    scale = ['q', '2', 'w', '3', 'e', 'r', '5', 't', '6', 'y', '7', 'u']
    octave_up = 'left-shift'
    octave_down = 'left-ctrl'

    # win32con keyboard events
    keymap = {
        'left-shift': 0xA0,
        'left-ctrl': 0xA2,
        'q': 0x51,
        '2': 0x32,
        'w': 0x57,
        '3': 0x33,
        'e': 0x45,
        'r': 0x52,
        '5': 0x35,
        't': 0x54,
        '6': 0x36,
        'y': 0x59,
        '7': 0x37,
        'u': 0x55,
    }

    def __init__(self, keymap=None):
        self.keymap = keymap or self.keymap

    def convert(self, note):
        keys = []
        note_key = self.scale[note.number % 12]
        if note.octave == 5:
            keys.append(self.octave_up)
        elif note.octave == 3:
            keys.append(self.octave_down)
        keys.append(note_key)

        return [ self.keymap[i] for i in keys ]

class FFXIV(object):
    def __init__(self, process_title="FINAL FANTASY XIV"):
        self.process_title = process_title
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def focus(self):
        self.shell.AppActivate(self.process_title)
        time.sleep(0.5) # wait for the focus to finish

    def press_keys(self, keys):
        for key in keys:
            win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.02)
        for key in keys:
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

def option_parser():
    cli = optparse.OptionParser(prog='warble')
    cli.add_option('-v', '--vendor-id', default='0x0499',
      help="hexidecimal representation of the MIDI device's vendor ID. Defaults to 0x0499 (YAMAHA)"
    )
    cli.add_option('-p', '--product-id', default='0x1039',
      help="hexidecimal representation of the MIDI device's product ID. Defaults to 0x1039 (YAMAHA PORTABLE GRAND PIANO)"
    ),
    cli.add_option('--process', default='FINAL FANTASY XIV',
      help="process title to focus"
    )
    return cli

def main():
    cli = option_parser()
    opts, args = cli.parse_args()

    vendor_id = int(opts.vendor_id, 16)
    product_id = int(opts.product_id, 16)

    device = Device(
        vendor_id=vendor_id,
        product_id=product_id,
    )
    filter = MIDIFilter()
    converter = FFXIVNoteConverter()
    ffxiv = FFXIV(process_title=opts.process)

    ffxiv.focus()

    for data in device.read():
        note = filter.filter(data)

        if not note:
            continue

        keys = converter.convert(note)
        print "note: %s, key: %s" % (note, keys)
        ffxiv.press_keys(keys)

        if note.letter == 'C' and note.octave == 8:
            break

if __name__ == '__main__':
    main()
