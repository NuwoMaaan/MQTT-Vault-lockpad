package internal

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"

	"tinygo.org/x/bluetooth"
)

type BLEData struct {
	UUID      string
	LocalName string
	Token     string
}

func Register(adapter *bluetooth.Adapter) (*BLEData, error) {
	var ble *BLEData
	found := make(chan bluetooth.ScanResult, 1)

	err := adapter.Scan(func(adapter *bluetooth.Adapter, device bluetooth.ScanResult) {
		if device.LocalName() != "padlockAuth" {
			return
		}

		_ = adapter.StopScan()
		found <- device
	})
	if err != nil {
		return nil, err
	}

	device := <-found

	token, err := tokenGenerate()
	if err != nil {
		return nil, err
	}

	err = ConnectAndWriteToken(adapter, device, token)
	if err != nil {
		return nil, err
	}

	ble = newBLEData(
		device.Address.String(),
		device.LocalName(),
		token,
	)

	return ble, nil
}

func newBLEData(uuid string, localName string, token string) *BLEData {
	return &BLEData{
		UUID:      uuid,
		LocalName: localName,
		Token:     token,
	}
}

func tokenGenerate() (string, error) {
	b := make([]byte, 32) // 32 bytes = 256-bit token
	_, err := rand.Read(b)
	if err != nil {
		return "", fmt.Errorf("failed to generate token: %w", err)
	}

	return hex.EncodeToString(b), nil
}
