package src

import (
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"time"
)

func HealthCheck(LogLevel string) {
	log.Println("Health check started")
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	client := http.Client{
		Timeout: 5 * time.Second,
	}
	
	// Используем адрес бэкенда из конфигурации
	backendHost := GetBackendHost()
	healthURL := "http://" + backendHost + "/health"
	
	for range ticker.C {
		resp, err := client.Get(healthURL)
		if err != nil || resp.StatusCode != http.StatusOK {
			log.Println("Backend health check failed: ", err)
			os.Exit(1)
		}
		if LogLevel == "debug" {
			log.Println("Backend health check passed")
		}
		resp.Body.Close()
	}
}

func buildCmdArgs(LogLevel string, DryRun bool, RawLogs bool) []string {
	var mainPath string
	if runtime.GOOS == "windows" {
		mainPath = "app/main.py"
	} else {
		mainPath = "main.py"
	}
	cmdArgs := []string{mainPath, "-l", LogLevel}
	if DryRun {
		cmdArgs = append(cmdArgs, "--dry-run")
	}
	if RawLogs {
		cmdArgs = append(cmdArgs, "--raw-logs")
	}
	return cmdArgs
}

func createVenv() {
	currentDir, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Creating virtual environment in", currentDir+"/.venv")
	createCmd := exec.Command("python", "-m", "venv", ".venv")
	createCmd.Stdout = os.Stdout
	createCmd.Stderr = os.Stderr
	if err := createCmd.Run(); err != nil {
		log.Fatal("Failed to create venv:", err)
	}
	log.Println("Virtual environment created. Installing dependencies...")
	pipCmd := ".venv\\Scripts\\pip"
	installCmd := exec.Command(pipCmd, "install", "-r", "app/requirements.txt")
	installCmd.Stdout = os.Stdout
	installCmd.Stderr = os.Stderr
	if err := installCmd.Run(); err != nil {
		log.Fatal("Failed to install dependencies:", err)
	}
	log.Println("Dependencies installed")
}

func subprocessRun(args []string) *exec.Cmd {
	pythonCmd, args := args[0], args[1:]
	cmd := exec.Command(pythonCmd, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	go func() {
		if err := cmd.Start(); err != nil {
			log.Fatal("Python script failed:", err)
		}
	}()
	return cmd
}

func windowsStart(LogLevel string, DryRun bool, RawLogs bool) *exec.Cmd {
	pythonCmd := ".venv\\Scripts\\python"
	if _, err := os.Stat(".venv"); os.IsNotExist(err) {
		createVenv()
	}
	args := []string{pythonCmd}
	args = append(args, buildCmdArgs(LogLevel, DryRun, RawLogs)...)
	return subprocessRun(args)
}

func linuxStart(LogLevel string, DryRun bool, RawLogs bool) *exec.Cmd {
	args := []string{"python3"}
	args = append(args, buildCmdArgs(LogLevel, DryRun, RawLogs)...)
	return subprocessRun(args)
}

func PythonProcess(LogLevel string, DryRun bool, RawLogs bool) *exec.Cmd {
	if runtime.GOOS != "windows" {
		return linuxStart(LogLevel, DryRun, RawLogs)
	} else {
		return windowsStart(LogLevel, DryRun, RawLogs)
	}
}
