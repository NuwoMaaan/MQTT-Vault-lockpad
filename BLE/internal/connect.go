package internal

import (
	"bytes"
	"encoding/hex"
	"fmt"
	"os"

	"tinygo.org/x/bluetooth"
)

func ConnectToPeripheral(adapter *bluetooth.Adapter, device bluetooth.ScanResult, token string) error {
	fmt.Println("Attempting connection...")
	conn, err := adapter.Connect(device.Address, bluetooth.ConnectionParams{})
	if err != nil {
		return fmt.Errorf("Connct to periphal error: %w", err)
	}

	defer conn.Disconnect()

	discovery, err := Discover(&conn)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Discovery error:", err)
	}

	err = writeToPeripheral(discovery, token)
	if err != nil {
		fmt.Fprintln(os.Stderr, "write to peripheral error:", err)
	}

	return nil
}

func writeToPeripheral(discovery *Discovery, token string) error {

	payload, err := hex.DecodeString(token)
	if err != nil {
		return fmt.Errorf("decode token: %w", err)
	}
	_, err = discovery.deviceChar.WriteWithoutResponse(payload)
	if err != nil {
		return fmt.Errorf("write token: %w", err)
	}

	buf := make([]byte, 512) // oversized buffer is fine
	m, err := discovery.deviceChar.Read(buf)
	if err != nil {
		return fmt.Errorf("read back: %w", err)
	}

	got := buf[:m]
	if !bytes.Equal(got, payload) {
		return fmt.Errorf("verification failed: not equal")
	}
	// fmt.Println("wrote:", n, "bytes")
	// fmt.Println("read back hex:", hex.EncodeToString(got))
	// fmt.Println("verification passed")
	return nil
}
