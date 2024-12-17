#!/usr/bin/env pwsh
# Qualcomm DSP Check Script for Windows 11 Snapdragon Laptops
# Detect DSP driver, processes, and kernel modules.

Write-Output "=== Qualcomm DSP Detection Tool ==="

# Function to check Qualcomm DSP-related drivers
function Check-DSPDrivers {
    Write-Output "`n[+] Checking for Qualcomm DSP-related drivers..."

    # Searching for Qualcomm DSP or adsprpc drivers
    $dspDrivers = Get-WmiObject Win32_PnPSignedDriver | Where-Object {
        $_.DeviceName -match "Qualcomm" -or $_.InfName -match "dsp|adsprpc"
    }

    if ($dspDrivers) {
        Write-Output "[!] Qualcomm DSP Driver Detected:"
        $dspDrivers | Format-Table DeviceName, Manufacturer, DriverVersion, InfName -AutoSize
    } else {
        Write-Output "[+] No Qualcomm DSP-related drivers found."
    }
}

# Function to check for running processes with DSP interaction
function Check-DSPProcesses {
    Write-Output "`n[+] Checking for DSP-related processes..."

    # Look for running Qualcomm DSP processes
    $dspProcesses = Get-Process | Where-Object {
        $_.ProcessName -match "qcom|dsp|adsprpc"
    }

    if ($dspProcesses) {
        Write-Output "[!] Potential DSP-related processes found:"
        $dspProcesses | Format-Table ProcessName, Id, Path -AutoSize
    } else {
        Write-Output "[+] No DSP-related processes detected."
    }
}

# Function to check kernel drivers (loaded DSP modules)
function Check-KernelDrivers {
    Write-Output "`n[+] Checking loaded kernel drivers..."

    # List loaded drivers and search for Qualcomm DSP-related modules
    $kernelDrivers = Get-CimInstance Win32_SystemDriver | Where-Object {
        $_.Name -match "qcom|dsp|adsprpc"
    }

    if ($kernelDrivers) {
        Write-Output "[!] Qualcomm DSP-related kernel drivers found:"
        $kernelDrivers | Format-Table Name, State, PathName, StartMode -AutoSize
    } else {
        Write-Output "[+] No Qualcomm DSP-related kernel drivers detected."
    }
}

# Main Execution
Write-Output "`nStarting Qualcomm DSP Detection on Windows 11..."
Check-DSPDrivers
Check-DSPProcesses
Check-KernelDrivers

Write-Output "`n=== Detection Complete ==="
