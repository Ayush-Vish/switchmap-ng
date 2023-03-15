"""Module of switchmap.webserver routes.

Contains all routes that switchmap.s Flask webserver uses

"""

# Flask imports
from flask import Blueprint, jsonify


# Application imports
from switchmap.core import rest
from switchmap.core import graphene
from switchmap.dashboard.configuration import ConfigDashboard

# Define the API global variable
API = Blueprint("API", __name__)


@API.route("/dashboard", methods=["GET"])
def dashboard():
    """Get dashboard data.

    Args:
        None

    Returns:
        Webpage HTML

    """
    # Return content
    html = _dashboard()
    return html


@API.route("/dashboard/<int:idx_root>", methods=["GET"])
def historical_dashboard(idx_root):
    """Get dashboard data.

    Args:
        None

    Returns:
        Webpage HTML

    """
    # Return content
    html = _dashboard(idx_root)
    return html


@API.route("/events", methods=["GET"])
def roots():
    """Get event data.

    Args:
        None

    Returns:
        JSON of zone data

    """
    # Initialize key variables
    config = ConfigDashboard()
    query = """
{
  roots {
    edges {
      node {
        idxRoot
        event {
          tsCreated
        }
      }
    }
  }
}
"""
    # Get the data
    result = rest.get_graphql(query, config)
    normalized = graphene.normalize(result)

    # Get the zone data list
    data = normalized.get("data")
    roots = data.get("roots", {})

    # Return
    return jsonify(roots)


@API.route("/devices/<int:idx_device>", methods=["GET"])
def devices(idx_device):
    """Get device data.

    Args:
        None

    Returns:
        JSON of zone data

    """
    # Initialize key variables
    config = ConfigDashboard()
    query = """
{
  devices(filter: {idxDevice: {eq: IDX_DEVICE}}) {
    edges {
      node {
        hostname
        sysName
        sysDescription
        sysObjectid
        sysUptime
        lastPolled
        l1interfaces {
          edges {
            node {
              ifname
              ifalias
              ifoperstatus
              ifadminstatus
              ifspeed
              iftype
              duplex
              trunk
              cdpcachedeviceid
              cdpcacheplatform
              cdpcachedeviceport
              lldpremsysname
              lldpremportdesc
              lldpremsysdesc
              nativevlan
              macports {
                edges {
                  node {
                    macs {
                      mac
                      oui{
                        manufacturer
                      }
                      macips {
                        edges {
                          node {
                            ips {
                              address
                              version
                              hostname
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
              vlanports {
                edges {
                  node {
                    vlans {
                      vlan
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}


""".replace(
        "IDX_DEVICE", str(idx_device)
    )

    # Get the data
    result = rest.get_graphql(query, config)
    normalized = graphene.normalize(result)

    # Get the zone data list
    data = normalized.get("data")
    device = data.get("devices")[0]

    # Return
    return jsonify(device)


def _dashboard(idx_root=1):
    """Get dashboard data.

    Args:
        idx_root: Database Root table index

    Returns:
        JSON of event data

    """
    # Initialize key variables
    config = ConfigDashboard()
    query = """
{
  roots(filter: {idxRoot: {eq: ROOT}}) {
    edges {
      node {
        event {
          tsCreated
          zones {
            edges {
              node {
                name
                devices {
                  edges {
                    node {
                      hostname
                      idxDevice
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

""".replace(
        "ROOT", str(idx_root)
    )

    # Get the data
    result = rest.get_graphql(query, config)
    normalized = graphene.normalize(result)

    # Get the zone data list
    data = normalized.get("data")
    if bool(data) is True:
        roots = data.get("roots")
        event = roots[0].get("event")

        # Return
        return jsonify(event)
    else:
        # Return
        return jsonify({})
