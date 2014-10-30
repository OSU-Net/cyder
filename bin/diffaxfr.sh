#!/bin/bash

# How to install
# --------------
# mkdir diffaxfr/
# cd diffaxfr/
# chmod +x diffaxfr.sh
# vim diffaxfr.sh (you need to set ns[12] and ns[12]_target)
# ./diffaxfr.sh
#
# set ts=4

ns1=ns1.oregonstate.edu
ns1_target=ns1.oregonstate.edu

ns2=localhost
ns2_target=localhost

zones="
    0.0.127.in-addr.arpa
    10.in-addr.arpa
    139.201.199.in-addr.arpa
    193.128.in-addr.arpa
    16.211.140.in-addr.arpa
    17.211.140.in-addr.arpa
    18.211.140.in-addr.arpa
    19.211.140.in-addr.arpa
    20.211.140.in-addr.arpa
    21.211.140.in-addr.arpa
    23.211.140.in-addr.arpa
    26.211.140.in-addr.arpa
    28.211.140.in-addr.arpa
    33.211.140.in-addr.arpa
    71.211.140.in-addr.arpa
    162.211.140.in-addr.arpa
    163.211.140.in-addr.arpa
    165.211.140.in-addr.arpa
    168.211.140.in-addr.arpa
    224.211.140.in-addr.arpa
    225.211.140.in-addr.arpa
    226.211.140.in-addr.arpa
    227.211.140.in-addr.arpa
    228.211.140.in-addr.arpa
    229.211.140.in-addr.arpa
    230.211.140.in-addr.arpa
    231.211.140.in-addr.arpa
    232.211.140.in-addr.arpa
    233.211.140.in-addr.arpa
    234.211.140.in-addr.arpa
    235.211.140.in-addr.arpa
    236.211.140.in-addr.arpa
    237.211.140.in-addr.arpa
    238.211.140.in-addr.arpa
    239.211.140.in-addr.arpa
    aftol.org
    askmars.com
    askmars.net
    askmars.org
    barleyworld.org
    beaverarmy.com
    beavernation.is
    beaverracing.org
    beaverturf.com
    beetlebank.org
    campaignforosu.com
    campaignforosu.net
    campaignforosu.org
    cascadeprint.org
    code4lib.org
    collaborationcorvallis.org
    cordyceps.us
    ctemps.org
    deschutesexplorer.info
    educational-resources-pactrans.org
    eduy.ir
    ellieslog.com
    ellieslog.org
    eorganic.info
    eusesconsortium.org
    experienceosu.com
    extensionservice.com
    extensionservice.net
    extensionservice.org
    familybusinessonline.com
    familybusinessonline.org
    fishpathogens.net
    foodbizstartup.com
    foodbizstartup.org
    foodhero.org
    foodinnovationcenter.com
    foodinnovationcenter.org
    forestphytophthora.org
    forestphytophthoras.org
    globalclimatedata.org
    granderondeexplorer.info
    hoodexplorer.info
    hostcenter.dk
    hydroville.org
    icaarconcrete.org
    icoastalatlas.net
    iifet.org
    intertidalweb.org
    intunewith.com
    intunewith.info
    intunewith.net
    intunewith.org
    ipmnet.org
    ipmprime.org
    johndayexplorer.info
    kbvr.com
    kbvrtv.com
    klamathexplorer.info
    lakesbasinexplorer.info
    librariesoforegon.org
    libraryfind.org
    lowercolumbiaexplorer.info
    maizegametophyte.org
    majordiscovery.org
    marinecoastalgis.net
    marinemammalinstitute.com
    marinemammalinstitute.net
    marinemammalinstitute.org
    marinemammalprogram.org
    mbi-online.org
    mbi-online.us
    meetatosu.com
    micronbc.org
    midvalleycoastlearn.org
    milkweedgenome.org
    myorangerewards.com
    naafe.org
    nacse.org
    nichemeatprocessing.com
    nichemeatprocessing.org
    nitrificationnetwork.org
    northcoastexplorer.info
    nowebsto.org
    nwexplorer.info
    nwfirescience.org
    nwwildlife.org
    occri.net
    ockham.org
    opencampus-oregon.com
    opencampus-oregon.net
    opencampus-oregon.org
    opencampusoregon.com
    opencampusoregon.net
    opencampusoregon.org
    or-firstforce.org
    oraapt.org
    oregon-state.edu
    oregon4hfoundation.org
    oregonchannel.net
    oregonchannel.org
    oregonetic.org
    oregonexplorer.info
    oregonfic.com
    oregonflora.org
    oregonfoodsystems.com
    oregonfoodsystems.org
    oregonmasternaturalist.com
    oregonmasternaturalist.net
    oregonmasternaturalist.org
    oregonmetal.org
    oregonopencampus.com
    oregonopencampus.net
    oregonopencampus.org
    oregonpace.net
    oregonpers.info
    oregonpsm.org
    oregonrangelands.org
    oregonstate.biz
    oregonstate.edu
    oregonstate.eu
    oregonstate.info
    oregonvegetables.com
    oregonwin.com
    oregonwin.net
    oregonwin.org
    orforestdirectory.com
    orst.biz
    orst.com
    orst.edu
    orst.info
    orst.net
    orst.org
    ortop.org
    ortransfer.com
    orvsd.org
    ospud.org
    osu1868society.com
    osu1868society.net
    osu1868society.org
    osuaep.info
    osualum.com
    osucampaign.com
    osucampaign.net
    osucampaign.org
    osucascades.edu
    osucatering.com
    osucatering.org
    osucbee.org
    osudaily.mobi
    osuforestry.com
    osufoundation.com
    osufoundation.net
    osufoundation.org
    osufund.com
    osufund.net
    osufund.org
    osugero.org
    osumeetme.vc
    osummi.com
    osummi.net
    osummi.org
    osumu.org
    osupachyderm.org
    osupistol.org
    osupresidentscircle.com
    osupresidentscircle.net
    osupresidentscircle.org
    osusuccess.com
    ous.edu
    owri.org
    owyheemalheurexplorer.info
    paulingcatalog.org
    paulingcatalogue.org
    pbgworks.com
    pbgworks.org
    pdx.eu
    phytophthora-id.org
    pkts.asia
    planteome.org
    plantontology.org
    pnwcirc.org
    pnwclimate.org
    pnwfirst.org
    pnwhandbooks.org
    pnwpest.org
    pnwvegetables.com
    pnwvegetables.org
    powderexplorer.info
    poweredbyorange.com
    poweredbyorange.org
    qlz.cn
    rebeaved.com
    rogueexplorer.info
    rotbusters.org
    seafloormapping.net
    seps.org
    siantsis.com
    simearth.org
    singorange.com
    songsofpowerandprayer.com
    songsofpowerandprayer.org
    southcoastexplorer.info
    spottedwing.com
    spottedwing.org
    staterblog.com
    succession.org
    surveyc2c.com
    surveyc2c.net
    surveyc2c.org
    tahmo.info
    tanguaylab.com
    tiestotheland.net
    tiestotheland.org
    tillikum.org
    trtr.org
    ucoz.hu
    umatillaexplorer.info
    umpquaexplorer.info
    uoregon.eu
    usiale.org
    uspest.org
    wash4h.org
    webnibus.org
    weedemandreap.org
    weedmapper.org
    westernlandscapesexplorer.info
    wildstrawberry.org
    willametteexplorer.info
    yachatsdocuments.info
"



if [[ "$ns1" == "" ]] ||
   [[ "$ns2" == "" ]] ||
   [[ "$ns2_target" == "" ]] ||
   [[ "$ns2_target" == "" ]]
then
    echo "vim diffaxfr.sh (you need to set ns[12] and ns[12]_target)"
    exit 1
fi

dig_args="+nocmd +nostats"

BUILD_DIR="./build_dir"

function check_ret {
    if [ $? -ne 0 ];then
        echo 'Failure'
        exit 1
    fi
}

function axfr() {
	# $1 = host
	# $2 = target query ip
	# $3 = zone name
	# $4 = outfile
    build_out="$BUILD_DIR/$4.axfr"

    local outfile="$4"
    eval $outfile=$build_out  # Set it for the caller

    echo "ssh $1 dig $dig_args @$2 $3 axfr | etc."
    dig $dig_args @$2 $3 axfr |
        grep -v RSIG | # Don't care
        grep -v SOA | # Don't care
        grep -v NSEC3 | # Don't care
        grep -v DNSKEY | # Don't care
        grep -v unused | # Don't care
        sed -r 's/(\S+\s+)\S+(.*)/\1\2/' | # removes ttl
        sed -r 's/\s+/ /g' | # sanitize spaces
        tr '[A-Z]' '[a-z]' | # to lower case
        sort >> $build_out  # append. Don't clobber

    check_ret
}

# build the build env
rm -rf $BUILD_DIR
mkdir $BUILD_DIR

ns1_all_outfile=""
for zone in $zones
do
    echo "[NS1] AXFRing zone: $zone"
    axfr $ns1 $ns1_target $zone "ns1_all_outfile"
    check_ret
done

ns1_all_outfile=""
for zone in $zones
do
    echo "[NS2] AXFRing zone: $zone"
    axfr $ns2 $ns2_target $zone "ns2_all_outfile"
    check_ret
done

function sort_axfr () {
    cat $1 | sort | uniq > $1.sorted
}

echo "$BUILD_DIR/ns1_all_outfile.axfr"
sort_axfr $BUILD_DIR/ns1_all_outfile.axfr
sort_axfr $BUILD_DIR/ns2_all_outfile.axfr

vimdiff $BUILD_DIR/ns1_all_outfile.axfr.sorted $BUILD_DIR/ns2_all_outfile.axfr.sorted
