package internal

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"tinygo.org/x/bluetooth"
)

type PresenceEvent struct {
	Present    bool
	DeviceUUID string
}

const (
	presenceTimeout = 1500 * time.Millisecond
	checkInterval   = 200 * time.Millisecond
	scanLoopDelay   = 300 * time.Millisecond
)

func ListenAndDetect(adapter *bluetooth.Adapter, ble *BLEData) error {
	seenCh := make(chan time.Time, 1)
	go monitorPresence(ble.DeviceUUID, seenCh)

	lastVerified := time.Now().Add(-10 * time.Second)

	for {
		device, err := waitForTarget(adapter, ble)
		if err != nil {
			return fmt.Errorf("scan error: %w", err)
		}

		if time.Since(lastVerified) < presenceTimeout {
			pushSeen(seenCh)
			time.Sleep(scanLoopDelay)
			continue
		}

		err = ConnectToPeripheral(adapter, device, ble.Token, "read")
		if err == nil {
			now := time.Now()
			lastVerified = now
			pushSeen(seenCh)
		}

		time.Sleep(scanLoopDelay)
	}
}

func waitForTarget(adapter *bluetooth.Adapter, ble *BLEData) (bluetooth.ScanResult, error) {
	foundCh := make(chan bluetooth.ScanResult, 1)

	err := adapter.Scan(func(adapter *bluetooth.Adapter, device bluetooth.ScanResult) {
		if device.LocalName() != ble.LocalName || device.Address.String() != ble.DeviceUUID {
			return
		}

		select {
		case foundCh <- device:
		default:
		}

		_ = adapter.StopScan()
	})
	if err != nil {
		return bluetooth.ScanResult{}, err
	}

	device := <-foundCh
	return device, nil
}

func pushSeen(seenCh chan time.Time) {
	now := time.Now()

	select {
	case seenCh <- now:
	default:
		<-seenCh
		seenCh <- now
	}
}

func monitorPresence(uuid string, seenCh <-chan time.Time) {
	currentlyPresent := false
	lastSeen := time.Now().Add(-10 * time.Second)

	ticker := time.NewTicker(checkInterval)
	defer ticker.Stop()

	for {
		select {
		case t := <-seenCh:
			lastSeen = t

		case <-ticker.C:
			present := time.Since(lastSeen) < presenceTimeout
			if present != currentlyPresent {
				currentlyPresent = present
				event := newPresentEvent(present, uuid)
				json.NewEncoder(os.Stdout).Encode(event)
			}
		}
	}
}

func newPresentEvent(present bool, uuid string) *PresenceEvent {
	return &PresenceEvent{
		Present:    present,
		DeviceUUID: uuid,
	}
}
