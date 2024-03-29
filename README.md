# ProGlove Streams

[![Build Status](https://travis-ci.com/workaroundgmbh/proglove_streams_api_reference.svg?branch=master)](https://travis-ci.com/workaroundgmbh/proglove_streams_api_reference)
[![Coverage Status](https://coveralls.io/repos/github/workaroundgmbh/proglove_streams_api_reference/badge.svg?branch=master)](https://coveralls.io/github/workaroundgmbh/proglove_streams_api_reference?branch=master)

ProGlove Streams API reference implementation in Python.

## API documentation

<https://docs.proglove.com/en/streams-api.html>

## Requirements

- Python >= 3.9

## Install dependencies

Install Python 3.9 on your machine
In a terminal (or command prompt) install and initialize the project

    make init

This will also install the package requirements. To do this separately, run
  
    make install-deps

## Run the sample application

To run the sample application you can simply type

    make run

which is equivalent to:
  
    poetry run python3 -m proglove_streams

Optionally, there is the possibility to specify the path to the serial port by appending `-p PORT` to the above command where `PORT` represents the serial port path attached to the Gateway (e.g. `/dev/ttyACM0`, `COM1`). This defaults to `COM1` on Windows and `/dev/ttyACM0` on Linux.

Once connected to the serial device the application runs forever until a
Ctrl-C keyboard event is received.

## Application command line arguments

  ```
usage: proglove_streams [-h] [-L LEVEL] [-b VALUE] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -L LEVEL, --logging-level LEVEL
                        set the logging level (default is DEBUG)
  -b VALUE, --baudrate VALUE
                        use a specific baudarate (default is 115200)
  -p PORT, --port PORT  path to the serial device port (e.g. COM1, /dev/ttyACM0). Defaults to /dev/ttyACM0 on Linux and COM1 on Windows.
  ```

### Baudrate

The default baudrate used by the application is `115200`.

### Logging level

The default logging level is `DEBUG`.

## Use the application

Once a scanner is connected to the Gateway a `scanner_state` event
will be received. You can now scan a barcode containing one of the
following text:

- `DISPLAY` to tell the sample app to send a display command to a Mark
  Display

  ![](qrcodes/display.png)

- `BLOCK` to block the single press trigger for 3 seconds

  ![](qrcodes/block.png)

- `UNBLOCK` to unblock the trigger

  ![](qrcodes/unblock.png)

- `FEEDBACK_OK` to play a positive feedback on the Mark device

  ![](qrcodes/feedback_ok.png)

- `FEEDBACK_NOK` to play a negative feedback on the Mark device

  ![](qrcodes/feedback_nok.png)

- `STATE` to get the Gateway state

  ![](qrcodes/state.png)

## Develop your own application

This project includes a sample application in `app_example.py` which uses
the two main classes:

- `Gateway` the main client used to communicate with the serial port of a
  Gateway.
- `GatewayMessageHandler` the Streams API handler that will parse a received
  JSON message and call the proper application callback.

## Callbacks

The `GatewayMessageHandler` class implements the following callbacks:

- `on_scan` called when a Mark scan event is received
- `on_scanner_connected` called when a Mark is connected to the Gateway
- `on_scanner_disconnected` called when a Mark is disconnected from the Gateway
- `on_error` called when a Streams API error event is received
- `on_gateway_state_event` called when a Gateway State Event is received
- `on_button_pressed` called when a Mark button press is received

## Commands

The `Gateway` client can send commands to the connected Gateway with
the following methods:

- `get_gateway_state` to get the Gateway state (the
  `on_gateway_state_event` will be called on a successful event
  received from the Gateway)
- `send_feedback` to send a visual feedback to a connected Mark
- `set_display` to display something on the Mark Display
- `set_trigger_block` to block the trigger of a connected Mark

## Models

All Streams API events are based on the streams API library models as defined internally by the ProGlove Development Team. These models can be found [here](https://dl.cloudsmith.io/rOwxaCA5uRoiGzOs/proglove/python-packages/python/simple/).

## Copyright

(c) Workaround GmbH 2021

## End User License Agreement

End User License Agreement ProGlove Streams Software

Important: By (1) downloading the ProGlove Software from Cloudsmith or
via the ProGlove Insight Webportal, (2) installing (3) and/or using
(“Downloading”) the ProGlove Software accompanying this End User
License Agreement (“License Agreement”), you are agreeing to be bound
by this License Agreement. Please read this License Agreement before
Downloading the ProGlove Software. If you are Downloading the ProGlove
Software on behalf of your employer, you represent that you have the
authority to bind your employer to the terms of the License
Agreement. If you do not have such authority or if you do not agree
with the terms of this License Agreement, do not install or use the
ProGlove Software.

## 1. ProGlove Software

(a) ProGlove Software means the (1) Mark Family firmware and/or MARK
Family special firmware installed on your ProGlove devices and/or
downloadable from the Insight webportal, (2) ProGlove Insight Mobile
(Android) or ProGlove Connect software downloadable through the
Insight webportal or any other source, (3) the Feature Demo App or the
Trade Fair Demo App software downloadable through the Insight
webportal or any other source, (4) the Insight Mobile (iOS) software
downloadable through the Insight webportal or any other source, (5)
the Gateway application firmware installed on your ProGlove Gateway
device and/or downloadable from the Insight webportal, or (6)
documentation, (code) samples and interfaces to any of the foregoing,
each accompanying this License Agreement and described as ProGlove
Software in the documentation or release note (“ProGlove
Software”). ProGlove Software is licensed, not sold, to you by
Workaround GmbH (“ProGlove”) for use only under and pursuant to the
terms of this License Agreement.  (b) ProGlove, at its discretion, may
make available future ProGlove Software updates. The ProGlove Software
updates, if any, may not necessarily include all existing software
features or new features that ProGlove releases. The terms of this
License Agreement will govern any ProGlove Software updates provided
by ProGlove, unless such ProGlove Software update is accompanied by a
separate license agreement, in which case you agree that the terms of
that license agreement will govern. ProGlove has no support or
maintenance obligations with respect to the ProGlove Software.  (c)
The ProGlove Software includes basic features, early access features
and premium features (as indicated in the documentation or release
note). Until further notice your license to the basic features and
early access features is royalty-free but subject to termination with
three months prior notice by ProGlove.  (d) A feature is an early
access feature, if it is described as Alpha or Beta in the
documentation or release note, product documentation or product
itself. Your use of early access features is time-based and on your
own risk as an early access feature.  (e) Your license to premium
features is time-based and subject to you (i) signing a ProGlove order
form, (ii) paying the license fees and, if applicable, the maintenance
& support fees specified in the ProGlove order form, (iii) complying
with the time, volume and device type limitations specified in the
ProGlove order form and (iv) not sharing your license key with
entities not specified in the ProGlove order form. Please note you are
strictly prohibited from sharing your license key with entities not
specified in the ProGlove order form.

## 2. Permitted License Uses and Restrictions

(a) Subject to the terms and conditions of this License Agreement, you
are granted a limited non-exclusive license to use the ProGlove
Software on your Android mobile smartphone and/or tablet for use with
ProGlove devices only.  (b) You are not permitted to: • Edit, alter,
modify, adapt, translate or otherwise change the whole or any part of
the ProGlove Software, or permit the whole or any part of the ProGlove
Software to be combined with or become incorporated in any other
software, or decompile, disassemble or reverse engineer the ProGlove
Software or attempt to do any such things (except as and only to the
extent any foregoing restriction is prohibited by applicable law or by
licensing terms governing the use of open source components that may
be included with the ProGlove Software), • Rent, lease, lend, sell,
redistribute, or sublicense the ProGlove Software, • Allow any third
party to use the ProGlove Software on behalf of or for the benefit of
any third party, • Use the ProGlove Software for any purpose that
ProGlove considers is a breach of this License Agreement, or • Remove,
obscure, or alter any proprietary notices (including trademark and
copyright notices) that may be affixed to or contained within the
ProGlove Software.  (c) You agree to use the ProGlove Software in
compliance with all applicable laws, including local laws of the
country or region in which you reside or in which you download or use
the ProGlove Software. Download of the ProGlove Software requires a
unique username and password combination. You will use commercially
reasonable efforts to prevent unauthorized access to or use of the
ProGlove Software and notify ProGlove promptly of any such
unauthorized access or use.

## 3. Authorized Partners

If you are an authorized ProGlove distribution partner, your customers
still have to receive a unique username and password combination and
complete the registration form in order to accept the License
Agreement, download and use the ProGlove Software. If you are an
authorized ProGlove distribution Partner, you may use the ProGlove
Software for showcase purposes (but you may not replace the ProGlove
logo with your logo in the ProGlove Software). You may also not share
your license key with your customers.

## 4. Ownership

ProGlove and its licensors retain ownership of the ProGlove Software
and reserve all rights not expressly granted to you. ProGlove reserves
the right to grant licenses to use the ProGlove Software to third
parties.

## 5. Feedback

ProGlove may use and include any feedback that you provide to improve
the ProGlove Software or other ProGlove products or technologies. All
feedback becomes the sole property of ProGlove and may be used in any
manner ProGlove sees fit. ProGlove has no obligation to respond to
feedback or to incorporate feedback into the ProGlove
Software. ProGlove may also use the feedback that you provide to
provide notices to you which may be of use or interest to you.

## 6. Termination

This License Agreement is effective until terminated. Your rights
under this License Agreement will terminate automatically without
notice from ProGlove if you fail to comply with any term(s) of this
License Agreement. Upon the termination of this License Agreement, you
shall cease all use of the ProGlove Software. Sections 4,5,7,8, and 11
of this License Agreement shall survive any such termination.

## 7. Disclaimer of Warranties

(a) YOU EXPRESSLY ACKNOWLEDGE AND AGREE THAT, TO THE EXTENT PERMITTED
BY APPLICABLE LAW, USE OF THE PROGLOVE SOFTWARE IS AT YOUR SOLE RISK
AND THAT THE ENTIRE RISK AS TO SATISFACTORY QUALITY, PERFORMANCE,
ACCURACY AND EFFORT IS WITH YOU.  (B) TO THE MAXIMUM EXTENT PERMITTED
BY APPLICABLE LAW, THE PROGLOVE SOFTWARE IS PROVIDED “AS IS” AND “AS
AVAILABLE” AND WITHOUT WARRANTY OF ANY KIND.  (C) YOU FURTHER
ACKNOWLEDGE THAT THE PROGLOVE SOFTWARE IS NOT SUITABLE FOR USE IN
SITUATIONS OR ENVIRONMENTS WHERE THE FAILURE OR TIME DELAYS OF, OR
ERRORS OR INACCURACIES IN, THE CONTENT, DATA OR INFORMATION PROVIDED
BY THE PROGLOVE SOFTWARE COULD LEAD TO DEATH, PERSONAL INJURY, OR
SEVERE PHYSICAL OR ENVIRONMENTAL DAMAGE.

## 8. Limitation of Liability

ProGlove shall be liable for any of your damages resulting from
grossly negligent or intentional behavior of ProGlove, which are due
to culpable injury to life, body, and health, or which arise due to
the assumption of a guarantee or according to the German Product
Liability Act. In all other cases, ProGlove’s liability for damages is
limited to the infringement of material obligations of the
agreement. Material obligations are only such obligations which
fulfillments allow the proper execution of the agreement in the first
place and where you may rely on the compliance with these
obligations. ProGlove’s liability for the loss of data is limited to
the typical expenditures required for the restoration thereof, which
are normal and typical if security copies have been made. ProGlove’s
liability in case of negligent infringement of material obligations of
the agreement by ProGlove shall be limited to foreseeable damages
which are typical for this type of contract. A strict liability of
ProGlove for defects existing at the time of entering into this
License Agreement is hereby expressly excluded. All claims against
ProGlove for damages shall be statute barred 6 months after
download. This shall not apply to any claims in tort. The foregoing
limitations of liability also apply with regard to all ProGlove’s
representatives, including but not limited to its directors, legal
representatives, employees, and other vicarious agents.

## 9. Export Control

You may not use or otherwise export or re-export the ProGlove Software
except as authorized by German law and the laws of the jurisdiction(s)
in which the ProGlove Software was obtained. In particular, but
without limitation, the ProGlove Software may not be exported or
re-exported (a) into any U.S. embargoed countries or (b) to anyone on
the U.S. Treasury Department’s list of Specially Designated Nationals
or the U.S. Department of Commerce Denied Person’s List or Entity List
or any other restricted party lists.

## 10. Third Party Software Components

Portions of the ProGlove Software may utilize or include third party
software and other copyrighted material. Acknowledgements, licensing
terms and disclaimers for such material are contained in the
electronic documentation for the ProGlove Software and/or in this
License Agreement. Your use of such material is governed by the third
party owners’ respective terms. If a software component is described
as open source in the documentation, the relevant open source license
terms apply. The open source and proprietary software for Mark Family
firmware, Insight Mobile (iOS) and Gateway 1 application firmware is
specified in the Addendum to this License Agreement called Legal
Notice Mark Family Firmware and Mark Family Special Firmware, Legal
Notice ProGlove Insight Mobile (iOS) and Legal Notice Gateway
Application Firmware respectively. For ProGlove Insight Mobile,
ProGlove Connect, the Trade Fair Demo App or the Feature Demo App
software downloadable through the Insight webportal or any other
source, the open source documentation can be found in the About
section of the secondary menu in the software.

## 11. Controlling Law

This License Agreement will be governed by and construed in accordance
with the laws of Germany, excluding its conflict of law principles and
excluding the United Nations Convention on Contracts for the
International Sale of Goods. If for any reason a court of competent
jurisdiction finds any provision, or portion thereof, to be
unenforceable, the remainder of this License Agreement shall continue
in full force and effect.

## 12. Complete Agreement

This License Agreement constitutes the entire agreement between you
and ProGlove relating to the ProGlove Software and supersedes all
prior or contemporaneous understandings regarding such subject
matter. No amendment to or modification of this License Agreement will
be binding unless in writing and signed by ProGlove.
