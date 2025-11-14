#!/bin/bash
# WiFi Hotspot Setup for Performance Companion
# Creates a WiFi access point on the Raspberry Pi Zero W

set -e

echo "=== Performance Companion - WiFi Hotspot Setup ==="
echo ""

# Configuration
SSID="Performance-AP"
PASSWORD="perform123"
CHANNEL=6

echo "This script will configure your Pi Zero W as a WiFi hotspot"
echo "SSID: $SSID"
echo "Password: $PASSWORD"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Install required packages
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y hostapd dnsmasq

# Stop services
echo "Stopping services..."
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Configure static IP for wlan0
echo "Configuring static IP for wlan0..."
sudo tee /etc/dhcpcd.conf > /dev/null <<EOF
# Static IP configuration for hotspot
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF

# Configure dnsmasq (DHCP server)
echo "Configuring DHCP server..."
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true
sudo tee /etc/dnsmasq.conf > /dev/null <<EOF
# DHCP server configuration for hotspot
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/gw.wlan/192.168.4.1
EOF

# Configure hostapd (WiFi AP)
echo "Configuring WiFi access point..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOF
# WiFi AP configuration
interface=wlan0
driver=nl80211
ssid=$SSID
hw_mode=g
channel=$CHANNEL
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Point hostapd to config file
sudo tee /etc/default/hostapd > /dev/null <<EOF
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Unmask and enable services
echo "Enabling services..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo ""
echo "=== Hotspot Setup Complete ==="
echo ""
echo "SSID: $SSID"
echo "Password: $PASSWORD"
echo "IP Address: 192.168.4.1"
echo "Web Interface: http://192.168.4.1:5000"
echo ""
echo "Reboot required to activate hotspot:"
echo "  sudo reboot"
echo ""
