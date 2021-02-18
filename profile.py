#!/usr/bin/env python

import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.igext as IG
import geni.rspec.emulab as EL
import geni.rspec.emulab.pnext as PN
import geni.urn as URN


#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN


#
# Global variables that should remain relatively static
#
class GLOBALS(object):
    EPCIMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:OEPC-more-events.V2")
    MSIMG = "urn:publicid:IDN+emulab.net+image+PhantomNet:mobilestream-v1"
    SRSLTE="urn:publicid:IDN+emulab.net+image+PhantomNet:srsLTE"
#
# Create our in-memory model of the RSpec -- the resources we're going
# to request in our experiment, and their configuration.
#
rspec = PG.Request()

#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()
#request = pc.makeRequestRSpec()


#
# Describe profile.  Will be rendered in Markdown on Portal.
#
tourDescription = \
"""
Use this profile to instantiate an experiment to realize MobileStream with a different type of Radio access networks
"""

tourInstructions = \
"""
This profile makes use of user-supplied parameters. 
These are the possible options. We will support more components (e.g., Nexus 5, ip.access, and OAI)
1) "Emulator : "emulated eNBs from OpenEPC"
1) "SDR : "srsUE + srseNB from srsLTE"
"""

#
# Setup the Tour info with the above description and instructions.
#  
tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN,tourDescription)
tour.Instructions(IG.Tour.MARKDOWN,tourInstructions)
rspec.addTour(tour)

#
# Define some parameters for OpenEPC experiments.
#

#portal.context.defineParameter( "n", "Number of storm nodes", portal.ParameterType.INTEGER, 1 )

pc.defineParameter("TYPE", "Radio type",
                   portal.ParameterType.STRING,"Emulator",[("Emulator","eNB emulator(s) from OpenEPC"),("SDR","srsUE + srseNB from srsLTE")],
                   longDescription="Type of Radio (SDR-based UE and eNB or emulated eNBs in OpenEPC software")

pc.defineParameter("NUMSTORM", "Number of storm nodes.",
                   portal.ParameterType.INTEGER, 1,
                   longDescription="Number of storm nodes May be from 1 to 9 (inclusive).")

pc.defineParameter("HWTYPE","Node Hardware Type",
                   portal.ParameterType.STRING, "pcvm",
                   [("pc","Any available (compatible) physical machine type"),
                    ("pc3000","Emulab pc3000 nodes"),
                    ("d710","Emulab d710 nodes"),
                    ("d430","Emulab d430 nodes"),
                    ("m510","Utah m510 nodes"),
                    ("xl170","Utah xl170 nodes"),
                    ("pcvm","Any available (compatible) virtual machine type"),
                    ("pc3000vm","Virtual machines on top of pc3000 nodes."),
                    ("d710vm","Virtual machines on top of d710 nodes."),
                    ("d430vm","Virtual machines on top of d430 nodes.")],
                   longDescription="Specify which node resource type to use for OpenEPC nodes. Note that only those types that are compatible with the OpenEPC image(s) are listed.")

pc.defineParameter("NUMENB", "Number of eNodeB nodes.",
                   portal.ParameterType.INTEGER, 1,
                   longDescription="Number of emulated eNodeB (LTE base station) nodes to allocate.  May be from 1 to 3 (inclusive).",
		   advanced=True)


pc.defineParameter("LINKBW","Default Link Bandwidth (Mbps)",
                  portal.ParameterType.INTEGER, 0,
                   longDescription="Specify the default LAN bandwidth in Mbps for all EPC LANs. Leave at \"0\" to indicate \"best effort\". Values that do not line up with common physical interface speeds #(e.g. 10, 100, or 1000) WILL cause the insertion of link shaping elements.",
                   advanced=True)


#
# Get any input parameter values that will override our defaults.
#
params = pc.bindParameters()

#
# Verify parameters and setup errors/warnings to be reported back.
#
if params.NUMSTORM < 1 or params.NUMSTORM > 10:
    perr = portal.ParameterError("You cannot ask for fewer than one or more than 10 Storm nodes!", ['NUMSTORM'])
    pc.reportError(perr)
    pass

if params.NUMENB < 1 or params.NUMENB > 3:
    perr = portal.ParameterError("You cannot ask for fewer than one or more than three eNodeB nodes!", ['NUMENB'])
    pc.reportError(perr)
    pass

if int(params.LINKBW) not in [0, 10, 100, 1000]:
    pwarn = portal.ParameterWarning("You are asking for a default link bandwidth that is NOT a standard physical link speed. Link shaping resources WILL be inserted!", ['LINKBW'])
    pc.reportWarning(pwarn)
    pass

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()

#
# Scale link bandwidth parameter to kbps
#

#
# If the generic hardware type "pc" was requested, don't set the
# type at all.
#
if params.HWTYPE == "pc":
    params.HWTYPE = None

#
# Set the hardware and image for the epc node factory function
#
PN.EPCNodeFactorySettings.hardware_type = params.HWTYPE
PN.EPCNodeFactorySettings.disk_image = GLOBALS.EPCIMG

#
# Create the lans we need
#
usevms = 0
net_d = rspec.EPClan(PN.EPCLANS.NET_D, vmlan = usevms)


# TODO : limit up to 9 machines.
netmask="255.255.255.0"

if params.TYPE == "Emulator":
    #
    # Force gigabit speed for d430 nodes.
    #
    params.LINKBW *= 1000
    if params.HWTYPE == "d430":
       if params.LINKBW == 0:
           params.LINKBW = 1000 * 1000

    net_d.bandwidth = params.LINKBW
    # Create the lans we need
    mgmt = rspec.EPClan(PN.EPCLANS.MGMT, vmlan = usevms)
    mgmt.bandwidth = params.LINKBW
    # Hack for d430 node type ...
    if params.LINKBW != 0:
        mgmt.best_effort = False
    an_lte = rspec.EPClan(PN.EPCLANS.AN_LTE, vmlan = usevms)
    an_lte.bandwidth = params.LINKBW

    # Create the requested number of eNodeB nodes
    for i in range(1, params.NUMENB + 1):
        ename = "enb%d" % i
        enb = PN.mkepcnode(ename, PN.EPCROLES.ENODEB, hname = ename)
        enb.exclusive = True
        rspec.addResource(enb)
        mgmt.addMember(enb)
        net_d.addMember(enb)
        an_lte.addMember(enb)
else:
    # add sdr enb
    sdrenb = rspec.RawPC("srseNB")
    sdrenb.hardware_type = "nuc5300"
    sdrenb.disk_image = GLOBALS.SRSLTE
    sdrenbif = sdrenb.addInterface("enbint")
    sdr_enb_ip="192.168.4.90"
    cintf = net_d.addMember(sdrenb)
    caddr = PG.IPv4Address(sdr_enb_ip, netmask)
    cintf.addAddress(caddr)

    # add sdr ue
    sdrue = rspec.RawPC("srsUE")
    sdrue.hardware_type = "nuc5300"
    sdrue.disk_image = GLOBALS.SRSLTE
    sdrueif = sdrue.addInterface("ueint")

    rflname = "rflink"
    rflink = rspec.RFLink(rflname)
    rflink.addInterface(sdrenbif)
    rflink.addInterface(sdrueif)


for i in range( params.NUMSTORM ):
    ip_prefix="192.168.4.8%d"
    node = rspec.RawPC( "node" + str( i ) )
    node.hardware_type = params.HWTYPE
    node.disk_image = GLOBALS.MSIMG
    ip = ip_prefix % i
    cintf = net_d.addMember(node)
    caddr = PG.IPv4Address(ip, netmask)
    cintf.addAddress(caddr)

#
# Print and go!
#
pc.printRequestRSpec(rspec)
