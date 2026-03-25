package internal

import (
	"fmt"

	"tinygo.org/x/bluetooth"
)

// serviceUUID, err := bluetooth.ParseUUID("0D5549A6-DDAF-4600-9EC5-8F1069B2D9C9")
// if err != nil {
// 	return err
// }

// charUUID, err := bluetooth.ParseUUID("2AC9F864-1B2F-4FE3-BD6C-6BB12EB04185")
// if err != nil {
// 	return err
// }

type Discovery struct {
	deviceService bluetooth.DeviceService
	deviceChar    bluetooth.DeviceCharacteristic
}

func Discover(conn *bluetooth.Device) (*Discovery, error) {
	// fmt.Println("Attempting to discover services...")
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
		return nil, fmt.Errorf("Discovery serviceUUID error: %w", err)
	}

	characteristics, err := services[0].DiscoverCharacteristics([]bluetooth.UUID{charUUID})
	if err != nil {
		return nil, fmt.Errorf("Discovery charactisticUUID error: %w", err)
	}

	// Right now discovery is limited to one device
	discovery := &Discovery{
		deviceService: services[0],
		deviceChar:    characteristics[0],
	}

	return discovery, nil
}
