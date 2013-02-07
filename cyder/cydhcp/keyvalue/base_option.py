from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.validation import validate_name
from cyder.cydhcp.keyvalue.models import KeyValue

import ipaddr


class CommonOption(KeyValue):
    is_option = models.BooleanField(default=False)
    is_statement = models.BooleanField(default=False)
    has_validator = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        if self.is_option:
            if self.is_quoted:
                return "option {0} \"{1}\"".format(self.key, self.value)
            return "option {0} {1}".format(self.key, self.value)
        elif self.is_statement:
            if self.is_quoted:
                return "{0} \"{1}\"".format(self.key, self.value)
            return "{0} {1}".format(self.key, self.value)

    def _get_value(self):
        value = self.value.strip('\'" ')
        value = value.strip(';')
        value = value.strip()
        return value

    def _aa_deny(self):
        """
        See allow.
        """
        choices = ["unknown-clients", "bootp", "booting", "duplicates",
                   "declines", "client-updates", "dynamic bootp clients"]
        self.is_statement = True
        self.is_option = False
        self.has_validator = True
        value = self._get_value()
        values = value.split(',')
        for value in values:
            if value in choices:
                continue
            else:
                raise ValidationError("Invalid option ({0}) parameter "
                                      "({1})'".format(self.key, self.value))

    def _aa_allow(self):
        """
        The following usages of allow and deny will work in any scope, although
        it is not recommended that they be used in pool declarations.

            allow unknown-clients;
            deny unknown-clients;
            ignore unknown-clients;

            allow bootp;
            deny bootp;
            ignore bootp;
            allow booting;
            deny booting;
            ignore booting;

            allow duplicates;
            deny duplicates;

            allow declines;
            deny declines;
            ignore declines;

            allow client-updates;
            deny client-updates;

            allow dynamic bootp clients;
            deny dynamic bootp clients;
        """

        choices = ["unknown-clients", "bootp", "booting", "duplicates",
                   "declines", "client-updates", "dynamic bootp clients"]
        self.is_statement = True
        self.is_option = False
        self.has_validator = True
        value = self._get_value()
        values = value.split(',')
        for value in values:
            if value.strip() in choices:
                continue
            else:
                raise ValidationError("Invalid option ({0}) parameter "
                                      "({1})'".format(self.key, self.value))

    def _aa_routers(self):
        """
        option routers ip-address [, ip-address... ];

            The routers option specifies a list of IP addresses for routers on
            the client's subnet. Routers should be listed in order of
            preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_ntp_servers(self):
        """
        option ntp-servers ip-address [, ip-address... ];

            This option specifies a list of IP addresses indicating NTP (RFC
            1035) servers available to the client. Servers should be listed in
            order of preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_domain_name_servers(self):
        """
        option domain-name-servers ip-address [, ip-address... ];

            The domain-name-servers option specifies a list of Domain Name
            System (STD 13, RFC 1035) name servers available to the client.
            Servers should be listed in order of preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_domain_name(self):
        """
        option domain-name text;

            The 'text' should be a space seperated domain names. I.E.:
            phx.mozilla.com phx1.mozilla.com This option specifies the domain
            name that client should use when resolving hostnames via the Domain
            Name System.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        value = self._get_value()
        for name in value.split(' '):
            validate_name(name)
        self.value = value

    def _aa_search_domain(self):
        """
        The domain-search option specifies a 'search list' of Domain Names to
        be used by the client to locate not-fully-qualified domain names. The
        difference between this option and historic use of the domain-name
        option for the same ends is that this option is encoded in RFC1035
        compressed labels on the wire. For example:

            option domain-search "example.com", "sales.example.com";
        """
        self.is_option = True
        self.is_quoted = True
        self.is_statement = False
        self.has_validator = True
        self._domain_list_validator()

    def _domain_list_validator(self):
        value = self._get_value()
        for name in value.split(','):
            # Bug here. Ex: "asf, "'asdf"'
            name = name.strip(' ')
            if not name:
                raise ValidationError("Each name needs to be a non empty "
                                      "domain name surrounded by \"\"")

            if name[0] != '"' and name[len(name) - 1] != '"':
                raise ValidationError("Each name needs to be a non empty "
                                      "domain name surrounded by \"\"")
            validate_name(name.strip('"'))

    def _ip_list(self):
        #ip_list = self._get_value()
        """
        try:
            ips = [ipaddr.IPv4Address(ip.strip()) for ip in ip_list.split(',')]
        except ipaddr.AddressValueError:
            raise Exception(ip_list)
        """
        pass

    def _single_ip_validator(self):
        ip = self._get_value()
        # TODO Add ipv6 check
        try:
            ipaddr.IPv4Address(ip)
        except ipaddr.AddressrValueError:
            raise ValidationError("Invalid option ({0}) parameter "
                                  "({1})'".format(self.key, ip))

    def _int_size_validator(self, bits):
        value = int(self._get_value())
        if value > 2 ** bits or value < 0:
                raise ValidationError(
                        "{0} is more than {1} allowed bits for {2}".format(
                            value, bits, self.key))

    def _int_list_validator(self, bits):
        value = self._get_value()
        bad = [x for x in value.split(',') if int(x) < 0 or int(x) > 2 ** bits]
        if bad:
            raise ValidationError(
                    "{0} contains invalid ints".format(", ".join(bad)))

    def _boolean_validator(self):
        value = self._get_value()
        if value.lower() not in ["true", "false"]:
            raise ValidationError("{0} not a boolean value".format(value))

    def _single_string_validator(self):
        pass

    def _aa_time_offset(self):
        """
        The time-offset option

            option time-offset 28800;

            The time offset field specifies the offset of the client's subnet
            in seconds from Coordinated Universal Time (UTC).  The offset is
            expressed as a two's complement 32-bit integer.  A positive offset
            indicates a location east of the zero meridian and a negative
            offset indicates a location west of the zero meridian.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._int_size_validator(32)

    def _aa_netbios_node_type(self):
        """
        The net-bios-node-type

            option netbios-node-type 8;

           The NetBIOS node type option allows NetBIOS over TCP/IP clients
           which
           are configurable to be configured as described in RFC 1001/1002.
           The
           value is specified as a single octet which identifies the
           client type
           as follows:

                Value         Node Type
                -----         ---------
                0x1           B-node
                0x2           P-node
                0x4           M-node
                0x8           H-node
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = False

    def _aa_netbios_name_servers(self):
        """
        The netbios-name-servers option

            option netbios-name-servers 123.123.123.123, ... , 124.124.124.124;

            The NetBIOS name server (NBNS) option specifies a list of
            RFC 1001/1002 NBNS name servers listed in order of preference.
            NetBIOS Name Service is currently more commonly referred to as
            WINS. WINS servers can be specified using the netbios-name-servers
            option.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_subnet_mask(self):
        """
        The subnet-mask option

            option subnet-mask 255.255.255.0;

            The subnet mask option specifies the client's subnet mask as per
            RFC 950. If no subnet mask option is provided anywhere in scope, as
            a last resort dhcpd will use the subnet mask from the subnet
            declaration for the network on which an address is being assigned.
            However, any subnet-mask option declaration that is in scope for
            the address being assigned will override the subnet mask specified
            in the subnet declaration.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._single_ip_validator()

    def _aa_broadcast_address(self):
        """
        The broadcast address option

            option broadcast-address 123.123.123.123;

            This option specifies the broadcast address in use on the client's
            subnet. Legal values for broadcast addresses are specified in
            section 3.2.1.3 of STD 3 (RFC1122).

        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._single_ip_validator()

    def _aa_time_servers(self):
        """
        The time-servers option

            option time-servers 123.123.123.123, ..., 124.124.124.124;

            The time-server option specifies a list of RFC 868 time servers
            available to the client. Servers should be listed in order of
            preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_always_reply_rfc1048(self):
        """
        The always-reply-rfc1048 statement

            always-reply-rfc1048 boolean;

            Some BOOTP clients expect RFC1048-style responses, but do not
            follow RFC1048 when sending their requests. You can tell that a
            client is having this problem if it is not getting the options you
            have configured for it and if you see in the server log the message
            "(non-rfc1048)" printed with each BOOTREQUEST that is logged.

            If you want to send rfc1048 options to such a client, you can set
            the always-reply-rfc1048 option in that client's host declaration,
            and the DHCP server will respond with an RFC-1048-style vendor
            options field. This flag can be set in any scope, and will affect
            all clients covered by that scope.
        """
        self.is_option = False
        self.is_statement = True
        self.has_validator = False

    def _aa_log_servers(self):
        """
        The log-servers option

            option log-servers 123.123.123.123, ..., 124.124.124.124;

            The log-server option specifies a list of MIT-LCS UDP log servers
            available to the client. Servers should be listed in order of
            reference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_next_server(self):
        """
        The next-server statement

            next-server server-name;

             The next-server statement is used to specify the host address of
             the server from which the initial boot file (specified in the
             filename statement) is to be loaded.  Server-name should be a
             numeric IP address or a domain name.  If no next-server parameter
             applies to a given client, the DHCP server's IP address is used.
        """
        self.is_option = False
        self.is_statement = True
        self.has_validator = False
        self._single_string_validator()

    def _aa_ipphone(self):
        """
        """
        pass

    def _aa_slp_directory_agent(self):
        """
        The slp-directory-agent option

            option slp-directory-agent 123.123.123.123, ..., 124.124.124.124;

            This option specifies two things: the IP addresses of one or more
            Service Location Protocol Directory Agents, and whether the use of
            these addresses is mandatory. If the initial boolean value is true,
            the SLP agent should just use the IP addresses given. If the value
            is false, the SLP agent may additionally do active or passive
            multicast discovery of SLP agents (see RFC2165 for details).

            Please note that in this option and the slp-service-scope option,
            the term "SLP Agent" is being used to refer to a Service Location
            Protocol agent running on a machine that is being configured using
            the DHCP protocol.

            Also, please be aware that some companies may refer to SLP as NDS.
            If you have an NDS directory agent whose address you need to
            configure, the slp-directory-agent option should work.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._boolean_string_validator()

    def _aa_slp_scope(self):
        """
        The slp-scope option
            option slp-scope boolean string;

            The Service Location Protocol Service Scope Option specifies two
            things: a list of service scopes for SLP, and whether the use of
            this list is mandatory. If the initial boolean value is true, the
            SLP agent should only use the list of scopes provided in this
            option; otherwise, it may use its own static configuration in
            preference to the list provided in this option.

            The text string should be a comma-seperated list of scopes that the
            SLP agent should use. It may be omitted, in which case the SLP
            Agent will use the aggregated list of scopes of all directory
            agents known to the SLP agent.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = False
        self._boolean_string_validator()

    def _boolean_string_validator(self):
        value = self._get_value().split(' ')
        # TODO import re write regex
        if len(value) != 2 and (value[0].lower() not in ["true", "false"]):
            raise ValidationError("does not match the pattern bool string")

    def _aa_default_lease_time(self):
        """
        The default-lease-time statement

            default-lease-time time;

            Time should be the length in seconds that will be assigned to a
            lease if the client requesting the lease does not ask for a
            specific expiration time.
        """
        self.is_option = False
        self.is_statement = True
        self.has_validator = True
        self._int_size_validator(32)

    def _aa_dhcp_parameter_request_list(self):
        """
        The dhcp-parameter-request-list option

            option dhcp-parameter-request-list uint16, uint16 ...

            This option, when sent by the client, specifies which options the
            client wishes the server to return. Normally, in the ISC DHCP
            client, this is done using the request statement. If this option is
            not specified by the client, the DHCP server will normally return
            every option that is valid in scope and that fits into the reply.
            When this option is specified on the server, the server returns the
            specified options. This can be used to force a client to take
            options that it hasn't requested, and it can also be used to tailor
            the response of the DHCP server for clients that may need a more
            limited set of options than those the server would normally return.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._int_list_validator(16)

    def _aa_dns_servers(self):
        """A list of DNS servers for this network."""
        self.is_statement = False
        self.is_option = False
        self._ip_list(self.network.ip_type)

    def _aa_filename(self):
        """
        The filename statement

            filename "filename";

            The filename statement can be used to specify the name of the
            initial boot file which is to be loaded by a client.  The
            filename should be a filename recognizable to whatever file
            transfer protocol the client can be expected to use to load the
            file.
        """
        self.is_option = False
        self.is_statement = True
        self.has_validator = True
        self._single_string_validator()

    def _aa_host_name(self):
        """
        The host-name option

            option host-name string;

            This option specifies the name of the client. The name may or may
            not be qualified with the local domain name (it is preferable to
            use the domain-name option to specify the domain name). See RFC
            1035 for character set restrictions. This option is only honored by
            dhclient-script(8) if the hostname for the client machine is not
            set.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._single_string_validator()

    def _aa_max_lease_time(self):
        """
        The max-lease-time statement

            max-lease-time time;

            Time  should be the maximum length in seconds that will be assigned
            to a lease if the client requesting the lease asks for a specific
            expiration time.
        """
        self.is_option = False
        self.is_statement = True
        self.has_validator = False

    def _aa_min_lease_time(self):
        """
        The min-lease-time statement

            min-lease-time time;

            Time should be the minimum length in seconds that will be assigned
            to a lease. The default is the minimum of 300 seconds or
            max-lease-time.
        """
        self.is_option = False
        self.is_statement = True
        self.has_validator = False
        #TODO implement check if this model has a max lease-time

    def _aa_default_ip_ttl(self):
        """
        The default-ip-ttl option

            option default-ip-ttl uint8;

            This option specifies the default TTL that the client should use
            when sending TCP segments. The minimum value is 1.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._int_size_validator(8)

    def _aa_cookie_servers(self):
        """
        The cookie server

            option cookie-servers ip-address [, ip-address... ];

            The cookie server option specifies a list of RFC 865 cookie servers
            available to the client. Servers should be listed in order of
            preference.
        """
        self.is_option = True
        self.is_statement = True
        self.has_validator = True
        self._ip_list()

    def _aa_finger_server(self):
        """
        The finger-server option

            option finger-server ip-address [, ip-address... ];

            The Finger server option specifies a list of Finger available to
            the client. Servers should be listed in order of preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_font_server(self):
        """
        The font-server option

            option font-servers ip-address [, ip-address... ];

            This option specifies a list of X Window System Font servers
            available to the client. Servers should be listed in order of
            preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()

    def _aa_impress_server(self):
        """
        The impress-server option

            option impress-servers ip-address [, ip-address... ];

            The impress-server option specifies a list of Imagen Impress
            servers available to the client. Servers should be listed in order
            of preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list()
