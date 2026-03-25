package main

import (
	"fmt"
	"os"

	"github.com/NuwoMaaan/MQTT-Vault-lockpad/BLE/internal"
	"tinygo.org/x/bluetooth"
)

var adapter = bluetooth.DefaultAdapter

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: main.go detect")
		os.Exit(1)
	}

	if err := adapter.Enable(); err != nil {
		fmt.Fprintln(os.Stderr, "adapter enable error:", err)
	}

	switch os.Args[1] {
	case "detect":
		ble, err := internal.Register(adapter)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}

		if err := internal.ListenAndDetect(adapter, ble); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}

		select {} // keep process alive

	default:
		fmt.Fprintln(os.Stderr, "unknown mode")
		os.Exit(1)
	}
}
