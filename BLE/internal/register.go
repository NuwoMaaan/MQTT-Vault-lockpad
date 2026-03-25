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

	token, err := TokenGenerate()
	if err != nil {
		return nil, err
	}

	err = connectAndWriteToken(adapter, device, token)
	if err != nil {
		return nil, err
	}

	ble = NewBLEData(
		device.Address.String(),
		device.LocalName(),
		token,
	)

	return ble, nil
}

func NewBLEData(uuid string, localName string, token string) *BLEData {
	return &BLEData{
		UUID:      uuid,
		LocalName: localName,
		Token:     token,
	}
}

func TokenGenerate() (string, error) {
	b := make([]byte, 32) // 32 bytes = 256-bit token
	_, err := rand.Read(b)
	if err != nil {
		return "", fmt.Errorf("failed to generate token: %w", err)
	}

	return hex.EncodeToString(b), nil
}

func connectAndWriteToken(adapter *bluetooth.Adapter, device bluetooth.ScanResult, token string) error {
	fmt.Println("Attempting connection...")
	conn, err := adapter.Connect(device.Address, bluetooth.ConnectionParams{})
	if err != nil {
		return fmt.Errorf("Connct to periphal error: %w", err)
	}
	fmt.Println(token)

	defer conn.Disconnect()

	err = discoverServices(conn)
	return err
}

func discoverServices(conn bluetooth.Device) error {
	fmt.Println("Attempting to discover services...")
	serviceUUID := bluetooth.NewUUID([16]byte{
		0x0D, 0x55, 0x49, 0xA6,
		0xDD, 0xAF,
		0x46, 0x00,
		0x9E, 0xC5,
		0x8F, 0x10, 0x69, 0xB2, 0xD9, 0xC9,
	})

	charUUID := bluetooth.NewUUID([16]byte{
		0x2A, 0xC9, 0xF8, 0x64,
		0x1B, 0x2F,
		0x4F, 0xE3,
		0xBD, 0x6C,
		0x6B, 0xB1, 0x2E, 0xB0, 0x41, 0x85,
	})

	services, err := conn.DiscoverServices([]bluetooth.UUID{serviceUUID})
	if err != nil {
		return err
	}

	for i, service := range services {
		fmt.Println(i, "service uuid:", service.UUID())
		characteristics, err := service.DiscoverCharacteristics([]bluetooth.UUID{charUUID})
		if err != nil {
			return err
		}
		fmt.Println(characteristics)
	}

	return nil
}
