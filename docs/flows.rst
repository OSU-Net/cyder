.. _flows:

Network Flows
=============
Network Flow language::

    <stmt>    -> permit <sevice> from <objects>

    <service>   -> <app> | <app>, <service>
    <app>       -> <proto>: <port> <DSO>
    <proto>     -> ICMP | UDP | TCP ...
    <port>      -> [0 .. 2**32]
    <DSO>       -> Device (system) specific options

    <objects>   -> <net_list> <site_list> <host_list>

    <net_list>  -> <network> | <network>, <net_list> | Null
    <network>   -> IPv6Network | IPv4Network

    <site_list> -> <site> | <site>, <site_list> | Null
    <site>      -> Network with shortest prefix length in the site

    <host_list> -> <system> | <system>, <system_list> | Null
    <host>      -> <hostname> <limiter>

    <limiter>   -> <interface name> | <vlan> | <vlan>:<site>

    <intr_name> -> ethX.Y | mgmtX.Y
    <vlan>      -> <name> | <number>

    <site>      -> <name>
