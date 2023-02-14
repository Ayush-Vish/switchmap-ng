#!/usr/bin/env python3
"""Test the macport module."""

import os
import sys
import unittest
import random

from sqlalchemy import select

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.abspath(
            os.path.join(
                os.path.abspath(
                    os.path.join(
                        os.path.abspath(
                            os.path.join(
                                os.path.abspath(
                                    os.path.join(EXEC_DIR, os.pardir)
                                ),
                                os.pardir,
                            )
                        ),
                        os.pardir,
                    )
                ),
                os.pardir,
            )
        ),
        os.pardir,
    )
)
_EXPECTED = """\
{0}switchmap-ng{0}tests{0}switchmap_{0}server{0}db{0}misc""".format(
    os.sep
)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case the repo has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print(
        """This script is not installed in the "{0}" directory. Please fix.\
""".format(
            _EXPECTED
        )
    )
    sys.exit(2)


# Create the necessary configuration to load the module
from tests.testlib_ import setup

CONFIG = setup.config()
CONFIG.save()

from switchmap.server.db.table import macport
from switchmap.server.db.table import event
from switchmap.server.db.table import zone
from switchmap.server.db.table import oui
from switchmap.server.db.table import mac
from switchmap.server.db.table import macip
from switchmap.server.db.table import device
from switchmap.server.db.table import l1interface
from switchmap.server.db.models import MacPort
from switchmap.server.db.table import IMacPort
from switchmap.server.db.table import IMac
from switchmap.server.db.table import IEvent
from switchmap.server.db.table import IZone
from switchmap.server.db.table import IOui
from switchmap.server.db.table import IDevice
from switchmap.server.db.table import IL1Interface
from switchmap.server.db.table import IMacIp
from switchmap.server.db import models
from switchmap.server.db import db as realdb

from tests.testlib_ import db
from tests.testlib_ import data

from switchmap.server.db.misc import device as testimport
from switchmap.server.db.misc.interface import mac as macdetail

MAXMAC = 100
OUIS = list(set([data.mac()[:6] for _ in range(MAXMAC * 10)]))[:MAXMAC]
MACS = ["{0}{1}".format(_, data.mac()[:6]) for _ in OUIS]
HOSTNAMES = list(set([data.random_string() for _ in range(MAXMAC * 2)]))[
    :MAXMAC
]
IFALIASES = ["ALIAS_{0}".format(data.random_string()) for _ in range(MAXMAC)]
ORGANIZATIONS = ["ORG_{0}".format(data.random_string()) for _ in range(MAXMAC)]
IPADDRESSES = list(set([data.ip_() for _ in range(MAXMAC * 2)]))[:MAXMAC]
IDX_MACS = [random.randint(1, MAXMAC) for _ in range(MAXMAC)]
RANDOM_INDEX = [random.randint(1, MAXMAC) for _ in range(MAXMAC)]


class TestDevice(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    @classmethod
    def setUpClass(cls):
        """Execute these steps before starting each test."""
        # Load the configuration in case it's been deleted after loading the
        # configuration above. Sometimes this happens when running
        # `python3 -m unittest discover` where another the tearDownClass of
        # another test module prematurely deletes the configuration required
        # for this module
        config = setup.config()
        config.save()

        # Create database tables
        models.create_all_tables()

        # Pollinate db with prerequisites
        _prerequisites()

    @classmethod
    def tearDownClass(cls):
        """Execute these steps after each tests is completed."""
        # Drop tables
        database = db.Database()
        database.drop()

        # Cleanup the
        CONFIG.cleanup()

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test_device(self):
        """Testing function device."""
        # Initialize key variables
        device_ = device.idx_exists(1)
        hostname = device_.hostname

        # Test
        expected = device.exists(hostname)
        meta = testimport.Device(hostname)
        result = meta.device()
        self.assertEqual(result, expected)

    def test_interfaces(self):
        """Testing function interfaces."""
        # Initialize key variables
        device_ = device.idx_exists(1)
        hostname = device_.hostname

        # Test
        meta = testimport.Device(hostname)
        results = meta.interfaces()

        for key in range(MAXMAC):
            # Initialize loop variables
            macresult = []
            idx_macs = []

            # Test interface
            idx_l1interface = key + 1
            expected_interface = l1interface.idx_exists(idx_l1interface)
            self.assertEqual(results[key].RL1Interface, expected_interface)

            # Get the MAC idx_mac values associated with the interface.
            statement = select(MacPort).where(
                MacPort.idx_l1interface == idx_l1interface,
            )
            rows = realdb.db_select_row(1197, statement)
            for row in rows:
                idx_macs.append(row.idx_mac)

            # Get the MacDetail values
            for item in idx_macs:
                macresult.extend(macdetail.by_idx_mac(item))

            # Test macs
            self.assertEqual(results[key].MacDetails, macresult)


def _prerequisites():
    """Create prerequisite rows.

    Args:
        None

    Returns:
        result: dict {idx_mac: [List of MacDetail objects]}

    """
    # Insert the necessary rows
    event.insert_row(IEvent(name=data.random_string(), enabled=1))
    zone.insert_row(
        IZone(
            name=data.random_string(),
            company_name=data.random_string(),
            address_0=data.random_string(),
            address_1=data.random_string(),
            address_2=data.random_string(),
            city=data.random_string(),
            state=data.random_string(),
            country=data.random_string(),
            postal_code=data.random_string(),
            phone=data.random_string(),
            notes=data.random_string(),
            enabled=1,
        )
    )
    oui.insert_row(
        [
            IOui(oui=OUIS[key], organization=value, enabled=1)
            for key, value in enumerate(ORGANIZATIONS)
        ]
    )
    mac.insert_row(
        [
            IMac(
                idx_oui=key + 1, idx_event=1, idx_zone=1, mac=value, enabled=1
            )
            for key, value in enumerate(MACS)
        ]
    )
    device.insert_row(
        IDevice(
            idx_zone=1,
            idx_event=1,
            sys_name=data.random_string(),
            hostname=data.random_string(),
            name=data.random_string(),
            sys_description=data.random_string(),
            sys_objectid=data.random_string(),
            sys_uptime=random.randint(0, 1000000),
            last_polled=random.randint(0, 1000000),
            enabled=1,
        )
    )
    l1interface.insert_row(
        [
            IL1Interface(
                idx_device=1,
                ifindex=random.randint(0, 1000000),
                duplex=random.randint(0, 1000000),
                ethernet=1,
                nativevlan=random.randint(0, 1000000),
                trunk=1,
                ifspeed=random.randint(0, 1000000),
                ifalias=value,
                ifdescr=data.random_string(),
                ifadminstatus=random.randint(0, 1000000),
                ifoperstatus=random.randint(0, 1000000),
                ts_idle=random.randint(0, 1000000),
                cdpcachedeviceid=data.random_string(),
                cdpcachedeviceport=data.random_string(),
                cdpcacheplatform=data.random_string(),
                lldpremportdesc=data.random_string(),
                lldpremsyscapenabled=data.random_string(),
                lldpremsysdesc=data.random_string(),
                lldpremsysname=data.random_string(),
                enabled=1,
            )
            for _, value in enumerate(IFALIASES)
        ]
    )

    # Insert MacPort entries
    macports_ = [
        IMacPort(idx_l1interface=value, idx_mac=key + 1, enabled=1)
        for key, value in enumerate(RANDOM_INDEX)
    ]
    macport.insert_row(macports_)

    # Insert MacIp entries
    macips_ = [
        IMacIp(
            idx_device=1,
            idx_mac=value,
            ip_=IPADDRESSES[key].address,
            version=IPADDRESSES[key].version,
            hostname=HOSTNAMES[key],
            enabled=1,
        )
        for key, value in enumerate(IDX_MACS)
    ]
    macip.insert_row(macips_)


if __name__ == "__main__":
    # Do the unit test
    unittest.main()
