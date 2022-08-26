.. _RockPi4:

RockPi4
#######

This document describes how to build and run for RockPi4b+ target.

Building
********

Build meta-ts
=============

Refer to the trusted substrate docs for more information
https://trusted-substrate.readthedocs.io/en/latest/

.. code-block:: bash

	$ pip install kas
	$ git clone https://gitlab.com/Linaro/trustedsubstrate/meta-ts.git
	$ cd meta-ts
	$ kas build ci/rockpi4b.yml

Build ewaol plus ledge security rootfs image
================================================
.. code-block:: bash

	$ mkdir trs
	$ cd trs
	$ git clone https://gitlab.com/Linaro/ewaol/meta-ewaol-machine.git -b kirkstone-dev
	$ cd meta-ewaol-machine
	$ ./build.sh ledge-secure-qemuarm64 baremetal

	# Note: the rootfs is common with other arm64 targets, so the same .wic image can be used

Run
***
How to prepare the images to run on the RockPi 4 board is explained here,
copied/annotated below:

Firmware boots from an SD card. While rootfs and ESP partition are on a USB
stick. This allows the USB stick to be easily used in multiple boards.

Prepare SD with
===============

Refer to trusted substrate docs for more information
https://trusted-substrate.readthedocs.io/en/latest/building/install_firmware.html

Assuming your SD card is /dev/sda

.. code-block:: bash

	$ cp meta-ts/build/tmp/deploy/images/rockpi4b/ts-firmware-rockpi4b.wic.gz .
	$ zcat ts-firmware-rockpi4b.wic.gz >/dev/sda

.. warning::

	Make sure the device in ``/dev`` is present before doing this or you will
	create a file in ``/dev`` and put nothing on the SD card, and the card will
	not be seen until you delete the file!

Prepare USB stick with
======================

To flash the rootfs image you built above, from your trs build directory

.. code-block:: bash

	$ sudo dd if=build/ledge-secure-qemuarm64/tmp_baremetal/deploy/images/ledge-secure-qemuarm64/ewaol-baremetal-image-ledge-secure-qemuarm64.wic of=/dev/sda bs=1M status=progress
	$ sync

.. note::

	The ``qemuarm64`` above not a typo, the rootfs is multi-platform. If you
	used USB stick in other machine with current firmware before booting delete
	``ubootefi.var`` file for ESP (first one) partition.

Attach USB stick and SD card
============================

Plug both USB stick and SD card into the board. The USB stick has to be in one
of the black USB ports (at least for me it wouldn’t be detected by U-Boot when
in one of the blue USB3 ports; I’m using a CF card in a USB adapter). Power it
on and wait for the U-boot prompt.
Add kernel board specific kernel parameters and EFI boot order
==============================================================

.. code-block:: bash

	$ efidebug boot add -b 1 BootLedge usb 0:1 efi/boot/bootaa64.efi -i usb 0:1 ledge-initramfs.rootfs.cpio.gz -s 'console=ttyS2,1500000 console=tty0 root=UUID=6091b3a4-ce08-3020-93a6-f755a22ef03b rootwait panic=60' ; efidebug boot order 1


Restart
=======

Power cycle board it and it has to boot automatically now.

.. note::
	Second boot with a fresh root fs is quite slow, please wait for a couple
	of minutes. This is caused by the rootfs being encrypted on first boot.

Serial port info: https://wiki.radxa.com/Rockpi4/dev/serial-console. We've been
using this script:

.. code-block:: bash

	#!/bin/bash
	#
	# miniterm.py is in Ubuntu package python-serial
	# $ sudo apt-get install python-serial
	#
	# Adjust USB device as needed

	DEV=${1:-/dev/ttyUSB0}
	pyserial-miniterm --raw --eol CR ${DEV} 1500000


FAQ
***

Q: How to increase OP-TEE core log level?
=========================================
Add ``CFG_TEE_CORE_LOG_LEVEL=3`` to ``EXTRA_OEMAKE`` in
``meta-ts/meta-arm/recipes-security/optee/optee-os.inc`` and rebuild (kas
build…)

Q: How to modify optee-os sources locally and rebuild?
======================================================

	#. Remove line ``INHERIT += rm_work`` in ``ci/base.yml``
	#. Run ``$ kas shell ci/rockpi4b.yml``
		#. ``bitbake -c cleansstate optee-os`` # WARNING removes source in work directory
		#. ``$ bitbake optee-os``
		#. Edit source files in ``build/tmp/work/rockpi4b-poky-linux/optee-os/<ver>/git``
		   ``$ bitbake -c compile -f optee-os`` # mandatory before kas build below it seems
	#. Exit kas shell and run ``$ kas build ci/rockpi4b.yml``

Q: Why is the internal eMMC not detected?
=========================================
Try a different USB-C power supply. We use a Dell one. I have another no-name PS
supposedly rated PD 100W which doesn’t work reliably.

Q: How to skip initramfs and boot to rootfs directly?
=====================================================

.. code-block:: bash

	$ efidebug boot add -b 1 BootLedge usb 0:1 efi/boot/bootaa64.efi -s 'console=ttyS2,1500000 console=tty0 root=UUID=6091b3a4-ce08-3020-93a6-f755a22ef03b rootwait panic=60 root=/dev/sda2' ; efidebug boot order 1 ; bootefi bootmgr

Q: On boot, the kernel logs warnings about GPT, how to fix them?
================================================================
They are harmless, they are caused by the fact that the actual device (USB key)
is larger than the image copied to it. The warnings can be removed by running
``gparted /dev/sdaX`` and accepting the prompt to fix the GPT info.

Q: On boot, the kernel logs “EXT4 … recovery complete”, what’s wrong?
=====================================================================
Usually harmless. The board was not powered off or rebooted cleanly. Use
``systemctl halt`` or ``systemctl reboot``.

Q: symbolize.py on hb2 (on e.g., the fTPM TA) prints DWARF warnings and no source file/line info. Why?
======================================================================================================
The default toolchains (``aarch64-linux-gnu-*``) is too old (7.2). Put a more
recent one in your ``PATH`` before invoking ``symbolize.py`` (Note: some source/file
line info are still missing, could be due to build flags)

Q: My board randomly hangs or crashes under system load. Why?
=====================================================================
RockPi4b boards are very fussy about their PSU. Ensure you are using an official
PSU like
https://shop.allnetchina.cn/products/power-supply-adapter-qc-3-0-for-rock-pi-4

Do not use a 5v only USB-C PSU (such as a USB port on your laptop), as you will
hit random board stability issues.
