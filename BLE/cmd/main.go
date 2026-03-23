package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/NuwoMaaan/MQTT-Vault-lockpad/BLE/internal"
	"tinygo.org/x/bluetooth"
)

var adapter = bluetooth.DefaultAdapter

func main() {
	must("enable BLE stack", adapter.Enable())

	err := adapter.Scan(func(adapter *bluetooth.Adapter, device bluetooth.ScanResult) {
		if device.LocalName() != "My BLE Tester" {
			return
		}

		token, err := internal.TokenGenerate()
		if err != nil {
			fmt.Fprintln(os.Stderr, "token generation failed:", err)
			return
		}

		ble := internal.NewBLEData(
			device.Address.String(),
			device.LocalName(),
			token,
		)

		json.NewEncoder(os.Stdout).Encode(ble)

		must("stop scan", adapter.StopScan())

	})

	must("start scan", err)
}

func must(action string, err error) {
	if err != nil {
		panic("failed to " + action + ": " + err.Error())
	}
}
