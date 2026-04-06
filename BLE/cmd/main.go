package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/NuwoMaaan/MQTT-Vault-lockpad/BLE/internal"
	"tinygo.org/x/bluetooth"
)

// Overview:
// BLE data upon first start be registered and stored in MongoDB via backend api.
// BLE device is inserted with a token that is used in verifying the BLE device when detected.
// If VaultPadlock is restarted, BLE data is read from stdin if data was stored in MongoDB.
// This means that the BLE data is only registered once, and subsequent runs of the program will use the stored data and
// require that same device to be present for authentication. (Note: To re-register a new device, simply delete the existing
// BLE data in MongoDB and restart the program.)

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

	// BLE data non-existent in MongoDB, register, stdout and listen for BLE device.
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

		select {}

	// BLE data exists in MongoDB, read from stdin and directly goes to detection state.
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
