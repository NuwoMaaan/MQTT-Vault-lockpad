package internal

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
)

type BLEData struct {
	UUID      string
	LocalName string
	Token     string
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
