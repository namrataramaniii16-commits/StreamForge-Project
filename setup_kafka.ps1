$ErrorActionPreference = "Stop"
$ToolsDir = "C:\Users\lenovo\StreamForge\StreamForge-Project\.tools"
if (-Not (Test-Path $ToolsDir)) {
    New-Item -ItemType Directory -Path $ToolsDir | Out-Null
}

# 1. Download & Extract Java
$JavaZip = "$ToolsDir\java.zip"
if (-Not (Test-Path "$ToolsDir\java")) {
    if (-Not (Test-Path $JavaZip)) {
        Write-Host "Downloading OpenJDK..."
        # Using Microsoft Build of OpenJDK 17
        Invoke-WebRequest -Uri "https://aka.ms/download-jdk/microsoft-jdk-17-windows-x64.zip" -OutFile $JavaZip
    }
    Write-Host "Extracting OpenJDK..."
    Expand-Archive -Path $JavaZip -DestinationPath "$ToolsDir\java" -Force
}

$JavaHome = (Get-ChildItem -Path "$ToolsDir\java" -Directory | Select-Object -First 1).FullName
$env:JAVA_HOME = $JavaHome
$env:PATH = "$JavaHome\bin;" + $env:PATH

# Verify Java
Write-Host "Java Version:"
java -version

# 2. Download & Extract Kafka
$KafkaTgz = "$ToolsDir\kafka.tgz"
if (-Not (Test-Path "$ToolsDir\kafka_2.13-3.6.1")) {
    if (-Not (Test-Path $KafkaTgz)) {
        Write-Host "Downloading Kafka 3.6.1..."
        Invoke-WebRequest -Uri "https://archive.apache.org/dist/kafka/3.6.1/kafka_2.13-3.6.1.tgz" -OutFile $KafkaTgz
    }
    Write-Host "Extracting Kafka..."
    Set-Location $ToolsDir
    tar -xzf kafka.tgz
}

$KafkaDir = "$ToolsDir\kafka_2.13-3.6.1"

# 3. Modify Kafka config to run nicely on Windows (fix data dirs)
$ZkConfig = "$KafkaDir\config\zookeeper.properties"
$KafkaConfig = "$KafkaDir\config\server.properties"

(Get-Content $ZkConfig) -replace 'dataDir=/tmp/zookeeper', "dataDir=$($ToolsDir.Replace('\','/'))/zookeeper-data" | Set-Content $ZkConfig
(Get-Content $KafkaConfig) -replace 'log.dirs=/tmp/kafka-logs', "log.dirs=$($ToolsDir.Replace('\','/'))/kafka-logs" | Set-Content $KafkaConfig

# 4. Start Zookeeper (in background)
Write-Host "Starting Zookeeper..."
Start-Process -FilePath "$KafkaDir\bin\windows\zookeeper-server-start.bat" -ArgumentList "$ZkConfig" -WindowStyle Minimized

Start-Sleep -Seconds 10

# 5. Start Kafka (in background)
Write-Host "Starting Kafka..."
Start-Process -FilePath "$KafkaDir\bin\windows\kafka-server-start.bat" -ArgumentList "$KafkaConfig" -WindowStyle Minimized

Write-Host "Kafka successfully started on localhost:9092!"
