package src

import (
	"fmt"
	"os/exec"
	"runtime"
)

func OpenApp() error {
	var err error
	url := "http://localhost:3000"
	switch runtime.GOOS {
	case "windows":
		err = exec.Command("cmd", "/c", "start", url).Run()
	case "darwin": // macOS
		err = exec.Command("open", url).Run()
	case "linux":
		err = exec.Command("xdg-open", url).Run()
	default:
		return fmt.Errorf("unsupported platform: %s", runtime.GOOS)
	}

	if err != nil {
		return fmt.Errorf("failed to open browser: %w", err)
	}

	return nil
}
