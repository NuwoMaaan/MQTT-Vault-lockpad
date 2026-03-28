package internal

import (
	"bytes"
	"encoding/hex"
	"fmt"
	"time"

	"tinygo.org/x/bluetooth"
)

func ConnectToPeripheral(adapter *bluetooth.Adapter, device bluetooth.ScanResult, token string, flag string) error {
	conn, err := adapter.Connect(device.Address, bluetooth.ConnectionParams{})
	if err != nil {
		return fmt.Errorf("connect to peripheral error: %w", err)
	}
	defer conn.Disconnect()

	discovery, err := Discover(&conn)
	if err != nil {
		return fmt.Errorf("discovery error: %w", err)
	}

	if flag == "read" {
		if err := readFromPeripheral(discovery, token); err != nil {
			return fmt.Errorf("read peripheral fail: %w", err)
		}
	}

	if flag == "write" {
		if err := writeToPeripheral(discovery, token); err != nil {
			return fmt.Errorf("write peripheral error: %w", err)
		}
	}

	return nil
}

func readFromPeripheral(discovery *Discovery, token string) error {
	buf := make([]byte, 512)
	m, err := discovery.deviceChar.Read(buf)
	if err != nil {
		return fmt.Errorf("read back: %w", err)
	}
	byteToken, err := hex.DecodeString(token)
	read := buf[:m]
	if !bytes.Equal(read, byteToken) {
		return fmt.Errorf("verification failed: invalid token")
	}
	return nil
}

func writeToPeripheral(discovery *Discovery, token string) error {
	payload, err := hex.DecodeString(token)
	if err != nil {
		return fmt.Errorf("hex decode to bytes (token): %w", err)
	}
	_, err = discovery.deviceChar.WriteWithoutResponse(payload)
	if err != nil {
		return fmt.Errorf("write token: %w", err)
	}
	time.Sleep(300 * time.Millisecond)
	return nil
}
