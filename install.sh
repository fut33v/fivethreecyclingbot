#!/bin/sh

sudo cp  fivethreecyclingbot /etc/init.d
sudo chmod +x /etc/init.d/fivethreecyclingbot
sudo update-rc.d fivethreecyclingbot defaults
