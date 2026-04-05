package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/NuwoMaaan/MQTT-Vault-lockpad/BLE/internal"
	"tinygo.org/x/bluetooth"
)

var adapter *bluetooth.Adapter = bluetooth.DefaultAdapter

const (
	registerArg string = "register"
	detectArg   string = "detect"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: main.go detect | register")
		os.Exit(1)
	}

	if err := adapter.Enable(); err != nil {
		fmt.Fprintln(os.Stderr, "adapter enable error:", err)
	}

	switch os.Args[1] {
	case registerArg:
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

	case detectArg:
		var ble internal.BLEData
		if err := json.NewDecoder(os.Stdin).Decode(&ble); err != nil {
			fmt.Fprintln(os.Stderr, "stdin decode error:", err)
			os.Exit(1)
		}

		if err := internal.ListenAndDetect(adapter, &ble); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}

		select {}

	default:
		fmt.Fprintln(os.Stderr, "unknown mode")
		os.Exit(1)
	}
}
