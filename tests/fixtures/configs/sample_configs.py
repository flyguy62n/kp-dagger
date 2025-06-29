"""Sample Cisco IOS configuration for testing."""

CISCO_IOS_CONFIG = """
!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname Router01
!
boot-start-marker
boot-end-marker
!
!
no aaa new-model
!
!
!
no ip domain lookup
ip domain name example.com
ip cef
no ipv6 cef
!
!
!
username admin privilege 15 secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
!
!
!
!
!
interface GigabitEthernet0/0
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 description WAN Interface
 ip address 10.0.0.1 255.255.255.252
 duplex auto
 speed auto
!
interface Serial0/0/0
 no ip address
 shutdown
 clock rate 2000000
!
!
ip route 0.0.0.0 0.0.0.0 10.0.0.2
!
!
access-list 101 permit tcp any host 192.168.1.100 eq 80
access-list 101 permit tcp any host 192.168.1.100 eq 443
access-list 101 deny ip any any log
!
!
!
line con 0
line aux 0
line vty 0 4
 login local
 transport input ssh
!
!
end
"""

CISCO_ASA_CONFIG = """
!
ASA Version 9.8(2)
!
hostname ASA01
enable password 8Ry2YjIyt7RRXU24 encrypted
passwd 2KFQnbNIdI.2KYOU encrypted
names
!
interface GigabitEthernet0/0
 nameif outside
 security-level 0
 ip address 203.0.113.1 255.255.255.0
!
interface GigabitEthernet0/1
 nameif inside
 security-level 100
 ip address 192.168.1.1 255.255.255.0
!
access-list OUTSIDE_ACCESS_IN extended permit tcp any host 192.168.1.100 eq www
access-list OUTSIDE_ACCESS_IN extended permit tcp any host 192.168.1.100 eq https
access-list OUTSIDE_ACCESS_IN extended deny ip any any log
!
access-group OUTSIDE_ACCESS_IN in interface outside
!
route outside 0.0.0.0 0.0.0.0 203.0.113.254 1
!
username admin password Pa$$w0rd123
username admin attributes
 vpn-group-policy ADMIN_POLICY
!
end
"""
