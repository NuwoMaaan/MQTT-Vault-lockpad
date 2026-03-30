package internal

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
	"tinygo.org/x/bluetooth"
)

// serviceUUID := bluetooth.NewUUID([16]byte{
// 	0x0D, 0x55, 0x49, 0xA6,
// 	0xDD, 0xAF,
// 	0x46, 0x00,
// 	0x9E, 0xC5,
// 	0x8F, 0x10, 0x69, 0xB2, 0xD9, 0xC9,
// })

// charUUID := bluetooth.NewUUID([16]byte{
// 	0x2A, 0xC9, 0xF8, 0x64,
// 	0x1B, 0x2F,
// 	0x4F, 0xE3,
// 	0xBD, 0x6C,
// 	0x6B, 0xB1, 0x2E, 0xB0, 0x41, 0x85,
// })

type Discovery struct {
	deviceService bluetooth.DeviceService
	deviceChar    bluetooth.DeviceCharacteristic
}

func loadEnv() error {
	err := godotenv.Load()
	if err != nil {
		return fmt.Errorf("Error loading .env file: %w", err)
	}
	return nil
}

func Discover(conn *bluetooth.Device) (*Discovery, error) {
	if err := loadEnv(); err != nil {
		return nil, err
	}

	serviceUUIDStr := os.Getenv("ServiceUUID")
	charUUIDStr := os.Getenv("CharacteristicUUID")

	if serviceUUIDStr == "" {
		return nil, fmt.Errorf("ServiceUUID is empty")
	}
	if charUUIDStr == "" {
		return nil, fmt.Errorf("CharacteristicUUID is empty")
	}

	serviceUUID, err := bluetooth.ParseUUID(serviceUUIDStr)
	if err != nil {
		return nil, fmt.Errorf("invalid ServiceUUID %q: %w", serviceUUIDStr, err)
	}

	charUUID, err := bluetooth.ParseUUID(charUUIDStr)
	if err != nil {
		return nil, fmt.Errorf("invalid CharacteristicUUID %q: %w", charUUIDStr, err)
	}

	services, err := conn.DiscoverServices([]bluetooth.UUID{serviceUUID})
	if err != nil {
		return nil, fmt.Errorf("Discovery serviceUUID error: %w", err)
	}
	if len(services) == 0 {
		return nil, fmt.Errorf("service not found: %s", serviceUUID.String())
	}

	characteristics, err := services[0].DiscoverCharacteristics([]bluetooth.UUID{charUUID})
	if err != nil {
		return nil, fmt.Errorf("Discovery charactisticUUID error: %w", err)
	}
	if len(characteristics) == 0 {
		return nil, fmt.Errorf("characteristic not found: %s", charUUID.String())
	}

	// Right now discovery is limited to one device
	discovery := &Discovery{
		deviceService: services[0],
		deviceChar:    characteristics[0],
	}

	return discovery, nil
}
