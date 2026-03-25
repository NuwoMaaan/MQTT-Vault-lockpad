package internal

import (
	"fmt"

	"tinygo.org/x/bluetooth"
)

func ConnectAndWriteToken(adapter *bluetooth.Adapter, device bluetooth.ScanResult, token string) error {
	fmt.Println("Attempting connection...")
	conn, err := adapter.Connect(device.Address, bluetooth.ConnectionParams{})
	if err != nil {
		return fmt.Errorf("Connct to periphal error: %w", err)
	}

	defer conn.Disconnect()

	err = Discover(conn, token)
	return err
}
