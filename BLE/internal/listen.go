package internal

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"tinygo.org/x/bluetooth"
)

type PresenceEvent struct {
	Present bool
	UUID    string
	Token   string
}

func ListenAndDetect(adapter *bluetooth.Adapter, ble *BLEData) error {
	lastSeen := time.Now().Add(-10 * time.Second)
	go monitorPresence(ble.UUID, &lastSeen, ble.Token)

	err := adapter.Scan(func(adapter *bluetooth.Adapter, device bluetooth.ScanResult) {
		if device.LocalName() != ble.LocalName {
			return
		}
		lastSeen = time.Now()
	})

	if err != nil {
		return fmt.Errorf("scan error: %w", err)
	}

	return nil
}

func monitorPresence(uuid string, lastSeen *time.Time, token string) {
	currentlyPresent := false

	for {
		now := time.Now()
		present := now.Sub(*lastSeen) < 5*time.Second

		if present != currentlyPresent {
			currentlyPresent = present

			event := NewPresentEvent(present, uuid, token)

			json.NewEncoder(os.Stdout).Encode(event)
		}

		time.Sleep(1 * time.Second)
	}
}

func NewPresentEvent(present bool, uuid string, token string) *PresenceEvent {
	event := &PresenceEvent{
		Present: present,
		UUID:    uuid,
		Token:   token,
	}
	return event
}
