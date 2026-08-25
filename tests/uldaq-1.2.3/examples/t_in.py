#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
from time import sleep
from os import system
from sys import stdout

from uldaq import (
    get_net_daq_device_descriptor,
    DaqDevice,
    TempScale,
    AiChanType,
    TcType,
    ULException,
    ULError
)

IP_ADDRESS = "169.254.69.179"
PORT = 54211
INTERFACE_NAME = "eth0"

LOW_CHANNEL = 0
HIGH_CHANNEL = 7
SCALE = TempScale.CELSIUS
TC_TYPE = TcType.R


def main():
    daq_device = None

    try:
        desc = get_net_daq_device_descriptor(IP_ADDRESS, PORT, INTERFACE_NAME)
        print("Found device:", desc)

        daq_device = DaqDevice(desc)

        ai_device = daq_device.get_ai_device()
        if ai_device is None:
            raise RuntimeError(
                "Error: The DAQ device does not support analog input"
            )

        ai_info = ai_device.get_info()
        chan_types = ai_info.get_chan_types()
        if AiChanType.TC not in chan_types:
            raise RuntimeError(
                "Error: The DAQ device does not support thermocouple channels"
            )

        number_of_channels = ai_info.get_num_chans()
        high_channel = min(HIGH_CHANNEL, number_of_channels - 1)

        print("\nConnecting to device - please wait...")
        daq_device.connect(connection_code=0)

        descriptor = daq_device.get_descriptor()
        print("\n{} ready".format(descriptor.dev_string))
        print("    Function demonstrated: ai_device.t_in()")
        print("    Channels: {}-{}".format(LOW_CHANNEL, high_channel))

        ai_config = ai_device.get_config()
        for chan in range(LOW_CHANNEL, high_channel + 1):
            ai_config.set_chan_type(chan, AiChanType.TC)
            ai_config.set_chan_tc_type(chan, TC_TYPE)

            chan_type = ai_config.get_chan_type(chan)
            tc_type = ai_config.get_chan_tc_type(chan)
            print("        Channel {} type: {} Type {}".format(
                chan, chan_type.name, tc_type.name
            ))

        print("    Temperature scaling:", SCALE.name)

        try:
            input("\nHit ENTER to continue\n")
        except (NameError, SyntaxError):
            pass

        system("clear")

        try:
            while True:
                display_strings = []

                for channel in range(LOW_CHANNEL, high_channel + 1):
                    try:
                        data = ai_device.t_in(channel, SCALE)
                        display_strings.append(
                            "Channel({}) Data: {:10.6f}".format(channel, data)
                        )
                    except ULException as ul_error:
                        if ul_error.error_code == ULError.OPEN_CONNECTION:
                            display_strings.append(
                                "Channel({}) Data: Open Connection".format(channel)
                            )
                        else:
                            display_strings.append(
                                "Channel({}) Data: ERR {}: {}".format(
                                    channel, ul_error.error_code, ul_error
                                )
                            )

                reset_cursor()
                print("Please enter CTRL + C to terminate the process\n")
                print(
                    "Active DAQ device: {} ({})\n".format(
                        descriptor.dev_string, descriptor.unique_id
                    )
                )

                for display_string in display_strings:
                    clear_eol()
                    print(display_string)

                sleep(0.5)

        except KeyboardInterrupt:
            pass

    except RuntimeError as error:
        print("\n", error)
    except ULException as error:
        print("\nUL Error:", error)
    finally:
        if daq_device:
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()


def reset_cursor():
    stdout.write("\033[1;1H")


def clear_eol():
    stdout.write("\x1b[2K")


if __name__ == "__main__":
    main()
